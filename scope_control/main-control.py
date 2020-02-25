# coding:utf-8
# This code is used to control the Self-Positioning Microscope stand
# More details in the wiki: https://github.com/dlx-designlab/Attune/wiki

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics.texture import Texture

# used to control the cope position via GRBL
import serial
import time
from time import localtime, strftime

# Used to control the scope camera
import uvc  # >> https://github.com/pupil-labs/pyuvc
import logging
import cv2

video_w = 1280
video_h = 720
video_fps = 30


class ScopeSettings:

    # todo: add app settings to config default values

    xPos = -1.0
    yPos = -1.0
    zPos = -1.0
    focus = 55
    white_balance = 6000
    stepSize = 0.5


# Sending commands to GRBL Arduino
def send_grbl_cmd(grbl_cmd):
    print(f"Sending: {grbl_cmd}")
    s.write((grbl_cmd + '\n').encode())  # Send g-code block to grbl
    grbl_out_string = s.readline()  # Wait for grbl response with carriage return
    print(f"got response: {grbl_out_string.strip()}")


# A parent widget to hold the camera image
class CamViewer(BoxLayout):

    curframe = None

    def __init__(self, **kwargs):
        super(CamViewer, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Set the app refresh rate to be same like the scope FPS
        Clock.schedule_interval(self.update, 1.0 / video_fps)

        Window.minimum_height = 200
        Window.minimum_width = 200
        Window.size = (300, 500)

        # Update all the info labels
        self.stp_label.text = str(ScopeSettings.stepSize)

        # todo: Fix this later as the initial scope pos might be different from the actual pos before/after homing cycle
        self.pos_lbl.text = f"X:{ScopeSettings.xPos}, Y:{ScopeSettings.yPos}, Z:{ScopeSettings.zPos}"

    def update(self, dt):
        # ret, frame = self.capture.read()
        self.curframe = cap.get_frame_robust()
        cv2.imshow("microscope feed", self.curframe.bgr)

    def _keyboard_closed(self):
        print('keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Keycode is composed of an integer + a string
        # Check which key was pressed
        if keycode[1] == 'w':
            self.jog_scope_position(0, 1, 0)
        elif keycode[1] == 's':
            self.jog_scope_position(0, -1, 0)
        elif keycode[1] == 'a':
            self.jog_scope_position(-1, 0, 0)
        elif keycode[1] == 'd':
            self.jog_scope_position(1, 0, 0)
        elif keycode[1] == 'q':
            self.jog_scope_position(0, 0, 1)
        elif keycode[1] == 'z':
            self.jog_scope_position(0, 0, -1)
        elif keycode[1] == 'e':
            self.jog_focus(1)
        elif keycode[1] == 'c':
            self.jog_focus(-1)

        # Return True to accept the key. Otherwise, it will be used by the system.
        return True

    def set_auto_focus(self):
        # print(f"Focus Value {controls_dict['Absolute Focus'].value}")
        controls_dict['Auto Focus'].value = 1
        print("Auto Focus on")

    def set_white_balance(self):
        # Set Auto-WB to false and set a custom value
        controls_dict['White Balance temperature,Auto'].value = 0

        if ScopeSettings.white_balance >= 6000:
            ScopeSettings.white_balance = 3000
        else:
            ScopeSettings.white_balance += 1000

        controls_dict['White Balance temperature'].value = ScopeSettings.white_balance
        print(f"White Balance: {ScopeSettings.white_balance}")

    def jog_focus(self, val):
        ScopeSettings.focus += val
        controls_dict['Auto Focus'].value = 0
        controls_dict['Absolute Focus'].value = ScopeSettings.focus
        print(f"focus: {ScopeSettings.focus}")

    def adjust_step_size(self, step):
        ScopeSettings.stepSize += step
        ScopeSettings.stepSize = round(ScopeSettings.stepSize, 1)
        self.stp_label.text = str(ScopeSettings.stepSize)

    # Move the Scope to new position
    # Dist is +1 or -1 to determine direction
    # The scope will be moved by one step
    def jog_scope_position(self, x_dist, y_dist, z_dist):
        ScopeSettings.xPos = round(ScopeSettings.xPos + ScopeSettings.stepSize * x_dist, 1)
        ScopeSettings.yPos = round(ScopeSettings.yPos + ScopeSettings.stepSize * y_dist, 1)
        ScopeSettings.zPos = round(ScopeSettings.zPos + ScopeSettings.stepSize * z_dist, 1)

        the_cmd = f'G0 X{ScopeSettings.xPos} Y{ScopeSettings.yPos} Z{ScopeSettings.zPos}'
        send_grbl_cmd(the_cmd)

        # update gui with new position data
        self.pos_lbl.text = f"X:{ScopeSettings.xPos}, Y:{ScopeSettings.yPos}, Z:{ScopeSettings.zPos}"

    def run_home_cycle(self):

        print("Homing...")
        send_grbl_cmd('$H')

        # todo: create default setings file
        ScopeSettings.xPos = -1.0
        ScopeSettings.yPos = -1.0
        ScopeSettings.zPos = -1.0

        print("Moving to start position...")
        the_cmd = f'G0 X{ScopeSettings.xPos} Y{ScopeSettings.yPos} Z{ScopeSettings.zPos}'
        send_grbl_cmd(the_cmd)

        self.pos_lbl.text = f"X:{ScopeSettings.xPos}, Y:{ScopeSettings.yPos}, Z:{ScopeSettings.zPos}"
        print("Homing Done!")

    def capture_panorama(self):
        # print("Panorama mode disabled!")
        # for i in range(0, 6):
        #     self.jog_x_axis(i/10)
        #     time.sleep(1)
        #
        #     # Update frame and save it
        timestamp = strftime("%Y_%m_%d-%H_%M_%S", localtime())
        filename = f"pics/cap_{timestamp}.jpg"
        print(f"saving file: {filename}")
        self.curframe = cap.get_frame_robust()
        cv2.imshow("microscope feed", self.curframe.bgr)
        cv2.imwrite(filename, self.curframe.bgr)
        print("file saved!")

    def quit_app(self):
        App.get_running_app().stop()
        Window.close()

        # Close connection to the G-Scope
        print("releasing scope...")
        cap = None
        print("scope released!")

        # Release Serial Port
        print("releasing GRBL serial...")
        s.close()
        print("GRBL serial released!")

        print("Closing App...")
        exit()


# Main Kivi App Class
class CamApp(App):
    def build(self):
        # self.capture = cv2.VideoCapture(0)
        # self.my_camera = KivyCamera(capture=self.capture, fps=30)
        # return self.my_camera
        return CamViewer()

    def on_stop(self):
        pass
        #without this, app will not exit even if the window is closed
        # self.capture.release()
        # cap = None


if __name__ == '__main__':

    # Open serial port to communicate with GRBL
    s = serial.Serial('/dev/cu.usbmodem142401', 115200)

    # Wake up grbl
    s.write(('\r\n\r\n').encode())
    time.sleep(2)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    # Sent Test Command - HOME
    # send_grbl_cmd('$H')

    # UVC Setup
    logging.basicConfig(level=logging.INFO)
    dev_list = uvc.device_list()
    print(dev_list)

    # Add new capture device and its control properties
    cap = uvc.Capture(dev_list[0]["uid"])
    controls_dict = dict([(c.display_name, c) for c in cap.controls])

    print(cap.avaible_modes)
    print("--- Available Controls: ---")
    for control in controls_dict:
        print(control)
    print("------")

    time.sleep(1)

    # Capture a frame to initialize the cope
    cap.frame_mode = (video_w, video_h, video_fps)
    init_frame = cap.get_frame_robust()

    time.sleep(1)

    # Set Auto-focus to false and set a custom value
    controls_dict['Auto Focus'].value = 0
    controls_dict['Absolute Focus'].value = ScopeSettings.focus

    # Set Auto-WB to false and set a custom value
    controls_dict['White Balance temperature,Auto'].value = 0
    controls_dict['White Balance temperature'].value = ScopeSettings.white_balance

    time.sleep(1)

    # Run Kivy App
    CamApp().run()


print("releasing scope...")
cap = None
print("scope released!")

print("releasing GRBL serial...")
s.close()
print("GRBL serial released!")