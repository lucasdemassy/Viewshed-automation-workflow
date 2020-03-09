# Cumulative viewsheds creator - a QGIS plugin

**All viewsheds must be in an unique folder without any other kind of file**

This QGIS plugin creates a cumulative viewshed which is a merge of ﬁelds of view of input observation points.  
This tool is also very useful to manage and visualize viewsheds when you have a lot of observation points.

This cumulative viewshed is sightly diﬀerent than a previous viewsheds because his values range between 0 and the number of input observation points and mean how many observation points can see the target pixel.

A plugin use example is to select some observation points, then [run the QGIS plugin](../images/QGIS_Tuto_text.PNG). The checkbox `Selected features only` is very useful and should always be checked to avoid computing all viewsheds of a region

![Plugin_QGIS](../images/pluginQGIS.png)
<center>
  <u>The plugin interface</u>
</center>
