# import imutils
# from imutils.video import VideoStream
from flask import Response
from flask import Flask, jsonify, redirect, url_for, request
from flask import render_template
import threading
import argparse
import time
from time import localtime, strftime
import uvc  # >> https://github.com/pupil-labs/pyuvc
import logging
import cv2

# initialize a flask object
app = Flask(__name__)

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame = None
lock = threading.Lock()


class ScopeSettings:

    # todo: add app settings to config default values

    # xPos = -1.0
    # yPos = -1.0
    # zPos = -1.0
    # stepSize = 0.5
    # x_center_pos = -9  # the X - position at which the scope is in the middle of the finger
    # min_tof_dist = 27  # min distance in mm between the TOF sensor and the user finger

    video_w = 1280
    video_h = 720
    video_fps = 30
    focus = 100
    white_balance = 6000


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/set_control', methods=['POST'])
def set_ctrl():
    if request.method == 'POST' and request.is_json:
        req_data = request.get_json()
        ctrl = req_data['control']
        val = req_data['value']

        # increment the scope focus by by a step
        # todo: sort auto-focus to manual focus smooth transition
        if ctrl == 'Absolute Focus':
            # print(controls_dict['Absolute Focus'].value)
            # ScopeSettings.focus = controls_dict['Absolute Focus'].value
            val = ScopeSettings.focus = ScopeSettings.focus + val

        # Apply the setting to the scope
        print(f"control: {ctrl}  /  value: {val}")
        controls_dict[ctrl].value = int(val)
    else:
        print("did not set!")

    return "property set!"


# Save an image file to the server
@app.route('/save_image', methods=['POST'])
def save_image():
    timestamp = strftime("%Y_%m_%d-%H_%M_%S", localtime())
    filename = f"pics/cap_{timestamp}.png"
    print(f"saving file: {filename}")
    cv2.imwrite(filename, outputFrame)
    print("file saved!")

    return "File Saved!"


def capture_frame():
    # grab global references to the video stream, output frame, and lock variables
    global outputFrame, lock
    while True:
        frame = cap.get_frame_robust()
        with lock:
            outputFrame = frame.bgr


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # commandline argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True, help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())

    # UVC Setup
    logging.basicConfig(level=logging.INFO)
    dev_list = uvc.device_list()
    print(dev_list)

    # Todo: make sure it always connects to the G-Scope
    # Add new capture device and its control properties
    cap = uvc.Capture(dev_list[0]["uid"])
    controls_dict = dict([(c.display_name, c) for c in cap.controls])

    print(cap.avaible_modes)
    print("--- Available Controls: ---")
    for control in controls_dict:
        print(control)
    print("---------------------------")

    time.sleep(1)

    # Capture a frame to initialize the microscope
    cap.frame_mode = (ScopeSettings.video_w, ScopeSettings.video_h, ScopeSettings.video_fps)
    init_frame = cap.get_frame_robust()
    time.sleep(2)

    # Set Auto-focus to false and set a custom value
    controls_dict['Auto Focus'].value = 0
    ScopeSettings.focus = controls_dict['Absolute Focus'].value

    # Set Auto-WB to false and set a custom value
    controls_dict['White Balance temperature,Auto'].value = 0
    controls_dict['White Balance temperature'].value = ScopeSettings.white_balance

    time.sleep(1)

    # Start a thread that will capture frames from the scope
    t = threading.Thread(target=capture_frame, args=())
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)


print("releasing scope...")
cap = None
print("scope released!")
print("APP CLOSED!")