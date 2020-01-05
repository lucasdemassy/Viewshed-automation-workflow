# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 22:48:33 2019

@author: lucas
"""

import os
import time
import numpy as np


def main(path= 'visible_area_viewshed.txt', path_new_file = 'visible_area_unique_viewshed.txt'):
    """
    A building can have several summits and so several viewsheds.
    This script improves the Visible_area_file_creation.py file. 
    It seeks in the output text file of the previous script the value 1 occurence
    Then the algorithm takes the maximum between viewsheds of the same building and discard the others.
    Maximum values are saved in a new text file.
    INPUT:
        path : string
        path_new_file : string
    OUTPUT:
        return none
    """

    if os.path.isfile(path_new_file):  #If this path already exist
        os.remove(path_new_file)       #Removing the file at this url
        
    #Initialize the new text file
    new_file    = open(path_new_file, "w+")    
    file_header = open(path, "r")
    new_file.write(file_header.readline())
    new_file.write(file_header.readline())

    #Read the older text file
    file         = np.genfromtxt(path, delimiter=';',skip_header=2)
    row_count    = len(file)
    old_viewshed = file[0]  #temporary variable
    several      = False    #Take in count if a building has several viewsheds
    for i in range(1, row_count):
        new_viewshed = file[i]

        if old_viewshed[0] != new_viewshed[0] and not several:  #This condition means that there is only one viewshed for this building
            new_file.write('{:0.0f};{:0.0f};{:0.0f}'.format(old_viewshed[0], old_viewshed[1], old_viewshed[2]))  #Write the maximum in the text file
            new_file.write("\n")

        if old_viewshed[0] == new_viewshed[0] and not several:  #In this case, we have to find the maximum between two viewsheds for the first time for this building
            position_max = i-1              #Initialize maximum position
            maximum      = old_viewshed[2]  #Initialize maximum value
            several      = True
            if new_viewshed[2] > maximum:   #Change the maximum value and position if the second viewsheds is better
                maximum      = new_viewshed[2]
                position_max = i

        if old_viewshed[0] == new_viewshed[0] and several:  #In this case, we have to find the maximum between two viewsheds of the same building
            if new_viewshed[2] > maximum:
                maximum      = new_viewshed[2]
                position_max = i
                
        if old_viewshed[0] != new_viewshed[0] and several:  #It means that we have a maximum for a building
            several = False
            new_file.write('{:0.0f};{:0.0f};{:0.0f}'.format(file[position_max][0], file[position_max][1], file[position_max][2]))   #Write the maximum in the text file
            new_file.write("\n")
        old_viewshed = new_viewshed

    #After entirely reading the text file, we have write the maximum if the last building have several viewsheds
    if several:
        new_file.write('{:0.0f};{:0.0f};{:0.0f}'.format(file[position_max][0], file[position_max][1], file[position_max][2]))

    #Close the file
    new_file.close()
    
if __name__ == "__main__":
    print("Hello World")
    start1 = time.time()
    
    main(path = "visible_area_viewshed_4732_5519_to_8473.txt", path_new_file = "visible_area_unique_viewshed_4732_5519_to_8473.txt")
    
    done = time.time()
    elapsed = done - start1
    print("Overall process: " + str(elapsed))
        