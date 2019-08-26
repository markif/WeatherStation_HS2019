# Discover IP Address

Let your Raspberry Pi email its IP address on every startup. This allows you to connect (ssh) to your Raspberry Pi without needing a display, keyboard and mouse connected to it (you can run it on server mode). This was inspired by [Where is my Raspberry Pi?](https://medium.com/@oliverscheer/where-is-my-raspberry-pi-let-your-pi-send-you-an-email-with-its-ip-address-3a4feba7bef4).

```bash
# prepare folder structure
sudo mkdir -p /scripts/mail_ip
cd /scripts/mail_ip

# download the script
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/src/main.py
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/src/secrets.py
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/src/send-ip.service
sudo chmod +x main.py

# replace placeholders where appropriate 
sudo nano secrets.py
sudo chmod 700 secrets.py


# test the script
python3 main.py

# make sure it gets executed on startup
sudo cp send-ip.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/send-ip.service
sudo systemctl daemon-reload
sudo systemctl enable send-ip.service

# test if script is executed at startup
sudo shutdown -r now
```
