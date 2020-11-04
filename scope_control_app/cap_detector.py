import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
from collections import deque
from scipy import ndimage as ndi
from skimage.filters import gabor_kernel

class CapDetector:
    
    def __init__(self):
        self.focus_kernel = np.real(gabor_kernel(0.4, theta=0, sigma_x=3, sigma_y=3))

    
    def check_focus(self, frame):
        resized_frame = cv2.resize(frame.gray, (320, 180), interpolation=cv2.INTER_CUBIC)
        focus_val = ndi.convolve(resized_frame, self.focus_kernel, mode='wrap').var()
        
        return focus_val


    def check_caps(self, frame):
        return 0
