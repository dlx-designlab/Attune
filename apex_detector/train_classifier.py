""" Capilary Apex Detector Creation """
from sklearn import svm
import time
import pickle

from skimage import feature
from imutils import paths
import cv2
import numpy as np
import functions

sample_size = 60

# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

# loop over the image paths in the training set
print("Loading training data")
for imagePath in paths.list_images("data/training/"):
    # extract the tag
    tag = imagePath.split("/")[-2]

    # load the image
    image = cv2.imread(imagePath)

    # Check image Size is correct and fix
    if image.shape[0] < sample_size or image.shape[1] < sample_size:
        print(f"resizing: {imagePath} original size: {image.shape} to {sample_size} x {sample_size}")
        image = cv2.resize(image, (sample_size, sample_size), interpolation=cv2.INTER_CUBIC)

    # prepare the image for analysis remove noise, extract gren channel, etc...
    gray = functions.enhance_green(image)

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

# "Train" the SVM / Random-Forest classifier
print("[INFO] Training classifier...")
model = svm.LinearSVC(max_iter=10, random_state=42)
model.fit(data, labels)
pickle.dump(model, open('model', 'wb'))