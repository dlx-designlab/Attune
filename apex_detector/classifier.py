""" Capilary Apex Classifier Test"""
from sklearn.ensemble import RandomForestClassifier
# from skimage import exposure
from skimage import feature
from imutils import paths
import cv2
import numpy as np
import functions

sample_size = 60
min_conf = 0.75
sl_win_step = 10
box_overlap_thresh = 0.3

# initialize the data matrix and labels
print("[INFO] extracting features...")
data = []
labels = []

# loop over the image paths in the training set
# for imagePath in paths.list_images(args["training"]):
print("Loading training data")
for imagePath in paths.list_images("data/training/"):
    # extract the tag
    tag = imagePath.split("/")[-2]

    # load the image, convert it to grayscale, and detect edges
    image = cv2.imread(imagePath)

    # Check image Size is correct
    if image.shape[0] < sample_size or image.shape[1] < sample_size:
        print(imagePath, image.shape)
        image = cv2.resize(image, (60,60), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # extract Histogram of Oriented Gradients from the logo
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

# X = np.array(data)
# Y = np.array(labels)
# X.reshape(30,-1)

# "train" the Random Forest classifier
print("[INFO] Training classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(data, labels)
print("[INFO] Evaluating...")

# Load test image
test_img = cv2.imread("data/test/full_frame/cap00106.jpg")
test_gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)

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
    (H) = feature.hog(window,
                      orientations=9,
                      pixels_per_cell=(10, 10),
                      cells_per_block=(3, 3),
                      transform_sqrt=True, block_norm="L1")

    # pred = model.predict(H.reshape(1, -1))[0]
    pred = model.predict_proba(H.reshape(1, -1))[0]

    # add detection frame to the image
    if pred[0] > min_conf:
        detected_objects.append([x, y, x + winW, y + winH])
        # detected_objects = np.append(detected_objects, [(x, y, x + winW, y + winH)], axis=0)


# convert detected objects to NumPy Arra and preform Non-Maximum Suppression
detected_objects_array = np.array(detected_objects)
refined_detector = functions.non_max_suppression_fast(detected_objects_array, 0.3)

clone_img = test_img.copy()
# Draw Refined results:
for box in refined_detector:
    # cv2.rectangle(clone_img, (x, y), (x + winW, y + winH), (0, 0, 255), 1)
    cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)

# Draw original results:
# for box in detected_objects_array:
#     cv2.rectangle(clone_img, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 1)


cv2.imshow("RESULT!", clone_img)
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

cv2.waitKey(0)
