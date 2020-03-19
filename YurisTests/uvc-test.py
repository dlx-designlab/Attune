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

# Add new capture device and its control properties
cap = uvc.Capture(dev_list[0]["uid"])
controls_dict = dict([(c.display_name, c) for c in cap.controls])

print(cap.avaible_modes)
print("--- Available Controls: ---")
for control in controls_dict:
    print(control)
print("------")

# Capture a frame to initialize the cope
cap.frame_mode = (1920, 1080, 20)
frame = cap.get_frame_robust()

# Set Auto-focus to false and set a custom value
# controls_dict['Auto Focus'].value = 0
# controls_dict['Absolute Focus'].value = 200
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
    if k == ord('f'):    # Esc key to stop
        controls_dict['Auto Focus'].value = 1
    if k == ord('q'):    # Esc key to stop
        break
    elif k == -1:
        continue
    else:
        print(k)

cap = None