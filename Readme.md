# Weather Station

## InfluxData TICK Stack

[Sandbox](https://github.com/influxdata/sandbox) provides a TICK Stack that runs with Docker.

```bash
git clone https://github.com/influxdata/sandbox.git
cd sandbox 
./sandbox up
```

## Load Weather Data

Use [Import_Data.py](Import_Data.py) to import weather data from the a dataset provided by the [Wasserschutzpolizei Zurich](https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen). Once a day, this script also imports recent data using their [REST API](https://tecdottir.herokuapp.com/docs/).

## Visualize Data

### Chronograf

The TICK Stack comes with Chronograf. It runs on `http://localhost:8888` and provides the possibility to visualize data. 

![alt text](./pics/query_01.png "Visualization of air temperature")

## Jupiter Notebook

I used a [jupiter notebook](Import_Data.ipynb) to craft the [python code](Import_Data.py). Either use your local installation or run

```bash
docker run --name datascience-notebook --net=host -p 8888:8888 -v "$(pwd)":/home/jovyan/work -it --rm i4ds/datascience-notebook start-notebook.sh --NotebookApp.token=''
firefox http://127.0.0.1:8888
```

In order to extract the python script run

```bash
docker exec -it datascience-notebook /bin/bash
jupyter nbconvert --to script Import_Data.ipynb
```
