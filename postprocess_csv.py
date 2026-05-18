import pandas as pd
import os

output_folder = "/home/lgaudin/stage/Task1_Remote_Sensing/automatique/res"

distances = range(10,400,20)   # distances de buffer

csv_input = os.path.join(output_folder, f"histo_polys.csv")
df = pd.read_csv(csv_input)
print(df.head())
fn = df["HISTO_0"].sum()
tp = df["hist_1"].sum()



for dist in distances:

    print(f"Traitement pour distance = {dist}")

    csv_input = os.path.join(output_folder, f"histo_FA_{dist}m.csv")
    df = pd.read_csv(csv_input)
    print(df.head())

    fp = df["hist_1"].sum()
    tn = df["hist_0"].sum()
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1_score = 2*(precision*recall)/(precision+recall)

    df_new = df = pd.DataFrame({
    "distance_buffer": [dist],
    "precision": [precision],
    "recall": [recall],
    "f1-score": [f1_score]
    })

    csv_output = os.path.join(output_folder, f"results.csv")
    df_new.to_csv(csv_output, mode="a", sep=";", header=not os.path.exists(csv_output), index=False)

    print(f"✔ Terminé pour {dist}")