#!/usr/bin/env python

import grass.script as gscript
from grass.pygrass.gis import Mapset
from grass.script import run_command


def main():
    """
    Delete all raster files which the name begin by "vshed"
    """
    gscript.run_command('g.region', flags='p')
    m = Mapset()
    liste_viewshed = m.glist('raster', pattern='vshed*')
    print(liste_viewshed)
    for viewshed_layer in liste_viewshed:
        run_command("g.remove", flags="f", type="raster", name=viewshed_layer)


if __name__ == '__main__':
    main()