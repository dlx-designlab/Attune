""" Capilary Apex Detector Test """
import time
from skimage import feature
import cv2
import numpy as np
import functions
import pickle
from cap_detector import CapDetector

cap_detector = CapDetector()

# Measure execution time
start_time = time.time()

# Load test image
test_img = cv2.imread("data/test/full_frame/tough.png")
refined_detector = cap_detector.check_caps(test_img)

print(f"Total Took: {time.time() - start_time} seconds ---")
print("[INFO] Done!")

clone_img = test_img.copy()

# Draw Refined results:
for box in refined_detector:
    cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
    cv2.putText(clone_img, f"{box[4]}", (box[0], box[1]-3), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

cv2.imshow("Result", clone_img)
cv2.waitKey(0)
