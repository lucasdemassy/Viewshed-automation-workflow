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
                       QgsRasterLayer,
                       QgsGeometry,
                       QgsFeature,
                       QgsPointXY,
                       QgsPoint,
                       QgsWkbTypes,
                       QgsField,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFile,
                       QgsProject,
                       QgsVectorFileWriter,
                       QgsProcessingParameterField,
                       QgsMapLayer)
import processing
from qgis.core import QgsProcessingMultiStepFeedback
import os.path
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

    INPUT_AREA = 'INPUT_AREA'
    INPUT_FIELD = 'INPUT_FIELD'
    INPUT_DEM = 'INPUT_DEM'
    OUTPUT_SUMMIT = 'OUTPUT_SUMMIT'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    
    

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
        return 'summitprocess_2'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Summit process using a GDAL tool')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Example scripts')

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
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_DEM, self.tr('Input DEM'), defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_AREA,self.tr('Input area'),[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_SUMMIT, self.tr('Summits in the area of interest (Only gpkg format supported)'), type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterField(self.INPUT_FIELD, self.tr("Unique ID field"), optional=False, type=QgsProcessingParameterField.Any, parentLayerParameterName=self.INPUT_AREA, allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_FOLDER, self.tr("Folder for intermediate results")))

    
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        source_dem    = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        source_area   = self.parameterAsVectorLayer(parameters, self.INPUT_AREA, context)
        source_field  = self.parameterAsFields(parameters, self.INPUT_FIELD, context)
        output_summit = self.parameterAsOutputLayer(parameters, self.OUTPUT_SUMMIT, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        
        #Initializing output variables
        results = {}
        outputs = {}

        feedback.pushInfo('Hello World')
        if not os.path.exists(output_folder):   #If the folder indicated is not existing
            os.makedirs(output_folder)          #Creating the folder
        output_folder = output_folder.replace("\\", "/")
        url_buffer_0  = output_folder + '/building_incremental.shp'
        url_buffer_1  = output_folder + '/polygon_layer.gpkg'
        liste_url     = [url_buffer_0, url_buffer_1]
        for url_buffer in liste_url:    
            if os.path.isfile(url_buffer):  #If one of these url already exist
                os.remove(url_buffer)       #Removing the file at this url
            

        #Zonal statistics
        #Add a field "_max" showing the maximum height in each polygon
        alg_params = {
            'COLUMN_PREFIX': '_',
            'INPUT_RASTER': source_dem,
            'INPUT_VECTOR': source_area,
            'RASTER_BAND': 1,
            'STATS': 6
        }
        outputs['ZonalStatistics'] = processing.run('qgis:zonalstatistics', alg_params, context=context, feedback=feedback)

        
        layer_polygon  = source_area
        features       = layer_polygon.getFeatures()     #Getting the features
        liste_fields   = []                              #Initializing a field list in order to create the output summit fields list
        polygon_lambda = layer_polygon.getFeature(1)     #Getting one feature from the polygon layer
        for i in range(polygon_lambda.fields().size()):  #For each fields
            field_i = polygon_lambda.fields().field(i)
            liste_fields.append([field_i.name(), field_i.typeName()])                 #[Name of the field, Type of the field]
        layer_summit = _create_layer("Point", "32616", liste_fields, "layer_summit")  #Create a new point layer
        summit_ID    = 0                                                              #Initializing the ID summit

        total = 100 / layer_polygon.featureCount()
        for index, polygon in enumerate(features):  #For each polygon in the input polygon layer with the added max field
            feedback.setProgress(int(index * total))

            if feedback.isCanceled():
                return None
            
            #feedback.pushInfo("Index: " + str(index))
            #feedback.pushInfo("Polygon attributes: " + str(polygon.attributes()))
            url_buffer_polygon = output_folder + '/polygon_layer_' + str(index) +'.gpkg'
            if os.path.isfile(url_buffer_polygon):  #If the url already exist
                os.remove(url_buffer_polygon)       #Removing the file at this url
                #feedback.pushInfo("Removing: " + url_buffer)
            layer_polygon.select(polygon.id())
            #feedback.pushInfo("Selected polygon (expect 1): " + str(layer_polygon.selectedFeatureCount())) 
            writer_polygon = QgsVectorFileWriter.writeAsVectorFormat(layer_polygon,url_buffer_polygon,"utf-8", onlySelected=True)
            layer_polygon.deselect(polygon.id())
            
            
            #GDAL clip
            #Clip raster by mask layer
            #Clip the DEM according to the shape of the polygon
            alg_params = {
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'DATA_TYPE': 0,
                'INPUT': source_dem,
                'KEEP_RESOLUTION': False,
                'MASK': url_buffer_polygon,
                'OUTPUT': output_folder + "/clip_dem_" + str(index) + ".tif"
            }
            outputs['ClipRasterByMaskLayer'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback)
            
            rlayer               = QgsRasterLayer(outputs['ClipRasterByMaskLayer']['OUTPUT'], "raster_layer") #Create a raster layer on the output of the previous processing
            step_X               = rlayer.rasterUnitsPerPixelX()                                        #Getting X resolution
            step_Y               = rlayer.rasterUnitsPerPixelY()                                        #Getting Y resolution
            extent_string        = rlayer.dataProvider().extent().toString()                            #"xmin,ymin : xmax,ymax"
            extent_split         = extent_string.split(":")                                             #["xmin,ymin" , "xmax,ymax"]
            extent_string_origin = extent_split[0].split(",")                                           #["xmin", "ymin"]
            extent_string_final  = extent_split[1].split(",")                                           #["xmax", "ymax"]
            origin               = [float(extent_string_origin[0]), float(extent_string_origin[1])]     #[xmin, ymin]
            final                = [float(extent_string_final[0]), float(extent_string_final[1])]       #[xmax, ymax]
                                                                              
            for x in np.arange(origin[0]+(step_X/2), final[0]+step_X, step_X):
                for y in np.arange(origin[1]+(step_Y/2), final[1]+step_Y, step_Y):
                    value, boolean = rlayer.dataProvider().sample(QgsPointXY(x,y), 1)   #the second parameter indicates the band number
                    if value == polygon.attribute("_max"):                              #If the algorithm has found one of the peak
                        feature    = QgsFeature(layer_summit.fields(), summit_ID)       #Creating a QgsFeature object with the summit ID and has the summit layer fields
                        #feedback.pushInfo("Validity feature :" + str(feature.isValid()))
                        #feedback.pushInfo("Feature fields: " + str(feature.fields().toList()))
                        summit_ID += 1                                       #Incrementing the summit ID
                        feature.setGeometry(QgsPoint(x,y))                   #Set the geometry of the QgsFeature object
                        #feedback.pushInfo("Feature geometry: " + str(feature.geometry()))
                        feature.setAttributes(polygon.attributes())          #Set the attributes of the QgsFeature object
                        #feedback.pushInfo("Feature attributes: " + str(feature.attributes()))
                        feature.deleteAttribute("_max")
                        layer_summit.startEditing()                          #Enabling edition
                        layer_summit.dataProvider().addFeatures([feature])   #Adding summits of the current polygon
                        layer_summit.commitChanges()                         #Commiting the changes
        # Drop field(s)
        alg_params = {
            'COLUMN': "_max",
            'INPUT': layer_summit,
            'OUTPUT': output_summit
        }
        outputs['DropFields'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        results['OUTPUT_SUMMIT'] = output_summit        
        return results



def _create_layer(geometry_type, srid, fields, title):
        """
        Creates an empty memory layer
        :param geometry_type: 'Point', 'LineString', 'Polygon', etc.
        :param srid: CRS ID of the layer
        :param fields: list of (field_name, field_type, length, precision)
        :param title: title of the layer
        """
        string_field = ''
        for i in range(len(fields)):
            if str(fields[i][1]) == "Integer64":
                fields[i][1] = "integer"
            if str(fields[i][1]) == "Real":
                fields[i][1] = "double"
            string_field += "&field=" + str(fields[i][0]) + ":" + str(fields[i][1])   
        layer = QgsVectorLayer(geometry_type + "?crs=EPSG:" + srid + string_field, title, "memory")
        return layer 

