import uasyncio as asyncio
import machine
import sys

# temp library
import random
# Custome File Imports
import BLEConnect
import MQTTConnect

# wifi credentials
WIFI_SSID = "Huz-Matebook"
WIFI_PASS = "bu*mrbwrQ59iY^"

# thingspeak credentials
CLIENT_ID = 'CjE0JyYnIQkdExQNKSI2JSc'
API_USER = 'CjE0JyYnIQkdExQNKSI2JSc'
API_PASS = 'hbvwNovW4GNpPlfByQ5BVGLi'
CHANNEL_ID = '2068835'

# Wheatstone Bridge Pins 
ref_branch = 14 		# A2 reference voltage
flex_sensor_branch = 6 	# A4 flex sensor voltage
# Flex sensor reading parameters
num_readings = 50 		# number of readings to avg adc reading over
reading_delay_ms = 100

# Wireless objects
device_id = 20
M40 = BLEConnect.BLEDevice(device_id)
segment_counter = 0

CALF_MONITOR_API = None

calf_circ = 0

# task definitions
tasks = []
ble = None
network = None

async def ble_task():
    global segment_counter
    last_data_segment = 0
    while True:
        # get device data
        if segment_counter != last_data_segment:
            print("Segment " + str(segment_counter) + " of BLE Data Collected!")
            print(M40.ble_data)
            last_data_segment = segment_counter
            # send the last second worth of data to the API
            await network_task(M40.ble_data, M40.ble_timestamps)
        else:
            await M40.read_device()
            if len(M40.ble_data) == 10:
                   segment_counter += 1
                    
async def network_task(data, timestamps):
    global CALF_MONITOR_API, calf_circ
    CALF_MONITOR_API.send_data(calf_circ, data, timestamps)
    print("Data Sent Over Network\n")
    return
        
        
async def read_cc():
    global calf_circ
    calf_circ = random.uniform(30,45)
#     global num_readings, reading_delay_ms, calf_circ
#     adc_delta_readings = bytearray(num_readings)
#     
#     # ADC objects
#     ref_adc = machine.ADC(machine.Pin(ref_branch))
#     flex_sensor_adc = machine.ADC(machine.Pin(flex_sensor_branch))
#     
#     for i in range (num_readings):
#         adc_delta_readings[i] = flex_sensor_adc.read() - ref_adc.read()
#         await asyncio.sleep_ms(reading_delay_ms)
#     
#     adc_delta_avg = sum(adc_delta_readings)
#     volt_delt_avg = adc_delta_avg * (3.3 / 4095)
#     
#     calf_circ = adc_delta_avg # calculate cc in MATLAB


async def main():
    global CALF_MONITOR_API, M40, CLIENT_ID, API_USER, API_PASS, CHANNEL_ID, ble, network, calf_circ
    await read_cc()
    print("Calf Circumference: " + str(calf_circ))
    
    if MQTTConnect.configure_network(WIFI_SSID, WIFI_PASS):
        print("Network Connected")
        try:
            CALF_MONITOR_API = MQTTConnect.MQTTLink(CLIENT_ID, API_USER, API_PASS, CHANNEL_ID)
            print("API Connected")
        except:
            print("API Connection Failed")
    # Call the find_device method to find the device
    if not await M40.get_device():
        sys.exit()
        return
    print("BLE Device Connected")
    
    await read_cc()
    tasks = [asyncio.create_task(ble_task())]
    res = await asyncio.gather(*tasks)
    
asyncio.run(main())
