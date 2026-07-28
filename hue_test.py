import requests
import time

BRIDGE_IP = "192.168.11.2"
USERNAME = "bIJglK7T9JNqTP9iW6O2kfxqt8f4PWMIp08iwfti"

url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/4/state"

colors = [
    0,      # 赤
    12750,  # 黄
    25500,  # 緑
    46920,  # 青
    52000,  # 紫
]

for hue in colors:
    requests.put(
    url,
    json={
        "on": True,
        "xy": [0.1532, 0.0475],
        "bri": 254
    }
)