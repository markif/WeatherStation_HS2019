#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
get_ipython().system('{sys.executable} -m pip install ./fhnw_ds_hs2019_weatherstation_api/dist/fhnw_ds_hs2019_weatherstation_api-0.1-py3-none-any.whl')


# In[2]:


from fhnw_ds_hs2019_weatherstation_api import data_import as weather
import os

# DB and CSV config
config = weather.Config()
# define CSV path
config.historic_data_folder='.'+os.sep+'data'
# define DB host
config.db_host='localhost'

client = weather.DataFrameClient(host=config.db_host, port=config.db_port, database=config.db_name)
client.switch_database(config.db_name)
# clean DB
weather.clean_db(client, config)
weather.read_historic_data_from_file(client, config)
weather.read_data_from_api(client, config, append_to_csv=False, periodic_read=False)


# In[ ]:




