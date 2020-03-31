from flask import Response, send_file
from flask import Flask, jsonify, redirect, url_for, request, make_response
from flask import render_template
import json

import argparse
import threading
import uuid
import time
from time import localtime, strftime
import datetime
import logging

import spidev as SPI
import ST7789

import uvc  # >> https://github.com/pupil-labs/pyuvc
from PIL import Image, ImageDraw, ImageFont

# import keyboard
# import cv2

# Raspberry Pi pin config:
RST = 27
DC = 25
BL = 24
bus = 0 
device = 0

# init 240x240 display with hardware SPI:
disp = ST7789.ST7789(SPI.SpiDev(bus, device),RST, DC, BL)
disp.Init()
disp.clear()

# initialize a flask object
app = Flask(__name__)

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
lock = threading.Lock()
outputFrame = None
isCapturing = True
cap = None
focus = 100

@app.route("/")
def index():

    cookies = request.cookies

    # Check for existing cookie with UID. Make a new one if doesnt exist
    if cookies.get("scan_uuid"):
        uid = cookies.get("scan_uuid")
        res = make_response(render_template("index.html", scopeSettings=controls_dict, userId=uid))
    else:
        # Generate a random UID 8 characters long
        uid = uuid.uuid4().hex
        uid = uid.upper()[0:8]
        res = make_response(render_template("index.html", scopeSettings=controls_dict, userId=uid))
        # Create the cookie
        res.set_cookie(
            "scan_uuid",
            value=uid,
            max_age=None,
            expires=datetime.datetime.now() + datetime.timedelta(days=90),
            path='/',
            domain=None,
            secure=False,
        )

    # return the rendered template
    return res


@app.route('/set_control', methods=['POST'])
def set_ctrl():
    global controls_dict, focus

    if isCapturing and request.method == 'POST' and request.is_json:
        req_data = request.get_json()
        ctrl = req_data['control']
        val = int(req_data['value'])

        # Adjust scope controls
        # todo: fix smooth transition between auto-focus and manual focus
        if ctrl == 'Absolute Focus':
            # print(controls_dict['Absolute Focus'])
            # foc = int(controls_dict['Absolute Focus'].value)
            focus += val
            print(focus)
            controls_dict['Absolute Focus'].value = focus
            print(controls_dict['Absolute Focus'])
        else:
            print(f"control: {ctrl}  /  value: {val}")
            controls_dict[ctrl].value = val

        # if ctrl == "Auto Focus":
        #     time.sleep(2)
        #     scopeSettings.focus = controls_dict['Absolute Focus'].value
        #     print(f"{controls_dict['Absolute Focus'].value} // {scopeSettings.focus}")
        res = "property set!"
    else:
        print("did not set!")
        res = "could not set!"

    return res


# Save an image file to the server
@app.route('/save_image', methods=['POST'])
def save_image():

    if isCapturing:
        # get User Id from cookie
        cookies = request.cookies
        uid = cookies.get("scan_uuid")

        # get current timestamp
        timestamp = strftime("%Y_%m_%d-%H_%M_%S", localtime())
        filename = f"pics/cap_{uid}_{timestamp}.png"
        print(f"saving img file: {filename}")

        # Convert BGR to RGB and save the image
        im_rgb = outputFrame.bgr[:, :, [2, 1, 0]]
        Image.fromarray(im_rgb).save(filename)
        # cv2.imwrite(filename, outputFrame.bgr)
        res = "file saved!"
    else:
        res = "could not save!"

    print(res)
    return res


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# Captures frames in the background (in a separate thread)
def capture_frame():
    # grab global references to the video stream, output frame, and lock variables
    global cap, outputFrame, lock, isCapturing
    while True:
        if isCapturing:
            frame = cap.get_frame_robust()
            with lock:
                outputFrame = frame
        else:
            time.sleep(0.5)


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock, isCapturing

    # An image to display when the scope is off
    placeholderImage = open("static/img/scope_off.jpg", "rb").read()

    while True:
        with lock:
            if isCapturing and outputFrame is None:
                continue

        if isCapturing:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(outputFrame.jpeg_buffer) + b'\r\n')
        else:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + placeholderImage + b'\r\n')


def toggle_capture(e):
    global isCapturing, cap

    if not isCapturing:
        init_scope()
        isCapturing = True
        print("Start Capturing!")
    else:
        isCapturing = False
        cap = None
        print("Stopped Capturing!")


def init_scope():
    global cap, uvc_settings, controls_dict, dev_list, scopeDeviceId

    # Add G-Scope as new capture device and get its control properties
    cap = uvc.Capture(dev_list[scopeDeviceId]["uid"])
    time.sleep(1)

    # Load supported device controls list
    controls_dict = dict([(c.display_name, c) for c in cap.controls])

    print(cap.avaible_modes)
    print("--- Available Controls & Init Values: ---")
    for control in controls_dict:
        print(f"{control}: {controls_dict[control].value}")
    print("---------------------------")
    # Apply Custom Setting to the Scope via UVC
    print("--- Adjusting custom control settings: ---")
    for control in controls_dict:
        controls_dict[control].value = uvc_settings[control]
        print(f"{control}: {controls_dict[control].value}")
    print("---------------------------")
    time.sleep(1)

    # Capture one frame to initialize the microscope
    cap.frame_mode = (uvc_settings["video_w"], uvc_settings["video_h"], uvc_settings["video_fps"])
    cap.get_frame_robust()
    time.sleep(1)


# commandline argument parser
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
# ap.add_argument("-o", "--port", type=int, required=True,
#   help="ephemeral port number of the server (1024 to 65535)")
# args = vars(ap.parse_args())

logging.basicConfig(level=logging.INFO)

# Create blank image for drawing on display.
disp_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
draw = ImageDraw.Draw(disp_image)
fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 16)
draw.text((5, 5), 'Conecting to G-Scope...', font=fnt, fill = "WHITE")
disp.ShowImage(disp_image,0,0)


# Load scope settings from a JSON File
with open('scope_settings.json', 'r') as f:
    uvc_settings = json.load(f)

# Find the G-Scope device number within all attached devices.
dev_list = uvc.device_list()
scopeDeviceId = 0
for i, device in enumerate(dev_list):
    print(f"{i}: {device['name']}")
    if "G-Scope" in device["name"]:
        scopeDeviceId = i
print(f"G-Scope device id is: {scopeDeviceId}")

# Connect to the scope...
init_scope()

draw.text((5, 25), 'G-Scope Online!', font=fnt, fill = "WHITE")
draw.text((5, 45), 'Please connect to the \n "cap_app" WiFi Network', font=fnt, fill = "WHITE")
disp.ShowImage(disp_image,0,0)

# Start a thread that will capture frames from the scope
t = threading.Thread(target=capture_frame, args=())
t.daemon = True
t.start()

print("Press the S key to Start/Stop Capturing")
# keyboard.on_release_key("s", toggle_capture)


if __name__ == '__main__':
    # start the flask app
    # app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=False)