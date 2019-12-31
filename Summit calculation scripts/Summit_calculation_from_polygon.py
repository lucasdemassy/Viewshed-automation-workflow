# -*- coding: utf-8 -*-
"""
Created on Tue Aug 06 15:19:23 2019

@author: lucas
"""

import os
import rasterio
from rasterio.mask import mask
from rasterio.transform import xy
import numpy as np
from shapely.geometry import Point, mapping
import fiona
import time




def calcSummits(building_path, name_ID_field, raster_path, output_path = "OUTPUT_SUMMITS.shp"):
    """
    This function creates a new shapefile which contains summits of each feature of the building layer.
    The new file has a point geometry and has the ID field given as an input.
    The algorithm crops the input DEM according to each feature and found the highest value
    A feature can have several summits if there are pixels with the same altitude.
    
    Parameters:
        building_path: The path of a polygon shapefile
        name_ID_field: The ID field name of the polygon shapefile
        raster_path: The path of a raster. The polygon file and the raster must overlap 
        output_path: The path of the output point shapefile. The format must be shapefile
    Return:
        String
    """
    start1 = time.time()
    #If the output path already exist, end the script
    if os.path.isfile(output_path):     
        return("The output path already exists")

    #Reading data
    buildings = fiona.open(building_path)
    DEM       = rasterio.open(raster_path)
    
    #Initializing a list to collect summit coordinates and altitude
    all_summits = []

    #For each building
    for building in buildings:

        #Get the DEM masked by the building outline
        #Only pixels with their centre point intersecting the polygon are taken in count 
        DEM_building_value, DEM_building_affine = mask(DEM, [building['geometry']], nodata=-1, crop=True)

        #Calculating the maximum altitude
        max_altitude = np.amax(DEM_building_value)
        
        #-1 means nodata. 
        #So if the maximum equals nodata, it means that the building shape is too small compared to the spatial resolution of pixels
        #Consequently we create a new DEM where each pixel intersecting the polygon are taken in count 
        if max_altitude == -1:
            DEM_building_value, DEM_building_affine = mask(DEM, [building['geometry']], nodata=-1, crop=True, all_touched=True)     
            max_altitude = np.amax(DEM_building_value)
        
        #Getting points with the highest altitude
        summits = np.where(DEM_building_value == max_altitude)
        
        #For each summit
        #Conversion from [row, column] to [x, y]
        #The summit point is located in the centre of the pixel
        #Then, adding the coordinates and the ID of the building in a list
        for i in range(len(summits[1])):
            summit_row, summit_column = summits[1][i], summits[2][i]
            summit_x, summit_y        = xy(DEM_building_affine, summit_row, summit_column) #Center of the pixel
            all_summits.append([summit_x, summit_y, building['properties'][name_ID_field]])

    # Define a point feature geometry with one attribute
    schema = {
        'geometry': 'Point',
        'properties': {name_ID_field : 'int'},
    }
    
    # Write a new Shapefile
    with fiona.open(output_path, 'w', 'ESRI Shapefile', schema) as c:
        for summit in all_summits:
            c.write({
                'geometry': mapping(Point(summit[0], summit[1])),
                'properties': {name_ID_field : summit[2]},
            })
    
    done = time.time()
    elapsed = done - start1
    print("Overall process: " + str(elapsed))



if __name__ == "__main__":
    print("Hello World")
    
    calcSummits("QGIS_Project/Data_shp_Lucas/stavbe_id_autoincremental.shp", "AUTO", "QGIS_Project/Data_shp_Lucas/DEM_BIG_UTM16.tif", output_path= "QGIS_Project/Data_shp_Lucas/Summits_test_time.shp")
    

    