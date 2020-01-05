The GRASS viewshed creation process takes a lot of time.
Consequently, an user is likely to divide the viewshed creation in different parts and compute them one after the other.
However, viewshed file names might be inconsistant especially the ID summit part which is auto-incremented.
The following file `rename_file.py` remedies this issue by renaming all files beginning by "vshed".
The GRASS process returns viewsheds and calls them by "vshed_ID-building_ID-summit".
The python script renames viewshed by sorting the ID building and then set the auto-incremented ID summit.