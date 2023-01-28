import sys

sys.path.append("")

from micropython import const
import time
import uasyncio as asyncio
import bluetooth
import aioble
import time
import random
import struct

# Service
_DEV_INFO_UUID = bluetooth.UUID(0x180A)
# Characteristic
_MODEL_NO_UUID = bluetooth.UUID(0x2A24)

# Service
_AUTO_ID_UUID = bluetooth.UUID(0x1815)
# Characteristic
_DIGITAL_IN_UUID = bluetooth.UUID(0x2A56)
_ANALOG_UUID = bluetooth.UUID(0x2A58)

async def find_devices():    
    async with aioble.scan(5000, interval_us=10000, window_us=10000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing 
            if result.name() == "ANR Corp M40" and result.manufacturer(0x05da) is not None:
                return result.device
            
    return None

async def main():
    device = await find_devices()
    
    if not device:
        print("EMG sensor not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
    
    async with connection:
        try:
            dev_auto_service = await connection.service(_AUTO_ID_UUID)
            dev_digital_in_characteristic = await dev_auto_service.characteristic(_DIGITAL_IN_UUID)
            dev_analog_characteristic = await dev_auto_service.characteristic(_ANALOG_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return
        
        try:
            setID_colour_response = await dev_digital_in_characteristic.write(bytes([3]))
        except asyncio.TimeoutError:
            print("Device ID Set Fail")
            return
        
        await dev_analog_characteristic.subscribe(notify=True)
        
        while True:
            raw_data = await dev_analog_characteristic.notified()
            muscle_activity = int.from_bytes(raw_data, "little")
            print(muscle_activity)  
    
asyncio.run(main())
    
