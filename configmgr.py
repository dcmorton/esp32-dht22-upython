import network
import socket
import ure
import os

server_socket = None

def get_config():

    # Try to import the config.py file and return the configuation if all keys are configured
    try:
        import config
        config = verify_config()
        if config:
            return config
    except Exception as e:
        print(e)
        print("failed to load config")
        pass

    # We don't seem to be configured; start the config web server
    print("starting config setup")
    config = start()

    return config

def verify_config():
    import config
    if hasattr(config, 'PROTOCOL') and hasattr(config, 'INFLUX_HOST') and hasattr(config, 'INFLUX_PORT') and hasattr(config, 'INFLUX_DB') and hasattr(config, 'DHT_PIN') and hasattr(config, 'LOCATION'):
        if len(config.PROTOCOL) >= 4 and len(config.INFLUX_HOST) > 0 and len(config.INFLUX_PORT) > 0 and len(config.INFLUX_DB) > 0 and len(config.DHT_PIN) > 0 and len(config.LOCATION) > 0:
            return config
        else:
            return None
    else:
        return None

def write_config(config):
    lines = []
    try:
        for item in config:
            lines.append("{0}=\"{1}\"\n".format(item, str(config[item])))
        with open('config.py', "w") as f:
            f.write(''.join(lines))
        return True
    except:
        return False

def send_header(client, status_code=200, content_length=None ):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    if content_length is not None:
      client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")


def send_response(client, payload, status_code=200):
    content_length = len(payload)
    send_header(client, status_code, content_length)
    if content_length > 0:
        client.sendall(payload)
    client.close()

def handle_root(client):
    send_header(client)
    client.sendall("""\
        <html>
            <h1 style="color: #5e9ca0; text-align: center;">
                <span style="color: #ff0000;">
                    InfluxDB Client & DHT Sensor Setup
                </span>
            </h1>
            <form action="configure" method="post">
                <table style="margin-left: auto; margin-right: auto;">
                    <tbody>
    """)
    client.sendall("""\
                        <tr>
                            <td>Protocol (HTTP/HTTPS):</td>
                            <td><input name="PROTOCOL" type="text" value="HTTP" /></td>
                        </tr>
                        <tr>
                            <td>InfluxDB Host:</td>
                            <td><input name="INFLUX_HOST" type="text" /></td>
                        </tr>
                        <tr>
                            <td>InfluxDB Port:</td>
                            <td><input name="INFLUX_PORT" type="number" value="8086" /></td>
                        </tr>
                        <tr>
                            <td>InfluxDB DB:</td>
                            <td><input name="INFLUX_DB" type="text" /></td>
                        </tr>
                        <tr>
                            <td>Sensor Location:</td>
                            <td><input name="LOCATION" type="text" value="ESP32" /></td>
                        </tr>
                        <tr>
                            <td>DHT Pin:</td>
                            <td><input name="DHT_PIN" type="number" /></td>
                        </tr>
                    </tbody>
                </table>
                <p style="text-align: center;">
                    <input type="submit" value="Submit" />
                </p>
            </form>
            <p>&nbsp;</p>
            <hr />
            <h2 style="color: #2e6c80;">
                Some useful infos:
            </h2>
            <ul>
                <li>
                    Original code from <a href="https://github.com/cpopp/MicroPythonSamples"
                        target="_blank" rel="noopener">cpopp/MicroPythonSamples</a> & <a href="https://github.com/tayfunulu/WiFiManager"
                        target="_blank" rel="noopener">tayfunulu/WiFiManager</a>.
                </li>
                <li>
                    This code available at <a href="https://github.com/dcmorton/esp32-dht22-upython"
                        target="_blank" rel="noopener">dcmorton/esp32-dht22-upython</a>.
                </li>
            </ul>
        </html>
    """)
    client.close()

def handle_configure(client, request):
    match = ure.search("PROTOCOL=([^&]*)&INFLUX_HOST=(.*)&INFLUX_PORT=(.*)&INFLUX_DB=(.*)&LOCATION=(.*)&DHT_PIN=(.*)", request)

    if match is None:
        send_response(client, "Parameters not found", status_code=400)
        return False
    # version 1.9 compatibility
    try:
        PROTOCOL = match.group(1).decode("utf-8")
        INFLUX_HOST = match.group(2).decode("utf-8")
        INFLUX_PORT = match.group(3).decode("utf-8")
        INFLUX_DB = match.group(4).decode("utf-8")
        LOCATION = match.group(5).decode("utf-8")
        DHT_PIN = match.group(6).decode("utf-8")
    except Exception:
        print("failed to match request groups")

    if len(PROTOCOL) == 0:
        send_response(client, "Protocol must be provided", status_code=400)
        return False
    if len(INFLUX_HOST) == 0:
        send_response(client, "InfluxDB Host must be provided", status_code=400)
        return False
    if len(INFLUX_PORT) == 0:
        send_response(client, "InfluxDB Port must be provided", status_code=400)
        return False
    if len(INFLUX_DB) == 0:
        send_response(client, "InfluxDB Database must be provided", status_code=400)
        return False
    if len(LOCATION) == 0:
        send_response(client, "Location must be provided", status_code=400)
        return False
    if len(DHT_PIN) == 0:
        send_response(client, "DHT Pin must be provided", status_code=400)
        return False

    config = {'PROTOCOL': PROTOCOL.lower(), 'INFLUX_HOST': INFLUX_HOST, 'INFLUX_PORT': INFLUX_PORT, 'INFLUX_DB': INFLUX_DB, 'LOCATION': LOCATION, 'DHT_PIN': DHT_PIN}

    if write_config(config):
        response = """\
            <html>
                <center>
                    <br><br>
                    <h1 style="color: #5e9ca0; text-align: center;">
                        <span style="color: #ff0000;">
                            ESP successfully configured. Reset ESP32 to get started.
                        </span>
                    </h1>
                    <br><br>
                </center>
            </html>
        """
        send_response(client, response)

        return True
    else:
        response = """\
            <html>
                <center>
                    <h1 style="color: #5e9ca0; text-align: center;">
                        <span style="color: #ff0000;">
                            ESP configuration unsuccessful.
                        </span>
                    </h1>
                    <br><br>
                    <form>
                        <input type="button" value="Go back!" onclick="history.back()"></input>
                    </form>
                </center>
            </html>
        """
        send_response(client, response)
        return False

def handle_not_found(client, url):
    send_response(client, "Path not found: {}".format(url), status_code=404)

def stop():
    global server_socket

    if server_socket:
        server_socket.close()
        server_socket = None


def start(port=80):
    global server_socket

    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    stop()

    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)

    while True:

        client, addr = server_socket.accept()
        print('client connected from', addr)
        try:
            client.settimeout(5.0)

            request = b""
            try:
                while "\r\n\r\n" not in request:
                    request += client.recv(1024)
            except OSError:
                pass

            print("Request is: {}".format(request))
            if "HTTP" not in request:  # skip invalid requests
                continue

            # version 1.9 compatibility
            try:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).decode("utf-8").rstrip("/")
            except Exception:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).rstrip("/")
            print("URL is {}".format(url))

            if url == "":
                handle_root(client)
            elif url == "configure":
                handle_configure(client, request)
            else:
                handle_not_found(client, url)

        finally:
            client.close()
