# This Code uses the Pupil Labs PYUVC library:
# https://github.com/pupil-labs/pyuvc

# from __future__ import print_function
# import time
import uvc  # >> https://github.com/pupil-labs/pyuvc
import logging
import cv2

logging.basicConfig(level=logging.DEBUG)

dev_list = uvc.device_list()
print(dev_list)

# Add new capture device and its control properties
cap = uvc.Capture(dev_list[0]["uid"])
controls_dict = dict([(c.display_name, c) for c in cap.controls])

print(cap.avaible_modes)
print(controls_dict)

# Capture a frame to initialize the cope
cap.frame_mode = (640, 480, 30)
frame = cap.get_frame_robust()

# Set Auto-focus to false and set a custom value
controls_dict['Auto Focus'].value = 0
controls_dict['Absolute Focus'].value = 200

# Set Auto-WB to false and set a custom value
controls_dict['White Balance temperature,Auto'].value = 0
controls_dict['White Balance temperature'].value = 2000

# Capture some frames
for x in range(100):
    controls_dict['White Balance temperature'].value = 2000
    frame = cap.get_frame_robust()
    # print(frame.img.shape)
    cv2.imshow("img", frame.bgr)
    cv2.waitKey(1)

cap = None