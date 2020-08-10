import wifimgr
import dht
from machine import Pin, deepsleep, reset
import configmgr
import urequests
from time import localtime
import ntptime
import sys

wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

config = configmgr.get_config()
if config is None:
    print("Could not set application configuration.")
    while True:
        pass  # you shall not pass :D

try:
    ntptime.settime()
except:
    pass

def date_string():
    return "{0}-{1:02}-{2:02} {3:02}:{4:02}:{5:02}Z".format(localtime()[0], localtime()[1], localtime()[2], localtime()[3], localtime()[4], localtime()[5])

def write_points(measurement, data):

    url = '{0}://{1}:{2}/write?db={3}'.format(config.PROTOCOL, config.INFLUX_HOST, int(config.INFLUX_PORT), config.INFLUX_DB)
    payload = '{0},location={1} value={2}'.format(measurement, config.LOCATION, data)

    try:
        r = urequests.post(url, data=payload)
        if r.status_code == 204:
            r.close()
            pass
        else:
            print("{0} - Failed to POST data to InfluxDB".format(date_string()))
            print(r.status_code)
            print(r.content)
            r.close()
    except Exception as e:
        print(e)
        print("{0} - Failed to POST data to InfluxDB".format(date_string()))
        print("{0} - Soft Resetting".format(date_string()))
        reset()
        pass

def read_sensor():
    sensor = dht.DHT22(Pin(int(config.DHT_PIN)))
    try:
        sensor.measure()
        temp_c = sensor.temperature()
        humidity = sensor.humidity()
        temp_f = temp_c * (9/5) + 32.0
        return {'temp_c': temp_c, 'temp_f': temp_f, 'humidity': humidity}
    except OSError as e:
        print('{0} - Failed to read sensor'.format(date_string()))
        print("{0} - Soft Resetting".format(date_string()))
        reset()
        return

def create_influx_db():
    url = '{0}://{1}:{2}/query?q=CREATE%20DATABASE%20%22{3}%22'.format(config.PROTOCOL, config.INFLUX_HOST, int(config.INFLUX_PORT), config.INFLUX_DB)
    try:
        r = urequests.post(url)
        if r.status_code != 200:
            print("{0} - Failed to create InfluxDB database".format(date_string()))
            r.close()
        else:
            r.close()
    except Exception as e:
        print(e)
        print("{0} - Failed to create InfluxDB database".format(date_string()))
        print("{0} - Soft Resetting".format(date_string()))
        reset()
        pass

print("Starting ESP32 Temperature & Humidity Monitor")
create_influx_db()
readings = read_sensor()
for item in readings:
    write_points(item, readings[item])
print("{0} - {1}".format(date_string(), readings))
deepsleep(45000)
