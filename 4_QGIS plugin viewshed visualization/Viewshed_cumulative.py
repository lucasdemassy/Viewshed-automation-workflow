# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import math as m
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsVectorLayer,
                       QgsVectorLayerJoinInfo,
                       QgsGeometry,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFile,
                       QgsProject,
                       QgsRasterLayer,
                       QgsVectorFileWriter,
                       QgsProcessingParameterField,
                       QgsMapLayer)
from qgis.gui import QgisInterface
import processing
from qgis.core import QgsProcessingMultiStepFeedback
import os.path
import rasterio
from shutil import copy2
import numpy as np

class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_SUMMITS              = 'INPUT_SUMMITS'
    INPUT_FOLDER               = 'INPUT_FOLDER'
    INPUT_FIELD                = 'INPUT_FIELD'
    OUTPUT_CUMULATIVE_VIEWSHED = 'OUTPUT_CUMULATIVE_VIEWSHED'    
    
    

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'cumulativeviewshed'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Cumulative viewshed creation')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Custom scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Beforehand, select points in the input observation point layer, and check the box 'selected features only'. \n All viewsheds must be in a single folder.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm
        """
        current_work_folder = QgsProject().instance().fileName()[:-(len(QgsProject().instance().baseName())+4)]
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_SUMMITS,self.tr('Input observation points'),[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFile(self.INPUT_FOLDER, self.tr("Folder containing all the viewshed files"), behavior=1))
        self.addParameter(QgsProcessingParameterField(self.INPUT_FIELD, self.tr("Unique ID field"),
            type=QgsProcessingParameterField.Any,
            parentLayerParameterName=self.INPUT_SUMMITS, 
            allowMultiple=False, 
            defaultValue=None))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_CUMULATIVE_VIEWSHED, 
            self.tr("Output cumulative viewshed"), 
            defaultValue=current_work_folder+"cumulative.tif"))
        

    
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        This algorithm displays viewsheds according to the ID of input observation points.
        It also returns a cumulative viewshed of the previous fields of view selected.
        All viewshed files must be in one directory without anything else (even a folder)
        """
        
        #Getting values given by the user
        source_summits             = self.parameterAsSource(parameters, self.INPUT_SUMMITS, context)
        source_folder              = self.parameterAsString(parameters, self.INPUT_FOLDER, context)
        source_field               = self.parameterAsFields(parameters, self.INPUT_FIELD, context)
        output_cumulative_viewshed = self.parameterAsString(parameters, self.OUTPUT_CUMULATIVE_VIEWSHED, context)
        
        #Initializing the String output
        results = {}
        
        feedback.pushInfo('Hello World')

        #Get the viewshed files
        files = os.listdir(source_folder)
        #Get the features from summits
        summits = source_summits.getFeatures()
        #Initializing a ID list of the selected summits
        liste_ID = []
        #Get the ID of all summits
        feedback.pushInfo("ID summit to check :")
        for index, summit in enumerate(summits):
            liste_ID.append('{:0.0f}'.format(summit.attribute(source_field[0])))
            feedback.pushInfo("  " + '{:0.0f}'.format(summit.attribute(source_field[0])))
            
        #Opening the first viewshed file as array
        sum_raster = rasterio.open(source_folder + '/' + files[0])
        
        #Boolean to check if the first file has been read
        first_file = True

        #List of viewshed displayed at the end of the script
        raster_list = []

        #For each viewshed file
        for viewshed_file in files:
            viewshed_file_split = viewshed_file.split("_")
            #If the name of the viewshed is matching the ID summit
            if viewshed_file_split[1] in liste_ID:
                entire_path = source_folder + '/' + viewshed_file
                #Get the ID viewshed
                layer_name = viewshed_file[:-4]
                #Open the viewshed in QGIS format
                rlayer = QgsRasterLayer(entire_path, layer_name, 'gdal')
                if not rlayer.isValid():
                    feedback.pushInfo("Layer failed to load!")
                else:
                    feedback.pushInfo("Adding " + entire_path)
                    #Adding the viewshed to the display list
                    raster_list.append(rlayer)
                    results[layer_name] = entire_path       
                    #Open the viewshed as array
                    raster_layer = rasterio.open(entire_path)
                    #If it's the first viewshed matching the ID summit
                    if first_file:
                        band1 = raster_layer.read(1)
                        first_file = False
                    else:
                        band1 += raster_layer.read(1)
                    raster_layer.close()
        
        if first_file == False:
            #Create a cumulative raster
            cumulative_raster = rasterio.open(output_cumulative_viewshed, 
            'w', 
            driver='GTiff', 
            height=band1.shape[0],
            width=band1.shape[1],
            count=1,
            dtype=band1.dtype,
            crs=sum_raster.crs,
            transform=sum_raster.transform,)
            cumulative_raster.write(band1,1)
            cumulative_raster.close()
            sum_raster.close()
            
            
            results[str(output_cumulative_viewshed[:-4])] = str(output_cumulative_viewshed)
            #Open the viewshed in QGIS format
            rlayer = QgsRasterLayer(str(output_cumulative_viewshed), str(output_cumulative_viewshed[:-4]), 'gdal')
            if not rlayer.isValid():
                feedback.pushInfo("Layer failed to load!")
            else:
                raster_list.insert(0,rlayer)
            
            #Display viewsheds and the cumulative one 
            QgsProject.instance().addMapLayers(raster_list)
            
            return results
        else:
            feedback.pushInfo("No viewshed file related to any input points")



    
    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading