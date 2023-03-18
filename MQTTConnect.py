# networking libraries
import network
from umqtt.robust import MQTTClient
import time
import gc
import sys
# rgb status LED libraries
import neopixel
from machine import Pin
import feathers3
#library for random data
import random
# status led controller class
import ledControl

neopixel = ledControl.DeviceStatus(0.05, 'red')

def configureNetwork(ssid, password):
    # turn on the station interface to connect network
    wifi = network.WLAN(network.STA_IF)
    # activate the station interface
    wifi.active(True)
    # attempt to connect to laptop hotspot max 5 attempts
    if not wifi.isconnected():
        try:
            wifi.connect(ssid, password)
        except OSError:
            print("WiFi not available")
    for i in range(5):
        if wifi.isconnected():
            neopixel.set_led('green')
            return True
        wifi.connect(ssid, password)
    neopixel.set_led('red')
    print("Could not connect to WiFi")
    return False

class MQTTConnection:
    def __init__(self, client_id, username, password, channel_id):
        # API credentials
        self.client_id = client_id
        self.username = username
        self.password = password
        self.channel_id = channel_id
        # create client with secure connection
        self.client = MQTTClient(server=b"mqtt3.thingspeak.com",
                            client_id=self.client_id,
                            user=self.username,
                            password=self.password,
                            ssl=True)
        try:
            self.client.connect()
            # neopixel.colorwheel()
        except Exception as e:
            print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
            sys.exit()
            
    def sendEMG(self):
        data = []
        for i in range(50):
            data.append(random.randint(0,1024))
        
        credentials = bytes("channels/{:s}/publish".format(self.channel_id), 'utf-8')  
        payload = bytes("field1={}\n".format(data), 'utf-8')
        self.client.publish(credentials, payload)
        print("EMG Data Published")
    
    def sendCC(self):
        data = random.uniform(30,40)
        credentials = bytes("channels/{:s}/publish".format(self.channel_id), 'utf-8')  
        payload = bytes("field2={:.2f}\n".format(data), 'utf-8')
        self.client.publish(credentials, payload)
        print("CC Data Published")
    
def main():
    # wifi credentials
    wifi_ssid = "Huz-Matebook"
    wifi_pass = "bu*mrbwrQ59iY^"
    
    # MQTT API credentials
    client_id = 'CjE0JyYnIQkdExQNKSI2JSc'
    username = 'CjE0JyYnIQkdExQNKSI2JSc'
    password = 'hbvwNovW4GNpPlfByQ5BVGLi'
    channel_id = '2068835'
    
    if configureNetwork(wifi_ssid, wifi_pass):
        try:
            calf_monitor = MQTTConnection(client_id, username, password, channel_id)
            print("API Connected!")
        except:
            print("API Connection Failed")
            
    calf_monitor.sendCC()
    while True:
        calf_monitor.sendEMG()
        time.sleep(1)
main()

