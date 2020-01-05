These two scripts save in text files the value 1 occurence for each viewshed.
This value is an indicator of the visible amount for a building.
The first script `Visible_area_file_creation.py` saves values for all viewsheds.
However a building can have several summits and so several viewsheds. 
We can't simply sum the value 1 occurence, we have to take the best viewshed for each building.
The best viewshed of a building is considered as the one with the best visibility and so the bigger value 1 occurence.
The second script `Visible_unique_area_file_creation.py` creates a text file from the one returned by the first script and keeps only maximum for each building.

Consequently, the user must excute in the order:
1. First, the `Visible_area_file_creation.py` file
2. Then, `Visible_unique_area_file_creation.py`