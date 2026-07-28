import os

os.environ["PATH"] = (
    r"C:\Users\sachi\AppData\Local\Programs\Python\Python311\Lib\site-packages\libusb_package;"
    + os.environ["PATH"]
)

from PyDMXControl.controllers import OpenDMXController
from PyDMXControl.profiles.Generic import Custom

dmx = OpenDMXController()

light = dmx.add_fixture(Custom, name="moving", start_channel=1, channels=9)

def set_color(r, g, b, w=0, master=100):
    light.set_channel(2, master)
    light.set_channel(3, r)
    light.set_channel(4, g)
    light.set_channel(5, b)
    light.set_channel(6, w)

def turn_off():
    set_color(0, 0, 0, 0, master=0)

try:
    while True:
        print("\n0〜255で入力してください。終了は q")
        r = input("R: ")
        if r == "q":
            break

        g = input("G: ")
        b = input("B: ")
        w = input("W: ")

        r = int(r)
        g = int(g)
        b = int(b)
        w = int(w)

        set_color(r, g, b, w)
        print(f"R={r}, G={g}, B={b}, W={w} で点灯中")

finally:
    turn_off()
    dmx.close()