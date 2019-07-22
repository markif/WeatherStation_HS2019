from setuptools import setup

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setup(name='fhnw_ds_hs2019_weatherstation_api',
      version='0.14',
      description='Provides access to the Wasserschutzpolizei Zurich live and historic weather data.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/markif/WeatherStation_HS2019',
      author='Fabian',
      license='MIT',
      packages=['fhnw_ds_hs2019_weatherstation_api'],
 #     install_requires=[
 #         'pandas',
 #         'numpy',
 #         'influxdb',
 #         'requests',
 #         'json',
 #         'datetime',
 #         'tzlocal',
 #         'pytz',
 #     ],
      zip_safe=False)
