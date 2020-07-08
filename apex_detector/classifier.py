""" Capilary Apex Classifier Test"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

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
sl_win_step = 10
box_overlap_thresh = 0.3
nr_level = 5

# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

def enhance_green(img):
    # remoe noise
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
# for imagePath in paths.list_images(args["training"]):
print("Loading training data")
for imagePath in paths.list_images("data/training/"):
    # extract the tag
    tag = imagePath.split("/")[-2]

    # load the image, convert it to grayscale, and detect edges
    image = cv2.imread(imagePath)

    # Check image Size is correct and fix
    if image.shape[0] < sample_size or image.shape[1] < sample_size:
        print(imagePath, image.shape)
        image = cv2.resize(image, (60,60), interpolation=cv2.INTER_CUBIC)

    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray = cv2.medianBlur(gray, 5)
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

# # DATASET TESTER:
# n_estimators = [1, 2, 4, 8, 16, 32, 64, 100]
# train_results = []
# test_results =[]

# print("splitting data...")
# x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.25, random_state=4)
# # "train" the Random Forest classifier
# print("training...")
# rf = RandomForestClassifier(n_estimators=32, random_state=42)
# rf.fit(x_train, y_train)

# print("[INFO] Predicting...")
# train_pred = rf.predict(x_train)
# test_pred = rf.predict(x_test)

# train_score = accuracy_score(y_train, train_pred)
# test_score = accuracy_score(y_test, test_pred)

# print(f"train score: {train_score}, test score: {test_score}")

#####

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

# ###############################

# "train" the Random Forest classifier
print("[INFO] Training classifier...")
model = RandomForestClassifier(n_estimators=36, random_state=42)
model.fit(data, labels)

print("[INFO] Evaluating...")
# Load test image
test_img = cv2.imread("data/test/full_frame/cap00074.jpg")
test_gray = enhance_green(test_img)
# test_gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)

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

    # Apply Classifier: Extract HOG from the twindow and predict
    window = cv2.medianBlur(window, nr_level)
    (H) = feature.hog(window,
                      orientations=9,
                      pixels_per_cell=(10, 10),
                      cells_per_block=(3, 3),
                      transform_sqrt=True, 
                      block_norm="L1")

    # pred = model.predict(H.reshape(1, -1))[0]
    pred = model.predict_proba(H.reshape(1, -1))[0]

    # add detection frame to the image
    if pred[0] > min_conf:
        detected_objects.append([x, y, x + winW, y + winH, int(pred[0]*100)])
        # detected_objects = np.append(detected_objects, [(x, y, x + winW, y + winH)], axis=0)


# convert detected objects to NumPy Arra and preform Non-Maximum Suppression
detected_objects_array = np.array(detected_objects)
refined_detector = functions.non_max_suppression_fast(detected_objects_array, box_overlap_thresh)

clone_img = test_img.copy()

# Draw original results:
# for box in detected_objects_array:
#     cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 1)
#     cv2.putText(clone_img, f"{box[4]}%", (box[0], box[1]), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

# Draw Refined results:
for box in refined_detector:
    cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
    cv2.putText(clone_img, f"{box[4]}%", (box[0], box[1]-3), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

print("[INFO] Done!")
cv2.imshow("RESULT!", clone_img)
cv2.waitKey(0)


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