#!/usr/bin/env python

############################################################################
#
# MODULE:       g.exportgtiff
#
# AUTHOR(S):    BRES Lucas <lucas.bres96 gmail.com>
#
# PURPOSE:      Export all raster files as gtiff which the name begin by "vshed"
#
# COPYRIGHT:    (C) 2020 by Bres Lucas
#
#               This program is free software under the GNU General
#               Public License (>=v2). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################

#%module
#% label:  Export all raster files as tiff which the name begin by "vshed".
#% description: By default only extensions built against different GIS Library are rebuilt.
#% keyword: gtiff
#% keyword: export
#%end

#%option G_OPT_M_DIR
#% key: output
#% description: outputh path
#%end

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
        output_string = options["output"] + "\\" + map + ".tif"

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

