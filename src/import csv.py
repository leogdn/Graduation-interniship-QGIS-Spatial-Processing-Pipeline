import csv

def csv_to_latex(csv_file, latex_file, delimiter=","):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f, delimiter=delimiter))
    
    if not reader:
        print("Le fichier CSV est vide.")
        return

    num_cols = len(reader[0])

    with open(latex_file, "w", encoding="utf-8") as out:
        # Début du tableau
        out.write("\\begin{tabular}{" + "|".join(["c"] * num_cols) + "}\n")
        out.write("\\hline\n")

        for i, row in enumerate(reader):
            line = " & ".join(row) + " \\\\\n"
            out.write(line)
            out.write("\\hline\n")

        # Fin du tableau
        out.write("\\end{tabular}\n")

    print(f"Tableau LaTeX généré dans : {latex_file}")


# Exemple d'utilisation
csv_to_latex("donnees.csv", "tableau.tex")