""" The Main Module of the cope control APP """
import json
import logging
import threading
import time
import uuid
import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path
from pyzip import PyZip
from pyfolder import PyFolder
# import argparse
# import keyboard
import cv2
# Camera UVC Properties control library
import uvc  # >> https://github.com/pupil-labs/pyuvc
# GRBL Control Class
from grbl import GrblControl
# Sensors feed class
from sensors import SensorsFeed

# Flask web app framework
from flask import (Flask, Response, jsonify, make_response, redirect,
                   render_template, request, send_file, url_for)

# initialize a flask object
APP = Flask(__name__)

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
lock = threading.Lock()
outputFrame = None
isCapturing = True
cap = None
controls_dict = dict()
FOCUS = 100
# the FPS at which videos are being captured
CAP_FPS = 20
# the FPS at whiche the videos is streamed to the browser
STREAM_FPS = 12
UVC_SETTINGS = None
# In Seconds, How often to reset the G-Scope to avoid crashing (PYUVC clock correction workaround)
SCOPE_RESET_FREQ = 90
SCOPE_RESET_REQUIRED = False


@APP.route("/")
def index():

    cookies = request.cookies

    # Check for existing cookie with UID. Make a new one if doesnt exist
    if cookies.get("scan_uuid"):
        uid = cookies.get("scan_uuid")
        res = make_response(render_template("index.html", 
                                            scopeSettings=controls_dict, 
                                            userId=uid, 
                                            settingsMode=UVC_SETTINGS["setting_available"], 
                                            roboscopeMdde = UVC_SETTINGS["robo_scope_mode"],
                                            step_size = UVC_SETTINGS["default_step_size"],
                                            feed_rate = UVC_SETTINGS["default_feed_rate"]))
    else:
        # Generate a random UID 8 characters long
        uid = uuid.uuid4().hex
        uid = uid.upper()[0:8]
        res = make_response(render_template("index.html", 
                                            scopeSettings=controls_dict, 
                                            userId=uid, 
                                            settingsMode=UVC_SETTINGS["setting_available"], 
                                            roboscopeMdde = UVC_SETTINGS["robo_scope_mode"],
                                            step_size = UVC_SETTINGS["default_step_size"],
                                            feed_rate = UVC_SETTINGS["default_feed_rate"]))
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


@APP.route('/set_control', methods=['POST'])
def set_ctrl():
    global controls_dict, FOCUS

    if isCapturing and request.method == 'POST' and request.is_json:
        req_data = request.get_json()
        ctrl = req_data['control']
        val = int(req_data['value'])

        # Adjust scope controls
        if ctrl == 'Absolute Focus':
            if controls_dict['Auto Focus'].value == 1:
                controls_dict['Auto Focus'].value = 0
                FOCUS = get_current_focus(FOCUS)

            # print(FOCUS)
            FOCUS += val
            controls_dict['Absolute Focus'].value = FOCUS
            res = f"Absolute Focus: {FOCUS}"
            # print(controls_dict['Absolute Focus'].value)
            # print(FOCUS)
        else:
            controls_dict[ctrl].value = val
            res = f"{ctrl}: {val}"

    else:
        res = "could not set!"

    print(res)
    return res

@APP.route('/grbl', methods=['POST'])
def parse_grbl_cmd():
    if request.method == 'POST' and request.is_json:
        req_data = request.get_json()
        cmd = req_data['command']
        val = float(req_data['value'])
        
        if  cmd == 'H':
            grbl_control.run_home_cycle()
        elif cmd == 'STP':
            grbl_control.stepSize = val
        elif cmd == 'FDR':
            grbl_control.feedRate = val            
        elif cmd == 'X':
            grbl_control.jog_step(val, 0, 0)
        elif cmd == 'Y':
            grbl_control.jog_step(0, val, 0)
        elif cmd == 'Z':
            grbl_control.jog_step(0, 0, val)
        
        res = f"XYZ: {grbl_control.xPos} : {grbl_control.yPos} : {grbl_control.zPos} • RNG:{ sensors.get_range() } TMP: {sensors.get_temp()}"
    else:
        res = "could not set!"

    return res


# Save an image file to the server
@APP.route('/save_image', methods=['POST'])
def save_image():

    if isCapturing:
        filename = make_file_name(request.get_json(), "png")
        print(f"saving img file: {filename}")
        # Convert BGR to RGB and save the image
        # im_rgb = outputFrame.bgr[:, :, [2, 1, 0]]
        # Image.fromarray(im_rgb).save(filename)
        with lock:
            cv2.imwrite(filename, outputFrame.bgr)
            res = "file saved!"
    else:
        res = "could not save!"

    print(res)
    return res


