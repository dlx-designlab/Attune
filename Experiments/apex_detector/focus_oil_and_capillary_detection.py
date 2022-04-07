import cv2
import functions
import uvc
import matplotlib.pyplot as plt
import numpy as np
import time
from collections import deque
from scipy import ndimage as ndi
from skimage.filters import frangi, gabor_kernel, hessian

MIN_FOCUS = 5
MAX_FOCUS = 60
ADJUSTMENT_STEP = 1
WINDOW_SIZE = 59
REFOCUS_THRESHOLD = 0.5
OIL_THRESHOLD = 0.7
CAPILLARY_THRESHOLD = 0.8
FOCUS_DELAY = 10
COOLDOWN = 50
CAP_COOLDOWN = 50

FOCUS_KERNEL = np.real(gabor_kernel(0.4, theta=0, sigma_x=3, sigma_y=3))
CAPILLARY_KERNEL = np.real(gabor_kernel(0.25, theta=0, sigma_x=2, sigma_y=2))
kernel = FOCUS_KERNEL

cap = uvc.Capture(uvc.device_list()[0]["uid"])
controls_dict = dict([(c.display_name, c) for c in cap.controls])

hd_cap_mode = cap.avaible_modes[2]
cap.frame_mode = (hd_cap_mode[0], hd_cap_mode[1], hd_cap_mode[2])

# Initialise the microscope.
cap.get_frame_robust()
time.sleep(1)

controls_dict["Auto Focus"].value = 0
controls_dict["White Balance temperature,Auto"].value = 0
controls_dict["White Balance temperature"].value = 6000
controls_dict["Backlight Compensation"].value = 0
controls_dict["Contrast"].value = 160
controls_dict["Power Line frequency"].value = 1
controls_dict["Hue"].value = 0
controls_dict["Saturation"].value = 250
controls_dict["Gamma"].value = 1
controls_dict["Gain"].value = 0
controls_dict["Brightness"].value = 210
controls_dict["Auto Exposure Mode"].value = 1
controls_dict["Absolute Exposure Time"].value = 365

controls_dict["Absolute Focus"].value = MAX_FOCUS

# Give the microscope time to apply the settings.
time.sleep(1)

focus = MAX_FOCUS
focusing = True
optimum_focus = focus
optimal_gabor_mean = 0
cooldown = 0
cap_cooldown = 0
top_gabor_means = deque([0]*5)
bottom_gabor_means = deque([0]*5)
cap_top_gabor_means = deque([0]*5)
cap_bottom_gabor_means = deque([0]*5)
oil = False

while(True):
    controls_dict["Absolute Focus"].value = focus

    frame = cap.get_frame_robust()

    small_frame = cv2.resize(frame.gray, (320, 180), interpolation=cv2.INTER_CUBIC)
    top_frame = small_frame[0:90, 0:320]
    bottom_frame = small_frame[90:180, 0:320]

    top_gabor_means.pop()
    top_gabor_means.appendleft(ndi.convolve(top_frame, kernel, mode='wrap').mean())
    top_gabor_mean = np.mean(top_gabor_means)
    bottom_gabor_means.pop()
    bottom_gabor_means.appendleft(ndi.convolve(bottom_frame, kernel, mode='wrap').mean())
    bottom_gabor_mean = np.mean(bottom_gabor_means)

    max_gabor_mean = top_gabor_mean if top_gabor_mean > bottom_gabor_mean else bottom_gabor_mean
    optimal_gabor_mean = optimal_gabor_mean if max_gabor_mean < optimal_gabor_mean else max_gabor_mean

    if focusing:
        if optimal_gabor_mean == max_gabor_mean:
            optimum_focus = focus
        focus -= 1

    if focus <= MIN_FOCUS:
        focus = optimum_focus + FOCUS_DELAY
        focusing = False
        cooldown = COOLDOWN

    if cooldown > 0:
        cooldown -= 1

    if not focusing and cooldown == 0 and top_gabor_mean < optimal_gabor_mean * 0.5 and not oil:
        focusing = True
        focus = MAX_FOCUS
        optimal_gabor_mean = 0

    if not oil and not focusing and bottom_gabor_mean < top_gabor_mean * OIL_THRESHOLD:
        oil = True
        cap_cooldown = CAP_COOLDOWN

    monitor_frame = cv2.resize(frame.bgr, (640, 360), interpolation=cv2.INTER_CUBIC)
    if focusing:
        cv2.putText(monitor_frame, "Focusing", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
    else:
        cv2.putText(monitor_frame, f"Focused ({focus})", (8, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

    if oil:
        cv2.putText(monitor_frame, "Crossed to Oil", (8, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
    elif not focusing:
        cv2.putText(monitor_frame, "Untreated Nail", (8, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

    if not oil:
        cv2.putText(monitor_frame, f"Top Gabor Mean: {top_gabor_mean:.2f}", (8, 330), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
        cv2.putText(monitor_frame, f"Bot Gabor Mean: {bottom_gabor_mean:.2f}", (8, 350), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

    if cap_cooldown > 0:
        cap_cooldown -= 1

    if oil:
        cap_top_gabor_means.pop()
        cap_top_gabor_means.appendleft(ndi.convolve(top_frame, CAPILLARY_KERNEL, mode='wrap').mean())
        cap_top_gabor_mean = np.mean(cap_top_gabor_means)
        cap_bottom_gabor_means.pop()
        cap_bottom_gabor_means.appendleft(ndi.convolve(bottom_frame, CAPILLARY_KERNEL, mode='wrap').mean())
        cap_bottom_gabor_mean = np.mean(cap_bottom_gabor_means)

        if cap_cooldown:
            cv2.putText(monitor_frame, "Capillary Detection Paused", (8, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
        elif cap_top_gabor_mean < cap_bottom_gabor_mean * CAPILLARY_THRESHOLD:
            cv2.putText(monitor_frame, "Capillaries", (8, 60), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        elif not focusing:
            cv2.putText(monitor_frame, "No Capillaries", (8, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

    cv2.imshow("Monitor", monitor_frame)
    cv2.waitKey(1)
