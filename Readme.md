# Weather Station

## Prerequisites

Make sure your Raspberry Pi can connect to the internet (e.g. open a Web-Browser and enter your credentials).

Make sure the time is correct (at FHNW your Pi is not abble to connect to the internet at startup to sync the time).

 (e.g. using Ubuntu from Microsoft Store - https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/)

```bash
# using a terminal on your Raspberry Pi
sudo date -s "13 AUG 2019 15:43:00" 
```

Alternatively, you might also want to send the current date from a computer (e.g. your Laptop) to your Raspberry Pi. In case you are using Windows you might want to use Ubuntu from Microsoft Store (please follow [this procedure](https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/) on how to install it).

```bash
# send the date of your computer to the Raspberry Pi - replace "host" with your Raspberry Pi's hostname or IP-address
ssh pi@host "date --set \"$(date)\""
```

Make sure you use newest software

```bash
sudo apt-get update
sudo apt-get upgrade 
```

## TICK Stack Installation

Please follow [this procedure](https://www.influxdata.com/blog/running-the-tick-stack-on-a-raspberry-pi) to install the TICK stack on your Raspberry Pi.


## Store Weather Data

This challenge uses the weather data provided by the [Wasserschutzpolizei Zurich](https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen).
The [weatherstation-api package](https://pypi.org/project/fhnw-ds-hs2019-weatherstation-api) provides the means to read historic and live data.

### Store Historc Weather Data

The script provided at the [weatherstation-api page](https://pypi.org/project/fhnw-ds-hs2019-weatherstation-api) indicates how to load historic data (stored in csv files) into InfluxDB.

### Store Live Weather Data

The Wasserschutzpolizei Zurich updates the weather data every 10 minutes. Accordingly, you should fetch the data from their API every 10 minutes (please make sure you do not fetch the data in a shorter period because otherwise your queries can result in a [denial of service attack](https://en.wikipedia.org/wiki/Denial-of-service_attack) (and the Wasserschutzpolizei will catch and arrest you!!!)).

There are several options on how to periodically fetch the weather data. One option is to setup a [systemd timer unit](https://www.putorius.net/using-systemd-timers.html).


## Query Weather Data

Use InfluxQL (InfluxDB's query language) to explore InfluxDB's [schema](https://docs.influxdata.com/influxdb/v1.7/query_language/schema_exploration) and [data](https://docs.influxdata.com/influxdb/v1.7/query_language/data_exploration). There are also Jupyter Notebooks available on our Jupyter Hub which show how to connect and query data from InfluxDB.

## Visualize Data

### Chronograf

The TICK Stack comes with Chronograf. It runs on `http://localhost:8888` and provides the possibility to visualize data. 

![alt text](./pics/query_01.png "Visualization of air temperature")

In order to get started you can import this simple [Dashboard](dashboard/Simple_Dashboard.json)

Otherwise use following procedure:
- Dashboards -> Create Dashbord
- Add Data
- Select "meteorology.autogen" -> mythenquai -> air_temperature
- Make sure you select a large enough duration (e.g. "Past 30d")
- You might want to add a second query (e.g. for "tiefenbrunnen")


# Reinstall Raspbian

You should do this if you really need to!

1. Format your SD Card by following [this](https://www.raspberrypi.org/documentation/installation/sdxc_formatting.md) (alternatively you might want to use [this](https://www.disk-partition.com/articles/raspberry-pi-sd-card-format-4125.html) for windows or [this](https://www.pcworld.com/article/3176712/how-to-format-an-sd-card-in-linux.html) for linux) procedure.
2. Install the operating system by following [this](https://www.raspberrypi.org/documentation/installation/installing-images/) procedure.


# System Tuning

## Raspberry Pi 3

[Enable ZRAM](https://github.com/novaspirit/rpi_zram) and disable Swap

```bash
sudo wget -O /usr/bin/zram.sh https://raw.githubusercontent.com/novaspirit/rpi_zram/master/zram.sh
sudo chmod +x /usr/bin/zram.sh
# add as second last line (before exit 0)
sudo sed -i "`wc -l < /etc/rc.local`i\\/usr/bin/zram.sh &\\" /etc/rc.local
sudo shutdown -r now
```

Alternatively, [increase Swap](https://wpitchoune.net/tricks/raspberry_pi3_increase_swap_size.html) and set swappiness as low as possible

```bash
sudo dphys-swapfile swapoff
echo "CONF_SWAPSIZE=1024" | sudo tee -a /etc/dphys-swapfile
echo "vm.swappiness = 1" | sudo tee -a /etc/sysctl.conf
sudo dphys-swapfile swapon
sudo shutdown -r now
```

