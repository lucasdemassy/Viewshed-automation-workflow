# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:30:17 2019

@author: lucas
"""

import os
import time
from natsort import natsorted

def rename_file(path):
    """
    Rename all viewshed files as followed
    from a folder given by the user: vshed_ID-summit_ID-viewshed
    INPUT:
        path: string
    OUTPUT:
        return: None
    """
    #All file in the folder are read
    Files = os.listdir(path)
    #Sort files according to the ID_summit
    files = natsorted(Files, key=lambda y: y.lower())
    #For each viewshed file
    for i in range(len(files)):
        #Get its name
        f = files[i]
        #f_split = ["vshed", "ID-summit", "older ID-viewshed"]
        f_split = f.split("_")
        #Rename the file
        os.rename(path+'/'+f, path + '/' + f_split[0] + "_" + '{:0.0f}'.format(float(f_split[1])) + "_" + str(i) + ".tif")

        
        


if __name__ == "__main__":
    print("Hello World")
    start1 = time.time()
    
    main(path = "")
    
    done = time.time()
    elapsed = done - start1
    print("Overall process: " + str(elapsed))
