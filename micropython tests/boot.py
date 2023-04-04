# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)

import ledControl
neopixel = ledControl.DeviceStatus(0.05, 'red')


WIFI_SSID = "Huz-Matebook"
WIFI_PASS = "bu*mrbwrQ59iY^"

def connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASS)
        # while the below while loop is part of the standard recommended approach,
        # I found it could hang the device if run with connect() on boot
        # while not sta_if.isconnected():
        #     pass
    # print('network config:', sta_if.ifconfig())
    return True

def showip():
    import network
    sta_if = network.WLAN(network.STA_IF)
    print('network config:', sta_if.ifconfig())

if connect():
    neopixel.set_led('purple')

import webrepl
webrepl.start()
neopixel.set_led('purple')




