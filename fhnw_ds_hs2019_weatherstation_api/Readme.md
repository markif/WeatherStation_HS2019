This library provides access to the [Wasserschutzpolizei Zurich](https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen) live (using this [REST API](https://tecdottir.herokuapp.com/docs/)) and historic (using these [CSV files](https://github.com/markif/WeatherStation_HS2019/tree/master/data)) weather data.

# Download Historic Data

```bash
mkdir data && cd data
wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_mythenquai_2007-2018.csv
wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_tiefenbrunnen_2007-2018.csv
wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_mythenquai_2019.csv
wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_tiefenbrunnen_2019.csv
cd ..
```

# Install Dependencies (Raspberry Pi)

```bash
wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh
chmod +x Berryconda3-2.0.0-Linux-armv7l.sh
./Berryconda3-2.0.0-Linux-armv7l.sh
sudo shutdown -r now
rm Berryconda3-2.0.0-Linux-armv7l.sh
python -m pip install --upgrade pip
conda install pandas
python -m pip install influxdb tzlocal fhnw_ds_hs2019_weatherstation_api
```

# Usage

```python
#!/usr/bin/env python

# import the library
from fhnw_ds_hs2019_weatherstation_api import data_import as weather
import os

# DB and CSV config
config = weather.Config()
# define CSV path
config.historic_data_folder='.'+os.sep+'data'
# set batch size for DB inserts (decrease for raspberry pi)
config.historic_data_chunksize=10000
# define DB host
config.db_host='localhost'

# connect to DB
weather.connect_db(config)
# clean DB
weather.clean_db(config)
# import historic data
weather.import_historic_data(config)
# import latest data (delta between last data point in DB and current time)
weather.import_latest_data(config)
```
