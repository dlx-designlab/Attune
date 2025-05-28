import math
from itertools import combinations
import csv
from icecream import ic

class MusicPicker:
    # No. of Apex / Density > Instrument (4)
    # Position / Distribution > Octaves (4)
    # Brightness > Scale of Sound (4)

    def __init__(self):
        self.users_path = "app/static/caps_img/"
        
        self.density_range = (5, 20)  
        self.density_thresholds = [5, 10, 15] 
        
        self.distribution_range = (200, 600) 
        self.distribution_thresholds = [200, 350, 500]  
        
        self.brightness_range = (5, 15) 
        self.brightness_thresholds = [5, 8, 11]  

    def dist(self, p1, p2):
        (x1, y1), (x2, y2) = p1, p2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def remap_values(self, value, fromMin, fromMax, toMin=0, toMax=3):
        """Remapper une valeur d'une plage à une autre"""
        value = max(fromMin, min(value, fromMax))
        
        # Figure out how 'wide' each range is
        fromRange = fromMax - fromMin
        toRange = toMax - toMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - fromMin) / float(fromRange)

        # Convert the 0-1 range into a value in the right range.
        return int(toMin + (valueScaled * toRange))

    def map_with_thresholds(self, value, thresholds):
        if value < thresholds[0]:
            return 0
        elif value < thresholds[1]:
            return 1
        elif value < thresholds[2]:
            return 2
        else:
            return 3

    def data_to_music(self, uuid):        
        csv_file = f"static/captured_pics/{uuid}/{uuid}.csv"
        data = []

        with open(csv_file, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                data = [row] 
                
        if not data:
            ic("No data found !")
            return "000"

        item = data[0]
        
        prominence_str = item.pop(-1)
        prominence = 0
        if prominence_str.startswith("ap_"):
            prominence = int(prominence_str.split("_")[1])
        
        coordinates_data = []
        for i in range(0, len(item), 2):
            if i + 1 < len(item) and item[i] and item[i+1]:
                try:
                    x = int(item[i])
                    y = int(item[i+1])
                    coordinates_data.append((x, y))
                except ValueError:
                    continue
        
        # Number of points 
        cap_density = len(coordinates_data)
        
        # Average distance
        cap_distribution = 0
        if len(coordinates_data) > 1:
            distances = [self.dist(p1, p2) for p1, p2 in combinations(coordinates_data, 2)]
            if distances:
                cap_distribution = sum(distances) / len(distances)
        
        # Brightness
        cap_brightness = prominence

        ic(f"Number of capillaries: {cap_density}")
        ic(f"Average distance: {cap_distribution:.2f}")
        ic(f"Prominance: {cap_brightness}")

        # Mapping using threshold
        density_mapped = self.map_with_thresholds(cap_density, self.density_thresholds)
        distribution_mapped = self.map_with_thresholds(cap_distribution, self.distribution_thresholds)
        brightness_mapped = self.map_with_thresholds(cap_brightness, self.brightness_thresholds)
        
        values_filename = f"{density_mapped}{distribution_mapped}{brightness_mapped}"
        
        # Display the global quality
        quality_score = density_mapped + distribution_mapped + brightness_mapped
        if quality_score >= 7:
            ic("Excellent quality !")
        elif quality_score >= 5:
            ic("Good quality.")
        else:
            ic("Bad quality.")
        
        return values_filename


# Old version of music_picker.py

# import math
# from itertools import combinations
# import csv
# from icecream import ic

# class MusicPicker:
#     # No. of Apex / Density > Instrument (4)
#     # Position / Distribution > Octaves (4)
#     # Brightness > Scale of Sound (4) (try OpenCV cv::meanStdDev())        

#     # Each line in the csv file contains the coordinates of the detected apex points an image.
#     # Thre is an even number of coordinates per line. each pair is X and Y. 
#     # for example [0] is X and [1] is Y. [2] is X and [3] is Y....

#     def __init__(self):
#         self.users_path = "app/static/caps_img/"
#         self.density_range = (0, 30)
#         self.distribution_range = (100, 1000)
#         self.brigntness_range = (6, 17)

#     def dist(self, p1, p2):
#         (x1, y1), (x2, y2) = p1, p2
#         return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


#     def remap_values(self, value, fromMin, fromMax, toMin = 0, toMax = 3):
#         # Figure out how 'wide' each range is
#         fromRange = fromMax - fromMin
#         toRange = toMax - toMin

#         # Convert the left range into a 0-1 range (float)
#         valueScaled = float(value - fromMin) / float(fromRange)

#         # Convert the 0-1 range into a value in the right range.
#         return toMin + (valueScaled * toRange)

#     def data_to_music(self, uuid):
#         # read csv file and convert data to music paramters

#         csv_file = f"static/captured_pics/{uuid}/{uuid}.csv"
#         # txt_file = f"{self.users_path}{uuid}/{uuid}.txt"
#         data = []

#         # load CSV file
#         with open(csv_file, 'r') as csvfile:
#             #csv_reader = csv.reader(csvfile, delimiter=',')
#             last_data = csvfile.readlines()[-1].strip().split(',')
#             data.append(last_data)
#             #for row in csv_reader:
#             #    data.append(row)
                
#         # Calculate capillary density, distribution, and brightness
#         cap_density = 0         # average ammount of apex points in a sample
#         cap_distribution = 0    # average distance between apex points in a sample
#         cap_brightness = 0      # average brightness of the sample

#         # convert data to coordinates
#         clean_data = []
#         for item in data:

#             # extract the 1st value which contains the apex prominace (brighness) data
#             ap = item.pop(-1).split("_")[1]
#             cap_brightness += int(ap)

#             # convert csv data to coordinates (x, y) format
#             coordinates_data = []
#             for i in range(0, len(item), 2):
#                 coordinates_data.append( (int(item[i]), int(item[i+1])) )
            
#             # count the ammount of apex points in the sample
#             cap_density += len(coordinates_data)

#             # calculate average distance between apex points
#             distances = [self.dist(p1, p2) for p1, p2 in combinations(coordinates_data, 2)]
#             if len(distances) > 0:
#                 cap_distribution += sum(distances) / len(distances)
            
#             # add coordinates to the clean data list
#             clean_data.append(coordinates_data)

#         cap_density = int(cap_density / len(clean_data))
#         cap_distribution = int(cap_distribution / len(clean_data))
#         cap_brightness = int(cap_brightness / len(clean_data))

#         ic(cap_density)
#         ic(cap_distribution)
#         ic(cap_brightness)

#         # remap values to a range of 0-3 and struct a filename to match the music file names
#         # Todo: find correct ranges for cap_density, cap_distribution, cap_brightness
#         values_filename = f"{int(self.remap_values(cap_density, self.density_range[0], self.density_range[1],))}{int(self.remap_values(cap_distribution, self.distribution_range[0], self.distribution_range[1],))}{int(self.remap_values(cap_brightness, self.brigntness_range[0], self.brigntness_range[1],))}"
        
#         print(f"writing values to file: {values_filename}")
#         return values_filename

#         # with open(txt_file, 'w') as txtfile:
#             # txtfile.write(values_filename)