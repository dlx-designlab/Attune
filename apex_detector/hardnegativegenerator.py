""" Capilary Apex Detector/ Classifier Test """
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import time

# from skimage import exposure
from skimage import feature
from imutils import paths
import cv2
import numpy as np
import functions
import pickle

import matplotlib as mpl
import matplotlib.pyplot as plt

sample_size = 60
sl_win_step = 20
box_overlap_thresh = 0.3
nr_level = 5
laplacian_threshold = 110000

def enhance_green(img):
    """ Prepares the image for analysis """

    # Remove noise
    img = cv2.medianBlur(img, nr_level)
    # Split RGB channels
    img_blue_c1, img_green_c1, img_red_c1 = cv2.split(img)

    return img_green_c1

model = pickle.load(open('model', 'rb'))

count = 0

for imagePath in paths.list_images("data/test/empty/"):
    # Load the image
    image = cv2.imread(imagePath)
    test_gray = enhance_green(image)

    detected_objects = []
    # Run sliding windows
    (winW, winH) = (sample_size, sample_size)
    for (x, y, window) in functions.sliding_window(test_gray,
                                                   stepSize=sl_win_step,
                                                   windowSize=(winW, winH)):
        # if the window does not meet our desired window size, ignore it
        if window.shape[0] != winH or window.shape[1] != winW:
            continue

        # Test if the sample has enough gragients for analysis
        laplacian = cv2.Laplacian(window, cv2.CV_64F, ksize=5)
        lap_abs = cv2.convertScaleAbs(laplacian)
        lap_abs_sum = np.sum(lap_abs)

        # if we have enough gradients, apply classifier and predict content
        if lap_abs_sum > laplacian_threshold:
            # Apply Classifier: Extract HOG from the window and predict
            # s_time = time.time()
            (H) = feature.hog(window,
                            orientations=9,
                            pixels_per_cell=(10, 10),
                            cells_per_block=(3, 3),
                            transform_sqrt=True,
                            block_norm="L1")

            pred_conf = int(model.decision_function(H.reshape(1, -1))[0] * 100)

            # add detection frame to the image
            if pred_conf < 0:
                detected_objects.append([x, y, x + winW, y + winH, abs(pred_conf)])


    # convert detected objects to NumPy Array and preform "Non-Maximum Suppression" to remove redundant detections
    detected_objects_array = np.array(detected_objects)
    refined_detector = functions.non_max_suppression_fast(detected_objects_array, box_overlap_thresh)

    clone_img = image.copy()

    # Draw Refined results and write cropped images to disk:
    for box in refined_detector:
        count += 1
        cropped_image = image[box[1]: box[3], box[0]: box[2]]
        if cropped_image.size:
            cv2.imwrite(f"hn_{count}.jpg", cropped_image)

