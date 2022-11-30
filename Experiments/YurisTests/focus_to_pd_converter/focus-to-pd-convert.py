from PIL import Image
# from PIL.ExifTags import TAGS

import glob
import csv

scope_name = 'gscope17'
images = []

for file in glob.glob(f"Experiments/YurisTests/focus_to_pd_converter/{scope_name}/*.jpg"):
    images.append(file)

with open(f'Experiments/YurisTests/focus_to_pd_converter/{scope_name}.csv', 'w', newline='') as csvfile:
    fieldnames = ['focus', 'pd']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for file_name in images:

        # open the image
        image = Image.open(file_name)        
        img_info = image.info['exif']

        gscope_metadata  = img_info[(img_info.find(b'SM:')):(img_info.find(b'PD:')+8)].decode('utf-8').split('/')
        focus = int(gscope_metadata[1].rsplit(':')[1])
        pd = float(gscope_metadata[8].rsplit(':')[1])

        # print(file_name)
        # print(f"Focus: {focus}")
        # print(f"PD: {pd}")

        writer.writerow({'focus': focus, 'pd': pd})



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

