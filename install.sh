# !/bin/bash

echo "Installing necessary Python packages..."
sudo pip3 install --break-system-packages numpy netifaces smbus2 influxdb paho-mqtt adafruit-blinka adafruit-circuitpython-mcp4725 scipy PyWavelets

echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

echo "Rebooting to apply I2C changes..."
sudo reboot