import os
import time

# libusb
os.environ["PATH"] = (
    r"C:\Users\sachi\AppData\Local\Programs\Python\Python311\Lib\site-packages\libusb_package;"
    + os.environ["PATH"]
)

from PyDMXControl.controllers import OpenDMXController
from PyDMXControl.profiles.Generic import Custom

# DMX接続
dmx = OpenDMXController()

# ライト登録
light = dmx.add_fixture(
    Custom,
    name="moving",
    start_channel=1,
    channels=9
)

# マスターON
light.set_channel(2, 100)

print("赤")
light.set_channel(3, 255)  # Red
light.set_channel(4, 0)
light.set_channel(5, 0)
light.set_channel(6, 0)
time.sleep(5)

print("緑")
light.set_channel(3, 0)
light.set_channel(4, 255)  # Green
light.set_channel(5, 0)
light.set_channel(6, 0)
time.sleep(5)

print("青")
light.set_channel(3, 0)
light.set_channel(4, 0)
light.set_channel(5, 255)  # Blue
light.set_channel(6, 0)
time.sleep(5)

print("白")
light.set_channel(3, 0)
light.set_channel(4, 0)
light.set_channel(5, 0)
light.set_channel(6, 255)  # White
time.sleep(5)

print("消灯")
light.set_channel(3, 0)
light.set_channel(4, 0)
light.set_channel(5, 0)
light.set_channel(6, 0)
light.set_channel(2, 0)

time.sleep(2)

dmx.close()