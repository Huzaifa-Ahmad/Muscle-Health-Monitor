import sys

sys.path.append("")

import time, gc, os
import neopixel
from machine import Pin
import feathers3
import uasyncio as asyncio
import bluetooth
import aioble

# Defining device Service UUID
_DEV_INFO_UUID = bluetooth.UUID(0x180A)
# Defining device service Characteristics
_MODEL_NO_UUID = bluetooth.UUID(0x2A24)

# defining automation Service UUID
_AUTO_ID_UUID = bluetooth.UUID(0x1815)
# defining automation service Characteristics
_DIGITAL_IN_UUID = bluetooth.UUID(0x2A56)
_ANALOG_UUID = bluetooth.UUID(0x2A58)

# Power Info
print("Power Info")
print("---------------------------")
print(f"5V present? {feathers3.get_vbus_present()}")
print(f"VBAT voltage is {feathers3.get_battery_voltage()}v")

# Create a NeoPixel instance
# Brightness of 0.3 is ample for the 1515 sized LED
pixel = neopixel.NeoPixel(Pin(feathers3.RGB_DATA), 1)
brightness = 0.05

# Create a colour wheel index int
color_index = 0
# Turn on the power to the NeoPixel 
feathers3.set_ldo2_power(True)
# LED is red while no BLE device connected
pixel[0] = (int(255*0.05), 0, 0)
pixel.write()

async def find_devices():
    # LED is yellow while BLE searching
    pixel[0] = (int(255*0.05), int(255*0.05), 0)
    pixel.write()
    # asynchronously active scan all ble devices in the area for 10 seconds
    async with aioble.scan(5000, interval_us=10000, window_us=10000, active=True) as scanner:
        # checking each ble result if it the M40 sensor
        async for result in scanner:
            # See if it matches our name and the defined manufacturer id
            if result.name() == "ANR Corp M40" and result.manufacturer(0x05da) is not None:
                # LED is blue when found
                pixel[0] = (0, 0, int(255*0.05))
                pixel.write()
                # defining the the peripheral device
                # peripheral address is public and address is known
                device = aioble.Device(aioble.ADDR_PUBLIC, "04:ee:03:5a:54:d4")
                return device
    return None

async def main():
    # call scanning method
    device = await find_devices()
    
    if not device:
        print("EMG sensor not found")
        # LED is red while no BLE device connected
        pixel[0] = (int(255*0.05), 0, 0)
        pixel.write()
        return
    # once the device is found connect the device
    try:
        print("Connecting to", device)
        connection = await device.connect()
        # LED is green when connected
        pixel[0] = (0, int(255*0.05), 0)
        pixel.write()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
        
    async with connection:
        try:
            # device the service and characteritics UUIDs
            dev_auto_service = await connection.service(_AUTO_ID_UUID)
            dev_digital_in_characteristic = await dev_auto_service.characteristic(_DIGITAL_IN_UUID)
            dev_analog_characteristic = await dev_auto_service.characteristic(_ANALOG_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return
        
        try:
            # set the Device ID in the Digital Characteristic value
            # should see LED colour change
            # device ID colours can be found in datasheets
            # 17: Magenta/Blue
            setID_colour_response = await dev_digital_in_characteristic.write(bytes([17]))          
        except asyncio.TimeoutError:
            print("Device ID Set Fail")
            return
        
        # subscribe to analog characteristics so updates are received every 100ms
        await dev_analog_characteristic.subscribe(notify=True)
        
        while True:
            r,g,b = feathers3.rgb_color_wheel( color_index )
    
            # setting brightness
            r = int(brightness*r)
            g = int(brightness*g)
            b = int(brightness*b)

            # Set the colour on the NeoPixel
            pixel[0] = (r, g, b)
            pixel.write()
            # Increase the wheel index
            color_index += 1

            # If the index == 255, loop it
            if color_index == 255:
                color_index = 0
                # Invert the internal LED state every half colour cycle
                feathers3.led_blink()
                
            # instead of subscribing and getting an udpate every 100ms await to get an update every second
            # raw_data = await dev_analog_characteristic.read()
            
            # receive and parse raw data from the subscription
            raw_data = await dev_analog_characteristic.notified()
            # encoding is little endian (LSB first)
            muscle_activity = int.from_bytes(raw_data, "little")
            print(muscle_activity)
            
            # 1s task delay, Fs = 1 Hz
            # await asyncio.sleep_ms(1000)
    
asyncio.run(main())
