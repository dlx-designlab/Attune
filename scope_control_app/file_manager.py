""" All file management related functions """
import os
from distutils import dir_util
from os import listdir
from os.path import isfile, isdir, join

class FileManager:
    
    def __init__(self):
        self.media_path = "/media/pi/"

    def copy_to_usb(self, uid = ""):
        
        usb_drives = [f for f in listdir(self.media_path) if isdir(join(self.media_path, f))]
        
        if len(usb_drives) > 0 :
            usb_path = self.media_path + usb_drives[0] + "/" + uid
            print(f"copying files to: {usb_path}")

            source = "static/captured_pics/" + uid

            destination =  dir_util.copy_tree(source, usb_path, update=1) 
            
            print(destination)
            print("done!")

        else:
            print("No USB Drives found!")


# if __name__ == "__main__":
    
    # f_mngr = FileManager()
    # f_mngr.copy_to_usb("2F6E98")
    