# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 22:48:33 2019

@author: lucas
"""

import os
import time
import numpy as np


def main(path= 'visible_area_viewshed.txt', path_new_file = 'visible_area_unique_viewshed.txt'):
    if os.path.isfile(path_new_file):  #If this path already exist
        os.remove(path_new_file)       #Removing the file at this url
        
    new_file = open(path_new_file, "w+")
    file_header = open(path, "r")
    new_file.write(file_header.readline())
    new_file.write(file_header.readline())
    file = np.genfromtxt(path, delimiter=';',skip_header=2)
    row_count = len(file)
    old_viewshed = file[0]
    several = False
    for i in range(1, row_count):
        new_viewshed = file[i]
        if old_viewshed[0] != new_viewshed[0] and not several:
            new_file.write('{:0.0f};{:0.0f};{:0.0f}'.format(old_viewshed[0], old_viewshed[1], old_viewshed[2]))
            #new_file.write(str(old_viewshed[0]) + ";" + str(old_viewshed[1]) + ";" + str(old_viewshed[2]))
            new_file.write("\n")
        if old_viewshed[0] == new_viewshed[0] and not several:
            
            position_max = i-1
            maximum = old_viewshed[2]
            several = True
            if new_viewshed[2] > maximum:
                maximum = new_viewshed[2]
                position_max = i
        if old_viewshed[0] == new_viewshed[0] and several:
            if new_viewshed[2] > maximum:
                maximum = new_viewshed[2]
                position_max = i
        if old_viewshed[0] != new_viewshed[0] and several:
            several = False
            new_file.write('{:0.0f};{:0.0f};{:0.0f}'.format(file[position_max][0], file[position_max][1], file[position_max][2]))
            #new_file.write(str(file[position_max][0]) + ";" + str(file[position_max][1]) + ";" + str(file[position_max][2]))
            new_file.write("\n")
        old_viewshed = new_viewshed
    if several:
        new_file.write('{:0.0f};{:0.0f};{:0.0f}'.format(file[position_max][0], file[position_max][1], file[position_max][2]))
        #new_file.write(str(file[position_max][0]) + ";" + str(file[position_max][1]) + ";" + str(file[position_max][2]))
    new_file.close()
    
if __name__ == "__main__":
    print("Hello World")
    start1 = time.time()
    
    main(path = "visible_area_viewshed_4732_5519_to_8473.txt", path_new_file = "visible_area_unique_viewshed_4732_5519_to_8473.txt")
    
    done = time.time()
    elapsed = done - start1
    print("Overall process: " + str(elapsed))
        