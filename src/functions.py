def list_to_file_name(ma_liste):
    """Convert a list of strings into a single string suitable for a file name.
    Args:
        ma_liste (list): A list of strings to be joined into a file name.
    Returns:
        str: A single string suitable for a file name.
    """
    return "_".join(map(str, ma_liste))

def create_layer_valid_polys(raster, layer, output_folder, threshold):
    """Create a polygon layer containing only polygons correctly detected
    according to a detection threshold.
    Args:
        raster (str): Path to the input raster file.
        layer (str): Path to the input vector layer (shapefile).
        output_folder (str): Path to the folder where the output layer will be saved.
        threshold (float): Detection threshold to filter valid polygons.
    Returns:
        str: Path to the output layer containing valid polygons.
    """
    import os
    import processing
    from qgis.core import (QgsVectorLayer, QgsProject, QgsRasterLayer,
                           QgsVectorFileWriter, QgsCoordinateReferenceSystem)

    input_shp = layer
    input_raster = raster

    print(f"SHP LAYER : {input_shp}")
    print(f"RASTER LAYER : {input_raster}")

    # Load the vector layer
    layer = QgsVectorLayer(input_shp, "layer", "ogr")
    if not layer.isValid():
        raise Exception("La couche ne s'est pas chargée correctement")
    QgsProject.instance().addMapLayer(layer)

    # Load the raster layer
    raster = QgsRasterLayer(input_raster, "Mon VRT")
    if not raster.isValid():
        raise Exception("Erreur de chargement du raster")
    QgsProject.instance().addMapLayer(raster)
    print("Raster chargé avec succès")

    # Reproject the layer to match the raster CRS (if needed)
    layer_reproj = os.path.join(output_folder, "layer_reproj.shp")
    processing.run("native:reprojectlayer", {
        'INPUT': layer,
        'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32722'),
        'CONVERT_CURVED_GEOMETRIES': False,
        'OPERATION': '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=utm +zone=22 +south +ellps=WGS84',
        'OUTPUT': layer_reproj,
    })

    # Zonal histogram to count pixels inside each polygon
    histo_zonal_polys = os.path.join(output_folder, "histo_zonal_polys_non_filtre.shp")
    processing.run("native:zonalhistogram", {
        'INPUT_RASTER': raster,
        'RASTER_BAND': 1,
        'INPUT_VECTOR': layer_reproj,
        'COLUMN_PREFIX': 'h_pol_',
        'OUTPUT': histo_zonal_polys,
    })

    # Filter polygons based on the detection threshold
    selection_polys_ok = os.path.join(output_folder, f"polys_map_biomas_filtered_{threshold}.shp")
    processing.run("native:extractbyexpression", {
        'INPUT': histo_zonal_polys,
        'EXPRESSION': f'"h_pol_1" / ("h_pol_1" + "h_pol_0") >= {threshold}',
        'OUTPUT': selection_polys_ok,
    })

    return selection_polys_ok

def create_layers_from_folders(folder_list,layer,raster_names,raster_paths,output_files,threshold):
    """
    Generate filtered polygon layers for multiple rasters.

    Args:
        folder_list : list
            List of working directories.

        layer : str
            Path to the polygon shapefile.

        raster_names : list
            Raster names.

        raster_paths : list
            Raster paths.

        output_files : list
            Output directories.

        threshold : float
            Detection threshold.

    Returns :
        list
            Paths to generated layers.
    """
    from tqdm import tqdm
    layers_paths = []
    print(f"Creation des layers pour chaque méthode, seuil de détection {threshold}")
    for folder_index in tqdm(range(len(folder_list)),
                            desc="Methods",
                            position=0,
                            leave=False):
        print(f"Traitement du raster {raster_names[folder_index]}")

        output_folder = output_files[folder_index]
        raster_name = raster_names[folder_index]
        raster = raster_paths[folder_index]

        layer_path = create_layer_valid_polys(raster,layer,output_folder,threshold)
        layers_paths.append(layer_path)

    return layers_paths

def process_qgis(raster,layer,output_folder,distances):
    """
    Execute the complete QGIS processing workflow.

    Workflow:
        1. Compute zonal histogram.
        2. Generate buffers.
        3. Compute symmetrical differences.
        4. Compute false alarm statistics.
        5. Join attribute tables.
        6. Compute precision / recall / F1-score.
        7. Export results to CSV.

    Parameters:
        raster : str
            Raster file path.

        layer : str
            Polygon shapefile path.

        output_folder : str
            Output directory.

        distances : list
            Buffer distances in meters.
    """
    import os
    import processing
    from qgis.core import QgsVectorLayer, QgsProject, QgsRasterLayer, QgsVectorFileWriter

    # Parameters
    input_shp = layer
    input_raster = raster
    output_folder = output_folder

    print(f"SHP LAYER : {input_shp}")
    print(f"RASTER LAYER : {input_raster}")

    # Load the vector layer
    layer = QgsVectorLayer(input_shp, "layer", "ogr")

    if not layer.isValid():
        raise Exception("La couche ne s'est pas chargée correctement")

    QgsProject.instance().addMapLayer(layer)

    # Load the raster layer
    raster = QgsRasterLayer(input_raster, "Mon VRT")

    if not raster.isValid():
        print("Erreur de chargement")
    else:
        QgsProject.instance().addMapLayer(raster)
        print("Raster chargé avec succès")

    QgsProject.instance().addMapLayer(raster)

    histo_output_polys = os.path.join(output_folder, f"histo_polys.shp")

    # Zonal histogram to count pixels inside each polygon
    processing.run("native:zonalhistogram", {
    'INPUT_RASTER': raster,
    'RASTER_BAND': 1,
    'INPUT_VECTOR': layer,
    'COLUMN_PREFIX': 'h_pol_',
    'OUTPUT': histo_output_polys
    })

    csv_path = os.path.join(output_folder, f"histo_polys.csv")
    histo_layer = QgsVectorLayer(histo_output_polys, f"histo_polys", "ogr")

    QgsVectorFileWriter.writeAsVectorFormat(
        histo_layer,
        csv_path,
        "UTF-8",
        layer.crs(),
        "CSV")

    # Loop over buffer distances
    for dist in distances:
        
        print(f"Traitement pour distance = {dist}")
        
        # Buffer
        buffer_output = os.path.join(output_folder, f"buffer_{dist}.shp")
        
        buffer_result = processing.run("native:buffer", {
            'INPUT': layer,
            'DISTANCE': dist,
            'SEGMENTS': 5,
            'END_CAP_STYLE': 0,
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'DISSOLVE': False,
            'OUTPUT': buffer_output
        })
        
        buffer_layer = QgsVectorLayer(buffer_output, f"buffer_{dist}", "ogr")
        
        # Symmetrical difference
        symdiff_output = os.path.join(output_folder, f"symdiff_{dist}.shp")
        
        processing.run("native:symmetricaldifference",{
            'INPUT': buffer_layer,
            'OVERLAY': histo_output_polys,
            'OUTPUT': symdiff_output
        })

        histo_output_FA = os.path.join(output_folder, f"histo_FA_{dist}m.shp")

        # Zonal histogram for false alarms
        processing.run("native:zonalhistogram", {
        'INPUT_RASTER': raster,
        'RASTER_BAND': 1,
        'INPUT_VECTOR': symdiff_output,
        'COLUMN_PREFIX': 'h_buf_',
        'OUTPUT': histo_output_FA
        })

        # Join attribute tables

        histo_buffer_layer = QgsVectorLayer(histo_output_FA, f"buffer_{dist}", "ogr")
        histo_output_joined = os.path.join(output_folder, f"histo_joined_{dist}m.shp")
        
        processing.run("native:joinattributestable", 
                        {'INPUT': histo_output_polys,
                        'FIELD': 'CODEALERTA',
                        'INPUT_2': histo_output_FA,
                        'FIELD_2': 'CODEALERTA',
                        'FIELDS_TO_COPY': [],  # assure-toi qu'ils existent
                        'METHOD': 1,
                        'DISCARD_NONMATCHING': False, #False par défaut
                        'PREFIX': '',
                        'OUTPUT': histo_output_joined})
        
        print("Attributes tables joined successfully")

        # Compute precision, recall, F1-score
        
        histo_input_joined = QgsVectorLayer(histo_output_joined, f"histo_joined_{dist}", "ogr")
        calc_output = os.path.join(output_folder,f"metrics_{dist}m.shp")

        calc1 = processing.run("native:fieldcalculator", {
            'INPUT': histo_output_joined,
            'FIELD_NAME': 'recall',
            'FIELD_TYPE': 0,  # 0 = float, 1 = int, 2 = string
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 3,
            'FORMULA': '"h_pol_1"/("h_pol_0"+"h_pol_1")',
            'OUTPUT': 'TEMPORARY_OUTPUT'  # ou chemin fichier
        })

        calc2 = processing.run("native:fieldcalculator", {
            'INPUT': calc1['OUTPUT'],
            'FIELD_NAME': 'precision',
            'FIELD_TYPE': 0,  # 0 = float, 1 = int, 2 = string
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 3,
            'FORMULA': '"h_pol_1"/("h_buf_1"+"h_pol_1")',
            'OUTPUT': histo_output_joined  # ou chemin fichier
        })

        calc3 = processing.run("native:fieldcalculator", {
            'INPUT': calc2['OUTPUT'],
            'FIELD_NAME': 'f1-score',
            'FIELD_TYPE': 0,  # 0 = float, 1 = int, 2 = string
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 3,
            'FORMULA': '2*"precision"*"recall"/("precision" + "recall")',
            'OUTPUT': calc_output 
        })

        # Save results to CSV
        csv_path = os.path.join(output_folder, f"histo_{dist}m.csv")

        histo_layer = QgsVectorLayer(calc_output, f"metrics_{dist}m", "ogr")

        QgsVectorFileWriter.writeAsVectorFormat(
        histo_layer,
        csv_path,
        "UTF-8",
        layer.crs(),
        "CSV")
    
        print(f"✔ Terminé pour {dist}")
        
    print("QGIS processing completed successfully")

def compute_distances(layer,output_folder):
    """
    Compute nearest-neighbor distances between polygons.

    Parameters:
        layer : str
            Polygon shapefile path.

        output_folder : str
            Output directory.
    """
    import os
    import processing
    from qgis.core import QgsVectorLayer, QgsProject, QgsRasterLayer, QgsVectorFileWriter

    # Parameters
    input_shp = layer
    output_folder = output_folder

    print(f"SHP LAYER : {input_shp}")

    # Load the vector layer
    layer = QgsVectorLayer(input_shp, "layer", "ogr")

    if not layer.isValid():
        raise Exception("La couche ne s'est pas chargée correctement")

    QgsProject.instance().addMapLayer(layer)

    print("Calcul des distances minimum")

    # Histogram of nearest neighbor distances between polygons
    hist_dist_output = os.path.join(output_folder,f"histo_dist_polys.shp")
    processing.run("native:joinbynearest", 
               {'INPUT':layer,
                'INPUT_2':layer,
                'FIELDS_TO_COPY':[],
                'DISCARD_NONMATCHING':False,
                'PREFIX':'',
                'NEIGHBORS':1,
                'MAX_DISTANCE':None,
                'OUTPUT':hist_dist_output})

    csv_path = os.path.join(output_folder, f"histo_dist_polys.csv")
    histo_dist_layer = QgsVectorLayer(hist_dist_output, f"histo_dist_polys", "ogr")

    QgsVectorFileWriter.writeAsVectorFormat(
        histo_dist_layer,
        csv_path,
        "UTF-8",
        layer.crs(),
        "CSV")
    
    print("Distances computed and saved to CSV successfully")