# Save a series of image files (panorama) along the X axis to the server
@APP.route('/save_image_panorma', methods=['POST'])
def save_image_panorma():

    x_pos = grbl_control.xPos
    y_pos = grbl_control.yPos
    z_pos = grbl_control.zPos        
    
    # Move to start point
    x_pos = 2
    grbl_control.jog_to_pos(x_pos, y_pos, z_pos)
    time.sleep(3)
    if isCapturing:
        while x_pos <= 10:
            grbl_control.jog_to_pos(x_pos, y_pos, z_pos)
            # time.sleep(1)
        
            filename = make_file_name(request.get_json(), "png", file_num=x_pos)
            print(f"saving img file: {filename}")
            with lock:
                cv2.imwrite(filename, outputFrame.bgr)
                res = "file saved!"

            x_pos += 0.5
        
        res = f"Panorma Done! XYZ: {grbl_control.xPos} : {grbl_control.yPos} : {grbl_control.zPos}"
    else:
        res = "could not save!"

    print(res)
    return res


# Capture a short video
@APP.route('/save_vid', methods=['POST'])
def save_video():

    # how long is the captured video (in frames)
    frames_to_capture = UVC_SETTINGS["video_cap_duration"] * CAP_FPS

    if isCapturing:
        filename = make_file_name(request.get_json(), "mp4")
        print(f"saving vid file: {filename}")

        # Capture object setup
        cap_vid_size = (UVC_SETTINGS["video_cap_w"], UVC_SETTINGS["video_cap_h"])
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(filename, fourcc, CAP_FPS, cap_vid_size)

        for i in range(frames_to_capture):
            time.sleep(1 / CAP_FPS)
            with lock:
                frame = cv2.resize(outputFrame.bgr, cap_vid_size, interpolation=cv2.INTER_AREA)
                out.write(frame)

        out.release()
        res = "file saved!"
    else:
        res = "could not save!"

    print(res)
    return res


@APP.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# An image gallery of captured images
@APP.route("/img_gallery")
def img_gallery():
    cookies = request.cookies
    uid = cookies.get("scan_uuid")

    user_files_path = f"static/captured_pics/{uid}"
    files_list = [f for f in listdir(user_files_path) if isfile(join(user_files_path, f))]
    files_list.sort(reverse=True)

    return render_template('gallery.html', userId=uid, images=files_list)


@APP.route("/download_gallery")
def download_gallery():
    cookies = request.cookies
    uid = cookies.get("scan_uuid")
    user_files_path = f"static/captured_pics/{uid}"

    pyzip = PyZip(PyFolder(user_files_path, interpret=False))
    zipped_filename = f"static/captured_pics/{uid}.zip"
    pyzip.save(zipped_filename)

    try:
        return send_file(zipped_filename, as_attachment=True, attachment_filename=f'{uid}.zip')
    except Exception as exception:
        return str(exception)


def make_file_name(req_data, file_ext, file_num = None):
    global FOCUS, controls_dict

    # get User Id from cookie
    cookies = request.cookies
    uid = cookies.get("scan_uuid")

    # Check if a directory with current UID exists, if not create one
    Path(f"static/captured_pics/{uid}").mkdir(parents=True, exist_ok=True)

    # get current timestamp
    time_stamp = int(req_data['timestamp'] / 1000)
    dt = datetime.datetime.fromtimestamp(time_stamp)
    date_string = f"{dt.year}-{dt.month:02d}-{dt.day:02d}_{dt.hour:02d}-{dt.minute:02d}-{dt.second:02d}"

    # Get current focus and add zeros if needed to make the file name consitent
    if controls_dict['Auto Focus'].value == 1:
        FOCUS = get_current_focus(FOCUS)

    if FOCUS > 99:
        foc = str(FOCUS)
    elif 9 < FOCUS < 100:
        foc = f"0{FOCUS}"
    elif FOCUS < 10:
        foc = f"00{FOCUS}"
    
    if file_num == None:
        file_num = 0
    
    file_name = f"static/captured_pics/{uid}/cap_{uid}_{date_string}_f{foc}_n{file_num}.{file_ext}"

    return file_name



# Captures frames in the background (in a separate thread)
def capture_frame():
    # grab global references to the video stream, output frame, and lock variables
    global SCOPE_RESET_REQUIRED, cap, outputFrame, lock, isCapturing
    # cap_mode = cap.avaible_modes[UVC_SETTINGS["capture_mode"]]

    while True:
        if isCapturing:            
            # reset scope capture setting every "SCOPE_RESET_FREQ" seconds. 
            # A workaround to avoid PYUVC clock correction and app crashing
            # if SCOPE_RESET_REQUIRED:
            #         cap.frame_mode = (cap_mode[0], cap_mode[1], cap_mode[2])
            #         SCOPE_RESET_REQUIRED = False

            # Grab a frame from the Scope
            frame = cap.get_frame_robust()
            with lock:
                outputFrame = frame

        else:
            time.sleep(0.5)


