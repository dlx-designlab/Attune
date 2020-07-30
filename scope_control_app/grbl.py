import serial
import time

class GrblControl:

    def __init__(self, dev_addr, def_step_size):
        
        self.xPos = 0
        self.yPos = 0
        self.zPos = 0
        self.focus = 0
        self.stepSize = def_step_size
        self.x_center_pos = 9  # the X - position at which the scope is in the middle of the finger
        self.min_tof_dist = 27  # min distance in mm between the TOF sensor and the user finger
        
        # Open serial port to communicate with GRBL
        print("Connecting to GRBL...")
        self.grbl_ser = serial.Serial(dev_addr, 115200, timeout=10.0, write_timeout=10.0)
        # Wake up grbl
        self.grbl_ser.write(('\r\n\r\n').encode())
        time.sleep(2)  # Wait for grbl to initialize
        self.grbl_ser.flushInput()  # Flush startup text in serial input
        print("Connected!")


    def send_grbl_cmd(self, grbl_cmd):
        print(f"Sending: {grbl_cmd}")
        # Send g-code block to grbl
        self.grbl_ser.write((grbl_cmd + '\n').encode())
        # Wait for grbl response with carriage return
        grbl_out_string = ((self.grbl_ser.readline()).strip()).decode("utf-8")
        print(f"got response: {grbl_out_string.strip()}")

        return(grbl_out_string)


    def adjust_step_size(self, step):
        self.stepSize = step
        self.stepSize = round(self.stepSize, 1)


    # Move the Scope to new position
    # Dist is +1 or -1 to determine direction
    # The scope will be moved by one step
    def jog_scope_position(self, x_dist, y_dist, z_dist):
        self.xPos = round(self.xPos + self.stepSize * x_dist, 1)
        self.yPos = round(self.yPos + self.stepSize * y_dist, 1)
        self.zPos = round(self.zPos + self.stepSize * z_dist, 1)

        the_cmd = f'$J=X{self.xPos} Y{self.yPos} Z{self.zPos} F1000'
        jog_result = self.send_grbl_cmd(the_cmd)
        
        # Cehck if jog was successful
        if "error" in jog_result:
            print("jog out of bounds")
            # Undo position adjustment
            self.xPos = round(self.xPos - self.stepSize * x_dist, 1)
            self.yPos = round(self.yPos - self.stepSize * y_dist, 1)
            self.zPos = round(self.zPos - self.stepSize * z_dist, 1)



    def run_home_cycle(self):
        print("Homing...")
        self.send_grbl_cmd('$H')

        # todo: create default setings file
        self.xPos = 0
        self.yPos = 0
        self.zPos = 0

        # print("Moving to start position...")
        # the_cmd = f'G0 X{self.xPos} Y{self.yPos} Z{self.zPos}'
        # self.send_grbl_cmd(the_cmd)

        print("Homing Done!")