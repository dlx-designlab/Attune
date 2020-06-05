import uvc
import logging
import cv2
import time

logging.basicConfig(level=logging.INFO)

dev_list = uvc.device_list()
print(dev_list)
cap = uvc.Capture(dev_list[0]["uid"])

# Print available Capture Modes
print("Availbale Capture Modes:")
for count, mode in enumerate(cap.avaible_modes):
    print(count, mode)

capture_mode = cap.avaible_modes[0]
cap.frame_mode = (capture_mode[0], capture_mode[1], capture_mode[2])

# Uncomment the following lines to configure the Pupil 200Hz IR cameras:
# controls_dict = dict([(c.display_name, c) for c in cap.controls])
# controls_dict['Auto Exposure Mode'].value = 1
# controls_dict['Gamma'].value = 200

# start_time=time.time()

# Capture some frames
while True:

    # controls_dict['White Balance temperature'].value = 2000

    frame = cap.get_frame_robust()
    cv2.imshow("img", frame.bgr)
    time.sleep(1/capture_mode[2])
    # print(frame.img.shape)

    # elapsed_time = time.time() - start_time
    # if elapsed_time > 90:
    #     print("time reset")
    #     start_time = time.time()
    #     cap.frame_mode = (capture_mode[0], capture_mode[1], capture_mode[2])


    # App controls
    k = cv2.waitKey(1)

    if k == ord('q'):    # Esc key to stop
        break

    elif k == -1:
        continue
    # else:
    #     print(k)

cap = None
