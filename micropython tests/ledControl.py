import neopixel
from machine import Pin
import feathers3
import time

class DeviceStatus:
    def __init__(self, brightness, default):
        #defining BLE status indicator LED
        self.pixel = neopixel.NeoPixel(Pin(feathers3.RGB_DATA), 1)
        self.brightness = brightness
        self.set_led(default)
    
    def set_led(self, state):
        if state == 'yellow' : # searching
            self.pixel[0] = (int(255*self.brightness), int(255*self.brightness), 0) # yellow
        elif state == 'blue' : # Device found 
            self.pixel[0] = (0, 0, int(255*self.brightness)) # blue
        elif state == 'red' : # not found 
            self.pixel[0] = (int(255*self.brightness), 0, 0) # red
        elif state == 'green' : # running
            self.pixel[0] = (0, int(255*self.brightness), 0) # green
        elif state == 'purple' : # connected
            self.pixel[0] = (int(255*self.brightness), 0, int(255*self.brightness)) # purple
        self.pixel.write()
        
    def colorwheel(self):
        color_index = 0
        while True:
            # Get the R,G,B values of the next colour
            r,g,b = feathers3.rgb_color_wheel(color_index)
            # Set the colour on the NeoPixel
            self.pixel[0] = (int(r*self.brightness), int(g*self.brightness), int(b*self.brightness))
            self.pixel.write()
            # Increase the wheel index
            color_index += 1

            # If the index == 255, loop it
            if color_index == 255:
                color_index = 0
                
            # Sleep for 15ms so the colour cycle isn't too fast
            time.sleep(0.015)