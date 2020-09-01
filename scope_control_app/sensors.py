import time
import board
import busio
import adafruit_vl6180x # TOF Sensor
import adafruit_mlx90614 # IR Temp sensor

class SensorsFeed:

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

        print("connecting to temperature senseor...")
        self.tmp_sensor = adafruit_mlx90614.MLX90614(self.i2c)
        
        print("connectig to range sensor...")
        self.rng_sensor = adafruit_vl6180x.VL6180X(self.i2c)

        print("Sensors online!")

    
    def get_temp(self):
        # print("Ambent Temp: ", self.tmp_sensor.ambient_temperature)
        # print("Object Temp: ", self.tmp_sensor.object_temperature)
        sensorVal = round(self.tmp_sensor.object_temperature, 1)
        return sensorVal


    def get_range(self):
        # print('Range: {0}mm'.format(self.rng_sensor.range))
        # print('Range status: {0}'.format(self.rng_sensor.range_status))
        # print('Light (1x gain): {0}lux'.format(self.rng_sensor.read_lux(adafruit_vl6180x.ALS_GAIN_1)))
        sensorVal = self.rng_sensor.range
        return sensorVal

        