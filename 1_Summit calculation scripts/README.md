This step calculates observation points of buildings thanks to a DTM and a vector layer of buildings (point or/and polygon geometries).
If you already have observation points, this step isn't necessary.
1. For a building polygon layer : Use the `Summit_calculation_from_polygon.py` script. You must install rasterio, fiona and shapely libraries, because this algorithm uses them (They can be easily installed thanks to anaconda) 
2. For a building point layer : Import the other two scripts in QGIS and use the `Local_summit_computing.py` QGIS plugin named "Local summit process around points" in the QGIS toolbox.
