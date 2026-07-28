import os
import time

os.environ["PATH"] = (
    r"C:\Users\sachi\AppData\Local\Programs\Python\Python311\Lib\site-packages\libusb_package;"
    + os.environ["PATH"]
)

from PyDMXControl.controllers import OpenDMXController
from PyDMXControl.profiles.Generic import Custom

dmx = OpenDMXController()

light = dmx.add_fixture(
    Custom,
    name="moving",
    start_channel=1,
    channels=9
)

def set_color(r, g, b, w=0, master=100):
    light.set_channel(2, master)  # Master
    light.set_channel(3, r)       # Red
    light.set_channel(4, g)       # Green
    light.set_channel(5, b)       # Blue
    light.set_channel(6, w)       # White

def turn_off():
    set_color(0, 0, 0, 0, master=0)

try:
    print("赤")
    set_color(255, 0, 0)
    time.sleep(3)

    print("緑")
    set_color(0, 255, 0)
    time.sleep(3)

    print("青")
    set_color(0, 0, 255)
    time.sleep(3)

    print("白")
    set_color(0, 0, 0, 255)
    time.sleep(3)

    print("紫")
    set_color(255, 0, 255)
    time.sleep(3)

    print("黄色")
    set_color(255, 255, 0)
    time.sleep(3)

    print("消灯")
    turn_off()
    time.sleep(2)

finally:
    dmx.close()