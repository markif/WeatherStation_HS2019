#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
#from influxdb import InfluxDBClient
from influxdb import DataFrameClient
import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
import signal
import sys
import datetime
import tzlocal
import pytz
from time import sleep
import os


# In[2]:


class Config:
    db_host='localhost'
    db_port=8086
    db_name='meteorology'
    stations = ['mythenquai', 'tiefenbrunnen']
    keys_mapping = {
        "values.air_temperature.value": "air_temperature",
        "values.barometric_pressure_qfe.value": "barometric_pressure_qfe",
        "values.dew_point.value": "dew_point",
        "values.global_radiation.value": "global_radiation",
        "values.humidity.value": "humidity",
        "values.precipitation.value": "precipitation",
        "values.timestamp_cet.value": "timestamp_cet",
        "values.water_temperature.value": "water_temperature",
        "values.wind_direction.value": "wind_direction",
        "values.wind_force_avg_10min.value": "wind_force_avg_10min",
        "values.wind_gust_max_10min.value": "wind_gust_max_10min",
        "values.wind_speed_avg_10min.value": "wind_speed_avg_10min",
        "values.windchill.value": "windchill"
    }
    historic_data_folder = '.'+os.sep+'data'
    client = None
    


# In[3]:


def __get_last_db_entry(config, station):
    query = "SELECT * FROM \"{}\" ORDER BY time DESC LIMIT 1".format(station)
    last = config.client.query(query)
    return last
    
def __extract_last_db_day(last_entry, station, default_last_db_day):
    val = last_entry[station]
          
    if val is not None: 
        if not val.index.empty:
            return val.index[0]
        
    return default_last_db_day

def __get_data_of_day(day, station):
    base_url = 'https://tecdottir.herokuapp.com/measurements/{}'
    day_str = day.strftime("%Y-%m-%d")
    print("Query "+ station +" at "+day_str)
    payload = {'startDate': day_str, 'endDate': day_str}
    url = base_url.format(station)
    response = requests.get(url, params=payload)
    if(response.ok):
        #print(response.json())
        jData = json.loads(response.content)
        return jData
    else:
        response.raise_for_status()
        
def __define_types(data, date_format):
    data['timestamp_cet'] = pd.to_datetime(data['timestamp_cet'], format=date_format)
    # set the correct timezone
    #data['timestamp_cet'] = data['timestamp_cet'].dt.tz_localize('Europe/Zurich')
    data.set_index('timestamp_cet', inplace=True)
    
    for column in data.columns[0:]:
        data[column] = data[column].astype(np.float64)
    
    return data
        
def __clean_data(config, data_of_last_day, last_db_entry, date_format, station):
    normalized = json_normalize(data_of_last_day['result'])
    
    for column in normalized.columns[0:]:   
        mapping = config.keys_mapping.get(column, None)
        if mapping is not None:
            normalized[mapping] = normalized[column]
            
        normalized.drop(columns=column, inplace=True)
    
    # make sure types/index are correct
    normalized = __define_types(normalized, date_format)
    
    #print("Normalized index "+str(normalized.index))
    #print("Last db index "+str(lastDBEntry[station].index))
    
    # remove all entries older than last element
    last_db_entry_time = last_db_entry[station].index[0].replace(tzinfo=None)   
    normalized.drop(normalized[normalized.index <= last_db_entry_time].index, inplace=True)
    
    return normalized
        
def __add_data_to_db(config, data, station):
    config.client.write_points(data, station, time_precision='s', database=config.db_name)
    
def __append_df_to_csv(data, csv_file_path, sep=","):
    header = False
    if not os.path.isfile(csv_file_path):
        header = True

    data.to_csv(csv_file_path, mode='a', sep=sep, header=header)
    
def __signal_handler(sig, frame):
    sys.exit(0)
    
def connect_db(config):
    """Connects to the database and initializes the client

    Parameters:
    config (Config): The Config containing the DB connection info

   """
    if config.client is None:
        # https://www.influxdata.com/blog/getting-started-python-influxdb/
        config.client = DataFrameClient(host=config.db_host, port=config.db_port, database=config.db_name)
        config.client.switch_database(config.db_name)

def clean_db(config):
    """Reads the historic data of the Wasserschutzpolizei Zurich from CSV files

    Parameters:
    config (Config): The Config containing the DB connection info and CSV folder info

   """
    config.client.drop_database(config.db_name)
    config.client.create_database(config.db_name)

