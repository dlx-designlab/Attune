# This Code uses the Pupil Labs PYUVC library:
# https://github.com/pupil-labs/pyuvc

# from __future__ import print_function
# import time
import uvc  # >> https://github.com/pupil-labs/pyuvc
import logging
import cv2
import time
import uvc

logging.basicConfig(level=logging.INFO)

dev_list = uvc.device_list()
print(dev_list)

abs_focus = 100

# Find the G-Scope device number from all attached devices.
scopeDeviceId = 0
for i, device in enumerate(dev_list):
    print(f"{i}: {device['name']}")
    if "G-Scope" in device["name"]:
        scopeDeviceId = i

print(f"G-Scope device id is: {scopeDeviceId}")

# Add new capture device and its control properties
cap = uvc.Capture(dev_list[scopeDeviceId]["uid"])
time.sleep(1)
controls_dict = dict([(c.display_name, c) for c in cap.controls])

print("All Capture Modes:")
for count, mode in enumerate(cap.all_modes):
    print(count, mode)

# Print available (supported) capture modes
print("Available (Supported) Capture Modes:")
for count, mode in enumerate(cap.available_modes):
    print(count, mode)

# Print available UVC controls
print("--- Available Controls: ---")
for control in controls_dict:
    print(f"{control}: {controls_dict[control].value} ({controls_dict[control].min_val}-{controls_dict[control].max_val})")
print("------")

frame = None
# Try custom modes with lower FPS

custom_modes = [
    CameraMode(width=1920, height=1080, fps=20, format_native=7, format_name='MJPG', supported=True),
    CameraMode(width=1920, height=1080, fps=10, format_native=7, format_name='MJPG', supported=True),
    CameraMode(width=1280, height=720, fps=20, format_native=7, format_name='MJPG', supported=True),
    CameraMode(width=1280, height=720, fps=10, format_native=7, format_name='MJPG', supported=True),
]

for i, mode in enumerate(custom_modes):
    try:
        print(f"Trying custom mode {i}: {mode}")
        cap.frame_mode = mode
        frame = cap.get_frame_robust()
        print(f"Custom mode {i} succeeded: {mode}")
        break
    except uvc.InitError as e:
        print(f"Custom mode {i} failed: {e}")
        if i == len(custom_modes) - 1:
            print("No custom modes worked, trying available modes")
            # Fallback to available modes
            for j, avail_mode in enumerate(cap.available_modes):
                try:
                    print(f"Trying available mode {j}: {avail_mode}")
                    cap.frame_mode = avail_mode
                    frame = cap.get_frame_robust()
                    print(f"Available mode {j} succeeded: {avail_mode}")
                    break
                except uvc.InitError as e:
                    print(f"Available mode {j} failed: {e}")
                    if j == len(cap.available_modes) - 1:
                        print("Error: No supported modes found")
                        exit(1)

if frame:
    print("Connection established")
    time.sleep(0.5)
    print("Frame captured")
    time.sleep(0.5)
else:
    print("Failed to capture frame")
    exit(1)
# Capture a frame to initialize the cope
# frame = cap.get_frame_robust()
# # capture_mode = cap.available_modes[2]

# cap.frame_mode = cap.available_modes[3]
# print("connection established")
# time.sleep(.5)
# print("frame captured")
# time.sleep(.5)

# Set Auto-focus to false and set a custom value
# controls_dict['Auto Focus'].value = 0
# controls_dict['Absolute Focus'].value = abs_focus
# controls_dict['Absolute Focus'].value = 100
#
# # Set Auto-WB to false and set a custom value
# controls_dict['White Balance temperature,Auto'].value = 0
# controls_dict['White Balance temperature'].value = 2000


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

# Capture some frames
while True:

    # controls_dict['White Balance temperature'].value = 2000

    frame = cap.get_frame_robust()
    cv2.imshow("img", frame.bgr)

    # print(frame.img.shape)

    # App controls
    k = cv2.waitKey(1)
    if k == ord('f'):    # f to autoFocus

        # Set camera to auto focus mode
        controls_dict['Auto Focus'].value = 1
        # Wait for the camerra focus to adjust
        time.sleep(3)

        abs_focus = get_current_focus(abs_focus)

        print(controls_dict['Absolute Focus'].value)
        print(abs_focus)
        print(controls_dict['Auto Focus'].value)

    if k == ord('g'):    # g to focus up
        if controls_dict['Auto Focus'].value == 1:
            controls_dict['Auto Focus'].value = 0
            abs_focus = get_current_focus(abs_focus)
            
        abs_focus += 1
        controls_dict['Absolute Focus'].value = abs_focus

    if k == ord('d'):    # d to focus down
        if controls_dict['Auto Focus'].value == 1:
            controls_dict['Auto Focus'].value = 0
            abs_focus = get_current_focus(abs_focus)

        controls_dict['Auto Focus'].value = 0
        print("---------------")
        abs_focus -= 1
        print(controls_dict['Absolute Focus'].value)
        controls_dict['Absolute Focus'].value = abs_focus
        print(controls_dict['Absolute Focus'].value)
        print(abs_focus)        
    
    if k == ord('w'):    # w whitebalance up
        controls_dict['White Balance temperature,Auto'].value = 0
        print("---------------")
        print(controls_dict['White Balance temperature'].value)
        controls_dict['White Balance temperature'].value += 100
        print(controls_dict['White Balance temperature'].value)


    if k == ord('r'):    # w whitebalance up
        cap.frame_mode = (1280, 720, 30)

    if k == ord('q'):    # Esc key to stop
        break

    elif k == -1:
        continue
    # else:
    #     print(k)

cap = None
