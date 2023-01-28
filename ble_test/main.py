import sys

sys.path.append("")

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

async def find_devices():
    # asynchronously active scan all ble devices in the area for 10 seconds
    async with aioble.scan(5000, interval_us=10000, window_us=10000, active=True) as scanner:
        # checking each ble result if it the M40 sensor
        async for result in scanner:
            # See if it matches our name and the defined manufacturer id
            if result.name() == "ANR Corp M40" and result.manufacturer(0x05da) is not None:
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
        return

    # once the device is found connect the device
    try:
        print("Connecting to", device)
        connection = await device.connect()
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
            # receive and parse raw data
            raw_data = await dev_analog_characteristic.notified()
            # encoding is little endian (LSB first)
            muscle_activity = int.from_bytes(raw_data, "little")
            print(muscle_activity)
    
asyncio.run(main())
    