#!/usr/bin/env python

import grass.script as gscript
from grass.pygrass.gis import Mapset
from grass.script import run_command


def main():
    gscript.run_command('g.region', flags='p')
    m = Mapset()
    liste_viewshed = m.glist('raster', pattern='vshed*')
    print(liste_viewshed)
    for viewshed_layer in liste_viewshed:
        #viewshed_layer_name = viewshed_layer + "@PERMANENT"
        run_command("g.remove", flags="f", type="raster", name=viewshed_layer)


if __name__ == '__main__':
    main()
