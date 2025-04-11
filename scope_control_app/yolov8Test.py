
import cv2
import csv 

#Image detection model
from ultralytics import YOLO
import os
import shutil

imgPath="static/captured_pics/DD668A/cap_DD668A_2024-06-06_14-58-57_f060_pan0.jpg"

trt_yolo=YOLO('yolo/best500apex.pt')

res1 = trt_yolo.predict(imgPath, conf=0.3, show=True)

print(len(res1[0]))