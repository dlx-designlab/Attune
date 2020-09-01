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

import matplotlib as mpl
import matplotlib.pyplot as plt

sample_size = 60
min_conf = 0.73
sl_win_step = 20
box_overlap_thresh = 0.3
nr_level = 5
laplacian_threshold = 110000
overexposure_threshold = 245
overexposure_count_threshold = 0
threshold_count_threshold = 0.8

# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []


def enhance_green(img):
    """ This function prepares the image for analysis """

    # remove noise
    img = cv2.medianBlur(img, nr_level)
    # split RGB channels
    img_blue_c1, img_green_c1, img_red_c1 = cv2.split(img)

    # img_green_c1 = cv2.medianBlur(img_green_c1, 5)

    # decide the Limit and the Grid size
    # clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    # cl1 = clahe.apply(img_green_c1) 
    # cl1 = cv2.medianBlur(cl1, 5)
    return img_green_c1


# loop over the image paths in the training set
print("Loading training data")
for imagePath in paths.list_images("data/training/"):
    # extract the tag
    tag = imagePath.split("/")[-2]

    # load the image
    image = cv2.imread(imagePath)
 
    # image = cv2.resize(image, (30, 30), interpolation=cv2.INTER_CUBIC) #0.93288
    # image = cv2.resize(image, (30, 30), interpolation=cv2.INTER_AREA) #0.9401
    # image = cv2.resize(image, (30, 30), interpolation=cv2.INTER_LANCZOS4) #0.9306
    # image = cv2.resize(image, (30, 30), interpolation=cv2.INTER_NEAREST) #0.9390
    # image = cv2.resize(image, (30, 30), interpolation=cv2.INTER_LINEAR) #0.0.9373

    # Check image Size is correct and fix
    if image.shape[0] < sample_size or image.shape[1] < sample_size:
        print(f"resizing: {imagePath} original size: {image.shape} to {sample_size} x {sample_size}")
        image = cv2.resize(image, (sample_size, sample_size), interpolation=cv2.INTER_CUBIC)

    # prepre the image for analysis remove noise, extract gren channel, etc...
    gray = enhance_green(image)

    # extract Histogram of Oriented Gradients from the image
    H = feature.hog(gray,
                    orientations=9,
                    pixels_per_cell=(10, 10),
                    cells_per_block=(3, 3),
                    transform_sqrt=True,
                    block_norm="L1")
    
    # update the data and labels
    data.append(H)
    labels.append(tag)

print("Data Loaded!")
print(f"Samples: {len(data)}")
print(f"Labels: {len(labels)}")



# --- An evaluation of the dataset and prediction accuracy, used to quickly test parameters ---

# # DATASET TESTER:
# n_estimators = [1, 2, 4, 8, 16, 32, 64, 100]
# train_results = []
# test_results =[]

print("splitting data...")
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.25, random_state=4)
# "train" the Random Forest classifier
print("training...")

# rf = RandomForestClassifier(n_estimators=32, random_state=42)
rf = svm.LinearSVC(max_iter=10, random_state=42)

rf.fit(x_train, y_train)

print("[INFO] Predicting...")
train_pred = rf.predict(x_train)
test_pred = rf.predict(x_test)

train_score = accuracy_score(y_train, train_pred)
test_score = accuracy_score(y_test, test_pred)

print(f"train score: {train_score}, test score: {test_score}")

# for estimator in n_estimators:

#     print("[INFO] Training classifier...")

#     # "train" the Random Forest classifier
#     rf = RandomForestClassifier(n_estimators=estimator, random_state=42)
#     rf.fit(x_train, y_train)

#     print("[INFO] Predicting...")
#     train_pred = rf.predict(x_train)
#     test_pred = rf.predict(x_test)

#     train_score = accuracy_score(y_train, train_pred)
#     test_score = accuracy_score(y_test, test_pred)

#     train_results.append(train_score)
#     test_results.append(test_score)


# from matplotlib.legend_handler import HandlerLine2D

# line1, = plt.plot(n_estimators, train_results, 'b', label="Training Set")
# line2, = plt.plot(n_estimators, test_results, 'r', label="Test Set")
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
# plt.ylabel("accuracy score")
# plt.xlabel("n_estimators")
# plt.show()

# --- end of evaluation and test ---

