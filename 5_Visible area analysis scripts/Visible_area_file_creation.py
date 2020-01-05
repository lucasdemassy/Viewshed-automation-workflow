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


def main(viewshed_path, text_file_path):
    """
    This script counts how many pixel with the value 1 there are in any viewshed files located in the input folder path.
    It creates a text file according to the input file and saves all value in it.
    INPUT:
        viewshed_path : string
        text_file_path : string
    OUTPUT:
        return : none
    """
    if os.path.isfile(text_file_path):  #If this text file path already exist
        os.remove(text_file_path)       #Removing the file at this url

    #All file in the folder are read
    Files = []
    files = os.listdir(viewshed_path)
    files_sorted = natsorted(files, key=lambda y: y.lower())
    for f in files_sorted:
        Files.append((viewshed_path+'/'+f))  
    
    #Open the first viewshed
    viewshed_0 = rasterio.open(Files[0])   

    #Initialize a text file
    text_file = open(text_file_path, "w+")
    text_file.write("#The viewshed file has " + str(viewshed_0.width*viewshed_0.height) + " pixels in total.")
    text_file.write("\n")
    text_file.write('{:20}'.format('#ID building;'))
    text_file.write('{:20}'.format('ID summit;'))
    text_file.write('{:20}'.format('Value 1 occurence'))
    text_file.write("\n")

    #For each viewshed located in the input folder
    for viewshed_path in Files:

        viewshed = rasterio.open(viewshed_path) #Open the viewhshed
        band1    = viewshed.read(1)             #Read the band number 1 (viewsheds from GRASS have only one band)
        print(viewshed_path)                    #Print its name so the user follows the progression

        #Get all interesting values
        unique, counts = numpy.unique(band1, return_counts=True)    #return two lists with unique pixel values and their occurence
        dict_value     = dict(zip(unique, counts))                  #Link these two lists with a dictionnary
        number_pixel_1 = dict_value[1]                              #Get occurence of pixel value 1
        viewshed_name_file = viewshed_path.split('/')               #Cut the viewshed path
        viewshed_name_split = viewshed_name_file[-1].split("_")     #Cut the viewshed name

        #Write values in the text file
        text_file.write('{:0.0f}'.format(float(viewshed_name_split[1])))        #ID building
        text_file.write(";")
        text_file.write('{:0.0f}'.format(float(viewshed_name_split[2][:-4])))   #ID summit
        text_file.write(";")
        text_file.write('{:0.0f}'.format(number_pixel_1))                       #Value 1 occurence
        text_file.write("\n")

    text_file.close()

if __name__ == "__main__":
    print("Hello World")
    start1 = time.time()
    
    main("Volume_sample_SRTM", 'visible_area_viewshed_Sample_SRTM.txt')
    
    done = time.time()
    elapsed = done - start1
    print("Overall process: " + str(elapsed))


        
        