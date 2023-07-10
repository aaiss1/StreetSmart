# StreetSmart

A micro-mobility safety device designed and built by 4 senior computer engineering students.

sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel

sudo python3 -m pip install --force-reinstall adafruit-blinka

sudo apt-get install python-dev python3-dev -y
sudo pip3 install --upgrade RPi.GPIO



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

On the Raspberry Side, the COMM Connections are
CSN_PIN = 0  # connected to GPIO8// ITS THE RASPI's CE PIN #
CE_PIN = 17  # connected to GPIO17

The hierachy is 
LEVEL 0: global_vars.py
LEVEL 1: main.py
LEVEL 2: lighting.py    comm.py     accel.py    distance.py           

run sudo python3 main.py

CTRL C to kill

How to Run streetsmart on startup
sudo cp streetSmart.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable streetSmart.service
sudo systemctl enable streetSmart.service --now
sudo systemctl disable streetSmart.service
