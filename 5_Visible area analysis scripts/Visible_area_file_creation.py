# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:00:06 2019

@author: lucas
"""

import os
import rasterio
import numpy
import time
from natsort import natsorted


def main(path = 'Test_new'):
    text_file_path = 'visible_area_viewshed_Sample_SRTM.txt'
    if os.path.isfile(text_file_path):  #If this path already exist
        os.remove(text_file_path)       #Removing the file at this url

    #All file in the folder are read
    Files = []
    files = os.listdir(path)
    files_sorted = natsorted(files, key=lambda y: y.lower())
    for f in files_sorted:
        Files.append((path+'/'+f))  
    
    viewshed_0 = rasterio.open(Files[0])   

    text_file = open(text_file_path, "w+")
    text_file.write("#The viewshed file has " + str(viewshed_0.width*viewshed_0.height) + " pixels in total.")
    text_file.write("\n")
    text_file.write('{:20}'.format('#ID building;'))
    text_file.write('{:20}'.format('ID summit;'))
    text_file.write('{:20}'.format('Value 1 occurence'))
    text_file.write("\n")

    for viewshed_path in Files:

        viewshed = rasterio.open(viewshed_path)
        print(viewshed_path)
        band1    = viewshed.read(1)

        unique, counts = numpy.unique(band1, return_counts=True)
        dict_value     = dict(zip(unique, counts))
        number_pixel_1 = dict_value[1]
        viewshed_name_file = viewshed_path.split('/')
        viewshed_name_split = viewshed_name_file[-1].split("_")

        text_file.write('{:0.0f}'.format(float(viewshed_name_split[1])))
        text_file.write(";")
        text_file.write('{:0.0f}'.format(float(viewshed_name_split[2][:-4])))
        text_file.write(";")
        text_file.write('{:0.0f}'.format(number_pixel_1))
        text_file.write("\n")

    text_file.close()

if __name__ == "__main__":
    print("Hello World")
    start1 = time.time()
    
    main("Volume_sample_SRTM")
    
    done = time.time()
    elapsed = done - start1
    print("Overall process: " + str(elapsed))


        
        