def postprocess_csv(mode,poly_list,folder_list,raster_names,results_folder,distances):
    """
    Compute statistics from exported CSV files.

    Parameters:
        mode : str
            Processing mode.

        poly_list : list or DataFrame
            Polygon identifiers.

        folder_list : list
            Output folders.

        raster_names : list
            Raster names.

        results_folder : str
            Output directory.

        distances : list
            Buffer distances.
    """
    import pandas as pd
    import os
    import numpy as np

    columns_names = ["Distance of buffer (m)"]
    mat_results = np.array([distances]).T
    f1_scores_names = []
    
    if mode=="global":

        for folder_index in range(len(folder_list)):

            mini_mat = np.empty((0,3))

            print(f"Processing raster {raster_names[folder_index]}")

            output_folder = folder_list[folder_index]

            raster_name = raster_names[folder_index]

            csv_input = os.path.join(output_folder, f"histo_polys.csv")
            df = pd.read_csv(csv_input)
            #print(df.head())
            fn = df["h_pol_0"].sum()
            tp = df["h_pol_1"].sum()

            for dist in distances:

                print(f"Processing for distance = {dist}")

                csv_input = os.path.join(output_folder, f"histo_{dist}m.csv")
                df = pd.read_csv(csv_input)
                #print(df.head())

                fp = df["h_buf_1"].sum()
                tn = df["h_buf_0"].sum()
                precision = tp/(tp+fp)
                recall = tp/(tp+fn)
                f1_score = 2*(precision*recall)/(precision+recall)

                new_line = np.array([[precision,recall,f1_score]])
                mini_mat = np.concatenate((mini_mat,new_line),axis=0)

                print(f"✔ Finished for {dist}")

            new_columns_names = np.array([f"{raster_name} precision",f"{raster_name} recall",f"{raster_name} F1 score"])
            #f1_scores_names.append(f"{raster_name} F1 score")
            columns_names = np.concatenate((columns_names,new_columns_names),axis=0)
            mat_results = np.concat((mat_results,mini_mat),axis=1)

        df2 = pd.DataFrame(mat_results, columns=columns_names)

        print(os.path.join(results_folder,"results.csv"))

        df2.to_csv(os.path.join(results_folder,"results.csv"), sep=';', index=False)

    else:

        functions_array = ["mean","std","median"]

        #print(len(distances))

        # Normalisation de poly_list selon son type
        if poly_list is not None:
            if isinstance(poly_list, pd.DataFrame):
                # ← remplace "CODEALERTA" par le vrai nom de colonne
                poly_values = poly_list["CODEALERTA"].tolist()
            elif isinstance(poly_list, pd.Series):
                poly_values = poly_list.tolist()
            else:
                poly_values = list(poly_list)  # déjà une liste
        else:
            poly_values = None

        for fun in functions_array:

            columns_names = ["Distance of buffer (m)"]
            mat_results = np.array([distances]).T
            f1_scores_names = []

            for folder_index in range(len(folder_list)):

                mini_mat = np.empty((0,1))

                print(f"Traitement du raster {raster_names[folder_index]}")

                output_folder = folder_list[folder_index]

                raster_name = raster_names[folder_index]

                csv_input = os.path.join(output_folder, f"histo_polys.csv")
                df_output = pd.DataFrame(columns=["buffer range (m)","f1-score mean"])

                for dist in distances:

                    print(f"Processing for distance = {dist}")

                    csv_input = os.path.join(output_folder, f"histo_{dist}m.csv")
                    df = pd.read_csv(csv_input)
                    #print(df.head())

                    # ✅ Filtre sur poly_list si fournie
                    if poly_list is not None and len(poly_values) > 0:
                        df = df[df["CODEALERTA"].isin(poly_values)]
                        if df.empty:
                            print(f"WARNING: No matching polygons found for distance={dist}, raster={raster_name}")

                    #f1_mean = df["f1-score"].mean()
                    f1_mean = getattr(df["f1-score"].dropna(), fun)()

                    print([dist,f1_mean])

                    new_line = np.array([[f1_mean]])
                    mini_mat = np.concatenate((mini_mat,new_line),axis=0)

                    #pd.concat([df_output, new_line], ignore_index=True)

                    print(f"✔ Finished for {dist}")

                new_columns_names = np.array([f"{raster_name} f1-score {fun}"])
                f1_scores_names.append(f"{raster_name} F1 score")
                columns_names = np.concatenate((columns_names,new_columns_names),axis=0)
                mat_results = np.concatenate((mat_results,mini_mat),axis=1)

            df_output = pd.DataFrame(mat_results, columns=columns_names)

            df_output[f"derivate of {fun}"] = np.gradient(df_output.iloc[:,1], df_output.iloc[:,0])

            results_folder_raster = os.path.join(results_folder, f"{raster_name}")
            os.makedirs(results_folder_raster, exist_ok=True)

            print(os.path.join(results_folder_raster,f"results_{fun}.csv"))

            df_output.to_csv(os.path.join(results_folder_raster,f"results_{fun}.csv"), sep=';', index=False)

