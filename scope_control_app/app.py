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
from pathlib import Path
from os import listdir
from os.path import isfile, join

# Imports to use with the Raspberry Pi 1.3" Display Hat
# import spidev as SPI
# import ST7789
# import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont



# Camera UVC Properties control library
import uvc  # >> https://github.com/pupil-labs/pyuvc

# import keyboard
# import cv2

# Raspberry Pi pin config:
# RST_PIN        = 25
# CS_PIN         = 8
# DC_PIN         = 24
#
# KEY_UP_PIN     = 6
# KEY_DOWN_PIN   = 19
# KEY_LEFT_PIN   = 5
# KEY_RIGHT_PIN  = 26
# KEY_PRESS_PIN  = 13
#
# KEY1_PIN       = 21
# KEY2_PIN       = 20
# KEY3_PIN       = 16
#
# RST = 27
# DC = 25
# BL = 24
# bus = 0
# device = 0

# init 240x240 display with hardware SPI:
# disp = ST7789.ST7789(SPI.SpiDev(bus, device),RST, DC, BL)
# disp.Init()
# disp.clear()

#init GPIO
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

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

        # Check if a directory with current UID exists, if not create one
        Path(f"static/captured_pics/{uid}").mkdir(parents=True, exist_ok=True)

        # get current timestamp
        timestamp = strftime("%Y_%m_%d-%H_%M_%S", localtime())
        filename = f"static/captured_pics/{uid}/cap_{uid}_{timestamp}.png"
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


# An image gallery of captured images
@app.route("/img_gallery")
def img_gallery():
    cookies = request.cookies
    uid = cookies.get("scan_uuid")

    userFilesPath = f"static/captured_pics/{uid}"
    filesList = [f for f in listdir(userFilesPath) if isfile(join(userFilesPath, f))]

    return render_template('gallery.html', userId=uid, images=filesList)


# Captures frames in the background (in a separate thread)
def capture_frame():
    # grab global references to the video stream, output frame, and lock variables
    global cap, outputFrame, lock, isCapturing
    while True:
        if isCapturing:
            frame = cap.get_frame_robust()
            with lock:
                outputFrame = frame
                time.sleep(0.05)
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


def toggle_capture():
    global isCapturing, cap

    if not isCapturing:
        init_scope()
        isCapturing = True
        print("Start Capturing!")
    else:
        isCapturing = False
        cap = None
        print("Stopped Capturing!")        
        # Update LCD Display
        # draw.rectangle([(0,0),(240,240)],fill = "BLACK")
        # draw.text((5, 100), 'Scope is OFF', font=fnt, fill = "WHITE")
        # img = disp_image.rotate(90)
        # disp.ShowImage(img,0,0)

        

# def get_keypress():
#
#     key_a_pressed = False
#     key_b_pressed = False
#     key_c_pressed = False
#
#    # try:
#     while 1:
#         if GPIO.input(KEY1_PIN): # button is released
#             key_a_pressed = False
#         elif not key_a_pressed: # button is pressed:
#             key_a_pressed = True
#             print("KEY-A")
#
#         # Key B: Turns the scope on or off
#         if GPIO.input(KEY2_PIN): # button is released
#             key_b_pressed = False
#             time.sleep(1)
#         elif not key_b_pressed: # button is pressed:
#             key_b_pressed = True
#             toggle_capture()
#             print("KEY-B")
#
#         if GPIO.input(KEY3_PIN): # button is released
#             key_c_pressed = False
#         elif not key_c_pressed: # button is pressed:
#             key_c_pressed = True
#             print("KEY-C")
#
# #    except:
#  #       print("except")
#
#   #  GPIO.cleanup()
    


def init_scope():
    global cap, uvc_settings, controls_dict, dev_list, scopeDeviceId
    
    # Update LCD Display
    # draw.rectangle([(0,0),(240,240)],fill = "BLACK")
    # draw.text((5, 5), 'Conecting to G-Scope...', font=fnt, fill = "WHITE")
    # img = disp_image.rotate(90)
    # disp.ShowImage(img,0,0)

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
    
    # Update LCD Display
    # draw.text((5, 25), 'G-Scope Online!', font=fnt, fill = "WHITE")
    # draw.text((5, 100), '1. Connect to the \n "scoPi" WiFi \n\n 2. Goto: \n http://192.168.4.1:8000', font=fnt, fill = "WHITE")
    # img = disp_image.rotate(90)
    # disp.ShowImage(img,0,0)
    
    time.sleep(1)


# commandline argument parser
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
# ap.add_argument("-o", "--port", type=int, required=True,
#   help="ephemeral port number of the server (1024 to 65535)")
# args = vars(ap.parse_args())

logging.basicConfig(level=logging.INFO)

# Create blank image for drawing on display.
# disp.clear()
# disp_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
# draw = ImageDraw.Draw(disp_image)
# fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 16)


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


# Start a thread that will capture frames from the scope
capture_thread = threading.Thread(target=capture_frame, args=())
capture_thread.daemon = True
capture_thread.start()

# Start a thread that will capture button press on the PI LCD Screen Hat
# keypress_thread = threading.Thread(target=get_keypress, args=())
# keypress_thread.daemon = True
# keypress_thread.start()

print("Press the S key to Start/Stop Capturing")


if __name__ == '__main__':
    # start the flask app
    # app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=False)