def generate():
    # grab global references to the output frame and lock variables
    global SCOPE_RESET_REQUIRED, outputFrame, lock, isCapturing

    start_time = time.time()

    # An image to display when the scope is off
    placeholder_image = open("static/img/scope_off.jpg", "rb").read()

    while True:

        time.sleep(1 / STREAM_FPS)

        with lock:
            # reset scope capture setting every "SCOPE_RESET_FREQ" seconds.
            # A workaround to avoid PYUVC clock correction and app crashing
            # The actual settings reset is happening in capture_frame() to avoid crashes
            # elapsed_time = time.time() - start_time
            # if elapsed_time > SCOPE_RESET_FREQ:
            #     SCOPE_RESET_REQUIRED = True
            #     start_time = time.time()
            if isCapturing and outputFrame is None:
                continue

        if isCapturing:
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(outputFrame.jpeg_buffer) + b'\r\n'
        else:
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + placeholder_image + b'\r\n'


# Switching between scope capture on and off
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


def get_current_focus(focus):
    # PYUVC Workaround: Set "Absolute Focus" property to a random value
    # This will update the Property with the actual latest value from the camera (after AF adjustment)
    # And set the actual focus value in the camera to this random value
    controls_dict['Absolute Focus'].value = focus
    # Set the actual focus value in the camera back to it's latest original value
    controls_dict['Absolute Focus'].value = controls_dict['Absolute Focus'].value
    # Save this value in a variable for future reference
    focus = controls_dict['Absolute Focus'].value

    return focus


def init_scope():
    global cap, UVC_SETTINGS, controls_dict, dev_list, scopeDeviceId

    # Add G-Scope as new capture device and get its control properties
    cap = uvc.Capture(dev_list[scopeDeviceId]["uid"])
    time.sleep(1)

    # Load supported device controls list
    controls_dict = dict([(c.display_name, c) for c in cap.controls])

    # Capture one frame to initialize the microscope
    print("Available Capture Modes:", cap.avaible_modes)
    cap_mode = cap.avaible_modes[UVC_SETTINGS["capture_mode"]]
    print("Setting Capture Mode:", cap_mode)
    cap.frame_mode = (cap_mode[0], cap_mode[1], cap_mode[2])
    cap.get_frame_robust()
    time.sleep(1)

    # Set the FPS for video capturing from the scope
    CAP_FPS = cap_mode[2]

    print("--- Available Controls & Init Values: ---")
    for control in controls_dict:
        print(f"{control}: {controls_dict[control].value}")
    print("---------------------------")

    # Apply Custom Setting to the Scope via UVC
    print("--- Adjusting custom control settings: ---")
    for control in controls_dict:
        controls_dict[control].value = UVC_SETTINGS[control]
        print(f"{control}: {controls_dict[control].value}")
    print("---------------------------")

    # Set the Manual Focus Again (PYUVC workaround)
    # controls_dict['Absolute Focus'].value = FOCUS


# commandline argument parser
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
# ap.add_argument("-o", "--port", type=int, required=True,
#   help="ephemeral port number of the server (1024 to 65535)")
# args = vars(ap.parse_args())

logging.basicConfig(level=logging.INFO)

# Load scope settings from a JSON File
with open('scope_settings.json', 'r') as f:
    UVC_SETTINGS = json.load(f)
    STREAM_FPS = UVC_SETTINGS["stream_fps"]
    SCOPE_RESET_FREQ = UVC_SETTINGS["scope_reset_freq"]
    FOCUS = UVC_SETTINGS["Absolute Focus"]

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

# Connect to GRBL Positioning Controller and sensors
if (UVC_SETTINGS["robo_scope_mode"]):
    grbl_control = GrblControl(UVC_SETTINGS["grbl_controller_address"], UVC_SETTINGS["default_step_size"], UVC_SETTINGS["default_feed_rate"])
    sensors = SensorsFeed()
else:
    print("*** Roboscope Mode Disabled ***")

# Start a thread that will capture frames from the scope
CAPTURE_THREAD = threading.Thread(target=capture_frame, args=())
CAPTURE_THREAD.daemon = True
CAPTURE_THREAD.start()

# Start a thread that will capture button press on the PI LCD Screen Hat
# keypress_thread = threading.Thread(target=get_keypress, args=())
# keypress_thread.daemon = True
# keypress_thread.start()
# print("Press the S key to Start/Stop Capturing")


if __name__ == '__main__':
    # start the flask app
    # app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)
    APP.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=False)