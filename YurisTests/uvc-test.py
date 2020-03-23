# This Code uses the Pupil Labs PYUVC library:
# https://github.com/pupil-labs/pyuvc

# from __future__ import print_function
# import time
import uvc  # >> https://github.com/pupil-labs/pyuvc
import logging
import cv2

logging.basicConfig(level=logging.INFO)

dev_list = uvc.device_list()
print(dev_list)


# Find the G-Scope device number from all attached devices.
scopeDeviceId = 0
for i, device in enumerate(dev_list):
    print(f"{i}: {device['name']}")
    if "G-Scope" in device["name"]:
        scopeDeviceId = i

print(f"G-Scope device id is: {scopeDeviceId}")

# Add new capture device and its control properties
cap = uvc.Capture(dev_list[scopeDeviceId]["uid"])
controls_dict = dict([(c.display_name, c) for c in cap.controls])

# Print available UVC controls
print(cap.avaible_modes)
print("--- Available Controls: ---")
for control in controls_dict:
    print(control)
print("------")

# Capture a frame to initialize the cope
cap.frame_mode = (640, 480, 30)
frame = cap.get_frame_robust()

# Set Auto-focus to false and set a custom value
controls_dict['Auto Focus'].value = 0
controls_dict['Absolute Focus'].value = 100
#
# # Set Auto-WB to false and set a custom value
# controls_dict['White Balance temperature,Auto'].value = 0
# controls_dict['White Balance temperature'].value = 2000

# Capture some frames
while (True):

    # controls_dict['White Balance temperature'].value = 2000

    frame = cap.get_frame_robust()
    cv2.imshow("img", frame.bgr)

    # print(frame.img.shape)

    # App controls
    k = cv2.waitKey(1)
    if k == ord('f'):    # f to autoFocus
        if controls_dict['Auto Focus'].value == 1:
            controls_dict['Auto Focus'].value = 0
        else:
            controls_dict['Auto Focus'].value = 1

        print(controls_dict['Auto Focus'].value)

    if k == ord('g'):    # g to focus up
        controls_dict['Auto Focus'].value = 0
        print("---------------")
        print(controls_dict['Absolute Focus'].value)
        controls_dict['Absolute Focus'].value += 1
        print(controls_dict['Absolute Focus'].value)

    if k == ord('d'):    # d to focus down
        controls_dict['Auto Focus'].value = 0
        print("---------------")
        print(controls_dict['Absolute Focus'].value)
        controls_dict['Absolute Focus'].value -= 1
        print(controls_dict['Absolute Focus'].value)

    if k == ord('q'):    # Esc key to stop
        break

    elif k == -1:
        continue
    # else:
    #     print(k)

cap = None