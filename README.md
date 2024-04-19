# StreetSmart

A bicycle safety device designed and built by 4 senior computer engineering students.

## Installing the Neopixel Library
```
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka
sudo apt-get install python-dev python3-dev -y
sudo pip3 install --upgrade RPi.GPIO
```

## Installing the RF24 Library
```
mkdir ~/rf24libs
cd ~/rf24libs
git clone https://github.com/TMRh20/RF24
cd ~/rf24libs/RF24
./configure
sudo make install
#Choose the SPIDEV Option
sudo apt-get install python3-dev libboost-python-dev
#Use ldconfig -p | grep libboost_python to find the number after libboost_python
sudo ln -s $(ls /usr/lib/arm-linux-gnueabihf/libboost_python3*.so | tail -1) /usr/lib/arm-linux-gnueabihf/libboost_python3.so
sudo apt-get install python3-setuptools
cd pyRF24/
sudo python3 setup.py build
sudo python3 setup.py install
sudo apt-get install python3-dev python3-rpi.gpio
```
## Connections for NRF24L01
```
On the Raspberry Side, the COMM Connections are
CSN_PIN = 0  # connected to GPIO8// ITS THE RASPI's CE PIN #
CE_PIN = 17  # connected to GPIO17
```

## File Hierarchy
- global_vars.py
    - main.py
        - lighting.py
        - comm.py     
        - accel.py    
        - lidar_dist.py          


## StreetSmart Service
### How to Run streetsmart on startup
```
sudo cp streetSmart.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable streetSmart.service # Requires Reboot
#OR
sudo systemctl enable streetSmart.service --now #Runs as soon as called
```
### How to Stop streetsmart from running on startup
```
sudo systemctl disable streetSmart.service
```

### How to stop streetsmart when it is already running on startup
```
sudo systemctl stop streetSmart.service
```

## How to Run StreetSmart Manually

```
sudo python3 main.py

#CTRL C to kill
```
