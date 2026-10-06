from flask import Flask, request, jsonify, send_from_directory
import requests
import colorsys

from PyDMXControl.controllers import OpenDMXController
from PyDMXControl.profiles.Generic import Custom


app = Flask(__name__)


# ==================================================
# Hue 設定
# ==================================================

BRIDGE_IP = "192.168.11.2"

# 直近でcurlで動作確認できたUSERNAME
USERNAME = "R4ts8FgXpun1rKBy2fmfDXEVwYZxpnbbWhqN5lxP"

# Hueテープライト
TAPE_LIGHT_ID = "4"

# Hueスマートライト
SMART_LIGHT_1_ID = "1"
SMART_LIGHT_2_ID = "2"


# ==================================================
# Hue 色変換
# ==================================================

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


# ==================================================
# Hue 共通処理
# ==================================================

def set_hue_color(light_id, color):
    hue, sat, bri = hex_to_hue_sat(color)

    url = (
        f"http://{BRIDGE_IP}"
        f"/api/{USERNAME}"
        f"/lights/{light_id}/state"
    )

    response = requests.put(
        url,
        json={
            "on": True,
            "hue": hue,
            "sat": sat,
            "bri": bri
        }
    )

    return response.json()


def set_hue_power(light_id, is_on):
    url = (
        f"http://{BRIDGE_IP}"
        f"/api/{USERNAME}"
        f"/lights/{light_id}/state"
    )

    response = requests.put(
        url,
        json={
            "on": is_on
        }
    )

    return response.json()


# ==================================================
# DMX 設定
# ==================================================

dmx = None
light = None

try:
    dmx = OpenDMXController()

    light = dmx.add_fixture(
        Custom,
        name="moving",
        start_channel=1,
        channels=9
    )

    print("DMX接続成功")

except Exception as e:
    print("DMXは接続されていません")
    print("Hueのみ使用できます")
    print("DMXエラー:", e)


# ==================================================
# DMX 初期位置
# ==================================================

def set_default_position():
    if light is None:
        return

    light.set_channel(0, 0)
    light.set_channel(1, 60)


if light is not None:
    set_default_position()


# ==================================================
# DMX 向き変更
# ==================================================

def set_dmx_position(pan, tilt):

    if light is None:
        print("DMX未接続のため向き変更をスキップ")
        return False

    pan = max(0, min(255, int(pan)))
    tilt = max(0, min(255, int(tilt)))

    light.set_channel(0, pan)
    light.set_channel(1, tilt)

    return True

@app.route(
    "/dmx/set_pan",
    methods=["POST", "OPTIONS"]
)
def dmx_set_pan_api():

    if request.method == "OPTIONS":
        return "", 200

    if light is None:
        return jsonify({
            "status":
                "dmx_not_connected"
        }), 200

    data = request.get_json()

    pan = int(
        data.get(
            "pan",
            0
        )
    )

    pan = max(
        0,
        min(255, pan)
    )

    # CH1 PAN
    light.set_channel(
        0,
        pan
    )

    return jsonify({
        "status": "ok",
        "pan": pan
    })

@app.route(
    "/dmx/set_tilt",
    methods=["POST", "OPTIONS"]
)
def dmx_set_tilt_api():

    if request.method == "OPTIONS":
        return "", 200

    if light is None:
        return jsonify({
            "status":
                "dmx_not_connected"
        }), 200

    data = request.get_json()

    tilt = int(
        data.get(
            "tilt",
            60
        )
    )

    tilt = max(
        0,
        min(255, tilt)
    )

    # CH2 TILT
    light.set_channel(
        1,
        tilt
    )

    return jsonify({
        "status": "ok",
        "tilt": tilt
    })

# ==================================================
# DMX 色変更
# ==================================================

def set_dmx_color(
    r,
    g,
    b,
    w=0,
    master=100
):

    if light is None:
        print("DMX未接続のため色変更をスキップ")
        return False

    light.set_channel(2, master)
    light.set_channel(3, r)
    light.set_channel(4, g)
    light.set_channel(5, b)
    light.set_channel(6, w)

    return True


def turn_off_dmx():

    if light is None:
        return False

    set_dmx_color(
        0,
        0,
        0,
        0,
        master=0
    )

    return True


# ==================================================
# HTML 表示
# ==================================================

@app.route("/")
def index():
    return send_from_directory(
        ".",
        "index.html"
    )


@app.route("/initial")
def initial():
    return send_from_directory(
        ".",
        "初期状態追加.html"
    )

@app.route("/izushi")
def izushi():
    return send_from_directory(
        ".",
        "出石レンタル.html"
    )


# ==================================================
# CORS
# ==================================================

@app.after_request
def after_request(response):

    response.headers.add(
        "Access-Control-Allow-Origin",
        "*"
    )

    response.headers.add(
        "Access-Control-Allow-Headers",
        "Content-Type"
    )

    response.headers.add(
        "Access-Control-Allow-Methods",
        "GET, POST, OPTIONS"
    )

    return response


