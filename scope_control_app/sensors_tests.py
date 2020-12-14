from matplotlib import pyplot as plt
from sensors import SensorsFeed
import time

# log time in seconds
log_duration = 5
# samples per mesurements (to average)
rng_samples = 20

sns = SensorsFeed()
ave_range_log = []
start_time = time.time()

while (time.time() - start_time) < log_duration:

    # tmp =  sns.get_temp()

    range_log = []
    while len(range_log) < rng_samples:
        range_log.append(sns.get_range())
        time.sleep(0.01)
    
    ave_rng = sum(range_log) / len(range_log)
    print(range_log)
    print(ave_rng)

    # time.sleep(0.1)

    # print("----------------")
    # print(tmp)
    # print(rng)    
    # print("----------------")

    ave_range_log.append(ave_rng)
    # time.sleep(1)

plt.plot(ave_range_log)
plt.show()

# with open("log.txt", "w") as txt_file:
#     for value in ave_range_log:
#         txt_file.write(f"{value},") 

# while not i2c.try_lock():
#     pass

# # Find the first I2C device available.
# devices = i2c.scan()
# while len(devices) < 1:
#     devices = i2c.scan()
#     print(devices)
#     time.sleep(1)

# print(devices)