# "Train" the SVM / Random-Forest classifier
print("[INFO] Training classifier...")
# model = RandomForestClassifier(n_estimators=36, random_state=42)
model = svm.LinearSVC(max_iter=10, random_state=42)
model.fit(data, labels)

print("[INFO] Evaluating...")

# Measure execution time
start_time = time.time()

# Load test image
test_img = cv2.imread("data/test/full_frame/cap00074.jpg")
# test_img = cv2.resize(test_img, (640, 360), interpolation=cv2.INTER_AREA)
test_gray = enhance_green(test_img)
threshold_image = cv2.adaptiveThreshold(cv2.medianBlur(test_gray, 11),
										255, cv2.ADAPTIVE_THRESH_MEAN_C,
										cv2.THRESH_BINARY, 51, 5)

# crop top half of the test img
# test_gray = test_gray[0:360, 0:1280]

# create an array of detected objects
# detected_objects = np.array([(0, 0, 60, 60)])
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
        # s_time = time.time()
        (H) = feature.hog(window,
                        orientations=9,
                        pixels_per_cell=(10, 10),
                        cells_per_block=(3, 3),
                        transform_sqrt=True,
                        block_norm="L1")
        # print(f"Feature Extraction Took: {time.time() - s_time} sec")

        # Predict the content of the window (apex or not)
        # s_time = time.time()
        # pred = model.predict(H.reshape(1, -1))[0]
        # pred = model.predict_proba(H.reshape(1, -1))[0]
        # pred = model.predict(H.reshape(1, -1))[0]
        pred_conf = int(model.decision_function(H.reshape(1, -1))[0] * 100)
        # print(f"Prediction Took: {time.time() - s_time} sec")

        # add detection frame to the image
        # if pred[0] > min_conf:
        if pred_conf < 0:
            # detected_objects.append([x, y, x + winW, y + winH, int(pred[0]*100)])
            detected_objects.append([x, y, x + winW, y + winH, abs(pred_conf)])
            # detected_objects = np.append(detected_objects, [(x, y, x + winW, y + winH)], axis=0)


# convert detected objects to NumPy Array and preform "Non-Maximum Suppression" to remove redundant detections
# s_time = time.time()
detected_objects_array = np.array(detected_objects)
refined_detector = functions.non_max_suppression_fast(detected_objects_array, box_overlap_thresh)
# print(f"Refining results took: {time.time() - s_time} sec")
print(f"Total Took: {time.time() - start_time} seconds ---")
print("[INFO] Done!")

clone_img = test_img.copy()

# Draw original results:
# for box in detected_objects_array:
#     cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 1)
#     cv2.putText(clone_img, f"{box[4]}%", (box[0], box[1]), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

# Draw Refined results:
for box in refined_detector:
    cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
    # cv2.putText(clone_img, f"{box[4]}%", (box[0], box[1]-3), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
    cv2.putText(clone_img, f"{box[4]}", (box[0], box[1]-3), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

cv2.imshow("RESULT!", clone_img)
cv2.waitKey(0)

######### older tests ###############
# cv2.waitKey(1)

# Create an large image placeholder for the results
# big_picture = np.zeros((300, 300, 3), np.uint8)
# # loop over the test dataset
# for (i, imagePath) in enumerate(paths.list_images("data/test/cap")):
#     # load the test image, convert it to grayscale, and resize it to
#     # the canonical size
#     image = cv2.imread(imagePath)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     # Extract HOG from the test image and predict
#     (H, hogImage) = feature.hog(gray,
#                                 orientations=9,
#                                 pixels_per_cell=(10, 10),
#                                 cells_per_block=(3, 3),
#                                 transform_sqrt=True, block_norm="L1",
#                                 visualize=True)

#     pred = model.predict(H.reshape(1, -1))[0]

#     # visualize the HOG image
#     # hogImage = exposure.rescale_intensity(hogImage, out_range=(0, 255))
#     # hogImage = hogImage.astype("uint8")
#     # cv2.imshow("HOG Image #{}".format(i + 1), hogImage)

#     # add the prediction on the test image
#     cv2.putText(image, pred.title(), (2, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)    

#     # add the image to the resutls grid
#     y = int(i / 5) * sample_size
#     x = (i % 5) * sample_size 
#     big_picture[y:y+sample_size,x:x+sample_size] = image
#     # cv2.imshow("Test Image #{}".format(i + 1), image)
    
# cv2.imshow("result!", big_picture)