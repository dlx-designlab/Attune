import math
from itertools import combinations
import csv
from icecream import ic

class MusicPicker:
    # No. of Apex / Density > Instrument (4)
    # Position / Distribution > Octaves (4)
    # Brightness > Scale of Sound (4) (try OpenCV cv::meanStdDev())        

    # Each line in the csv file contains the coordinates of the detected apex points an image.
    # Thre is an even number of coordinates per line. each pair is X and Y. 
    # for example [0] is X and [1] is Y. [2] is X and [3] is Y....

    def __init__(self):
        self.users_path = "app/static/caps_img/"
        self.density_range = (0, 30)
        self.distribution_range = (100, 1000)
        self.brigntness_range = (2, 30)

    def dist(self, p1, p2):
        (x1, y1), (x2, y2) = p1, p2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


    def remap_values(self, value, fromMin, fromMax, toMin = 0, toMax = 3):
        # Figure out how 'wide' each range is
        fromRange = fromMax - fromMin
        toRange = toMax - toMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - fromMin) / float(fromRange)

        # Convert the 0-1 range into a value in the right range.
        return toMin + (valueScaled * toRange)

    def data_to_music(self, uuid):
        # read csv file and convert data to music paramters

        csv_file = f"static/captured_pics/{uuid}/{uuid}.csv"
        # txt_file = f"{self.users_path}{uuid}/{uuid}.txt"
        data = []

        # load CSV file
        with open(csv_file, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                data.append(row)
                
        # Calculate capillary density, distribution, and brightness
        cap_density = 7         # average ammount of apex points in a sample
        cap_distribution = 0    # average distance between apex points in a sample
        cap_brightness = 7      # average brightness of the sample

        # convert data to coordinates
        clean_data = []
        for item in data:

            # extract the 1st value which contains the apex prominace (brighness) data
            ap = item.pop(-1).split("_")[1]
            cap_brightness += int(ap)

            # convert csv data to coordinates (x, y) format
            coordinates_data = []
            for i in range(0, len(item), 2):
                coordinates_data.append( (int(item[i]), int(item[i+1])) )
            
            # count the ammount of apex points in the sample
            cap_density += len(coordinates_data)

            # calculate average distance between apex points
            distances = [self.dist(p1, p2) for p1, p2 in combinations(coordinates_data, 2)]
            if len(distances) > 0:
                cap_distribution += sum(distances) / len(distances)
            
            # add coordinates to the clean data list
            clean_data.append(coordinates_data)

        cap_density = int(cap_density / len(clean_data))
        cap_distribution = int(cap_distribution / len(clean_data))
        cap_brightness = int(cap_brightness / len(clean_data))

        ic(cap_density)
        ic(cap_distribution)
        ic(cap_brightness)

        # remap values to a range of 0-3 and struct a filename to match the music file names
        # Todo: find correct ranges for cap_density, cap_distribution, cap_brightness
        values_filename = f"{int(self.remap_values(cap_density, self.density_range[0], self.density_range[1],))}{int(self.remap_values(cap_distribution, self.distribution_range[0], self.distribution_range[1],))}{int(self.remap_values(cap_brightness, self.brigntness_range[0], self.brigntness_range[1],))}"
        
        print(f"writing values to file: {values_filename}")
        return values_filename

        # with open(txt_file, 'w') as txtfile:
            # txtfile.write(values_filename)