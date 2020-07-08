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
from matplotlib.legend_handler import HandlerLine2D

sample_size = 60
min_conf = 0.75
sl_win_step = 10
box_overlap_thresh = 0.5
nr_level = 5

# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

# loop over the image paths in the training set
# for imagePath in paths.list_images(args["training"]):

# DATASET TESTER:
# n_estimators = [1, 2, 4, 8, 16, 32, 64, 100]
n_estimators = [3,5,7,9,11,13]
train_results = []
test_results =[]

def enhance_green(img):
    img = cv2.medianBlur(img, 5)
    img_blue_c1, img_green_c1, img_red_c1 = cv2.split(img)
    
    # cv2.imshow("red", img_blue_c1)
    # cv2.imshow("green", img_green_c1)
    # cv2.imshow("blue", img_red_c1)
    # # decide the Limit and the Grid size
    # clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    # cl1 = clahe.apply(img_green_c1)
    
    return img_green_c1

test_img = cv2.imread("data/test/full_frame/cap00084.jpg")


for estimator in n_estimators:

    data = []
    labels = []

    print("Loading training data")    
    for imagePath in paths.list_images("data/training/"):
        # extract the tag
        tag = imagePath.split("/")[-2]

        # load the image, convert it to grayscale, and detect edges
        image = cv2.imread(imagePath)
        # remove noise
        image = cv2.medianBlur(image, estimator)

        # Check image Size is correct
        if image.shape[0] < sample_size or image.shape[1] < sample_size:
            print(imagePath, image.shape)
            image = cv2.resize(image, (60,60), interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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


    print("splitting data")
    x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.5, random_state=4)

    # "train" the Random Forest classifier
    print("[INFO] Training classifier...")    
    rf = RandomForestClassifier(n_estimators=32, random_state=42)
    rf.fit(x_train, y_train)
    
    print("[INFO] Predicting...")
    train_pred = rf.predict(x_train)
    test_pred = rf.predict(x_test)
    
    train_score = accuracy_score(y_train, train_pred)
    test_score = accuracy_score(y_test, test_pred)
    
    train_results.append(train_score)
    test_results.append(test_score)


line1, = plt.plot(n_estimators, train_results, 'b', label="Training Set")
line2, = plt.plot(n_estimators, test_results, 'r', label="Test Set")
plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
plt.ylabel("accuracy score")
plt.xlabel("Blur Value")
plt.show()