# Headless Raspberry Pi

Run your Raspberry Pi without the need to attach a display, keyboard and mouse (i.e. run it on server mode).

## Enable SSH

Allows you to ssh to your Raspberry Pi (see also [here](https://www.raspberrypi.org/documentation/remote-access/ssh/)).

Add the file *ssh* onto the boot partition of the SD card.
 
```bash 
touch ssh
```

## TICK Installation (Native)

Please follow [this procedure](https://www.influxdata.com/blog/running-the-tick-stack-on-a-raspberry-pi) to install the TICK stack on your Raspberry Pi.

```bash
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
# make sure you use the correct version name (buster)
echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update
sudo apt-get install influxdb 
sudo systemctl restart influxdb
# install these if needed
sudo apt-get install telegraf chronograf kapacitor
```

## Store Historc Weather Data

The script provided at the [weatherstation-api page](https://pypi.org/project/fhnw-ds-hs2019-weatherstation-api) indicates how to load historic data (stored in csv files) into InfluxDB.

```bash
# prepare folder structure
sudo mkdir -p /scripts/store_data
cd /scripts/store_data

# download the script
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/store_data/store-historic-data.sh
sudo chmod u+x store-historic-data.sh

# get the historic data
sudo mkdir data
cd data
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_mythenquai_2007-2018.csv
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_tiefenbrunnen_2007-2018.csv
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_mythenquai_2019.csv
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/data/messwerte_tiefenbrunnen_2019.csv
cd ..


# store historic data
sudo ./store-historic-data.sh
```

## Store Live Weather Data

The Wasserschutzpolizei Zurich updates the weather data every 10 minutes. Accordingly, you should fetch the data from their API every 10 minutes (please make sure you do not fetch the data in a shorter period because otherwise your queries can result in a [denial of service attack](https://en.wikipedia.org/wiki/Denial-of-service_attack) (and the Wasserschutzpolizei will catch and arrest you!!!)).

There are several options on how to periodically fetch the weather data. One option is to setup a [systemd timer unit](https://www.putorius.net/using-systemd-timers.html).

```bash
# prepare folder structure
sudo mkdir -p /scripts/store_data
cd /scripts/store_data

# download the script
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/store_data/store-live-data.sh
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/store_data/store-live-data.service
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/store_data/store-live-data.timer
sudo chmod u+x store-live-data.sh

# enable the unit and timer
sudo cp store-live-data.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/store-live-data.service
sudo cp store-live-data.timer /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/store-live-data.timer
sudo systemctl daemon-reload
sudo systemctl enable store-live-data.service
sudo systemctl enable store-live-data.timer
sudo systemctl start store-live-data.timer

# check if the script runs
sudo systemctl start store-live-data.service 
journalctl -f -u store-live-data.service

# test if script is executed after startup
sudo shutdown -r now
# you will need to wait 5min
journalctl -f -u store-live-data.service
```


## Discover IP Address

Let your Raspberry Pi email its IP address on every startup. This was inspired by [Where is my Raspberry Pi?](https://medium.com/@oliverscheer/where-is-my-raspberry-pi-let-your-pi-send-you-an-email-with-its-ip-address-3a4feba7bef4).

```bash
# prepare folder structure
sudo mkdir -p /scripts/mail_ip
cd /scripts/mail_ip

# download the script
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/mail_ip/main.py
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/mail_ip/secrets.py
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/mail_ip/send-ip.service
sudo chmod u+x main.py

# replace placeholders where appropriate 
sudo nano secrets.py
sudo chmod 700 secrets.py


# test the script
sudo 
python3 main.py

# make sure it gets executed on startup
sudo cp send-ip.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/send-ip.service
sudo systemctl daemon-reload
sudo systemctl enable send-ip.service

# test the script
sudo systemctl start send-ip.service 

# test if script is executed after startup
sudo shutdown -r now
```
