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

def configure_network(ssid, password):
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
    # attempt connection 50 times
    for i in range(50):
        if wifi.isconnected():
            neopixel.set_led('green')
            return True
        wifi.connect(ssid, password)
    neopixel.set_led('red')
    print("Could not connect to WiFi")
    return False

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
            return
        
#         self.calf_circ = random.uniform(30,40) 			# standalone testing 
#             
#     def collectEMG(self): 								# standalone testing
#         data = []
#         timestamps = []
#         credentials = bytes("channels/{:s}/publish".format(self.channel_id), 'utf-8')
#         # generate random data
#         for i in range(10):
#             data.append(random.randint(0,1024))
#             timestamps.append(self.getTime())
#             # uncomment to replicate real time delay b/w api request
#             # time.sleep(1)
#         data_str = ' '.join(map(str, data))
#         time_str = ' '.join(timestamps)
#         return data_str, time_str
#         
#     def getTime(self):
#         year, month, day, hour, minute, second, weekday, yearday = utime.localtime(utime.time())
#         millisecond = utime.ticks_ms() % 1000
#         second = '.'.join(map(str, [second, millisecond]))
#         timestamp = ':'.join(map(str, [hour, minute, second]))
#         return timestamp
        
    def send_data(self, cc, data, timestamps):
#         standaloneflag = False							# standalone testing
#         if cc == 0:										# standalone testing 
#             standaloneFlag = True						# standalone testing
#         data, timestamps = self.collectEMG() 			# standalone testing
#         cc =  self.calf_circ      						# standalone testing
        credentials = bytes("channels/{:s}/publish".format(self.channel_id), 'utf-8')  
        payload = bytes("field1={:.2f}&field2={}\n&field3={}\n".format(cc, data, timestamps), 'utf-8')
        self.client.publish(credentials, payload)
#         if standaloneFlag:
#             print("CC: " + str(cc))
#             print("EMG Point: " + str(data[0]))			# standalone testing
#             print("Timestamp: " + str(timestamps[0]) + '\n')	# standalone testing
                  
    
def main():
    # wifi credentials
    wifi_ssid = "Huz-Matebook"
    wifi_pass = "bu*mrbwrQ59iY^"
    
    # MQTT API credentials
    client_id = 'CjE0JyYnIQkdExQNKSI2JSc'
    username = 'CjE0JyYnIQkdExQNKSI2JSc'
    password = 'hbvwNovW4GNpPlfByQ5BVGLi'
    channel_id = '2068835'
    
    if configure_network(wifi_ssid, wifi_pass):
        try:
            calf_monitor = MQTTLink(client_id, username, password, channel_id)
            # print("API Connected!")
        except:
            neopixel.set_led('red')
            # print("API Connection Failed")
            
    # calf_monitor.sendCC()
    #send 3 sets of EMG and time data
    i=0
    while True:
        print(str(i+1)	 + " Set published")
        calf_monitor.sendData(0,0,0)
        utime.sleep(1)
        i=i+1
        
# main()