def postprocess_by_polygon(poly_list, folder_list, raster_names, results_folder, distances):
    """
    Compute F1-score evolution for each polygon.

    Parameters:
        poly_list : DataFrame
            Polygon identifiers.

        folder_list : list
            Output folders.

        raster_names : list
            Raster names.

        results_folder : str
            Output directory.

        distances : list
            Buffer distances.
    """
    import numpy as np
    import os
    import pandas as pd

    results_folder_polys = os.path.join(results_folder, "by_polygon")
    os.makedirs(results_folder_polys, exist_ok=True)

    for poly in poly_list.iloc[1:,0]:
        columns_names = ["Distance of buffer (m)"]
        mat_results = np.array([distances]).T

        for folder_index in range(len(folder_list)):

            mini_mat = np.empty((0, 1))
            raster_name = raster_names[folder_index]
            output_folder = folder_list[folder_index]

            for dist in distances:

                csv_input = os.path.join(output_folder, f"histo_{dist}m.csv")
                df = pd.read_csv(csv_input)
                row = df.loc[df["CODEALERTA"] == poly, "f1-score"]

                if row.empty:
                    print(f"WARNING: Polygone {poly} non trouvé pour dist={dist}, raster={raster_name}")
                    f1_val = np.nan
                else:
                    f1_val = row.values[0]
                    #print(f1_val)

                new_line = np.array([[f1_val]])
                mini_mat = np.concatenate((mini_mat, new_line), axis=0)

            columns_names = np.concatenate(
                (columns_names, np.array([f"{raster_name} f1-score"])), axis=0
            )
            mat_results = np.concatenate((mat_results, mini_mat), axis=1)

        df_output = pd.DataFrame(mat_results, columns=columns_names)
        df_output[f"derivate"] = np.gradient(df_output.iloc[:, 1], df_output.iloc[:, 0])
        df_output.to_csv(
            os.path.join(results_folder_polys, f"results_{raster_name}_poly_{poly}.csv"),
            sep=';', index=False
        )
        print(f"✔ Polygone {poly} sauvegardé")

    print("Postprocessing by polygon completed successfully")

