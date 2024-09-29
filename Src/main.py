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
##Output            : web page at http://XXX.XXX.XXX.XX/index.html
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
### Toggle LED endpoint
###############################################
def toggle_led():
    print(led.value())
    
    if led.value() == 0: 
        for ii in range(n):
            np[ii] = (120, 153, 23)
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


###############################################
### Web server
###############################################
def web_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(addr)
    s.listen(1)
    print("Listening on", addr)

    while True:
        conn, addr = s.accept()
        print("Connection from:", addr)
        request = conn.recv(1024)

        if b"GET /toggle" in request:
            print(21*'#')
            response = toggle_led()
            print(response)
            conn.sendall("HTTP/1.1 200 OK\nContent-Type: application/json\nConnection: close\n" +
                         "Cache-Control: no-store\n\n" + str(response))
        elif b"GET /led_state" in request:
            print(21*'#')
            print('Request of the status')
            response = get_led_state()
            #print(response)
            conn.sendall("HTTP/1.1 200 OK\nContent-Type: application/json\nConnection: close\n" +
                         "Cache-Control: no-store\n\n" + json.dumps(response))  # Ensure the response is JSON-formatted
        else:
            print(21*'#')
            print('Connection')
            html_content = read_html_content()
            led_state = led.value()  # Change this to led.value() when you're ready to use the actual LED state
            html_content = html_content.replace('{{LED_STATE}}', str(led_state))
            conn.sendall("HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n" +
                         "Cache-Control: no-store\n\n" + html_content)

        conn.close()


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

    # WiFi settings
    wifi_credentials_ssid ='XXXX'
    wifi_credentials_password = 'XXX'
    static_ip = ('XXX.XXX.XXX.XX', 'XXX.XXX.XXX.X', 'XXX.XXX.XXX.X', 'XXX.XXX.XXX.X')

    wifi_ok = connect_wifi(wifi_credentials_ssid, wifi_credentials_password, static_ip)
    
    if wifi_ok:
        update_timus()
        web_server()
