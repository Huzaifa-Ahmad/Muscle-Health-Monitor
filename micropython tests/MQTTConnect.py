# networking libraries
import network
from umqtt.robust import MQTTClient
import utime
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

class MQTTLink:
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
        
    def send_data(self, cc, data, timestamps, session_state):
        credentials = bytes("channels/{:s}/publish".format(self.channel_id), 'utf-8')  
        payload = bytes("field1={:.2f}&field2={}\n&field3={}\n&field4={}".format(cc, data, timestamps, session_state), 'utf-8')
        self.client.publish(credentials, payload)

# def main():    
#     # MQTT API credentials
#     client_id = 'CjE0JyYnIQkdExQNKSI2JSc'
#     username = 'CjE0JyYnIQkdExQNKSI2JSc'
#     password = 'hbvwNovW4GNpPlfByQ5BVGLi'
#     channel_id = '2068835'
#     
#     try:
#         calf_monitor = MQTTLink(client_id, username, password, channel_id)
#         print("API Connected!")
#     except:
#         neopixel.set_led('red')
#         print("API Connection Failed")
#             
#     i=0
#     while True:
#         print(str(i+1)	 + " Set published")
#         calf_monitor.sendData(0,0,0)
#         utime.sleep(1)
#         i=i+1
#         
# main()