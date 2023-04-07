from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
# from PIL.ExifTags import TAGS

import glob
import csv


def make_csv(scope_name):

    images = []

    for file in glob.glob(f"Experiments/YurisTests/focus_to_pd_converter/{scope_name}/*.jpg"):
        images.append(file)

    with open(f'Experiments/YurisTests/focus_to_pd_converter/{scope_name}.csv', 'w', newline='') as csvfile:
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
    # Make sure to clean up the data and remove any outliers
    data = np.loadtxt(f'Experiments/YurisTests/focus_to_pd_converter/{scope_name}.csv', delimiter=',', skiprows=1)
    coefficients = np.polyfit(data[:, 0], data[:, 1], 1)
    slope = coefficients[0]                                                             
    intercept = coefficients[1]
    print('Slope:', slope)
    print('Intercept:', intercept)

    # Plot the data
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
    
    make_csv('gscope14')
    make_graph('gscope14')