def import_historic_data(config):
    """Reads the historic data of the Wasserschutzpolizei Zurich from CSV files

    Parameters:
    config (Config): The Config containing the DB connection info and CSV folder info

   """
    # read historic data from files
    chunksize = 10000
    
    for station in config.stations:
        last_entry = __get_last_db_entry(config, station)
          
        if last_entry is None or not last_entry:
            print("Load historic data for "+station + " ...")
        
            file_name = os.path.join(config.historic_data_folder ,"messwerte_" + station + "_2007-2018.csv")
            if os.path.isfile(file_name):
                print("\tLoad "+ file_name)
                for chunk in pd.read_csv(file_name, delimiter=',', chunksize=chunksize):
                    chunk = __define_types(chunk, '%Y-%m-%dT%H:%M:%S')
                    __add_data_to_db(config, chunk, station)
            else:
                print(file_name +" does not seem to exist.")
                
            current_time = datetime.datetime.now(tzlocal.get_localzone())
            running_year = 2019
            while running_year <= current_time.year:
                file_name = os.path.join(config.historic_data_folder ,"messwerte_" + station + "_"+ str(running_year) +".csv")
                if os.path.isfile(file_name):
                    print("\tLoad "+ file_name)
                    for chunk in pd.read_csv(file_name, delimiter=',', chunksize=chunksize):
                        chunk = __define_types(chunk, '%Y-%m-%d %H:%M:%S')
                        __add_data_to_db(config, chunk, station)
                else:
                    print(file_name +" does not seem to exist.")
                running_year+=1
            
    
        print("Historic data for "+station+" loaded.")
        
        
def import_latest_data(config, append_to_csv=False, periodic_read=False):
    """Reads the latest data from the Wasserschutzpolizei Zurich weather API

    Parameters:
    config (Config): The Config containing the DB connection info and CSV folder info
    append_to_csv (bool): Defines if the data should be appended to a CSV file
    periodic_read (bool): Defines if the function should keep reading after it imported the latest data (blocking through a sleep)

   """
    # access API for current data
    current_time = datetime.datetime.now(pytz.utc)
    last_api_call = current_time.replace(second=0, microsecond=0) - datetime.timedelta(minutes=10)
    last_db_days = [last_api_call] * len(config.stations)
    new_data_received = True

    for idx, station in enumerate(config.stations):
        last_db_entry = __get_last_db_entry(config, station)
        last_db_days[idx] = __extract_last_db_day(last_db_entry, station, last_db_days[idx])

    if periodic_read:
        signal.signal(signal.SIGINT, __signal_handler)
        print("\nPress Ctrl+C to stop!\n")

    while True:
        current_time = datetime.datetime.now(pytz.utc)

        # check if all historic data (retrieved from API) has been processed 
        if periodic_read and max(last_db_days) >= last_api_call: 
            # once every 10 Min
            sleep_until = current_time + datetime.timedelta(minutes=10)       
            # once per day
            # sleep_until = current_time + datetime.timedelta(days=1)
            # sleep_until = sleep_until.replace(hour=6, minute=0, second=0, microsecond=0)
            sleep_sec = (sleep_until - current_time).total_seconds()

            print("Sleep for "+str(sleep_sec) + "s (from " + str(current_time) +" until "+str(sleep_until) + ") when next data will be queried.")
            sleep(sleep_sec)
            current_time = datetime.datetime.now(pytz.utc)
            last_api_call = current_time.replace(second=0, microsecond=0)
        elif not periodic_read and not new_data_received:
            # stop here
            return;

        new_data_received = False
        for idx, station in enumerate(config.stations):
            last_db_entry = __get_last_db_entry(config, station)
            last_db_days[idx] = __extract_last_db_day(last_db_entry, station, last_db_days[idx])
            data_of_last_db_day = __get_data_of_day(last_db_days[idx], station)
            normalized_data = __clean_data(config, data_of_last_db_day, last_db_entry, '%d.%m.%Y %H:%M:%S', station)

            if normalized_data.size > 0:
                new_data_received = True
                __add_data_to_db(config, normalized_data, station)
                if append_to_csv:
                    __append_df_to_csv(normalized_data, os.path.join(config.historic_data_folder ,"messwerte_" + station + "_"+ str(current_time.year) +".csv"))
                print("Handle "+ station +" from "+ str(normalized_data.index[0]) +" to "+ str(normalized_data.index[-1])) 
            else:
                print("No new data received for "+station)


# In[7]:


