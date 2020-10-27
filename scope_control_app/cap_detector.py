import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
from collections import deque
from scipy import ndimage as ndi

# import pycuda.autoinit  # This is needed for initializing CUDA driver

# from utils.yolo_with_plugins import TrtYOLO

# import uvc

class CapDetector:
    
    def __init__(self):
        # self.focus_kernel = np.real(gabor_kernel(0.4, theta=0, sigma_x=3, sigma_y=3))
        self.oil_threshold = 0.8
        self.status = 0
        self.sample_size = 60
        self.sl_win_step = 40
        self.box_overlap_thresh = 0.3
        self.nr_level = 5
        self.laplacian_threshold = 110000
        self.overexposure_threshold = 200
        self.overexposure_count_threshold = 0
        self.threshold_count_threshold = 0.9

        print("Detector Ready!")

    
    def check_focus(self, frame):
        
        resized_frame = cv2.resize(frame.gray, (320, 180), interpolation=cv2.INTER_CUBIC)
        
        # TODO: crop to center of the frame
        # focus_val = ndi.convolve(resized_frame, self.focus_kernel, mode='wrap').mean()
        
        return focus_val


    def check_caps(self, frame):
        return 0
        # trt_yolo = TrtYOLO('yolov4-tiny-custom-416', (416, 416), 1)
        # boxes, confs, clss = trt_yolo.detect(frame.bgr, 0.3)
        # return len(boxes)


    #  HELPER FUNCTIONS

    def sliding_window(self, image, stepSize, windowSize):
        """ Sliding a window across an input image"""

        # slide a window across the image
        for y in range(0, image.shape[0], stepSize):
            for x in range(0, image.shape[1], stepSize):
                # yield the current window
                yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


    def non_max_suppression_fast(self, boxes, overlapThresh):
        """ Merges overlapping detection boxes """

        # if there are no boxes, return an empty list
        if len(boxes) == 0:
            return []
        # if the bounding boxes integers, convert them to floats --
        # this is important since we'll be doing a bunch of divisions
        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        # initialize the list of picked indexes
        pick = []

        # grab the coordinates of the bounding boxes
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        # compute the area of the bounding boxes and sort the bounding
        # boxes by the bottom-right y-coordinate of the bounding box
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)
        # keep looping while some indexes still remain in the indexes
        # list
        while len(idxs) > 0:
            # grab the last index in the indexes list and add the
            # index value to the list of picked indexes
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            # find the largest (x, y) coordinates for the start of
            # the bounding box and the smallest (x, y) coordinates
            # for the end of the bounding box
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])
            # compute the width and height of the bounding box
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)
            # compute the ratio of overlap
            overlap = (w * h) / area[idxs[:last]]
            # delete all indexes from the index list that have
            idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))
        # return only the bounding boxes that were picked using the
        # integer data type
        return boxes[pick].astype("int")
