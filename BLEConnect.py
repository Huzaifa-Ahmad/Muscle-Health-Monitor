# system and board libraries
import sys
import utime, gc, os
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
    def __init__(self, device_id):
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
        
        # desired device ID
        self.device_id = device_id
        # all ble data
        self.ble_data = []
        self.ble_timestamps = []
        
        #defining BLE status indicator LED
        self.neopixel = ledControl.DeviceStatus(0.05, 'red')
        
    async def get_device(self):
        async with aioble.scan(duration_ms=2000, interval_us=10000, window_us=10000, active=True) as scanner:
            async for result in scanner:
                if result.name() == self.device_name and result.manufacturer(0x05da) is not None:
                    self.device = aioble.Device(aioble.ADDR_PUBLIC, "04:ee:03:5a:54:d4")
                    self.neopixel.set_led('yellow')
                    if await self.connect_device():
                        return await self.set_device_id()
                    
        self.neopixel.set_led('red')
        print("Device not found")
        return False
    
    async def connect_device(self):
        try:
            self.connection = await self.device.connect()
            self.auto_serv = await self.connection.service(self.auto_io_serv_uuid)
            self.dig_dev_id_char = await self.auto_serv.characteristic(self.dig_dev_id_uuid)
            self.ana_emg_char = await self.auto_serv.characteristic(self.ana_emg_uuid)
            self.neopixel.set_led('blue')
            return True
        except Exception as e:
            self.neopixel.set_led('red')
            print("Failed to connect to device")
            print(e)
            return False
    
    async def set_device_id(self):
        try:
            # Set the Device ID in the Digital Characteristic value
            await self.dig_dev_id_char.write(bytes([self.device_id]))
            self.neopixel.set_led('blue')
            return True
        except Exception as e:
            self.neopixel.set_led('red')
            print("Failed to set device ID")
            print(e)
            return False
        
    async def get_time(self):
        year, month, day, hour, minute, second, weekday, yearday = utime.localtime(utime.time())
        second = '.'.join(map(str, [second, utime.ticks_ms() % 1000]))
        timestamp = ':'.join(map(str, [hour, minute, second]))
        return timestamp
        
    async def read_device(self):
        try:
            await self.ana_emg_char.subscribe(notify=True)
            self.ble_data.append(int.from_bytes(await self.ana_emg_char.notified(), "little"))
            self.ble_timestamps.append(await self.get_time())
            self.neopixel.set_led('green')
            return (self.ble_data[-1], self.ble_timestamps[-1])
        except Exception as e:
            self.neopixel.set_led('red')
            print("Failed to read from device")
            print(e)
            return False
         
async def main():
    device = BLEDevice(20)

     # Call the connect_device method to connect to the device
    if not await device.get_device():
        return
    
    while True:
        emg, time = await device.read_device()
        print(str(time) + ": " +  str(emg))
        if not emg:
            return
    
# asyncio.run(main())