def get_merged_df_from_folder(results_folder, raster_name, poly_list):
    """Merge CSV files by polygon into a single DataFrame.
    Args:
        results_folder (str): Path to the folder containing the CSV files.
        raster_name (str): Name of the raster to identify relevant files.
        poly_list (DataFrame): DataFrame containing the list of polygons to include.
    Returns:
        pd.DataFrame: Merged DataFrame containing results for all polygons.
    """
    import os
    import pandas as pd

    results_folder_polys = os.path.join(results_folder, "by_polygon")
    merged_df = pd.DataFrame()
    dfs = []

    for file in os.listdir(results_folder_polys):
        if file.startswith(f"results_{raster_name}_poly") and file.endswith(".csv"):
            polygone = file.split("_")[-1].split(".")[0]  # Extract the polygon identifier from the file name
            print(f"Taille de poly_list : {poly_list.iloc[1:,0].shape[0]}")
            print(f"Polygone extrait du nom de fichier : {polygone}")
            print(f"Liste des polygones dans poly_list : {poly_list.iloc[1:,0].values}")
            polygone_int = int(polygone)  # Convert as integer for comparison
            if polygone_int in poly_list.iloc[1:,0].values:  # Check if the polygon is in the list
                print(f"Read file {file} for polygon {polygone}")
                df = pd.read_csv(os.path.join(results_folder_polys, file), sep=';')
                df["CODEALERTA"] = polygone  # Add a column to identify the polygon
                dfs.append(df)
    
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)
        csv_output = os.path.join(results_folder, f"merged_results_{raster_name}.csv")
        merged_df.to_csv(csv_output, sep=';', index=False)
        print(f"Merged file saved : {csv_output}")
    else:
        print(f"No files found for raster {raster_name} in {results_folder_polys}")

    return merged_df

def get_aggregated_df_from_folder(merged_df, raster_name, results_folder):
    """Aggregate results by buffer distance and compute derivatives.
    Args:
        merged_df (pd.DataFrame): DataFrame containing merged results for all polygons.
        raster_name (str): Name of the raster to identify relevant columns.
        results_folder (str): Path to the folder where the aggregated results will be saved.
    Returns:
        pd.DataFrame: Aggregated DataFrame with statistics and derivatives."""
    import os
    import pandas as pd
    import numpy as np

    functions_array = ["mean","std","median"]

    for fun in functions_array:
        aggregated_df = merged_df.groupby("Distance of buffer (m)").agg({
            f"{raster_name} f1-score": [fun],
            f"derivate": [fun]

        }).reset_index()

        # Flatten MultiIndex columns 
        aggregated_df.columns = ['Distance of buffer (m)', f'{fun} of f1-score', f'{fun} of derivate']
        aggregated_df[f"derivate of {fun}"] = np.gradient(aggregated_df[f'{fun} of f1-score'], aggregated_df['Distance of buffer (m)'])
        output_folder = os.path.join(results_folder, f"{raster_name}")
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"results_{fun}.csv")
        aggregated_df.to_csv(output_file, sep=';', index=False)
        print(f"Merged file saved : {output_file}")

def get_codealerta_from_shp(shp_path):
    """
    Read a shapefile and extract the 'CODEALERTA' attribute into a DataFrame.
    Args:
        shp_path (str): Path to the .shp file

    Returns:
        pd.DataFrame: DataFrame with a 'CODEALERTA' column containing the values from the shapefile.
    """
    import geopandas as gpd
    import pandas as pd
    import os

    if not os.path.exists(shp_path):
        raise FileNotFoundError(f"Fichier introuvable : {shp_path}")

    gdf = gpd.read_file(shp_path)

    if "CODEALERTA" not in gdf.columns:
        colonnes_dispo = gdf.columns.tolist()
        raise KeyError(
            f"Attribut 'CODEALERTA' absent du shapefile.\n"
            f"Colonnes disponibles : {colonnes_dispo}"
        )

    df = pd.DataFrame({"CODEALERTA": gdf["CODEALERTA"]})
    df = df.dropna().reset_index(drop=True)

    print(df.head())

    return df

