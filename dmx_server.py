import os
from flask import Flask, request, jsonify, send_from_directory

# libusb の場所を追加
os.environ["PATH"] = (
    r"C:\Users\sachi\AppData\Local\Programs\Python\Python311\Lib\site-packages\libusb_package;"
    + os.environ["PATH"]
)

from PyDMXControl.controllers import OpenDMXController
from PyDMXControl.profiles.Generic import Custom

app = Flask(__name__)

# DMX初期化
dmx = OpenDMXController()

# 9CH / d001 のムービングライト
light = dmx.add_fixture(
    Custom,
    name="moving",
    start_channel=1,
    channels=9
)

def set_default_position():
    light.set_channel(0, 80)   # 実DMX CH1 X軸
    light.set_channel(1, 60)  # 実DMX CH2 Y軸

set_default_position()

def set_color(r, g, b, w=0, master=100):
    light.set_channel(2, master)  # 実DMX CH3 Master
    light.set_channel(3, r)       # 実DMX CH4 Red
    light.set_channel(4, g)       # 実DMX CH5 Green
    light.set_channel(5, b)       # 実DMX CH6 Blue
    light.set_channel(6, w)       # 実DMX CH7 White

def turn_off():
    set_color(0, 0, 0, 0, master=0)

# index.html を表示
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# CORS設定
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

# 実機ライトの色変更
@app.route("/set_color", methods=["POST", "OPTIONS"])
def set_color_api():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()

    r = int(data.get("r", 0))
    g = int(data.get("g", 0))
    b = int(data.get("b", 0))
    w = int(data.get("w", 0))
    master = int(data.get("master", 100))

    set_color(r, g, b, w, master)

    return jsonify({
        "status": "ok",
        "r": r,
        "g": g,
        "b": b,
        "w": w,
        "master": master
    })

# 実機ライト消灯
@app.route("/off", methods=["POST", "OPTIONS"])
def off_api():
    if request.method == "OPTIONS":
        return "", 200

    turn_off()
    return jsonify({"status": "off"})

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)