# ==================================================
# Hue スマートライト 色変更
# ==================================================

@app.route("/hue/smart1/set_color", methods=["POST", "OPTIONS"])
def smart1_set_color():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    color = data.get("color", "#ffffff")
    result = set_hue_color(SMART_LIGHT_1_ID,color)
    return jsonify({
      "status": "ok","color": color,"response": result
    })

@app.route("/hue/smart2/set_color", methods=["POST", "OPTIONS"])
def smart2_set_color():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    color = data.get("color", "#ffffff")
    result = set_hue_color(
        SMART_LIGHT_2_ID,color
    )
    return jsonify({
        "status": "ok","color": color,"response": result
    })


# ==================================================
# Hue スマートライト ON/OFF
# ==================================================
@app.route("/hue/smart1/set_power", methods=["POST", "OPTIONS"])
def smart1_set_power():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    is_on = data.get("on", False)
    result = set_hue_power(
        SMART_LIGHT_1_ID,is_on
    )
    return jsonify({
        "status": "ok",
        "on": is_on,
        "response": result
    })

@app.route("/hue/smart2/set_power", methods=["POST", "OPTIONS"])
def smart2_set_power():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    is_on = data.get("on", False)
    result = set_hue_power(
        SMART_LIGHT_2_ID,is_on
    )
    return jsonify({
      "status": "ok","on": is_on,"response": result
    })

# ==================================================
# Hue テープライト 色変更
# ==================================================

@app.route("/hue/tape/set_color", methods=["POST", "OPTIONS"])
def tape_set_color():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    color = data.get("color", "#ffffff")

    result = set_hue_color(
        TAPE_LIGHT_ID,
        color
    )

    return jsonify({
        "status": "ok",
        "color": color,
        "response": result
    })

# ==================================================
# Hue テープライト ON/OFF
# ==================================================
@app.route("/hue/tape/set_power", methods=["POST", "OPTIONS"])
def tape_set_power():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json()
    is_on = data.get("on", False)
    result = set_hue_power(
        TAPE_LIGHT_ID,
        is_on
    )
    return jsonify({
        "status": "ok",
        "on": is_on,
        "response": result
    })


# ==================================================
# DMX 色変更
# ==================================================

@app.route(
    "/dmx/set_color",
    methods=["POST", "OPTIONS"]
)
def dmx_set_color_api():

    if request.method == "OPTIONS":
        return "", 200

    if light is None:
        return jsonify({
            "status": "dmx_not_connected"
        }), 200

    data = request.get_json()

    r = int(data.get("r", 0))
    g = int(data.get("g", 0))
    b = int(data.get("b", 0))
    w = int(data.get("w", 0))

    master = int(
        data.get(
            "master",
            100
        )
    )

    set_dmx_color(
        r,
        g,
        b,
        w,
        master
    )

    return jsonify({
        "status": "ok",
        "r": r,
        "g": g,
        "b": b,
        "w": w,
        "master": master
    })


# ==================================================
# DMX 向き変更
# ==================================================

@app.route(
    "/dmx/set_position",
    methods=["POST", "OPTIONS"]
)
def dmx_set_position_api():

    if request.method == "OPTIONS":
        return "", 200

    if light is None:
        return jsonify({
            "status": "dmx_not_connected"
        }), 200

    data = request.get_json()

    pan = int(
        data.get(
            "pan",
            80
        )
    )

    tilt = int(
        data.get(
            "tilt",
            60
        )
    )

    set_dmx_position(
        pan,
        tilt
    )

    return jsonify({
        "status": "ok",
        "pan": pan,
        "tilt": tilt
    })


# ==================================================
# DMX 消灯
# ==================================================

@app.route(
    "/dmx/off",
    methods=["POST", "OPTIONS"]
)
def dmx_off_api():

    if request.method == "OPTIONS":
        return "", 200

    if light is None:
        return jsonify({
            "status": "dmx_not_connected"
        }), 200

    turn_off_dmx()

    return jsonify({
        "status": "off"
    })


# ==================================================
# 全実機消灯
# ==================================================

@app.route(
    "/all/off",
    methods=["POST", "OPTIONS"]
)
def all_off():

    if request.method == "OPTIONS":
        return "", 200
    # テープライト
    set_hue_power(
        TAPE_LIGHT_ID,
        False
    )
    # スマートライト1 OFF
    set_hue_power(
        SMART_LIGHT_1_ID,
        False
    )

    # スマートライト2 OFF
    set_hue_power(
        SMART_LIGHT_2_ID,
        False
    )

    # DMX
    if light is not None:
        turn_off_dmx()

    return jsonify({
        "status": "all_off"
    })


# ==================================================
# サーバー起動
# ==================================================

if __name__ == "__main__":
    app.run(
        debug=False,
        use_reloader=False
    )