# GRASS GIS scripts to easily handle big amount of files


## 1. g.exportgtiff command
### Installation
**You must change the path present in the `g.exportgtiff.bat` file.** <br>

- **For Windows environment**, If you have let the default parameter during the OSGeo or QGIS installation:

    - Put the `g.exportgtiff.bat` file in the folder `C:\OSGeo4W64\apps\grass\grass76\bin`
    - Put the `g.exportgtiff.py` file in the folder `C:\OSGeo4W64\apps\grass\grass76\scripts`
- Otherwise, you can put these files in their respective folder where you GRASS GIS is installed.


### Use a script in GRASS GIS

This command exports every viewshed files into GeoTIFF format.

We suppose here that viewshed raster files have their name beginning by `vshed`

If you have well installed the script, you can simply use the command in the GRASS shell.

Example :
`g.exportgtiff --ui`
## 2. g.deletevshed script
The user must launch the python script in order to use this command.

![launch script](../images/GRASS_script.png)
