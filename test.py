import os
import time

# libusb の場所をPython側でも追加
os.environ["PATH"] = r"C:\Users\sachi\AppData\Local\Programs\Python\Python311\Lib\site-packages\libusb_package;" + os.environ["PATH"]

from PyDMXControl.controllers import OpenDMXController
from PyDMXControl.profiles.Generic import Custom

dmx = OpenDMXController()

light = dmx.add_fixture(Custom, name="moving", start_channel=1, channels=9)

# 9CH / d001 用
light.set_channel(2, 100)  # 実DMX CH3 Master
light.set_channel(3, 255)  # 実DMX CH4 Red

print("赤く光るはずです")
print(dmx.channels)

time.sleep(20)

light.set_channel(3, 0)
light.set_channel(2, 0)

print("消灯しました")
time.sleep(3)

dmx.close()