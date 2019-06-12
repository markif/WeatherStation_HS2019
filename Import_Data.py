#!/usr/bin/env python
# coding: utf-8

# In[7]:


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
from time import sleep
import os

db_name='meteorology'
stations = ['mythenquai', 'tiefenbrunnen']
keysMapping = {
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
# https://www.influxdata.com/blog/getting-started-python-influxdb/
client = DataFrameClient(host='localhost', port=8086, database=db_name)


# In[8]:


def cleanDB(client, dbName):
    client.drop_database(dbName)
    client.create_database(dbName)

def getLastDBEntry(client, station):
    query = "SELECT * FROM \"{}\" ORDER BY time DESC LIMIT 1".format(station)
    last = client.query(query)
    return last
    
def extractLastDBDay(lastEntry, station):
    lastDay = lastEntry[station].index
    return lastDay[0]

def getDataOfDay(station, day):
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
        
def defineTypes(data, dateFormat):
    data['timestamp_cet'] = pd.to_datetime(data['timestamp_cet'], format=dateFormat)
    # set the correct timezone
    #data['timestamp_cet'] = data['timestamp_cet'].dt.tz_localize('Europe/Zurich')
    data.set_index('timestamp_cet', inplace=True)
    
    for column in data.columns[0:]:
        data[column] = data[column].astype(np.float64)
    
    return data
        
def cleanData(keysMapping, dataOfLastDay, lastDBEntry, station, dateFormat):
    normalized = json_normalize(dataOfLastDay['result'])
    
    for column in normalized.columns[0:]:   
        mapping = keysMapping.get(column, None)
        if mapping is not None:
            normalized[mapping] = normalized[column]
            
        normalized.drop(columns=column, inplace=True)
    
    # make sure types/index are correct
    defineTypes(normalized, dateFormat)
    
    #print("Normalized index "+str(normalized.index))
    #print("Last db index "+str(lastDBEntry[station].index))
    
    # remove all entries older than last element
    #normalized.drop(normalized[normalized.index <= lastDBEntry[station].index].index, inplace=True)
    
    return normalized
        
def addDataToDB(client, data, station, dbName):
    client.write_points(data, station, time_precision='s', database=dbName)
    
def appendDFToCSV(data, csvFilePath, sep=","):
    header = False
    if not os.path.isfile(csvFilePath):
        header = True

    data.to_csv(csvFilePath, mode='a', sep=sep, header=header)


# In[3]:


def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# In[11]:


# clean DB
cleanDB(client, db_name)
client.switch_database(db_name)
#client.get_list_database()


# In[15]:


# read historic data from files
chunksize = 10000
    
for station in stations:
    lastEntry = getLastDBEntry(client, station)
          
    if lastEntry is None or len(lastEntry) == 0:
        print("Load historic data for "+station + " ...")
        
        for chunk in pd.read_csv("./data/messwerte_" + station + "_2007-2018.csv", delimiter=',', chunksize=chunksize):
            defineTypes(chunk, '%Y-%m-%dT%H:%M:%S')
            addDataToDB(client, chunk, station, db_name)

        for chunk in pd.read_csv("./data/messwerte_" + station + "_2019.csv", delimiter=',', chunksize=chunksize):
            defineTypes(chunk, '%Y-%m-%d %H:%M:%S')
            addDataToDB(client, chunk, station, db_name)
            
    
    print("Historic data for "+station+" loaded.")


# In[16]:


# access API for current data
currentDayStart = datetime.datetime.now(tzlocal.get_localzone())
currentDayStart = currentDayStart.replace(hour=0, minute=0, second=0, microsecond=0)
lastDBDays = [datetime.datetime.strptime("2018-01-01", '%Y-%m-%d')] * len(stations)

for idx, station in enumerate(stations):
    lastDBEntry = getLastDBEntry(client, station)
    lastDBDays[idx] = extractLastDBDay(lastDBEntry, station)
    
while True:
    # check if all historic data (retrieved from API) has been processed    
    if max(lastDBDays) >= currentDayStart:
        currentTime = datetime.datetime.now(tzlocal.get_localzone()) 
        sleepUntil = currentTime + datetime.timedelta(days=1)
        sleepUntil = sleepUntil.replace(hour=6, minute=0, second=0, microsecond=0)
        sleepSec = (sleepUntil - currentTime).total_seconds()
        
        print("Sleep for "+str(sleepSec) + "s (from " + str(currentTime) +" until "+str(sleepUntil) + ") when next data will be queried.")
        sleep(sleepSec)
        currentDayStart = datetime.datetime.now(tzlocal.get_localzone())
        currentDayStart = currentDayStart.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for idx, station in enumerate(stations):
        lastDBEntry = getLastDBEntry(client, station)
        lastDBDays[idx] = extractLastDBDay(lastDBEntry, station)
        dataOfLastDBDay = getDataOfDay(station, lastDBDays[idx])
        normalizedData = cleanData(keysMapping, dataOfLastDBDay, lastDBEntry, station, '%d.%m.%Y %H:%M:%S')
        addDataToDB(client, normalizedData, station, db_name)
        appendDFToCSV(normalizedData, "./data/messwerte_" + station + "_2019.csv")
        
        print("Handle "+ station +" from "+ str(normalizedData.index[0]) +" to "+ str(normalizedData.index[-1]))    


# In[ ]:




