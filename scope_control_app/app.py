from flask import Response
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

import uvc  # >> https://github.com/pupil-labs/pyuvc
# import cv2
from PIL import Image

# initialize a flask object
app = Flask(__name__)
app.secret_key = '\x90\xb9\xd9\xaaj\x97\xee\xeb\x1c#\x16B\xb62\xb9\xa3rS\x15\xd2\x84;\x90c'

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame = None
lock = threading.Lock()

focus = 100

# class ScopeSettings:
#
#     # xPos = -1.0
#     # yPos = -1.0
#     # zPos = -1.0
#     # stepSize = 0.5
#     # x_center_pos = -9  # the X - position at which the scope is in the middle of the finger
#     # min_tof_dist = 27  # min distance in mm between the TOF sensor and the user finger
#
#     video_w = 1280
#     video_h = 720
#     video_fps = 30
#     focus = 100


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

    if request.method == 'POST' and request.is_json:
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

    else:
        print("did not set!")

    return "property set!"


# Save an image file to the server
@app.route('/save_image', methods=['POST'])
def save_image():

    # get User Id from cookie
    cookies = request.cookies
    uid = cookies.get("scan_uuid")

    # get current timestamp
    timestamp = strftime("%Y_%m_%d-%H_%M_%S", localtime())
    filename = f"pics/cap_{uid}_{timestamp}.png"
    print(f"saving file: {filename}")

    # Convert BGR to RGB and save the image
    im_rgb = outputFrame.bgr[:, :, [2, 1, 0]]
    Image.fromarray(im_rgb).save(filename)
    # cv2.imwrite(filename, outputFrame.bgr)
    print("file saved!")

    return "File Saved!"


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# Captures frames in the background (in a separate thread)
def capture_frame():
    # grab global references to the video stream, output frame, and lock variables
    global cap, outputFrame, lock
    while True:
        frame = cap.get_frame_robust()
        with lock:
            outputFrame = frame


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            # flag, encodedImage = cv2.imencode(".jpg", outputFrame)
            # if not flag:
            #     continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(outputFrame.jpeg_buffer) + b'\r\n')


if __name__ == '__main__':
    # commandline argument parser
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
    # ap.add_argument("-o", "--port", type=int, required=True,
    #   help="ephemeral port number of the server (1024 to 65535)")
    # args = vars(ap.parse_args())

    # Load scope settings from a JSON File
    with open('scope_settings.json', 'r') as f:
        uvc_settings = json.load(f)

    # UVC Setup
    logging.basicConfig(level=logging.INFO)
    dev_list = uvc.device_list()

    # Find the G-Scope device number within all attached devices.
    scopeDeviceId = 0
    for i, device in enumerate(dev_list):
        print(f"{i}: {device['name']}")
        if "G-Scope" in device["name"]:
            scopeDeviceId = i

    print(f"G-Scope device id is: {scopeDeviceId}")

    # Add G-Scope as new capture device and get its control properties
    cap = uvc.Capture(dev_list[scopeDeviceId]["uid"])
    controls_dict = dict([(c.display_name, c) for c in cap.controls])

    print(cap.avaible_modes)
    print("--- Available Controls & Init Values: ---")
    for control in controls_dict:
        print(f"{control}: {controls_dict[control].value}")
    print("---------------------------")

    time.sleep(1)

    # Capture one frame to initialize the microscope
    cap.frame_mode = (uvc_settings["video_w"], uvc_settings["video_h"], uvc_settings["video_fps"])
    init_frame = cap.get_frame_robust()
    time.sleep(2)

    # Apply Custom Setting to the Scope via UVC
    print("--- Adjusting custom control settings: ---")
    for control in controls_dict:
        controls_dict[control].value = uvc_settings[control]
        print(f"{control}: {controls_dict[control].value}")
    print("---------------------------")

    time.sleep(1)

    # Start a thread that will capture frames from the scope
    t = threading.Thread(target=capture_frame, args=())
    t.daemon = True
    t.start()

    # start the flask app
    # app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=False)


print("releasing scope...")
cap = None
print("scope released!")
print("APP CLOSED!")