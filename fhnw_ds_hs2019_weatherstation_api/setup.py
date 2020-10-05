from setuptools import setup

with open("Readme.md", "r") as fh:
    long_description = fh.read()

# need to use pandas<0.24 due to https://github.com/influxdata/influxdb-python/issues/696
setup(name='fhnw_ds_hs2019_weatherstation_api',
      version='0.20',
      description='Provides access to the Wasserschutzpolizei Zurich live and historic weather data.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/markif/WeatherStation_HS2019',
      author='Fabian',
      license='MIT',
      packages=['fhnw_ds_hs2019_weatherstation_api'],
      install_requires=[
          'pandas',
          'influxdb',
          'requests',
          'tzlocal',
          'pytz',
      ],
      zip_safe=False)
