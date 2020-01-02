# coding:utf-8
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import uvc  # >> https://github.com/pupil-labs/pyuvc
import logging
import cv2

video_w = 1280
video_h = 720
video_fps = 30


# A parent widget to hold the camera image
class CamViewer(BoxLayout):

    def __init__(self, **kwargs):
        super(CamViewer, self).__init__(**kwargs)

        Clock.schedule_interval(self.update, 1.0 / video_fps)

        Window.minimum_height = 200
        Window.minimum_width = 200
        Window.size = (300, 500)

    def update(self, dt):
        # ret, frame = self.capture.read()
        curframe = cap.get_frame_robust()
        cv2.imshow("microscope feed", curframe.bgr)

    def set_focus(self):
        controls_dict['Auto Focus'].value = 1

    def quit_app(self):

        App.get_running_app().stop()
        Window.close()
        cap = None
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
    controls_dict['White Balance temperature'].value = 2000

    # Run Kivy App
    CamApp().run()


print("releasing scope...")
cap = None
print("scope released!")