from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import argparse
# from PIL.ExifTags import TAGS

import glob
import csv


def make_csv(scope_name):

    images = []

    for file in glob.glob(f"./{scope_name}/*.jpg"):
        images.append(file)

    # images by alphabetic order descending
    images.sort(reverse=True)

    with open(f'{scope_name}.csv', 'w', newline='') as csvfile:
        fieldnames = ['focus', 'pd']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for file_name in images:

            # Open the image
            image = Image.open(file_name)        
            img_info = image.info['exif']

            gscope_metadata  = img_info[(img_info.find(b'SM:')):(img_info.find(b'PD:')+8)].decode('utf-8').split('/')
            focus = int(gscope_metadata[1].rsplit(':')[1])
            pd = float(gscope_metadata[8].rsplit(':')[1])

            # print(file_name)
            # print(f"Focus: {focus}")
            # print(f"PD: {pd}")

            writer.writerow({'focus': focus, 'pd': pd})            

    print(f"Created {scope_name}.csv")


def make_graph(scope_name):

    # Calculate the slope and intercept
    data = np.loadtxt(f'{scope_name}.csv', delimiter=',', skiprows=1)
    
    # Clean up the data and remove any outliers:
    # Check if data contains zero values
    data = data[data[:, 1] > 0]
    # Keep only unique values in the data (remove PD values outside the callibrated range)
    unique, counts = np.unique(data[:, 1], return_counts=True)
    # print(f"Unique values: {unique}, counts: {counts}")
    data = data[np.in1d(data[:, 1], unique[counts == 1])]
    
    # Calculate the slope and intercept
    coefficients = np.polyfit(data[:, 0], data[:, 1], 1)
    slope = coefficients[0]                                                             
    intercept = coefficients[1]
    print('Slope:', slope)
    print('Intercept:', intercept)

    # Plot the data
    print(f"Plotting {scope_name} data...")
    plt.title(scope_name)
    plt.xlabel('Focus')
    plt.ylabel('PD')
    plt.plot(data[:, 0], data[:, 1], 'o', label='Observations', markersize=2)
    plt.plot(data[:, 0], intercept + slope*data[:, 0], 'r', label='Fitted line')
    plt.legend()
    plt.show()


# get the exif data
# # extracting the exif metadata
# exifdata = image.getexif()

# looping through all the tags present in exifdata
# for tagid in exifdata:
#     # get the tag name, instead of human unreadable tag id
#     tagname = TAGS.get(tagid, tagid)
#     data = exifdata.get(tagid)
#     # decode bytes 
#     if isinstance(data, bytes):
#         data = data.decode()
#     print(f"{tagname:25}: {data}")


if __name__ == '__main__':
    
    #  get arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--scope', type=str, default='gscope01', help='Folder name which contains the Gscope images to process')
    args = parser.parse_args()
    
    print(f"Processing {args.scope}")

    make_csv(args.scope)
    make_graph(args.scope)