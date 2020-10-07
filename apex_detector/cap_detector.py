import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
from collections import deque
from scipy import ndimage as ndi
from skimage.filters import frangi, gabor_kernel, hessian
import pickle
from skimage import feature

# import uvc

class CapDetector:
    
    def __init__(self):
        self.focus_kernel = np.real(gabor_kernel(0.4, theta=0, sigma_x=3, sigma_y=3))
        self.oil_threshold = 0.8
        self.status = 0
        self.model = pickle.load(open('modelthresh', 'rb'))
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
        focus_val = ndi.convolve(resized_frame, self.focus_kernel, mode='wrap').mean()
        
        return focus_val


    def check_oil(self, frame):
        is_oil = False

        resized_frame = cv2.resize(frame.gray, (320, 180), interpolation=cv2.INTER_CUBIC)
        top_frame = resized_frame[0:90, 0:320]
        bottom_frame = resized_frame[90:180, 0:320]

        top_val = ndi.convolve(top_frame, self.focus_kernel, mode='wrap').mean()
        bottom_val = ndi.convolve(bottom_frame, self.focus_kernel, mode='wrap').mean()

        is_oil = bottom_val < top_val * self.oil_threshold
        return is_oil


    def enhance_green(self, img):
        """ This function prepares the image for analysis """

        # remove noise
        img = cv2.medianBlur(img, self.nr_level)
        # split RGB channels
        img_blue_c1, img_green_c1, img_red_c1 = cv2.split(img)

        return img_green_c1


    def check_caps(self, frame):        
        test_gray = self.enhance_green(frame.bgr)

        threshold_image = cv2.adaptiveThreshold(cv2.medianBlur(test_gray, 11),
                                                255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                cv2.THRESH_BINARY, 51, 5)
        
        detected_objects = []
        (winW, winH) = (self.sample_size, self.sample_size) 

        for (x, y, window) in self.sliding_window(test_gray,
                                                       stepSize=self.sl_win_step,
                                                       windowSize=(winW, winH)):
            # if the window does not meet our desired window size, ignore it
            if window.shape[0] != winH or window.shape[1] != winW:
                continue

            threshold_window = threshold_image[y: y+winH, x: x+winW]
            if (np.count_nonzero(threshold_window) >  self.threshold_count_threshold * self.sample_size ** 2):
                continue

            # If too many of the pixels are overexposed skip the entire window as glare is present
            if (np.count_nonzero(window > self.overexposure_threshold) > self.overexposure_count_threshold * self.sample_size ** 2):
                continue

            (H) =  threshold_window.flatten()

            pred_conf = int(self.model.decision_function(H.reshape(1, -1))[0] * 100)

            if pred_conf < 0:
                detected_objects.append([x, y, x + winW, y + winH, abs(pred_conf)])


        # convert detected objects to NumPy Array and preform "Non-Maximum Suppression" to remove redundant detections
        detected_objects_array = np.array(detected_objects)
        refined_detector = self.non_max_suppression_fast(detected_objects_array, self.box_overlap_thresh)

        top_count = sum(x[1] < 540 for x in refined_detector)
        bottom_count = len(refined_detector) - top_count

        print(f"Top    :{top_count}")
        print(f"Bottom :{bottom_count}")

        return bottom_count - top_count


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
