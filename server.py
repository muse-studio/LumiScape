from flask import Flask, request, jsonify, send_from_directory
import requests
import colorsys

from PyDMXControl.controllers import OpenDMXController
from PyDMXControl.profiles.Generic import Custom


app = Flask(__name__)


# =========================
# Hue 設定
# =========================
BRIDGE_IP = "192.168.11.2"
USERNAME = "bIJglK7T9JNqTP9iW6O2kfxqt8f4PWMIp08iwfti"
LIGHT_ID = "4"


# =========================
# Hue 色変換
# =========================
def hex_to_hue_sat(hex_color):
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    hue = int(h * 65535)
    sat = int(s * 254)
    bri = max(1, int(v * 254))

    return hue, sat, bri


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return r, g, b


# =========================
# DMX 設定
# =========================
dmx = OpenDMXController()

light = dmx.add_fixture(
    Custom,
    name="moving",
    start_channel=1,
    channels=9
)


def set_default_position():
    light.set_channel(0, 80)  # 実DMX CH1 X軸
    light.set_channel(1, 60)  # 実DMX CH2 Y軸


set_default_position()


def set_dmx_color(r, g, b, w=0, master=100):
    light.set_channel(2, master)  # 実DMX CH3 Master
    light.set_channel(3, r)       # 実DMX CH4 Red
    light.set_channel(4, g)       # 実DMX CH5 Green
    light.set_channel(5, b)       # 実DMX CH6 Blue
    light.set_channel(6, w)       # 実DMX CH7 White


def turn_off_dmx():
    set_dmx_color(0, 0, 0, 0, master=0)


# =========================
# HTML 表示
# =========================
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/initial")
def initial():
    return send_from_directory(".", "初期状態追加.html")


# =========================
# CORS 設定
# =========================
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


# =========================
# Hue 色変更
# URL: /hue/set_color
# =========================
@app.route("/hue/set_color", methods=["POST", "OPTIONS"])
def hue_set_color():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    color = data.get("color", "#ffffff")

    hue, sat, bri = hex_to_hue_sat(color)

    url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/{LIGHT_ID}/state"

    response = requests.put(url, json={
        "on": True,
        "hue": hue,
        "sat": sat,
        "bri": bri
    })

    return jsonify(response.json())


# =========================
# Hue ON/OFF
# URL: /hue/set_power
# =========================
@app.route("/hue/set_power", methods=["POST", "OPTIONS"])
def hue_set_power():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    is_on = data.get("on", False)

    url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/{LIGHT_ID}/state"

    response = requests.put(url, json={
        "on": is_on
    })

    return jsonify(response.json())


# =========================
# DMX 色変更
# URL: /dmx/set_color
# =========================
@app.route("/dmx/set_color", methods=["POST", "OPTIONS"])
def dmx_set_color_api():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()

    r = int(data.get("r", 0))
    g = int(data.get("g", 0))
    b = int(data.get("b", 0))
    w = int(data.get("w", 0))
    master = int(data.get("master", 100))

    set_dmx_color(r, g, b, w, master)

    return jsonify({
        "status": "ok",
        "r": r,
        "g": g,
        "b": b,
        "w": w,
        "master": master
    })


# =========================
# DMX 消灯
# URL: /dmx/off
# =========================
@app.route("/dmx/off", methods=["POST", "OPTIONS"])
def dmx_off_api():
    if request.method == "OPTIONS":
        return "", 200

    turn_off_dmx()

    return jsonify({
        "status": "off"
    })


# =========================
# 以前のHTML用：色変更
# URL: /set_color
#
# HTML側が fetch("/set_color") のままでも、
# Hue と DMX の両方を変更する
# =========================
@app.route("/set_color", methods=["POST", "OPTIONS"])
def set_color_all():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()

    color = data.get("color", "#ffffff")

    # Hue 色変更
    hue, sat, bri = hex_to_hue_sat(color)

    hue_url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/{LIGHT_ID}/state"

    hue_response = requests.put(hue_url, json={
        "on": True,
        "hue": hue,
        "sat": sat,
        "bri": bri
    })

    # DMX 色変更
    r, g, b = hex_to_rgb(color)

    set_dmx_color(r, g, b, w=0, master=100)

    return jsonify({
        "status": "ok",
        "color": color,
        "r": r,
        "g": g,
        "b": b,
        "hue": hue_response.json()
    })


# =========================
# 以前のHTML用：ON/OFF
# URL: /set_power
#
# HTML側が fetch("/set_power") のままでも、
# Hue と DMX の両方を制御する
# =========================
@app.route("/set_power", methods=["POST", "OPTIONS"])
def set_power_all():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    is_on = data.get("on", False)

    # Hue ON/OFF
    hue_url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/{LIGHT_ID}/state"

    hue_response = requests.put(hue_url, json={
        "on": is_on
    })

    # DMX ON/OFF
    if is_on:
        set_dmx_color(255, 255, 255, 0, master=100)
    else:
        turn_off_dmx()

    return jsonify({
        "status": "ok",
        "on": is_on,
        "hue": hue_response.json()
    })


# =========================
# 以前のHTML用：消灯
# URL: /off
#
# HTML側が fetch("/off") のままでも、
# Hue と DMX の両方を消灯する
# =========================
@app.route("/off", methods=["POST", "OPTIONS"])
def off_all():
    if request.method == "OPTIONS":
        return "", 200

    # Hue 消灯
    hue_url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/{LIGHT_ID}/state"

    hue_response = requests.put(hue_url, json={
        "on": False
    })

    # DMX 消灯
    turn_off_dmx()

    return jsonify({
        "status": "off",
        "hue": hue_response.json()
    })


# =========================
# サーバー起動
# =========================
if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)