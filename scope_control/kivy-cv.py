# coding:utf-8
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

# Used to control the scope camera
import uvc  # >> https://github.com/pupil-labs/pyuvc
import logging
import cv2

video_w = 1280
video_h = 720
video_fps = 30


# A parent widget to hold the camera image
class CamViewer(BoxLayout):

    xPos = 0
    yPos = 0
    zPos = 0
    focus = 104
    curframe = None

    def __init__(self, **kwargs):
        super(CamViewer, self).__init__(**kwargs)

        Clock.schedule_interval(self.update, 1.0 / video_fps)

        Window.minimum_height = 200
        Window.minimum_width = 200
        Window.size = (300, 500)

    def update(self, dt):
        # ret, frame = self.capture.read()
        self.curframe = cap.get_frame_robust()
        cv2.imshow("microscope feed", self.curframe.bgr)

    def set_auto_focus(self):
        # print(f"Focus Value {controls_dict['Absolute Focus'].value}")
        controls_dict['Auto Focus'].value = 1

    def jog_focus(self, val):
        self.focus += val
        controls_dict['Auto Focus'].value = 0
        controls_dict['Absolute Focus'].value = self.focus
        print(f"focus: {self.focus}")

    def jog_x_axis(self, dist):
        self.xPos += dist
        the_cmd = f'G0 X{self.xPos}'
        print(f"Sending: {the_cmd}")
        s.write((the_cmd + '\n').encode())  # Send g-code block to grbl
        grbl_out_string = s.readline()  # Wait for grbl response with carriage return
        print(f"got response: {grbl_out_string.strip()}")

    def jog_y_axis(self, dist):
        self.yPos += dist
        the_cmd = f'G0 Y{self.yPos}'
        print(f"Sending: {the_cmd}")
        s.write((the_cmd + '\n').encode())  # Send g-code block to grbl
        grbl_out_string = s.readline()  # Wait for grbl response with carriage return
        print(f"got response: {grbl_out_string.strip()}")

    def jog_z_axis(self, dist):
        self.zPos += dist
        the_cmd = f'G0 Z{self.zPos}'
        print(f"Sending: {the_cmd}")
        s.write((the_cmd + '\n').encode())  # Send g-code block to grbl
        grbl_out_string = s.readline()  # Wait for grbl response with carriage return
        print(f"got response: {grbl_out_string.strip()}")

    def capture_panorama(self):
        for i in range(0, 6):
            self.jog_x_axis(i/10)
            time.sleep(1)

            # Update frame and save it
            filename = f"frame{i}.jpg"
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
    s = serial.Serial('/dev/cu.usbmodem142101', 115200)

    # Wake up grbl
    s.write(('\r\n\r\n').encode())
    time.sleep(2)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    # Sent Test Command
    cmd = 'G0 X0 Y0 Z0'  # Strip all EOL characters for consistency
    print(f"Sending: {cmd}")
    s.write((cmd + '\n').encode())  # Send g-code block to grbl
    grbl_out = s.readline()  # Wait for grbl response with carriage return
    print(f"got response: {grbl_out.strip()}")

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

    # Capture a frame to initialize the cope
    cap.frame_mode = (video_w, video_h, video_fps)
    init_frame = cap.get_frame_robust()

    # Set Auto-focus to false and set a custom value
    controls_dict['Auto Focus'].value = 0
    controls_dict['Absolute Focus'].value = 200

    # Set Auto-WB to false and set a custom value
    controls_dict['White Balance temperature,Auto'].value = 0
    controls_dict['White Balance temperature'].value = 5000

    # Run Kivy App
    CamApp().run()


print("releasing scope...")
cap = None
print("scope released!")

print("releasing GRBL serial...")
s.close()
print("GRBL serial released!")