# system and board libraries
import sys
import time, gc, os
import uasyncio as asyncio
import neopixel
from machine import Pin
import feathers3
# ble libraries 
import bluetooth
import aioble
#import led control class
import ledControl

"""
The	M40	implements the following GATT Profile:	
Device Info Service UUID:            		0x180A	
  • Model Number Characteristic UUID:       0x2A24	
  • Serial Number CharacterisMc UUID:	    0x2A25	
  • Firmware Revision Characteristic UUID:  0x2A26	
  • Hardware Revision Characteristic UUID:  0x2A27	
  • Software Revision Characteristic UUID:  0x2A28
  
Automation IO Service UUID:	         		0x1815	
  • Analog Characteristic UUID:	            0x2A58	
  • Digital Characteristic UUID:	        0x2A56	
"""
class BLEDevice:
    def __init__(self):
        # defining device info
        self.device_name = "ANR Corp M40"
        self.device_addr = "04:ee:03:5a:54:d4"
        
        # defining device UUIDs
        # device info UUIDs
        self.dev_info_serv_uuid = bluetooth.UUID(0x180A)
        self.model_no_char_uuid = bluetooth.UUID(0x2A24) #model number characteristic
        # automation IO UUIDs
        self.auto_io_serv_uuid = bluetooth.UUID(0x1815)
        self.dig_dev_id_uuid = bluetooth.UUID(0x2A56)
        self.ana_emg_uuid = bluetooth.UUID(0x2A58)
        
        # defining device connection info
        self.device = None
        self.connection = None
        
        # defining device services and characteristics
        self.auto_serv = None
        self.dig_dev_id_char = None
        self.ana_emg_char = None
        
        #defining BLE status indicator LED
        self.neopixel = ledControl.DeviceStatus(0.05, 'red')
        
    async def find_device(self):
        async with aioble.scan(duration_ms=2000, interval_us=10000, window_us=10000, active=True) as scanner:
            async for result in scanner:
                if result.name() == self.device_name and result.manufacturer(0x05da) is not None:
                    self.device = aioble.Device(aioble.ADDR_PUBLIC, "04:ee:03:5a:54:d4")
                    self.neopixel.set_led('yellow')
                    return True
        self.neopixel.set_led('red')
        return False
    
    async def connect_device(self):
        try:
            self.connection = await self.device.connect()
            self.auto_serv = await self.connection.service(self.auto_io_serv_uuid)
            self.dig_dev_id_char = await self.auto_serv.characteristic(self.dig_dev_id_uuid)
            self.ana_emg_char = await self.auto_serv.characteristic(self.ana_emg_uuid)
            self.neopixel.set_led('blue')
            return True
        except:
            self.neopixel.set_led('red')
            return False
    
    async def set_device_id(self, id):
        try:
            # Set the Device ID in the Digital Characteristic value
            await self.dig_dev_id_char.write(bytes([id]))
            self.neopixel.set_led('blue')
            return True
        except:
            self.neopixel.set_led('red')
            return False
        
    async def read_device(self):
        try:
            await self.ana_emg_char.subscribe(notify=False)
            muscle_activity = int.from_bytes(await self.ana_emg_char.read(), "little")
            self.neopixel.set_led('green')
            print(muscle_activity)
            return True
        except:
            self.neopixel.set_led('red')
            return False
         
async def main():
    device = BLEDevice()
    
    # Call the find_device method to find the device
    if not (await device.find_device()):
        print("Device not found")
        return
    
     # Call the connect_device method to connect to the device
    if not await device.connect_device():
        print("Failed to connect to device")
        return
    
    if not await device.set_device_id(20): # see product sheet to see ID settings
        print("Failed to set device ID")
        return
    
    while True:
        if not await device.read_device():
            print("Failed to read from device")
            return
        try:
            await asyncio.sleep_ms(1000)
        except:
            pass
    
asyncio.run(main())
    
    
    