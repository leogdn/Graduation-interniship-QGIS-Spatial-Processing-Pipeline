import pandas as pd
import os
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.titlesize": 16
})

folder_list = ["/home/lgaudin/stage/Task1_Remote_Sensing/automatique/map_biomas","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/bocd","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/gfw","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/radd/","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/tropisco/"]
raster_names = ["MapBiomas","BOCD","GFW","RADD","Tropisco"]
raster_paths = ["/home/lgaudin/stage/Task1_Remote_Sensing/automatique/map_biomas/raster/output.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/bocd/raster/output.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/gfw/raster/gfw.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/radd/raster/radd.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/tropisco/raster/tropisco.vrt"]
results_folder = "/home/lgaudin/stage/Task1_Remote_Sensing/automatique/outputs/"
layers_list = ["/home/lgaudin/stage/Task1_Remote_Sensing/automatique/map_biomas/layer/map_alerta_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/bocd/layer/zones_75_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/gfw/layer/zones_75_gfw_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/radd/layer/zones_75_radd_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/tropisco/layer/zones_75_tropisco_reproj.shp"]


# Distances entre les polys les plus proches
print("Affichage des histogrammes des distances entre les polygones")

for folder_index in range(len(folder_list)):
    
    print(f"Traitement du raster {raster_names[folder_index]}")

    output_folder = folder_list[folder_index]
    raster_name = raster_names[folder_index]

    csv_input = os.path.join(output_folder, f"histo_dist_polys.csv")
    df = pd.read_csv(csv_input)
    quantile25 = df["distance"].quantile(0.25)
    quantile10 = df["distance"].quantile(.1)
    quantile5 = df["distance"].quantile(.05)
    quantile1 = df["distance"].quantile(.01)
    mean = df["distance"].mean()
    std = df["distance"].std()

    fig = px.histogram(df, x="distance", nbins=500,labels={"distance": "Distance (m)"},title=f"{raster_name}")

    # Ajouter des lignes pour les quantiles, la moyenne et l'écart-type
    fig.add_vline(x=mean, line=dict(color="red", dash="dash"), annotation_text="Moyenne", annotation_position="top left")
    #fig.add_vline(x=mean - std, line=dict(color="orange", dash="dot"), annotation_text="-1σ", annotation_position="top left")
    #fig.add_vline(x=mean + std, line=dict(color="orange", dash="dot"), annotation_text="+1σ", annotation_position="top left")
    fig.add_vline(x=quantile25, line=dict(color="green", dash="dash"), annotation_text="Q25", annotation_position="top left")
    #fig.add_vline(x=median, line=dict(color="blue", dash="dash"), annotation_text="Q50", annotation_position="top left")
    #fig.add_vline(x=quantile75, line=dict(color="green", dash="dash"), annotation_text="Q75", annotation_position="top left")
    fig.add_vline(x=quantile10, line=dict(color="purple", dash="dot"), annotation_text="Q10", annotation_position="top left")
    #fig.add_vline(x=quantile90, line=dict(color="purple", dash="dot"), annotation_text="Q90", annotation_position="top left")
    fig.add_vline(x=quantile5, line=dict(color="purple", dash="dot"), annotation_text="Q5", annotation_position="top left")
    fig.add_vline(x=quantile1, line=dict(color="purple", dash="dot"), annotation_text="Q1", annotation_position="top left")


    # Ajouter le texte en bas (pied de page)
    stats_text = f"Moyenne = {mean:.2f}, Écart-type = {std:.2f}, Q5 = {quantile5:.2f}, Q10 = {quantile10:.2f}, Q25 = {quantile25:.2f}, Q1 = {quantile1:.2f}"

    fig.add_annotation(
        text=stats_text,
        xref='paper', yref='paper',
        x=0, y=-0.15,  # position en bas à gauche
        showarrow=False,
        align='left',
        font=dict(size=16)
    )

    # Ajuster les marges pour que le texte soit visible
    fig.update_layout(margin=dict(b=150))  # augmente la marge inférieure

    #fig.show()
    #fig.write_image(os.path.join(results_folder,f"hist_dist_polys_{raster_name}.png"),width=1200,height=800,scale=2)
    fig.write_html(os.path.join(results_folder,f"hist_dist_polys_{raster_name}.html"))

    # Création du graphique
    plt.figure(figsize=(12, 8))

    # Histogramme
    plt.hist(df["distance"], bins=500)

    # Lignes verticales
    plt.axvline(mean, color="red", linestyle="--", label="Moyenne")
    plt.axvline(quantile25, color="green", linestyle="--", label="Q25")
    plt.axvline(quantile10, color="purple", linestyle=":", label="Q10")
    plt.axvline(quantile5, color="purple", linestyle=":", label="Q5")
    plt.axvline(quantile1, color="purple", linestyle=":", label="Q1")

    # Titre et labels
    plt.title(raster_name)
    plt.xlabel("Distance (m)")
    plt.ylabel("Fréquence")

    # Légende
    plt.legend()

    # Texte en bas (équivalent annotation Plotly)
    stats_text = (
        f"Moyenne = {mean:.2f}, Écart-type = {std:.2f}, "
        f"Q5 = {quantile5:.2f}, Q10 = {quantile10:.2f}, "
        f"Q25 = {quantile25:.2f}, Q1 = {quantile1:.2f}"
    )

    plt.figtext(0.1, 0.05, stats_text, ha="left", fontsize=13)

    # Ajustement des marges
    plt.subplots_adjust(bottom=0.2)

    # Sauvegarde
    output_path = os.path.join(results_folder, f"hist_dist_polys_{raster_name}.pdf")
    plt.savefig(output_path, dpi=200)

    # Affichage