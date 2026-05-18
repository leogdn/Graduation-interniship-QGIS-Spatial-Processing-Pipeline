from osgeo import gdal

def convert_vrt_to_float32(input_vrt, output_tif):
    # Ouvrir le VRT
    src = gdal.Open(input_vrt)
    if src is None:
        raise RuntimeError(f"Impossible d'ouvrir le fichier : {input_vrt}")

    # Conversion en Float32
    gdal.Translate(
        output_tif,
        src,
        outputType=gdal.GDT_Float32,
        creationOptions=[
            "COMPRESS=LZW",   # compression (optionnel mais conseillé)
            "TILED=YES"       # optimisation affichage QGIS
        ]
    )

    print(f"✅ Conversion terminée : {output_tif}")

if __name__ == "__main__":
    input_vrt = "Task1_Remote_Sensing/ms-BOCD Data/output.vrt"
    output_tif = "Task1_Remote_Sensing/ms-BOCD Data/output_vrt_float32.tif"

    convert_vrt_to_float32(input_vrt, output_tif)