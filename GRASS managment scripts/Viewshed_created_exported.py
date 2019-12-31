#!/usr/bin/env python

import grass.script as gscript

from grass.pygrass.gis import Mapset

from grass.script import run_command
import os




def main(): 
        #gscript.run_command('g.region', flags='p')  #Display the current region in the console
        m0 = Mapset()   #Getting data tree
        liste_DEM = m0.glist('raster', pattern='DEM_UTM_*') #Getting all the different DEM
        ### Viewshed creation
        for DEM_layer in liste_DEM: #iterating over all the DEM
            UTM_name = DEM_layer[-7:]   #Getting the UTM name
            #print("Salut je change l'emprise de la region")
            #Setting the region to the current DEM layer
            run_command('g.region',
                raster=DEM_layer,
                res=5)
            gscript.run_command('g.region', flags='p')  #Display the current region in the console
            #Creating the viewshed of all summit
            run_command("r.viewshed.cva", 
                flags="krcb", 
                verbose=True,
                input=DEM_layer, 
                vector= "Summit_" + UTM_name, 
                output="viewshed" + UTM_name, 
                observer_elevation=2, 
                target_elevation=0, 
                memory=10000,
                max_distance=50000, 
                name_column="ID_summit")

            m1 = Mapset() #Getting data tree
            liste_viewshed = m1.glist('raster', pattern='vshed*') #Getting all viewshed created

            for viewshed_layer in liste_viewshed:   #Iterating over viewsheds newly created
                ### Viewshed renaming in order to avoid overwrite issue
                new_name = UTM_name + "_" + viewshed_layer #New name
                #Renaming viewsheds
                run_command("g.rename", rast=[viewshed_layer,new_name])
        
        ### Merging viewshed of same summit    
        m2 = Mapset() #Getting data tree
        liste_total_viewshed = m2.glist('raster', pattern="UTM*") #Getting all viewshed of each area
        liste_total_viewshed_copie = liste_total_viewshed #Creating a copy of this previous list in order to iterate between all viewsheds
        for viewshed_layer_1 in liste_total_viewshed:   #Iterating over viewsheds
            liste_patch = [viewshed_layer_1]    #Creating a list that contains viewsheds of the same summit
            viewshed_id_summit_1 = viewshed_layer_1.split('_')[4] #Getting the summit ID
            for viewshed_layer_2 in liste_total_viewshed_copie: #iterating over viewsheds that have not been merged yet
                viewshed_id_summit_2 = viewshed_layer_2.split('_')[4] #Getting the summit ID
                if viewshed_id_summit_1 == viewshed_id_summit_2:    #If the ID are the same
                    liste_patch.append(viewshed_layer_2)    #Putting the viewshed of the same summit in the patching list
                    liste_total_viewshed_copie.pop(liste_total_viewshed_copie.index(viewshed_layer_2)) #Removing this previous viewshed of the list in order to keep only those which don't have been merged yet
                #Merging viewsheds of a same summit in order to make 
                run_command("r.patch", input=liste_patch, output="cumulative" + viewshed_id_summit_1, overwrite = True)
        
        
        directory = 'C:\\Users\\lucas\\Documents\\Ljubljana\\Viewshed_OUTPUT' #Setting the output directory
        if not os.path.exists(directory): #If the directory doesn't exist
            os.makedirs(directory)  #Creating a new directory

        m3 = Mapset() #Getting data tree
        liste_cumulative_viewshed = m3.glist('raster', pattern="cumulative*") #Getting cumulative viewsheds
        for cumulative_viewshed_layer in liste_cumulative_viewshed: #Iterating over cumulative viewsheds
                output_string = directory + '\\' + cumulative_viewshed_layer + ".tif" #Setting output name file
                ### Cumulative viewshed export
                run_command("r.out.gdal",
                    input = cumulative_viewshed_layer,
                    output = output_string,
                    format = "GTiff",
                    overviews = 0)
                """    
                ### Viewshed cleaning
                run_command("g.remove", 
                    flags="f", 
                    type="raster", 
                    name=viewshed_layer)
                """
        return 0



    
    


if __name__ == '__main__':
    main()
