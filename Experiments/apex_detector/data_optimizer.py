""" Training Data Optimization Tool"""
from sklearn.ensemble import RandomForestClassifier
from skimage import feature
from imutils import paths
import cv2
import numpy as np
import functions
import os

sample_size = 60
data = []
threshold = 110000
data_path = "data/training/cap/"

for imagePath in paths.list_images(data_path):

    # load the image, convert it to grayscale, and detect edges
    image = cv2.imread(imagePath)

    # Smoothing
    # smoothed0 = cv2.GaussianBlur(image, (3, 3), 0)
    smoothed = cv2.medianBlur(image, 5)
    # smoothed2 = cv2.bilateralFilter(image, 5, 10, 100)
    # smoothed3 = cv2.fastNlMeansDenoisingColored(image, None, 3, 3, 7, 21)
    # smoothed4 = cv2.fastNlMeansDenoisingColored(image, None, 6, 6, 7, 21)
    # smoothed5 = cv2.fastNlMeansDenoisingColored(image, None, 4, 15, 7, 21)

    # cv2.imshow("smoothed0", smoothed0)
    # cv2.imshow("smoothed1", smoothed1)
    # cv2.imshow("smoothed2", smoothed2)
    # cv2.imshow("smoothed3", smoothed3)
    # cv2.imshow("smoothed4", smoothed4)
    # cv2.imshow("smoothed5", smoothed5)                    
    cv2.imshow("smoothed", smoothed)                    
    cv2.waitKey(0)

    # Check image Size is correct
    # if image.shape[0] < sample_size or image.shape[1] < sample_size:
    #     print(imagePath, image.shape)

    gray = cv2.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)

    # sobelx = cv2.Sobel(gray,cv2.CV_64F,1,0,ksize=5)
    # sobely = cv2.Sobel(gray,cv2.CV_64F,0,1,ksize=5)

    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=5)
    lap_abs = cv2.convertScaleAbs(laplacian)
    lap_abs_sum = np.sum(lap_abs)
    
    # print(f"image name: {imagePath}")
    # print(f"Laplacian Summary: {lap_abs_sum}")

    if lap_abs_sum < threshold:
        file_name = imagePath.split("/")[-1]
        os.rename(imagePath, f"{data_path}no/{file_name}")

        # print(f"image name: {imagePath}")
        # print(f"Laplacian Summary: {lap_abs_sum}")
        # cv2.imshow(f"{imagePath} {lap_abs_sum}", image)

# cv2.waitKey(0)

    # # extract Histogram of Oriented Gradients from the image
    # H = feature.hog(gray,
    #                 orientations=9,
    #                 pixels_per_cell=(10, 10),
    #                 cells_per_block=(3, 3),
    #                 transform_sqrt=True,
    #                 block_norm="L1")

    # print(f"image name: {imagePath}")
    # print(f"HOG Result: {H}")
    # print(f"HOG Summary: {np.sum(H)}")
    # print("---")
    # data.append(H)
