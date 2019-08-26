# Discover IP Address

Let your Raspberry Pi email its IP address on every startup. This allows you to connect (ssh) to your Raspberry Pi without needing a display, keyboard and mouse connected to it (you can run it on server mode). This was inspired by [Where is my Raspberry Pi?](https://medium.com/@oliverscheer/where-is-my-raspberry-pi-let-your-pi-send-you-an-email-with-its-ip-address-3a4feba7bef4).

```bash
# prepare folder structure
sudo mkdir -p /scripts/mail_ip
cd /scripts/mail_ip

# download the script
sudo wget https://raw.githubusercontent.com/markif/WeatherStation_HS2019/master/pi/src/main.py
sudo chmod +x main.py

# replace where appropriate 
sudo cat > secrets.py <<EOL
sender_address = "yourname@gmail.com"
sender_password = "your password"
sender_server = 'smtp.gmail.com'
sender_port = 587
recipient_address = "yourrecipient@outlookc.com"
EOL
sudo chmod 700 secrets.py


# test the script
python3 main.py

# make sure it gets executed on startup
sudo cat > /lib/systemd/system/send-ip.service <<EOL
[Unit]
Description=Send IP Address
Wants=network-online.target
After=network.target network-online.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /scripts/mail_ip/main.py > /scripts/mail_ip/mail_ip.log 2>&1

[Install]
WantedBy=network-online.target
EOL

# enable service
sudo chmod 644 /lib/systemd/system/send-ip.service
sudo systemctl daemon-reload
sudo systemctl enable send-ip.service

# test if script is executed at startup
sudo shutdown -r now
```
