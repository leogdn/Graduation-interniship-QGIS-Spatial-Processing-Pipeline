"""
QGIS Spatial Processing Pipeline

This module provides utilities for:

- Zonal histogram computation
- Buffer analysis
- Precision / Recall / F1-score evaluation
- Polygon-based statistical analysis
- Automatic valid polygon detection

Author
------
Léonard Gaudin - Toulouse INP-ENSEEIHT - CESBIO

Dependencies
------------
- QGIS / PyQGIS
- geopandas
- pandas
- numpy
- tqdm
"""

import sys
import importlib

import functions
importlib.reload(functions)

folder_list = ["path/to/working/directory"]
raster_names = ["raster_name"]
raster_paths = ["path/to/raster.vrt"]
output_files = ["./outputs/"]
threshold = 0.75  # Detection threshold

layers_list = functions.create_layers_from_folders(
    folder_list, layer, raster_names, raster_paths, output_files, threshold)

distances = range(5, 1000, 5)  # List of buffer sizes to evaluate (5m, 10m, ..., 1000m)
mode = "local" # "local" for local processing (one folder at a time), "global" for global processing (all folders together)
poly_list = [] # List of valid polygons to use for evaluation (if empty, all polygons in the layer will be used)
detection_polys = True # Detect valid polygons in each folder and process them separately (True) or process all folders together without polygon detection (False)
detection_threshold = 0.0 # Convergence threshold for valid polygon detection (if detection_polys is True)

if not detection_polys :
    functions.process_folders(
    mode=mode,
    detection_polys=False,
    folder_list=folder_list,
    raster_names=raster_names,
    raster_paths=raster_paths,
    output_file=results_folder,
    layers_list=layers_list,
    poly_list=poly_list,
    distances=distances,
    detection_threshold=detection_threshold
    )
else:
    for folder_index in range(len(folder_list)):
        folder = [folder_list[folder_index]]
        raster_name = [raster_names[folder_index]]
        raster_path = [raster_paths[folder_index]]
        layer = [layers_list[folder_index]]
        functions.process_folders(
        mode=mode,
        detection_polys=True,
        folder_list=folder,
        raster_names=raster_name,
        raster_paths=raster_path,
        output_file=results_folder,
        layers_list=layer,
        poly_list=poly_list,
        distances=distances,
        detection_threshold=detection_threshold
        )