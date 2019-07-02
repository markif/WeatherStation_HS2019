# Build Python Package

Use the [jupiter notebook](data_import.ipynb) to craft the python package. Either use a local installation or run

```bash
docker run -e TZ=Europe/Zurich --name datascience-notebook --net=host -p 8888:8888 -v "$(pwd)":/home/jovyan/work -it --rm i4ds/datascience-notebook start-notebook.sh --NotebookApp.token=''
firefox http://127.0.0.1:8888
```

Increase the version number in [setup.py](../fhnw_ds_hs2019_weatherstation_api/setup.py).


In order to extract the python script and upload it to pypi run

```bash
docker exec -it datascience-notebook /bin/bash
cd work/src
jupyter nbconvert --to script data_import.ipynb
sed -i '/# Start load data code block/Q' data_import.py
cp data_import.py ../fhnw_ds_hs2019_weatherstation_api/fhnw_ds_hs2019_weatherstation_api/
rm -f data_import.py
cd ../fhnw_ds_hs2019_weatherstation_api
rm -rf dist/*
python3 setup.py bdist_wheel
python3 -m twine upload dist/*
cd ../src
```

Upload everything to the git repository.
