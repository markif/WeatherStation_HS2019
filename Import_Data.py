#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys
get_ipython().system('{sys.executable} -m pip install ./fhnw_ds_hs2019_weatherstation_api/dist/fhnw_ds_hs2019_weatherstation_api-0.11-py3-none-any.whl')


# In[3]:


from fhnw_ds_hs2019_weatherstation_api import data_import as weather
import os

# DB and CSV config
config = weather.Config()
# define CSV path
config.historic_data_folder='.'+os.sep+'data'
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


# In[ ]:




