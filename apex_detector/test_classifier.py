""" Capilary Apex Detector Test """
import time
from skimage import feature
import cv2
import numpy as np
import functions
import pickle

sample_size = 60
min_conf = 0.73
sl_win_step = 20
box_overlap_thresh = 0.3
nr_level = 5
laplacian_threshold = 110000
overexposure_threshold = 245
overexposure_count_threshold = 0
threshold_count_threshold = 0.8

model = pickle.load(open('model', 'rb'))

# Measure execution time
start_time = time.time()

# Load test image
test_img = cv2.imread("data/test/full_frame/cap00074.jpg")
test_gray = functions.enhance_green(test_img)
threshold_image = cv2.adaptiveThreshold(cv2.medianBlur(test_gray, 11),
										255, cv2.ADAPTIVE_THRESH_MEAN_C,
										cv2.THRESH_BINARY, 51, 5)

# create an array of detected objects
detected_objects = []
# Run sliding windows
(winW, winH) = (sample_size, sample_size) 
for (x, y, window) in functions.sliding_window(test_gray,
                                               stepSize=sl_win_step,
                                               windowSize=(winW, winH)):
    # if the window does not meet our desired window size, ignore it
    if window.shape[0] != winH or window.shape[1] != winW:
        continue

    # print(f"Window: {x}, {y}")

    threshold_window = threshold_image[y: y+winH, x: x+winW]
    if (np.count_nonzero(threshold_window) >  threshold_count_threshold * sample_size ** 2):
        continue

    # If too many of the pixels are overexposed skip the entire window as glare is present
    if (np.count_nonzero(window > overexposure_threshold) > overexposure_count_threshold * sample_size ** 2):
        continue

    # Test if the sample has enough gragients for analysis
    laplacian = cv2.Laplacian(window, cv2.CV_64F, ksize=5)
    lap_abs = cv2.convertScaleAbs(laplacian)
    lap_abs_sum = np.sum(lap_abs)

    # if we have enough gradients, apply classifier and predict content
    if lap_abs_sum > laplacian_threshold:
        # Apply Classifier: Extract HOG from the window and predict
        (H) = feature.hog(window,
                        orientations=9,
                        pixels_per_cell=(10, 10),
                        cells_per_block=(3, 3),
                        transform_sqrt=True,
                        block_norm="L1")

        pred_conf = int(model.decision_function(H.reshape(1, -1))[0] * 100)

        if pred_conf < 0:
            detected_objects.append([x, y, x + winW, y + winH, abs(pred_conf)])


# convert detected objects to NumPy Array and preform "Non-Maximum Suppression" to remove redundant detections
detected_objects_array = np.array(detected_objects)
refined_detector = functions.non_max_suppression_fast(detected_objects_array, box_overlap_thresh)

print(f"Total Took: {time.time() - start_time} seconds ---")
print("[INFO] Done!")

clone_img = test_img.copy()

# Draw Refined results:
for box in refined_detector:
    cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
    cv2.putText(clone_img, f"{box[4]}", (box[0], box[1]-3), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

cv2.imshow("Result", clone_img)
cv2.waitKey(0)
