import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.titlesize": 16
})

older_list = ["/home/lgaudin/stage/Task1_Remote_Sensing/automatique/map_biomas","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/bocd","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/gfw","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/radd/","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/tropisco/"]
raster_names = ["GFW","RADD","Tropisco"]
raster_paths = ["/home/lgaudin/stage/Task1_Remote_Sensing/automatique/map_biomas/raster/output.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/bocd/raster/output.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/gfw/raster/gfw.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/radd/raster/radd.vrt","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/tropisco/raster/tropisco.vrt"]
results_folder = "/home/lgaudin/stage/Task1_Remote_Sensing/automatique/outputs/"
layers_list = ["/home/lgaudin/stage/Task1_Remote_Sensing/automatique/map_biomas/layer/map_alerta_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/bocd/layer/zones_75_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/gfw/layer/zones_75_gfw_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/radd/layer/zones_75_radd_reproj.shp","/home/lgaudin/stage/Task1_Remote_Sensing/automatique/tropisco/layer/zones_75_tropisco_reproj.shp"]

detect_polys_ok = True

figures_folder = os.path.join(results_folder,"figures")
os.makedirs(figures_folder, exist_ok=True)

functions_array = ["mean","std","median"]

for raster_name in raster_names:
    print(f"Traitement de {raster_name}")
    for fun in functions_array:

        print(f"Traitement de {fun}")
        
        # Lecture du CSV
        df = pd.read_csv(os.path.join(results_folder, f"{raster_name}/results_{fun}.csv"),sep=';')
        print(df.head)

        # Plot : 1ère colonne = X, le reste = Y
        #fig = px.line(df, x=df.columns[0], y=df.columns[1:], title=fun, mode='lines+markers')

        fig = go.Figure()

        x_col = df.columns[0]

        plt.subplots(figsize=(6, 4.2))

        for col in df.columns[1:]:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                mode='lines+markers', 
                name=col
            ))
            plt.plot(df[x_col], df[col],'.-')

        fig.update_layout(title=f"{raster_name} - {fun}")

        fig.show()

        plt.grid(axis='x', linestyle='--')
        plt.grid(axis='y', linestyle='--')
        plt.xlabel(r"Buffer size (m)")
        plt.ylabel(r"F1-score")
        plt.legend(df.columns[1:])
        plt.title(f"{raster_name} - Agregation {fun}")
        plt.savefig(os.path.join(figures_folder, f"{raster_name}_{fun}.pdf"))
        plt.close()

        # Export
        '''fig.write_image(
            os.path.join(figures_folder, f"{raster_name}_{fun}.pdf"),
            width=1200,
            height=800,
            scale=2
        )'''

        fig.write_html(
            os.path.join(figures_folder, f"{raster_name}_{fun}.html")
        )

for fun in functions_array:

    print(f"Traitement de {fun}")
    
    # Lecture du CSV
    df = pd.read_csv(os.path.join(results_folder, f"results_{fun}.csv"),sep=';')
    print(df.head)

    # Plot : 1ère colonne = X, le reste = Y
    #fig = px.line(df, x=df.columns[0], y=df.columns[1:], title=fun, mode='lines+markers')

    fig = go.Figure()

    x_col = df.columns[0]

    plt.subplots(figsize=(6, 4.2))

    for col in df.columns[1:]:
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[col],
            mode='lines+markers', 
            name=col
        ))
        plt.plot(df[x_col], df[col],'.-')

    fig.update_layout(title=fun)

    fig.show()

    plt.grid(axis='x', linestyle='--')
    plt.grid(axis='y', linestyle='--')
    plt.xlabel(r"Buffer size (m)")
    plt.ylabel(r"F1-score")
    plt.legend(df.columns[1:])
    plt.title(f"Agregation{fun}")
    plt.savefig(os.path.join(figures_folder, f"{fun}.pdf"))
    plt.close()

    # Export
    '''fig.write_image(
        os.path.join(figures_folder, f"{fun}.pdf"),
        width=1200,
        height=800,
        scale=2
    )'''

    fig.write_html(
        os.path.join(figures_folder, f"{fun}.html")
    )

# nombre de fonctions
n = len(functions_array)

fig = make_subplots(
    rows=n,
    cols=1,
    shared_xaxes=True,
    subplot_titles=functions_array
)

for i, fun in enumerate(functions_array):

    df = pd.read_csv(os.path.join(results_folder, f"results_{fun}.csv"),sep=';')

    x = df.iloc[:, 0]

    for col in df.columns[1:]:

        fig.add_trace(
            go.Scatter(
                x=x,
                y=df[col],
                mode='lines+markers',
                name=col,
                showlegend=True  # légende seulement sur le 1er subplot
            ),
            row=i+1,
            col=1
        )

fig.update_layout(
    height=300 * n,
    width=1200,
    title="Toutes les fonctions",
    template="plotly_white"
)

fig.write_html(os.path.join(figures_folder, "all_functions.html"))
fig.show()
