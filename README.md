# QGIS Spatial Processing Pipeline

A comprehensive Python-based spatial processing pipeline for remote sensing analysis using QGIS/PyQGIS. This project performs zonal histogram computation, buffer analysis, and accuracy metrics evaluation on raster and vector data.

## Overview

This pipeline is designed for evaluating the accuracy of geospatial detection and detection results by:
- Computing zonal statistics (histograms) for polygons
- Filtering valid polygons based on detection thresholds
- Performing buffer analysis for spatial relationships
- Calculating precision, recall, and F1-score metrics
- Automating batch processing for multiple datasets

**Project Type:** Graduation Internship  
**Institution:** Toulouse INP-ENSEEIHT  
**Organization:** CESBIO (Centre d'Études Spatiales de la Biosphère)  
**Author:** Léonard Gaudin [(leonard.gaudin@etu.toulouse-inp.fr)](mailto:leonard.gaudin@etu.toulouse-inp.fr

## Requirements

### Dependencies
- **QGIS 3.x** with PyQGIS
- **Python 3.6+**
- **geopandas** - Vector data manipulation
- **pandas** - Data processing and CSV export
- **numpy** - Numerical computations
- **tqdm** - Progress bars
- **tifffile** - TIFF file handling
- **osgeo/GDAL** - Geospatial data processing

### Installation

1. Ensure QGIS is installed on your system
2. Clone this repository:
   ```bash
   git clone <repository-url>
   cd Task1_Remote_Sensing
   ```
3. Install Python dependencies:
   ```bash
   pip install geopandas pandas numpy tqdm tifffile
   ```

## Project Structure

```
.
├── README.md                          # Project documentation
├── main.py                            # Entry point (template)
├── postprocess_csv.py                 # Post-processing accuracy metrics
├── inputs/                            # Input data directory
│   ├── layers/                        # Vector layers (shapefiles)
|   └── raster/                        # Raster layers
├── outputs/                           # Output results directory
│   └── figures/                       # Figures
└── src/                               # Source code
    ├── main.py                        # Main processing entry point
    ├── functions.py                   # Core QGIS processing functions
    ├── convert_files_tif.py           # TIFF conversion utilities
    ├── convert_files_vrt.py           # VRT to Float32 conversion
    ├── import csv.py                  # CSV import utilities
    ├── plot_hist_dist_polys.py        # Histogram distribution plots
    ├── plot_results_polys_ok.py       # Valid polygons results plots
    └── plot_results.py                # General results visualization
```

## Key Features

### 1. Zonal Histogram Computation
Computes pixel value histograms within polygon boundaries to extract raster statistics.

### 2. Polygon Filtering
Automatically filters polygons based on a configurable detection threshold (default: 0.75).

### 3. Accuracy Metrics
Calculates:
- **Precision**: $\frac{\text{TP}}{\text{TP} + \text{FP}}$
- **Recall**: $\frac{\text{TP}}{\text{TP} + \text{FN}}$  
- **F1-Score**: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$

### 4. Buffer Analysis
Performs multi-distance buffer analysis for spatial error assessment.

### 5. Batch Processing
Processes multiple datasets and detection methods in parallel with progress tracking.

## Usage

### Basic Workflow

1. **Configure Input Data**
   - Place vector layers (shapefiles) in `inputs/layers/`
   - Place raster files (VRT or GeoTIFF) in appropriate paths

2. **Edit Configuration** in [src/main.py](src/main.py):
   ```python
   folder_list = ["path/to/working/directory"]
   raster_names = ["method_name"]
   raster_paths = ["path/to/raster.vrt"]
   output_files = ["./outputs/"]
   threshold = 0.75  # Detection threshold
   ```

3. **Run Main Pipeline**
   **The main pipeline cannot be run in a classical Python editor, it should be run with Python console of QGIS**
   **Steps:**
   1. Open QGIS
   2. Open Python console (Ctrl+Alt+P)
   3. Select Open editor
   4. Open the file `main.py`
   5. Run it in the editor


4. **Post-Process Results**
   ```bash
   python postprocess_csv.py
   ```

### Raster Conversion

Convert VRT to Float32 GeoTIFF:
```bash
python src/convert_files_vrt.py
```

Convert TIFF data types:
```bash
python src/convert_files_tif.py
```

### Visualization

Generate result plots:
```bash
python src/plot_results_polys_ok.py
python src/plot_hist_dist_polys.py
```

## Core Functions

### `create_layer_valid_polys()`
Filters polygons based on zonal histogram and detection threshold.

**Parameters:**
- `raster`: Path to input raster
- `layer`: Path to input vector layer (shapefile)
- `output_folder`: Output directory
- `threshold`: Detection threshold (0-1)

**Returns:** Path to filtered polygon layer

### `create_layers_from_folders()`
Batch processes multiple rasters and folders.

### `process_qgis()`
Executes the complete QGIS processing workflow including buffer analysis and accuracy metrics computation.

## Output Files

The pipeline generates:
- Filtered polygon shapefiles (with "_filtered_" suffix)
- Reprojected layers
- Zonal histogram results
- CSV files with accuracy metrics:
  - `histo_polys.csv` - Polygon histograms
  - `histo_FA_*.csv` - False alarm histograms by buffer distance
  - `results.csv` - Precision/Recall/F1-Score metrics
- Plots of F1-score and F1-score derivatives as functions of buffer sizes

## Workflow

The processing pipeline follows these steps:
1. Load vector layer (shapefile) and raster layer
2. Reproject layer to match raster CRS (EPSG:32722 by default)
3. Compute zonal histogram
4. Filter polygons by detection threshold expression
5. Generate buffers at multiple distances
6. Compute symmetrical differences
7. Join attribute tables
8. Export results to CSV

## Technical Details

- **CRS**: EPSG:32722 (UTM Zone 22S) - configurable
- **Data Types**: Float32 for raster layers
- **Compression**: LZW with tiling for QGIS optimization
- **Progress Tracking**: tqdm for batch operations

## Author

**Léonard Gaudin**  
Toulouse INP-ENSEEIHT  
CESBIO (Centre d'Études Spatiales de la Biosphère)

## License

[Specify your license here if applicable]

## Notes

- Some parameters are hardcoded in scripts (paths, thresholds). Edit configuration sections before running.
- Ensure all input data has consistent coordinate reference systems
- Buffer distances should be in meters
- QGIS must be properly installed with PyQGIS support