def detect_polys_ok(poly_list,raster_name,results_folder,threshold):
    """Detect polygons with stable F1-score evolution.
    Args:
        poly_list (DataFrame): DataFrame containing the list of polygons to analyze.
        raster_name (str): Name of the raster to identify relevant files.
        results_folder (str): Path to the folder containing the results CSV files.
        threshold (float): Threshold for the derivative to consider a polygon as "ok".
    Returns:
        pd.DataFrame: DataFrame containing the list of "ok" polygons.
    """
    import numpy as np
    import os
    import pandas as pd

    results_folder_polys = os.path.join(results_folder, "by_polygon")
    os.makedirs(results_folder_polys, exist_ok=True)

    output_list = []

    print("AFFICHAGE DE LA LISTE")
    print(poly_list.iloc[1:,0])
    k=0

    for poly in poly_list.iloc[1:,0]:
        k+=1
        print(f"Traitement du polygone {poly} ({k}/{len(poly_list.iloc[1:,0])})")
        source = os.path.join(results_folder_polys, f"results_{raster_name}_poly_{poly}.csv")
        df = pd.read_csv(source,sep=';')
        df["derivate"] = np.gradient(df.iloc[:,1], df.iloc[:,0])
        count=0
        if abs(df["derivate"].iloc[-1]) <= threshold:
            count+=1
            output_list.append(poly)
        df.to_csv(
            source,
            sep=';', index=False
        )

    data = {"CODEALERTA":output_list}

    output_df = pd.DataFrame(data)

    print(output_df.shape[0])

    output_df.to_csv(
            os.path.join(results_folder_polys, f"polys_ok_{raster_name}.csv"),
            sep=';', index=False
        )
    
    return output_df

def process_folders(mode,detection_polys,folder_list,raster_names,raster_paths,output_file,layers_list,poly_list=[],distances=[],detection_threshold=0.01):
    """Process multiple rasters and compute statistics.
    Args:
        mode (str): Processing mode.
        detection_polys (bool): Whether to detect polygons.
        folder_list (list): List of folders containing raster data.
        raster_names (list): List of raster names.
        raster_paths (list): List of paths to raster files.
        output_file (str): Path to the output file.
        layers_list (list): List of layers.
        poly_list (DataFrame, optional): DataFrame containing the list of polygons to analyze.
        distances (list, optional): List of distances.
        detection_threshold (float, optional): Threshold for the derivative to consider a polygon as "ok".
    Returns:
        None
    """
    import os
    print("TYPE REÇU :", type(folder_list))
    from tqdm import tqdm
    if detection_polys and (len(folder_list)>1) :
        raise Exception(f"Impossible de détecter les polys ok sur plusieurs raster à la fois, there are {len(folder_list)} rasters")
    print("Processing in Qgis")
    for folder_index in tqdm(range(len(folder_list)),
                            desc="Methods",
                            position=0,
                            leave=False):
        print(f"Traitement du raster {raster_names[folder_index]}")

        output_folder = folder_list[folder_index]
        raster_name = raster_names[folder_index]
        raster = raster_paths[folder_index]
        layer = layers_list[folder_index]

        if poly_list==[]:
            poly_list = get_codealerta_from_shp(shp_path=layer)

        compute_distances(layer,output_folder)
        process_qgis(raster,layer,output_folder,distances)
        name = raster_names[folder_index]

    poly_list.to_csv(os.path.join(output_file, "codealerta_list.csv"), index=False)

    print("Postprocessing the results : Postprocessing by polygons")
    postprocess_by_polygon(poly_list,folder_list,raster_names,output_file,distances)

    print("Postprocessing the results : Merging the df")
    df_merged = get_merged_df_from_folder(output_file, raster_name, poly_list)

    print("Postprocessing the results : Agregating the results by distances")
    get_aggregated_df_from_folder(df_merged, raster_name, output_file)

    if detection_polys:

        print("Postprocessing the results : Detection polys ok")
        polys_ok = detect_polys_ok(poly_list,raster_names[folder_index],output_file,detection_threshold)

        print("Postprocessing the results : Computing the stats on the valid polygons set")
        output_file = os.path.join(output_file, f"stats_on_polys_ok")
        os.makedirs(output_file, exist_ok=True)

        print("Postprocessing the results : Postprocessing by polygons on the valid polygons set")
        postprocess_by_polygon(polys_ok,folder_list,raster_names,output_file,distances)

        print("Postprocessing the results : Merging the df on the valid polygons set")
        df_merged = get_merged_df_from_folder(output_file, raster_name, polys_ok)

        print("Postprocessing the results : Agregating the results by distances on the valid polygons set")
        get_aggregated_df_from_folder(df_merged, raster_name, output_file)

    print("FINISHED ALL THE PROCESSING !")