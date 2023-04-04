import uasyncio as asyncio
import machine
from machine import Pin
import sys
import network

# Custom File Imports
import BLEConnect
import MQTTConnect
import ledControl

# thingspeak credentials
CLIENT_ID = 'CjE0JyYnIQkdExQNKSI2JSc'
API_USER = 'CjE0JyYnIQkdExQNKSI2JSc'
API_PASS = 'hbvwNovW4GNpPlfByQ5BVGLi'
CHANNEL_ID = '2068835'

# Wheatstone Bridge Pins 
ref_branch = 14 		# A2 reference voltage
flex_sensor_branch = 6 	# A4 flex sensor voltage
# Flex sensor reading parameters
num_readings = 25 		# number of readings to avg adc reading over
reading_delay_ms = 60

# Button Pin
button_pin = const(8)
button = Pin(button_pin, Pin.IN)

# Wireless objects
device_id = 20
M40 = BLEConnect.BLEDevice(device_id)
segment_counter = 0

CALF_MONITOR_API = None
calf_circ = 0

async def ble_task():
    global segment_counter
    last_data_segment = 0
    while True:
        # get device data
        if segment_counter != last_data_segment:
            print("Segment " + str(segment_counter) + " of BLE Data Collected!")
            last_data_segment = segment_counter
            # send the last second worth of data to the API
            await network_task(M40.ble_data, M40.ble_timestamps)
        else:
            await M40.read_device()
            if len(M40.ble_data) == 10:
                   segment_counter += 1
                    
async def network_task(data, timestamps):
    global CALF_MONITOR_API, calf_circ, button
    button_state = button.value()
    CALF_MONITOR_API.send_data(calf_circ, data, timestamps, button_state)
    print("Data Sent Over Network\n")
    if button_state == 1:
        print("Session Over")
        led = ledControl.DeviceStatus(0.05, 'red')
        sys.exit()
    return
        
async def read_cc():
    global calf_circ, num_readings, reading_delay_ms
    adc_delta_readings = [0] * num_readings
    adc_delta_avg = []
    num_tests = 0
    
    # ADC objects
    ref_adc = machine.ADC(machine.Pin(ref_branch))
    flex_sensor_adc = machine.ADC(machine.Pin(flex_sensor_branch))
    
    while (num_tests < 4):
        print("Collecting CC...")
        for i in range (num_readings):
            adc_delta_readings[i] = (flex_sensor_adc.read() - ref_adc.read())
            adc_delta_avg.append(sum(adc_delta_readings) / len(adc_delta_readings))
            await asyncio.sleep_ms(reading_delay_ms)
        num_tests += 1
    del adc_delta_avg[0]
    calf_circ = sum(adc_delta_avg) / len(adc_delta_avg) # calculate cc in MATLAB


async def main():
    global CALF_MONITOR_API, M40, CLIENT_ID, API_USER, API_PASS, CHANNEL_ID, calf_circ, button
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
    
    if calf_circ == 0:
        print()
        await read_cc()
        print("\nCC ADC: " + str(calf_circ))
    
    while True:
        if button.value():
            print("Workout session starting now...")
            break
    
    tasks = [asyncio.create_task(ble_task())]
    res = await asyncio.gather(*tasks)
    
asyncio.run(main())