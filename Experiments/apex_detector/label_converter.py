""" Converting labeles from Label-Me format to YOLO format  """
# import numpy as np
import cv2
import json
from imutils import paths
import math

img_w = 1280
img_h = 720
radius_padding = 10

for filename in paths.list_files("data/to_lbl/YOLO/test/", validExts=".json"):
    # open the JSON
    print(f"Loading: {filename}")

    # Load tags from a JSON File and crop positives
    with open(filename, 'r') as f:
        tag_points = []
        tags = json.load(f)

        txt_file_name = filename.split(".")[-2] + ".txt"
        f = open(txt_file_name, "w+")

        for count, tag in enumerate (tags["shapes"], 0):
            a = abs(tag["points"][0][0] - tag["points"][1][0])
            b = abs(tag["points"][0][1] - tag["points"][1][1])
            radius = math.sqrt(math.pow(a,2) + math.pow(b,2)) + radius_padding

            new_point = ((tag["points"][0][0]) / img_w, (tag["points"][0][1]) / img_h, radius * 2 / img_w, radius * 2 / img_h)
            f.write(f"1 {new_point[0]} {new_point[1]} {new_point[2]} {new_point[3]}\n")
            # print(new_point)
            tag_points.append(new_point)

        f.close()


print("DONE!")
