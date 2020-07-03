""" Capilary Apex cropper from labeled images """
# import numpy as np
import cv2
import json
import random
from imutils import paths

radius = 60
path_width = 1
color_a = (0, 255, 0)
color_b = (0, 0, 255)
imSize = (1280, 720)
cropSize = 60
rectRadius = int(cropSize/2)
tag_points = []
false_tag_points = []
negative_crops = 40

def check_overlap(point):
    for tag_point in tag_points:
        if (point[0] + rectRadius >= tag_point[0] - rectRadius) and \
        (point[0] - rectRadius <= tag_point[0] + rectRadius) and \
        (point[1] + rectRadius >= tag_point[1] - rectRadius) and \
        (point[1] - rectRadius <= tag_point[1] + rectRadius):
            # print("overlap detected")
            return True

    for tag_point in false_tag_points:
        if (point[0] + rectRadius >= tag_point[0] - rectRadius) and \
        (point[0] - rectRadius <= tag_point[0] + rectRadius) and \
        (point[1] + rectRadius >= tag_point[1] - rectRadius) and \
        (point[1] - rectRadius <= tag_point[1] + rectRadius):
            # print("overlap detected")
            return True

    return False


def crop_save(point, tag, cnt, file_name):

    global img, filename

    p_1 = (point[0] - rectRadius, point[1] - rectRadius)
    p_2 = (point[0] + rectRadius, point[1] + rectRadius)

    if tag == 1:
        path_color = color_a
        folder = "cap"
    else:
        folder = "no_cap"
        path_color = color_b

    # img = cv2.rectangle(img, p_1, p_2, path_color, path_width)

    crop_img = img[p_1[1]:p_2[1], p_1[0]:p_2[0]]

    f_name = file_name.split("/")[-1]
    f_name = f_name.split(".")[-2]
    f_name = f"data/training/{folder}/{f_name}_{cnt}.png"
    print(f"saving: {f_name}")
    cv2.imwrite(f_name, crop_img)

for filename in paths.list_images("data/to_lbl/labeled"):
    
    # check if its an image
    if filename.split(".")[-1] != "json":

        lblsFileName = filename.split(".")[-2] + ".json"

        # load image
        img = cv2.imread(filename)
        # imSize = (img.shape[1], img.shape[0])
        # print(imSize)
        print(f"Loading: {filename}, {lblsFileName}")

        # Load tags from a JSON File and crop positives
        with open(lblsFileName, 'r') as f:
            tag_points = []
            tags = json.load(f)
            for count, tag in enumerate (tags["shapes"], 0):
                new_point = (int(tag["points"][0][0]), int(tag["points"][0][1]))

                tag_points.append(new_point)    
                crop_save(new_point, 1, count, filename)

        print("Apex Tag Points:")
        print(tag_points)

        # Generare and crop random negatives
        false_tag_points = []
        for i in range(negative_crops):
            new_point = (random.randint(cropSize, imSize[0]-cropSize), random.randint(cropSize, imSize[1]-cropSize))
            is_overlapping = True
            while is_overlapping:
                is_overlapping = check_overlap(new_point)
                if is_overlapping:
                    new_point = (random.randint(cropSize, imSize[0]-cropSize), random.randint(cropSize, imSize[1]-cropSize))

            false_tag_points.append(new_point)
            crop_save(new_point, 0, i, filename)

        print(" No Apex Tag Points:")
        print(false_tag_points)

        # cv2.imshow("image", img)
        # cv2.waitKey(0)
    
print("DONE!")
