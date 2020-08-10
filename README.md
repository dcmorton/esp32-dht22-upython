# esp32-dht22-upython
A ESP32-based temperature monitor using micropython and a DHT22 sensor. This software sends data directly from the DHT22/ESP32 into an InfluxDB database.

## Installation
### Prerequisites
- Install micropython on ESP32. Further instructions [here](http://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
- Install file-copy tool such as [ampy](https://pypi.org/project/adafruit-ampy/)
- Clone repo: `https://github.com/dcmorton/esp32-dht22-upython`

### Copy files to board
- Use ampy to copy files to ESP32; ordering is important
```
ampy -p /dev/ttyUSB0 put configmgr.py
ampy -p /dev/ttyUSB0 put wifimgr.py
ampy -p /dev/ttyUSB put main.py
```

### Setup Sensor
- Reset sensor and connect your laptop, phone or other Wifi device with a browser to `ESP32Temp` Wifi Network with password `temperature`
- Once connected, browse to [http://192.168.4.1](http://192.168.4.1) to begin Wifi configuration
- After Wifi is configured on the ESP32, connect back to your Wifi AP at the IP Address assigned to the ESP32 to complete InfluxDB settings and DHT22 sensor configuration
