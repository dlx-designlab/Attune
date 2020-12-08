""" All file management related functions """
import os
import psutil
from distutils import dir_util
# from os import listdir
# from os.path import isfile, isdir, join

class FileManager:
    
    def __init__(self):
        self.media_path = "/media/"

    def copy_to_usb(self, uid = ""):
        
        usb_drives = sorted(self.get_usb_devices())
        # [f for f in listdir(self.media_path) if isdir(join(self.media_path, f))]
        
        if len(usb_drives) > 0 :
            print(f"Found {len(usb_drives)} USB Drives:")
            for device in usb_drives:
                print(device)
            
            usb_path = usb_drives[0] + "/" + uid
            print(f"copying files to: {usb_path}")

            source = "static/captured_pics/" + uid

            destination =  dir_util.copy_tree(source, usb_path, update=1) 
            
            print(destination)
            res = f"USB backup complete for user: {uid}"
            
        else:
            res = "No USB Drives found!"

        print(res)
        return(res)


    def get_usb_devices(self):
        values = []
        disk_partitions = psutil.disk_partitions(all=False)
        for partition in disk_partitions:
            if "/media" in partition.mountpoint:
                values.append(partition.mountpoint)
        
        return values 


# if __name__ == "__main__":

#     f_mngr = FileManager()
#     f_mngr.copy_to_usb("AEB383")
    