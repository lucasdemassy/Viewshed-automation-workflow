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
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFile,
                       QgsProject,
                       QgsVectorFileWriter,
                       QgsProcessingParameterField,
                       QgsMapLayer)
import processing
from qgis.core import QgsProcessingMultiStepFeedback
import os.path


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

    INPUT_POINTS   = 'INPUT_POINTS'
    INPUT_FIELD    = 'INPUT_FIELD'
    INPUT_DEM      = 'INPUT_DEM'
    INPUT_DISTANCE = 'INPUT_DISTANCE'
    OUTPUT_SUMMIT  = 'OUTPUT_SUMMIT'
    OUTPUT_FOLDER  = 'OUTPUT_FOLDER'
    
    

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
        return 'localsummitprocess'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Local summit process around points')

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

        self.addParameter(QgsProcessingParameterDistance(self.INPUT_DISTANCE, self.tr('Distance of the buffer')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_DEM, self.tr('Input DEM'), defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_POINTS,self.tr('Input points'),[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_SUMMIT, self.tr('Local summits near the points of interest'), type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterField(self.INPUT_FIELD, self.tr("Unique ID field"), optional=True, type=QgsProcessingParameterField.Any, parentLayerParameterName=self.INPUT_POINTS, allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_FOLDER, self.tr("Folder for intermediate results")))

    
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        source_distance = self.parameterAsDouble(parameters, self.INPUT_DISTANCE, context)
        source_dem      = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        source_points   = self.parameterAsVectorLayer(parameters, self.INPUT_POINTS, context)
        source_field    = self.parameterAsFields(parameters, self.INPUT_FIELD, context)
        output_summit   = self.parameterAsOutputLayer(parameters, self.OUTPUT_SUMMIT, context)
        output_folder   = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        
        
        results = {}
        outputs = {}
        #feedback = QgsProcessingMultiStepFeedback(3, feedback)
        feedback.pushInfo('Hello World')
        if not os.path.exists(output_folder):   #If the folder indicated is not existing
            os.makedirs(output_folder)          #Creating the folder
        url_buffer_1 = output_folder + '/buffer.shp'
        url_buffer_2 = output_folder + '/buffer_overlaping.shp'
        url_buffer_3 = output_folder + '/buffer_overlaping_summit.shp'
        url_buffer_4 = output_folder + '/buffer_AUTO.shp'
        url_buffer_5 = output_folder + '/points_incremented.shp'
        url_buffer_6 = output_folder + '/summit_process_all.gpkg'
        liste_url = [url_buffer_1, url_buffer_2, url_buffer_3, url_buffer_4, url_buffer_5, url_buffer_6]
        for url_buffer in liste_url:
            if os.path.isfile(url_buffer):  #If one of these url already exist
                os.remove(url_buffer)       #Removing the file at this url
                feedback.pushInfo("Removing: " + url_buffer)
        
        if source_field == []:
            feedback.pushInfo("Adding auto-incremental field to the point layer")
            # Add autoincremental field
            alg_params = {
                'FIELD_NAME': 'ID_Point',
                'GROUP_FIELDS': None,
                'INPUT': source_points,
                'SORT_ASCENDING': True,
                'SORT_EXPRESSION': '',
                'SORT_NULLS_FIRST': False,
                'START': 0,
                'OUTPUT': url_buffer_5
            }
            outputs['AddAutoincrementalField_start'] = processing.run('native:addautoincrementalfield', alg_params, context=context, feedback=feedback)
            source_field = ['ID_Point']
            source_points = outputs['AddAutoincrementalField_start']['OUTPUT']

        # Buffer
        #Buffer polygons have the same attributes as the points
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': source_distance,
            'END_CAP_STYLE': 0,
            'INPUT': source_points,
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': url_buffer_1
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback)

        # Summit process
        alg_params = {
            'INPUT_AREA': outputs['Buffer']['OUTPUT'],
            'INPUT_DEM': source_dem,
            'INPUT_FIELD': source_field[0],
            'OUTPUT_SUMMIT': url_buffer_6,
            'OUTPUT_FOLDER': output_folder + '/Summit_computing_all'
        }
        outputs['SummitProcess'] = processing.run('script:summitprocess_2', alg_params, context=context, feedback=feedback)

        # Extract by location: buffers overlaping between themselves
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'INTERSECT': outputs['Buffer']['OUTPUT'],
            'PREDICATE': 5,
            'OUTPUT': url_buffer_2
        }
        outputs['ExtractByLocation_1'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback)

        if feedback.isCanceled():
            return None

        # Extract by location: summits which are in a buffer intersecting another buffer polygon
        alg_params = {
            'INPUT': outputs['SummitProcess']['OUTPUT_SUMMIT'],
            'INTERSECT': outputs['ExtractByLocation_1']['OUTPUT'],
            'PREDICATE': 0,
            'OUTPUT': url_buffer_3
        }
        outputs['ExtractByLocation_2'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback)

        if feedback.isCanceled():
            return None
       
        ###Deletion from the overall summit layer, of summits which are in a buffer intersecting another buffer polygon
        layer_all_summit    = QgsVectorLayer(outputs['SummitProcess']['OUTPUT_SUMMIT'], "layer_all_summit", "ogr") #Create as a vector layer, a layer gathering all the summits
        layer_1             = QgsVectorLayer(outputs['ExtractByLocation_2']['OUTPUT'], "layer_1", "ogr")           #Create as a vector layer, a layer of the summits which may intersect multiples buffers
        features_all_summit = layer_all_summit.getFeatures()    #Getting the features
        features_1          = layer_1.getFeatures()             #Getting the features
        liste_suppress      = []                                #Initializing a list which will keep in memory the summits whiwh will be deleted
        fid_max             = layer_all_summit.featureCount()   #Get the number of summit. This value will be used to set the next summits id
        for index_all_summit, summit_all in enumerate(features_all_summit):     #Iterating over all summits
            layer_summit_buffer_chevauche = QgsVectorLayer(outputs['ExtractByLocation_2']['OUTPUT'], "layer_summit_buffer_chevauche", "ogr")    #Create as a vector layer, a layer
            features_summit_buffer_chevauche = layer_summit_buffer_chevauche.getFeatures()  #Getting the features
            for index_summit_buffer_chevauche, summit_buffer_chevauche in enumerate(features_summit_buffer_chevauche):  #Iterating over summits which are in a contentious buffer
                if summit_all.attributes() == summit_buffer_chevauche.attributes():     #if the contentious summit is in the overall summit layer
                    liste_suppress.append(summit_all.id())      #Add the summit to the suppress list
        feedback.pushInfo("Deletion of summits which intersect at least two buffers")
        layer_all_summit.startEditing()                             #Enabling edition
        layer_all_summit.deleteFeatures(liste_suppress)             #Deleting contentious summits of the overall summit layer
        layer_all_summit.commitChanges()                            #Commiting the changes
        feedback.pushInfo(str(layer_all_summit.commitErrors()))     #Displaying a message about the state of the commit

        

        
        total = 100 / layer_1.featureCount()        #Initializing the progress bar
        for index_1, summit_1 in enumerate(features_1):     #Iterating over contentious summits
            feedback.setProgress(int(index_1 * total))      #Update the progress bar
            layer_2    = QgsVectorLayer(outputs['ExtractByLocation_2']['OUTPUT'], "layer_2", "ogr")    #Create as a vector layer, the contentious summits
            features_2 = layer_2.getFeatures()              #Getting features
            for index_2, summit_2 in enumerate(features_2): #Iterating over contentious summits. These two loops allows to compare summits in the same layer
                summit_1_geometry = summit_1.geometry().asPoint()   #Getting the geometry of the summit number 1
                summit_2_geometry = summit_2.geometry().asPoint()   #Getting the geometry of the summit number 2
                if summit_1_geometry.toString() == summit_2_geometry.toString():    #If they have the same geometry (may be optimised by using the function equals())
                    ID_point_summit_1 = summit_1.attribute(source_field[0]) #Getting the ID of the buffer polygon of the summit number 1
                    ID_point_summit_2 = summit_2.attribute(source_field[0]) #Getting the ID of the buffer polygon of the summit number 2
                    if ID_point_summit_1 != ID_point_summit_2:              #If the two points don't come from the same buffer polygon
                        features_source_points = source_points.getFeatures()
                        for indx, points_source in enumerate(features_source_points):       #Searching in the point layer given by the user, the two current points
                            if points_source.attribute(source_field[0]) == ID_point_summit_1:
                                point_summit_1 = points_source                              #Getting the point which was be used to create the buffer polygon of the summit number 1
                            if points_source.attribute(source_field[0]) == ID_point_summit_2:
                                point_summit_2 = points_source                              #Getting the point which was be used to create the buffer polygon of the summit number 2
                        
                        #Calculating the minimal distance between the two original points and the summit
                        distance_min = m.sqrt(m.pow(point_summit_1.geometry().asPoint().x() - summit_1_geometry.x(), 2) + m.pow(point_summit_1.geometry().asPoint().y() - summit_1_geometry.y(), 2))
                        distance     = m.sqrt(m.pow(point_summit_2.geometry().asPoint().x() - summit_1_geometry.x(), 2) + m.pow(point_summit_2.geometry().asPoint().y() - summit_1_geometry.y(), 2))
                        if distance < distance_min:
                            distance_min = distance
                        

                        layer_2_copy    = QgsVectorLayer(outputs['ExtractByLocation_2']['OUTPUT'], "layer_2", "ogr")   #Create as a layer, the contentious summits in order to update the ID
                        features_2_copy = layer_2_copy.getFeatures()                           #Getting features
                        for index_2_copy, summit_2_copy in enumerate(features_2_copy):         #Iterating over the contentious summits
                            if str(summit_2_copy.attributes()) == str(summit_1.attributes()):  #Retrieving the summit number 1 in this layer in order to have the right ID
                                summit_1_in_layer_2 = summit_2_copy
                        feedback.pushInfo("Minimal distance: "+ str(distance_min))
                        feedback.pushInfo("Deleting: " + str(layer_2.getFeature(summit_2.id()).attributes()) + " and " + str(layer_2.getFeature(summit_1_in_layer_2.id()).attributes()))
                        layer_2.startEditing()                                              #Enabling edition mode
                        layer_2.deleteFeatures([summit_2.id(), summit_1_in_layer_2.id()])   #Deleting the two summits which have the same geometry
                        layer_2.commitChanges()                                             #Commiting changes
                        feedback.pushInfo(str(layer_2.commitErrors()))                      #Displaying a message about the commit state
                        
                        #Creating a temporary layer
                        liste_fields = []   #Initializing a field list in order to create the summit fields list
                        for i in range(summit_1.fields().size()):   #For each fields
                            field_i = summit_1.fields().field(i)    
                            liste_fields.append([field_i.name(), field_i.typeName()])   #[Name of the field, Type of the field]
                        new_layer = _create_layer("Point", "32616", liste_fields, "layer_2_points") #Create a new point layer
                        new_layer.startEditing()                                                #Enabling edition mode
                        point_summit_1.setAttributes([1] + point_summit_1.attributes())         #Setting the attributes in order to match to a new field "fid" added when the temporary layer was created
                        point_summit_2.setAttributes([2] + point_summit_2.attributes())         #Setting the attributes in order to match to a new field "fid" added when the temporary layer was created
                        new_layer.dataProvider().addFeatures([point_summit_1, point_summit_2])  #Adding the two summits which have the same geometry
                        new_layer.commitChanges()                                               #Commiting changes

                        #Setting a new folder to save intermediate files for each time when two summits have the same geometry
                        new_folder_string = output_folder + '/Summit_computing_buffer_' + str(ID_point_summit_1) + "_" + str(ID_point_summit_2)
                        if not os.path.exists(new_folder_string):   #If the folder indicated is not existing
                            os.makedirs(new_folder_string)          #Creating the folder
                        url_buffer_7 = new_folder_string + '/buffer_2_points.shp'
                        url_buffer_8 = new_folder_string + '/buffer_2_points_without_fid.shp'
                        liste_url = [url_buffer_7, url_buffer_8]
                        for url_buffer in liste_url:    
                            if os.path.isfile(url_buffer):  #If one of these url already exist
                                os.remove(url_buffer)       #Removing the file at this url

                        #Creating new buffer around the two original points which have their summits identical, but this time with a smaller distance
                        # Buffer
                        alg_params = {
                            'DISSOLVE': False,
                            'DISTANCE': distance_min,
                            'END_CAP_STYLE': 0,
                            'INPUT': new_layer,
                            'JOIN_STYLE': 0,
                            'MITER_LIMIT': 2,
                            'SEGMENTS': 5,
                            'OUTPUT': new_folder_string + '/buffer_2_points.shp'
                        }
                        outputs['Buffer_2_points'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback)
                        
                        #The "fid" field must be removed
                        # Drop field(s)
                        alg_params = {
                            'COLUMN': "fid",
                            'INPUT': outputs['Buffer_2_points']['OUTPUT'],
                            'OUTPUT': new_folder_string + '/buffer_2_points_without_fid.shp'
                        }
                        outputs['DropFields'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

                        if feedback.isCanceled():
                            return None

                        #Calculating summits in this new area
                        # Summit process
                        alg_params = {
                            'INPUT_AREA': outputs['DropFields']['OUTPUT'],
                            'INPUT_DEM': source_dem,
                            'INPUT_FIELD': source_field[0],
                            'OUTPUT_SUMMIT': new_folder_string + '/layer_2_points.gpkg',
                            'OUTPUT_FOLDER': new_folder_string
                        }
                        outputs['SummitProcess_2_points'] = processing.run('script:summitprocess_2', alg_params, context=context, feedback=feedback)

                        if feedback.isCanceled():
                            return None
                        
                        layer_2_points = QgsVectorLayer(outputs['SummitProcess_2_points']['OUTPUT_SUMMIT'], "layer_2_points", "ogr")    #Create as a vector layer, the new summits which they were identical 
                        features_2_points = layer_2_points.getFeatures()        #Getting features
                        for indx, new_summit in enumerate(features_2_points):   #For each new summit
                            layer_1.startEditing()                              #Enabling edition mode
                            layer_1.dataProvider().addFeatures([new_summit])    #Add the new summit to the contentious summit layer
                            layer_1.commitChanges()                             #Commiting changes
                            

                        
                       
        layer_output_summit = QgsVectorLayer(url_buffer_6, "layer_output_summit", "ogr")    #Create as a vector layer, the output layer
        features_2 = layer_2.getFeatures()              #Getting former contentious summits features
        for indx, summit_2 in enumerate(features_2):    #For each former contentious summits
            layer_output_summit.startEditing()          #Enabling edition mode
            summit_2.setAttributes([fid_max + indx] + summit_2.attributes()[1:])    #Setting the attributes in order to give a fid value than isn't already exist
            layer_output_summit.dataProvider().addFeatures([summit_2])              #Add the former contentious summit to the output summit layer
            layer_output_summit.commitChanges()                                     #Commiting changes
            feedback.pushInfo("Point added to the output layer " + str(summit_2.attributes()))
        layer_output_summit.endEditCommand()
        writer = QgsVectorFileWriter.writeAsVectorFormat(layer_output_summit,output_summit,"utf-8") #Saving the output layer in a vector layer at the path given by the user
        
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