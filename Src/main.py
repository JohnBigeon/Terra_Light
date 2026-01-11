# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 13:13:42 2023

@author: JBI
"""

"""
###############################################
##Title             : main.py
##Description       : Main script for TerraLight project
##Author            : John Bigeon   @ Github
##Date              : 20240116
##Version           : Test with
##Usage             : MicroPython (esp32-20220618-v1.19.1)
##Script_version    : 0.0.5 (not_release)
##Output            : web page at http://192.168.178.37/index.html
##Notes             :
###############################################
"""
###############################################
### Package
###############################################
from machine import Pin
import time
import network
import socket
import machine
import os
import utime
from utime import localtime
import ntptime
import random
import json
import network
from machine import Pin
import time
import neopixel

###############################################
### Wifi functions
###############################################
def query_wifi_params(ssid, password):
    # Connect to the WiFi network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_credentials_ssid, wifi_credentials_password)
    
    # Wait until the connection is established
    while not wlan.isconnected():
        pass
       
    print("Connected to Wi-Fi")
    print("IP Address:", wlan.ifconfig()[0])
    print("Subnet Mask:", wlan.ifconfig()[1])
    print("Gateway:", wlan.ifconfig()[2])
    print("DNS Server:", wlan.ifconfig()[3])

# Configure the ESP32 wifi
def connect_wifi(wifi_credentials_ssid, wifi_credentials_password, static_ip):
    sta = network.WLAN(network.STA_IF)
    time.sleep(1)
    if not sta.isconnected():
        print('Connecting to network...')
        sta.active(True)
        sta.connect(wifi_credentials_ssid, wifi_credentials_password)
        count = 0  # initialize the counter variable
        while not sta.isconnected() and count < 25:  # add the counter variable and conditional statement
            print('Not connected yet')
            count += 1  # increment the counter variable
            time.sleep(1)
            pass

    if sta.isconnected():
        print('Connected to network')
        # Configure the static IP address
        sta.ifconfig(static_ip)
        params_used = 'network config: %s' % str(sta.ifconfig())
        print(params_used)
        return True
    else:
        print('Failed to connect to network')
        return False

###############################################
### LED function
###############################################
def toggle_led(color):
    print(led.value())
    print(f'color selected: {color}')
    color_val = setColor(color)
    
    if led.value() == 0: 
        for ii in range(n):
            np[ii] = color_val
        np.write()
        
    else:
        for ii in range(n):
            np[ii] = (0, 0, 0)
        np.write()
    led.value(not led.value())
    print(led.value())

    return {"status": "success", "led_state": led.value()}

# Endpoint to get the LED state
def get_led_state():
    return {"led_state": led.value()}
    
  
def setColor(color='forest'):
    if color == 'space':
        out = (79, 23, 135)
    elif color == 'sunset':
        out = (232, 92, 13)
    else: # If not correct msg, go forest colors
        out = (120, 153, 23)
    return out
    
###############################################
### Read HTML content from file
###############################################
def read_html_content():
    try:
        with open('/www/index.html', 'r') as file:
            return file.read()
    except OSError:
        return "Error: Could not read HTML file"
    
    # Wait for a short time to avoid timing issues
    time.sleep(0.1)
    
    new_state = not led.value()
    led.value(new_state)
    
    print("New LED state:", led.value())
    
    return {"status": "success", "led_state": led.value()} #random.random()}#

def handle_request(conn, request):
    if not request:
        return

    try:
        request_str = request.decode('utf-8')
    except Exception:
        request_str = ""

    # --- Route : TOGGLE ---
    if "GET /toggle" in request_str:
        print(21*'#')
        response = toggle_led(setColor())  # toggle
        print("Toggle response:", response)
        
        json_data = json.dumps(response)
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "Cache-Control: no-store\r\n"
            "\r\n"
        )
        conn.sendall(header + json_data)

    # --- Route : SET_COLOR ---
    elif "GET /set_color/" in request_str:
        # Get color
        try:
            color = request_str.split("/set_color/")[1].split(" ")[0]
            print("Requested color:", color)
            
            color_value = setColor(color)
            response = {"status": "success", "color_set": color, "color_value": color_value}
            toggle_led(color)
        except Exception as e:
            response = {"status": "error", "message": str(e)}

        json_data = json.dumps(response)
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "Cache-Control: no-store\r\n"
            "\r\n"
        )
        conn.sendall(header + json_data)

    # --- Route : LED_STATE ---
    elif "GET /led_state" in request_str:
        print(21*'#')
        print('Requesting status...')
        response = get_led_state()
        
        json_data = json.dumps(response)
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "Cache-Control: no-store\r\n"
            "\r\n"
        )
        conn.sendall(header + json_data)

    # --- Route default : INDEX HTML ---
    else:
        print(21*'#')
        print('Serving Index Page')
        html_content = read_html_content()
        
        # Injection of the LED state into the HTML
        led_state = led.value()
        html_content = html_content.replace('{{LED_STATE}}', str(led_state))
        
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"
            "Cache-Control: no-store\r\n"
            "\r\n"
        )
        conn.sendall(header + html_content)

###############################################
### Dot-env method for micropython
###############################################
def load_dotenv(filename=".env"):
    env_vars = {}

    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()  # Remove any leading/trailing whitespace
                if line and not line.startswith("#"):  # Ignore empty lines and comments
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value

    except OSError as e:
        print(f"Error loading .env file: {e}")

    return env_vars

###############################################
### Web server
###############################################
def web_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Réutiliser l'adresse immédiatement après reboot
    s.bind(addr)
    s.listen(5) # Augmenter la file d'attente
    print("Listening on", addr)

    while True:
        conn = None
        try:
            conn, addr = s.accept()
            conn.settimeout(2.0) # Évite de rester bloqué si le client n'envoie rien
            print("Connection from:", addr)
            request = conn.recv(1024)
            if request:
                handle_request(conn, request)
        except Exception as e:
            print("Erreur lors de la requête:", e)
        finally:
            if conn:
                conn.close() # GARANTIT que la socket est libérée, même en cas d'erreur

###############################################
### Set the time using NTP
###############################################
def update_timus():
    ntptime.settime()

    # Get the current UTC time
    utc_time = machine.RTC().datetime()

    # Add 1 hour to the UTC time to adjust for the Belgium time zone
    belgium_time = utc_time[0], utc_time[1], utc_time[2], utc_time[3], utc_time[4] + 1, utc_time[5], utc_time[6], utc_time[7]

    # Set the adjusted time
    machine.RTC().datetime(belgium_time)


###############################################
### Main
###############################################
if __name__ == "__main__":
    # Use the onboard led to keep track of the Neopixel led
    led = machine.Pin(2, machine.Pin.OUT)
    
    # LED ring
    n = 15
    p = 12
    np = neopixel.NeoPixel(machine.Pin(p), n)

    # Get passwords via dotenv method
    env = load_dotenv()
    print(env)  # This will print out the dictionary of environment variables

    # WiFi settings
    wifi_credentials_ssid = env.get("wifi_credentials_ssid")
    wifi_credentials_password = env.get("wifi_credentials_password")
    static_ip_str = env.get("static_ip")
    static_ip = tuple(static_ip_str.split(','))

    wifi_ok = connect_wifi(wifi_credentials_ssid, wifi_credentials_password, static_ip)
    
    if wifi_ok:
        update_timus()
        web_server()

