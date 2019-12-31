import sys

import os

import atexit



from grass.script import parser, run_command
from grass.pygrass.gis import Mapset



def cleanup():

    pass



def main():
    m1 = Mapset() #Getting data tree
    liste_viewshed = m1.glist('raster', pattern='vshed*') #Getting all viewshed created

    for map in liste_viewshed:
        output_string = 'C:\\Users\\lucas\\Documents\\Ljubljana\\OUTPUT_VIEWSHED_3635_to_4287\\' + map + ".tif"

        run_command("r.out.gdal",

                    input = map,

                    output = output_string,

                    format = "GTiff",

                    overviews = 0)







    return 0



if __name__ == "__main__":

    options, flags = parser()

    atexit.register(cleanup)

    sys.exit(main())

