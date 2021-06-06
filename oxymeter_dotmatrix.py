'''
This Code prints SpO2 and Heart Rate data on DotMartix Display - Display is 24Wx8H
Sensor used is MAX30100
HW Raspberry Pi 2B
Sensor Connection to Raspberry Pi
Sensor Vcc - Raspberry Pi 3.3V (pin 1)
Sensor GND - Raspberry Pi GND (pin 9)
Sensor SCL - Raspberry Pi SCL(pin 5)
Sensor SDA - Raspberry Pi SDA(pin 3)

Dependency - you'll require to install luma library
try pip3 install luma
'''

import re
import time
import argparse
import datetime
import random
import os
import max30100

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
from luma.core import legacy
import time


mx30 = max30100.MAX30100()
mx30.enable_spo2()

# Generates Moving Average - This will filter data and improve stability of readings
def moving_average(numbers):
    window_size = 4
    i = 0
    # moving_averages = []
    while i < len(numbers) - window_size + 1:
        this_window = numbers[i : i + window_size]
        window_average = sum(this_window) / window_size
        # moving_averages.append(window_average)
        i += 1
    try:
        return int((window_average/100))
    except:
        pass

# If HeartRate is <10 function assumes Fingure Not present and will not show incorrect data
# Also If SpO2 readings goes beyond 100. It will be shown as 100.
def display_filter(moving_average_bpm,moving_average_sp02):
    try:
        if(moving_average_bpm<10):
            moving_average_bpm ='-'
            moving_average_sp02 = '-'
        else:
            if(moving_average_sp02>=100):
                moving_average_sp02 = 100
        return moving_average_bpm, moving_average_sp02
    except:
        return moving_average_bpm, moving_average_sp02

# Dot Matrix Initialization
def init_device():
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, width=24, height=8)
    device.contrast(0x7f)
    return device

def update_bpm(bpm,spo2):
    device = init_device()
    device.contrast(0x1f)
    with canvas(device) as draw:
        legacy.text(draw, (0, 0), "\0", fill="white", font=[[0x00, 0x1c, 0x3e, 0x7e, 0xfc, 0x7e, 0x3e, 0x1c]]) 
        text(draw, (10,0), str(bpm), fill="white", font=proportional(TINY_FONT))

def update_spo2(bpm,spo2):
    device = init_device()
    device.contrast(0x1f)
    with canvas(device) as draw:
        legacy.text(draw, (0, 0), "\0", fill="white", font=[[0x0e, 0x11, 0x11, 0x11, 0x0e, 0xe0, 0xa8, 0xb8]])  
        text(draw, (10,0), str(spo2), fill="white", font=proportional(TINY_FONT))

def intro_message():
    device = init_device()
    device.contrast(0x1f)
    msg = "Pulse Oxymeter using Raspberry Pi "
    show_message(device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay = 0.02)

def main():
    intro_message()
    while True:
        mx30.read_sensor()
        hb = int(mx30.ir / 100)
        spo2 = int(mx30.red / 100)
        if mx30.ir != mx30.buffer_ir :
            moving_average_bpm = (moving_average(mx30.buffer_ir))
        if mx30.red != mx30.buffer_red:
            moving_average_sp02 = (moving_average(mx30.buffer_red))
        bpm,spo2 = display_filter(moving_average_bpm,moving_average_sp02)
        update_bpm(bpm,spo2)
        time.sleep(1)
        update_spo2(bpm,spo2)
        time.sleep(1)

main()
