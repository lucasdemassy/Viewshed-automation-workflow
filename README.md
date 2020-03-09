##  <img src="/images/Viewshed_example.png" alt="Viewshed" width="80"/> Viewshed automation workflow


This repository contains multiple python scripts to automatize viewsheds creation from buildings thanks to a DTM (Digital Terrain Model) and a vector layer (point or polygon) of these buildings.

The workflow is divided into several steps :
1. [Observation points calculation](1_Summit calculation scripts/)
2. *(optional)* GRASS files management
3. *(optional)* Organizing viewshed files
4. QGIS plugin for viewshed visualization
5. *(optional)* Analysing statistically viewsheds

![Viewshed_workflow](images/Viewshed_workflow_transparent.png)

A majority of scripts require QGIS or GRASS GIS, both available at this link: https://www.qgis.org/en/site/forusers/download.html

I achieved this work during the 2019 internship summer at the Research Centre of the Slovenian Academy of Sciences and Arts ([ZRC-SAZU](https://iaps.zrc-sazu.si/)). The observation points creation process is designed for buildings in mind. User can adjust it for other purposes.

**Documentation about the project is in the PDF document**. It contains further explanation about how to use scripts, how they work and the overall viewshed analysis made for the ZRC-SAZU on the area around a Mayan city.

Please contact me if you have any questions at the following address: lucas.bres96@gmail.com
