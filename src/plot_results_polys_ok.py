"""
Plot F1-scores and derivatives vs buffer size for each aggregation function (mean, std, median).
- One figure per function
- All methods (GFW, RADD, Tropisco) superimposed on each figure
- Saved as PDF (matplotlib) and HTML (plotly)
- Includes a mean F1 curve with standard deviation envelope
- Individual plots per method with mean F1 and std band
- Superimposed plot of all methods with their mean F1 and std bands

Colonnes utilisées par position :
  - colonne 0 → buffer size
  - colonne 1 → F1-score  (peu importe le nom)
  - colonne 2 → dérivée
"""

import os
from matplotlib.ticker import FormatStrFormatter
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.titlesize": 16
})

# ── Configuration ────────────────────────────────────────────────────────────
BASE_DIR   = "/home/lgaudin/stage/Task1_Remote_Sensing/automatique/outputs/stats_on_polys_ok"
METHODS    = ["GFW", "RADD", "Tropisco"]
FUNCTIONS  = ["mean", "std", "median"]
OUTPUT_DIR = "/home/lgaudin/stage/Task1_Remote_Sensing/automatique/outputs/figures/on_polys_ok"

# Limites des axes Y par fonction d'agrégation : [y_min, y_max]
Y_LIMITS = {
    "mean":   [0.6, 0.9],
    "std":    [0., 0.2],
    "median": [0.6, 0.9]
}

# Limites des axes Y pour la dérivée : [y_min, y_max]
Y_LIMITS_DERIV = {
    "mean":   [-0.01, 0.01],
    "std":    [-0.01, 0.01],
    "median": [-0.01, 0.01]
}
# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS_MPL    = ["#E63946", "#2A9D8F", "#457B9D"]
COLORS_PLOTLY = COLORS_MPL


def load_data() -> dict:
    """Charge tous les CSV dans un dict data[method][function] = DataFrame."""
    data = {}
    for method in METHODS:
        data[method] = {}
        for func in FUNCTIONS:
            path = os.path.join(BASE_DIR, method, f"results_{func}.csv")
            if not os.path.exists(path):
                print(f"[WARN] Fichier manquant : {path}")
                data[method][func] = None
                continue
            df = pd.read_csv(path, sep=";")
            if df.shape[1] < 2:
                raise ValueError(f"Le fichier {path} doit avoir au moins 2 colonnes.")
            df = df.iloc[:, [0, 1, 2]].copy()
            df.columns = ["buffer", "f1", "derivate"]
            df = df.sort_values("buffer")
            data[method][func] = df
    return data


def plot_matplotlib(data: dict):
    """Génère une figure PDF par fonction d'agrégation."""
    for func in FUNCTIONS:
        y_min, y_max = Y_LIMITS[func]
        fig, ax = plt.subplots(figsize=(9, 5))

        for method, color in zip(METHODS, COLORS_MPL):
            df = data[method].get(func)
            if df is None:
                continue
            ax.plot(
                df["buffer"],
                df["f1"],
                marker="o",
                linewidth=2,
                markersize=5,
                color=color,
                label=method,
            )

        ax.set_title(f"F1-score vs Taille du buffer  —  agrégation : {func}",
                     fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Taille du buffer (m)", fontsize=11)
        ax.set_ylabel("F1-score", fontsize=11)
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.2f}"))
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Méthode", fontsize=10, title_fontsize=10)
        fig.tight_layout()

        out_path = os.path.join(OUTPUT_DIR, f"f1_scores_{func}.pdf")
        fig.savefig(out_path, format="pdf", dpi=150)
        plt.close(fig)
        print(f"[matplotlib] Sauvegardé → {out_path}")

        y_min, y_max = Y_LIMITS_DERIV[func]
        fig, ax = plt.subplots(figsize=(9, 5))

        for method, color in zip(METHODS, COLORS_MPL):
            df = data[method].get(func)
            if df is None:
                continue
            ax.plot(
                df["buffer"],
                df["derivate"],
                marker="o",
                linewidth=2,
                markersize=5,
                color=color,
                label=method,
            )

        ax.set_title(f"Dérivée vs Taille du buffer  —  agrégation : {func}",
                     fontsize=13, fontweight="bold", pad=12)
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xlabel("Taille du buffer (m)", fontsize=11)
        ax.set_ylabel("Dérivée", fontsize=11)
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.3f}"))
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Méthode", fontsize=10, title_fontsize=10)
        fig.tight_layout()

        out_path = os.path.join(OUTPUT_DIR, f"derivate_{func}.pdf")
        fig.savefig(out_path, format="pdf", dpi=150)
        plt.close(fig)
        print(f"[matplotlib] Sauvegardé → {out_path}")


def plot_plotly(data: dict):
    """Génère une figure HTML interactive par fonction d'agrégation."""
    for func in FUNCTIONS:
        y_min, y_max = Y_LIMITS[func]
        fig = go.Figure()

        for method, color in zip(METHODS, COLORS_PLOTLY):
            df = data[method].get(func)
            if df is None:
                continue
            fig.add_trace(go.Scatter(
                x=df["buffer"],
                y=df["f1"],
                mode="lines+markers",
                name=method,
                line=dict(color=color, width=2.5),
                marker=dict(size=6),
                hovertemplate=(
                    f"<b>{method}</b><br>"
                    "Buffer : %{x}<br>"
                    "F1-score : %{y:.4f}<extra></extra>"
                ),
            ))

        fig.update_layout(
            title=dict(
                text=f"F1-score vs Taille du buffer  —  agrégation : <b>{func}</b>",
                font=dict(size=16),
                x=0.5,
            ),
            xaxis=dict(title="Taille du buffer", showgrid=True, gridcolor="#E0E0E0"),
            yaxis=dict(title="F1-score", range=[y_min, y_max],
                       showgrid=True, gridcolor="#E0E0E0"),
            legend=dict(title="Méthode", bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#CCCCCC", borderwidth=1),
            plot_bgcolor="white",
            hovermode="x unified",
            width=900,
            height=520,
        )

        out_path = os.path.join(OUTPUT_DIR, f"f1_scores_{func}.html")
        fig.write_html(out_path, include_plotlyjs="cdn")
        print(f"[plotly]     Sauvegardé → {out_path}")

        y_min, y_max = Y_LIMITS_DERIV[func]
        fig = go.Figure()

        for method, color in zip(METHODS, COLORS_PLOTLY):
            df = data[method].get(func)
            if df is None:
                continue
            fig.add_trace(go.Scatter(
                x=df["buffer"],
                y=df["derivate"],
                mode="lines+markers",
                name=method,
                line=dict(color=color, width=2.5),
                marker=dict(size=6),
                hovertemplate=(
                    f"<b>{method}</b><br>"
                    "Buffer : %{x}<br>"
                    "Dérivée : %{y:.6f}<extra></extra>"
                ),
            ))

        fig.update_layout(
            title=dict(
                text=f"Dérivée vs Taille du buffer  —  agrégation : <b>{func}</b>",
                font=dict(size=16),
                x=0.5,
            ),
            xaxis=dict(title="Taille du buffer", showgrid=True, gridcolor="#E0E0E0"),
            yaxis=dict(title="Dérivée", range=[y_min, y_max],
                       showgrid=True, gridcolor="#E0E0E0"),
            legend=dict(title="Méthode", bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#CCCCCC", borderwidth=1),
            plot_bgcolor="white",
            hovermode="x unified",
            width=900,
            height=520,
        )

        out_path = os.path.join(OUTPUT_DIR, f"derivate_{func}.html")
        fig.write_html(out_path, include_plotlyjs="cdn")
        print(f"[plotly]     Sauvegardé → {out_path}")

def plot_method_f1_with_mean_std_band() -> None:
    """Trace pour chaque méthode le F1 moyen et la bande ± écart type."""
    for method, color in zip(METHODS, COLORS_MPL):
        mean_path = os.path.join(BASE_DIR, method, "results_mean.csv")
        std_path = os.path.join(BASE_DIR, method, "results_std.csv")

        if not os.path.exists(mean_path):
            print(f"[WARN] Fichier manquant : {mean_path}")
            continue
        if not os.path.exists(std_path):
            print(f"[WARN] Fichier manquant : {std_path}")
            continue

        mean_df = pd.read_csv(mean_path, sep=";")
        std_df = pd.read_csv(std_path, sep=";")
        if mean_df.shape[1] < 2 or std_df.shape[1] < 2:
            raise ValueError(f"Les fichiers {mean_path} et {std_path} doivent contenir au moins deux colonnes.")

        mean_df = mean_df.iloc[:, [0, 1]].copy()
        std_df = std_df.iloc[:, [0, 1]].copy()
        mean_df.columns = ["buffer", "mean"]
        std_df.columns = ["buffer", "std"]

        merged = pd.merge(mean_df, std_df, on="buffer", how="inner")
        merged = merged.sort_values("buffer")
        merged = merged.dropna(subset=["mean", "std"])
        merged["upper"] = merged["mean"] + merged["std"]
        merged["lower"] = merged["mean"] - merged["std"]

        y_min = max(0.0, merged["lower"].min() - 0.02)
        y_max = min(1.0, merged["upper"].max() + 0.02)

        # Matplotlib PDF
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(
            merged["buffer"],
            merged["mean"],
            marker="o",
            linewidth=2,
            markersize=5,
            color=color,
            label=f"{method} moyenne F1",
        )
        ax.fill_between(
            merged["buffer"],
            merged["lower"],
            merged["upper"],
            color=color,
            alpha=0.2,
            label="± écart type",
        )
        ax.set_title(f"{method} F1-score moyen et bande ± écart type", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Taille du buffer (m)", fontsize=11)
        ax.set_ylabel("F1-score", fontsize=11)
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.2f}"))
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Courbe", fontsize=10, title_fontsize=10)
        fig.tight_layout()

        out_path = os.path.join(OUTPUT_DIR, f"{method.lower()}")
        os.makedirs(out_path, exist_ok=True)
        out_path = os.path.join(out_path, f"{method.lower()}_f1_mean_std_band.pdf")
        fig.savefig(out_path, format="pdf", dpi=150)
        plt.close(fig)
        print(f"[matplotlib] Sauvegardé → {out_path}")

        # Plotly HTML
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["upper"],
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
            name="Supérieure",
        ))
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["lower"],
            mode="lines",
            fill="tonexty",
            fillcolor=f"rgba{tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (0.2,)}",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=True,
            name="± écart type",
        ))
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["mean"],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6),
            name=f"{method} moyenne F1",
            hovertemplate=(
                "Buffer : %{x}<br>"
                "Moyenne F1 : %{y:.4f}<extra></extra>"
            ),
        ))
        fig.update_layout(
            title=dict(
                text=f"{method} F1-score moyen et bande ± écart type",
                font=dict(size=16),
                x=0.5,
            ),
            xaxis=dict(title="Taille du buffer", showgrid=True, gridcolor="#E0E0E0"),
            yaxis=dict(title="F1-score", range=[y_min, y_max],
                       showgrid=True, gridcolor="#E0E0E0"),
            legend=dict(title="Courbe", bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#CCCCCC", borderwidth=1),
            plot_bgcolor="white",
            hovermode="x unified",
            width=900,
            height=520,
        )

        out_path = os.path.join(OUTPUT_DIR, f"{method.lower()}_f1_mean_std_band.html")
        fig.write_html(out_path, include_plotlyjs="cdn")
        print(f"[plotly]     Sauvegardé → {out_path}")

def plot_method_f1_derivate_with_mean_std_band() -> None:
    """Trace pour chaque méthode le F1 moyen et la bande ± écart type."""
    for method, color in zip(METHODS, COLORS_MPL):
        mean_path = os.path.join(BASE_DIR, method, "results_mean.csv")
        std_path = os.path.join(BASE_DIR, method, "results_std.csv")

        if not os.path.exists(mean_path):
            print(f"[WARN] Fichier manquant : {mean_path}")
            continue
        if not os.path.exists(std_path):
            print(f"[WARN] Fichier manquant : {std_path}")
            continue

        mean_df = pd.read_csv(mean_path, sep=";")
        std_df = pd.read_csv(std_path, sep=";")
        if mean_df.shape[1] < 2 or std_df.shape[1] < 2:
            raise ValueError(f"Les fichiers {mean_path} et {std_path} doivent contenir au moins deux colonnes.")

        mean_df = mean_df.iloc[:, [0, 2]].copy()
        std_df = std_df.iloc[:, [0, 2]].copy()
        mean_df.columns = ["buffer", "mean of derivate"]
        std_df.columns = ["buffer", "std of derivate"]

        merged = pd.merge(mean_df, std_df, on="buffer", how="inner")
        merged = merged.sort_values("buffer")
        merged = merged.dropna(subset=["mean of derivate", "std of derivate"])
        merged["upper"] = merged["mean of derivate"] + merged["std of derivate"]
        merged["lower"] = merged["mean of derivate"] - merged["std of derivate"]

        y_min = max(-1.0, merged["lower"].min() - 0.02)
        y_max = min(1.0, merged["upper"].max() + 0.02)

        # Matplotlib PDF
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(
            merged["buffer"],
            merged["mean of derivate"],
            marker="o",
            linewidth=2,
            markersize=5,
            color=color,
            label=f"{method} moyenne F1",
        )
        ax.fill_between(
            merged["buffer"],
            merged["lower"],
            merged["upper"],
            color=color,
            alpha=0.2,
            label="± écart type",
        )
        ax.set_title(f"{method} Moyenne de la dérivée du F1-score et bande ± écart type", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Taille du buffer (m)", fontsize=11)
        ax.set_ylabel("F1-score", fontsize=11)
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.5f}"))
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Courbe", fontsize=10, title_fontsize=10)
        fig.tight_layout()

        out_path = os.path.join(OUTPUT_DIR, f"{method.lower()}")
        os.makedirs(out_path, exist_ok=True)
        out_path = os.path.join(out_path, f"{method.lower()}_f1_derivate_mean_std_band.pdf")
        fig.savefig(out_path, format="pdf", dpi=150)
        plt.close(fig)
        print(f"[matplotlib] Sauvegardé → {out_path}")

        # Plotly HTML
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["upper"],
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
            name="Supérieure",
        ))
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["lower"],
            mode="lines",
            fill="tonexty",
            fillcolor=f"rgba{tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (0.2,)}",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=True,
            name="± écart type",
        ))
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["mean of derivate"],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6),
            name=f"{method} moyenne F1",
            hovertemplate=(
                "Buffer : %{x}<br>"
                "Moyenne F1 : %{y:.4f}<extra></extra>"
            ),
        ))
        fig.update_layout(
            title=dict(
                text=f"{method} Moyenne de la dérivée du F1-score et bande ± écart type",
                font=dict(size=16),
                x=0.5,
            ),
            xaxis=dict(title="Taille du buffer", showgrid=True, gridcolor="#E0E0E0"),
            yaxis=dict(title="Dérivée du F1-score", range=[y_min, y_max],
                       showgrid=True, gridcolor="#E0E0E0"),
            legend=dict(title="Courbe", bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#CCCCCC", borderwidth=1),
            plot_bgcolor="white",
            hovermode="x unified",
            width=900,
            height=520,
        )

        out_path = os.path.join(OUTPUT_DIR, f"{method.lower()}_f1_derivate_mean_std_band.html")
        fig.write_html(out_path, include_plotlyjs="cdn")
        print(f"[plotly]     Sauvegardé → {out_path}")

def plot_all_methods_superimposed() -> None:
    """Trace toutes les méthodes superposées avec leur moyenne F1 et bande ± écart type."""
    fig_mpl, ax_mpl = plt.subplots(figsize=(9, 5))
    fig_plotly = go.Figure()

    all_lower = []
    all_upper = []

    for method, color in zip(METHODS, COLORS_MPL):
        mean_path = os.path.join(BASE_DIR, method, "results_mean.csv")
        std_path = os.path.join(BASE_DIR, method, "results_std.csv")

        if not os.path.exists(mean_path):
            print(f"[WARN] Fichier manquant : {mean_path}")
            continue
        if not os.path.exists(std_path):
            print(f"[WARN] Fichier manquant : {std_path}")
            continue

        mean_df = pd.read_csv(mean_path, sep=";")
        std_df = pd.read_csv(std_path, sep=";")
        if mean_df.shape[1] < 2 or std_df.shape[1] < 2:
            raise ValueError(f"Les fichiers {mean_path} et {std_path} doivent contenir au moins deux colonnes.")

        mean_df = mean_df.iloc[:, [0, 1]].copy()
        std_df = std_df.iloc[:, [0, 1]].copy()
        mean_df.columns = ["buffer", "mean"]
        std_df.columns = ["buffer", "std"]

        merged = pd.merge(mean_df, std_df, on="buffer", how="inner")
        merged = merged.sort_values("buffer")
        merged = merged.dropna(subset=["mean", "std"])
        merged["upper"] = merged["mean"] + merged["std"]
        merged["lower"] = merged["mean"] - merged["std"]

        all_lower.extend(merged["lower"].tolist())
        all_upper.extend(merged["upper"].tolist())

        # Matplotlib
        ax_mpl.plot(
            merged["buffer"],
            merged["mean"],
            marker="o",
            linewidth=2,
            markersize=5,
            color=color,
            label=f"{method} moyenne F1",
        )
        ax_mpl.fill_between(
            merged["buffer"],
            merged["lower"],
            merged["upper"],
            color=color,
            alpha=0.2,
            label=f"{method} ± écart type",
        )
        '''
        # Plotly
        fig_plotly.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["upper"],
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
            name=f"{method} Supérieure",
        ))
        fig_plotly.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["lower"],
            mode="lines",
            fill="tonexty",
            fillcolor=f"rgba{tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (0.2,)}",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=True,
            name=f"{method} ± écart type",
        ))
        fig_plotly.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["mean"],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6),
            name=f"{method} moyenne F1",
            hovertemplate=(
                f"<b>{method}</b><br>"
                "Buffer : %{x}<br>"
                "Moyenne F1 : %{y:.4f}<extra></extra>"
            ),
        ))'''

    # Finaliser Matplotlib
    y_min = max(0.0, min(all_lower) - 0.02)
    y_max = min(1.0, max(all_upper) + 0.02)
    ax_mpl.set_title("Toutes les méthodes : F1-score moyen et bande ± écart type", fontsize=13, fontweight="bold", pad=12)
    ax_mpl.set_xlabel("Taille du buffer (m)", fontsize=11)
    ax_mpl.set_ylabel("F1-score", fontsize=11)
    ax_mpl.set_ylim(y_min, y_max)
    ax_mpl.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.2f}"))
    ax_mpl.grid(True, linestyle="--", alpha=0.5)
    ax_mpl.legend(title="Méthode", fontsize=10, title_fontsize=10)
    fig_mpl.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, "all_methods_f1_mean_std_superimposed.pdf")
    fig_mpl.savefig(out_path, format="pdf", dpi=150)
    plt.close(fig_mpl)
    print(f"[matplotlib] Sauvegardé → {out_path}")
    '''
    # Finaliser Plotly
    fig_plotly.update_layout(
        title=dict(
            text="Toutes les méthodes : F1-score moyen et bande ± écart type",
            font=dict(size=16),
            x=0.5,
        ),
        xaxis=dict(title="Taille du buffer", showgrid=True, gridcolor="#E0E0E0"),
        yaxis=dict(title="F1-score", range=[y_min, y_max],
                   showgrid=True, gridcolor="#E0E0E0"),
        legend=dict(title="Méthode", bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#CCCCCC", borderwidth=1),
        plot_bgcolor="white",
        hovermode="x unified",
        width=900,
        height=520,
    )

    out_path = os.path.join(OUTPUT_DIR, "all_methods_f1_mean_std_superimposed.html")
    fig_plotly.write_html(out_path, include_plotlyjs="cdn")
    print(f"[plotly]     Sauvegardé → {out_path}")'''

def plot_method_f1_with_mean_std_band_derivative() -> None:
    """Trace pour chaque méthode le F1 moyen et la bande ± écart type."""
    for method, color in zip(METHODS, COLORS_MPL):
        mean_path = os.path.join(BASE_DIR, method, "results_mean.csv")
        std_path = os.path.join(BASE_DIR, method, "results_std.csv")

        if not os.path.exists(mean_path):
            print(f"[WARN] Fichier manquant : {mean_path}")
            continue
        if not os.path.exists(std_path):
            print(f"[WARN] Fichier manquant : {std_path}")
            continue

        mean_df = pd.read_csv(mean_path, sep=";")
        std_df = pd.read_csv(std_path, sep=";")
        if mean_df.shape[1] < 2 or std_df.shape[1] < 2:
            raise ValueError(f"Les fichiers {mean_path} et {std_path} doivent contenir au moins deux colonnes.")

        mean_df = mean_df.iloc[:, [0, 1]].copy()
        std_df = std_df.iloc[:, [0, 1]].copy()
        mean_df.columns = ["buffer", "mean"]
        std_df.columns = ["buffer", "std"]

        merged = pd.merge(mean_df, std_df, on="buffer", how="inner")
        merged = merged.sort_values("buffer")
        merged = merged.dropna(subset=["mean", "std"])
        merged["upper"] = merged["mean"] + merged["std"]
        merged["lower"] = merged["mean"] - merged["std"]

        y_min = max(0.0, merged["lower"].min() - 0.02)
        y_max = min(1.0, merged["upper"].max() + 0.02)

        # Matplotlib PDF
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(
            merged["buffer"],
            merged["mean"],
            marker="o",
            linewidth=2,
            markersize=5,
            color=color,
            label=f"{method} moyenne F1",
        )
        ax.fill_between(
            merged["buffer"],
            merged["lower"],
            merged["upper"],
            color=color,
            alpha=0.2,
            label="± écart type",
        )
        ax.set_title(f"{method} F1-score moyen et bande ± écart type", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Taille du buffer (m)", fontsize=11)
        ax.set_ylabel("F1-score", fontsize=11)
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.2f}"))
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Courbe", fontsize=10, title_fontsize=10)
        fig.tight_layout()

        out_path = os.path.join(OUTPUT_DIR, f"{method.lower()}_f1_mean_std_band.pdf")
        fig.savefig(out_path, format="pdf", dpi=150)
        plt.close(fig)
        print(f"[matplotlib] Sauvegardé → {out_path}")

        # Plotly HTML
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["upper"],
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
            name="Supérieure",
        ))
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["lower"],
            mode="lines",
            fill="tonexty",
            fillcolor=f"rgba{tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (0.2,)}",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=True,
            name="± écart type",
        ))
        fig.add_trace(go.Scatter(
            x=merged["buffer"],
            y=merged["mean"],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6),
            name=f"{method} moyenne F1",
            hovertemplate=(
                "Buffer : %{x}<br>"
                "Moyenne F1 : %{y:.4f}<extra></extra>"
            ),
        ))
        fig.update_layout(
            title=dict(
                text=f"{method} F1-score moyen et bande ± écart type",
                font=dict(size=16),
                x=0.5,
            ),
            xaxis=dict(title="Taille du buffer", showgrid=True, gridcolor="#E0E0E0"),
            yaxis=dict(title="F1-score", range=[y_min, y_max],
                       showgrid=True, gridcolor="#E0E0E0"),
            legend=dict(title="Courbe", bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#CCCCCC", borderwidth=1),
            plot_bgcolor="white",
            hovermode="x unified",
            width=900,
            height=520,
        )

        out_path = os.path.join(OUTPUT_DIR, f"{method.lower()}_f1_mean_std_band.html")
        fig.write_html(out_path, include_plotlyjs="cdn")
        print(f"[plotly]     Sauvegardé → {out_path}")

def plot_all_methods_superimposed_derivative() -> None:
    """Trace toutes les méthodes superposées avec leur moyenne F1 et bande ± écart type."""
    fig_mpl, ax_mpl = plt.subplots(figsize=(9, 5))
    fig_plotly = go.Figure()

    all_lower = []
    all_upper = []

    for method, color in zip(METHODS, COLORS_MPL):
        mean_path = os.path.join(BASE_DIR, method, "results_mean.csv")
        std_path = os.path.join(BASE_DIR, method, "results_std.csv")

        if not os.path.exists(mean_path):
            print(f"[WARN] Fichier manquant : {mean_path}")
            continue
        if not os.path.exists(std_path):
            print(f"[WARN] Fichier manquant : {std_path}")
            continue

        mean_df = pd.read_csv(mean_path, sep=";")
        std_df = pd.read_csv(std_path, sep=";")
        if mean_df.shape[1] < 2 or std_df.shape[1] < 2:
            raise ValueError(f"Les fichiers {mean_path} et {std_path} doivent contenir au moins deux colonnes.")

        mean_df = mean_df.iloc[:, [0, 2]].copy()
        std_df = std_df.iloc[:, [0, 2]].copy()
        mean_df.columns = ["buffer", "mean of derivate"]
        std_df.columns = ["buffer", "std of derivate"]

        merged = pd.merge(mean_df, std_df, on="buffer", how="inner")
        merged = merged.sort_values("buffer")
        merged = merged.dropna(subset=["mean of derivate", "std of derivate"])
        merged["upper"] = merged["mean of derivate"] + merged["std of derivate"]
        merged["lower"] = merged["mean of derivate"] - merged["std of derivate"]

        all_lower.extend(merged["lower"].tolist())
        all_upper.extend(merged["upper"].tolist())

        # Matplotlib
        ax_mpl.plot(
            merged["buffer"],
            merged["mean of derivate"],
            marker="o",
            linewidth=2,
            markersize=5,
            color=color,
            label=f"{method} moyenne dérivée F1",
        )
        ax_mpl.fill_between(
            merged["buffer"],
            merged["lower"],
            merged["upper"],
            color=color,
            alpha=0.2,
            label=f"{method} ± écart type",
        )

    # Finaliser Matplotlib
    y_min = max(-1.0, min(all_lower) - 0.02)
    y_max = min(1.0, max(all_upper) + 0.02)
    ax_mpl.set_title("Toutes les méthodes : Moyenne de la dérivée du F1-score et bande ± écart type", fontsize=13, fontweight="bold", pad=12)
    ax_mpl.set_xlabel("Taille du buffer (m)", fontsize=11)
    ax_mpl.set_ylabel("Dérivée du F1-score", fontsize=11)
    ax_mpl.set_ylim(y_min, y_max)
    ax_mpl.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.5f}"))
    ax_mpl.grid(True, linestyle="--", alpha=0.5)
    ax_mpl.legend(title="Méthode", fontsize=10, title_fontsize=10)
    fig_mpl.tight_layout()
    fig_mpl.savefig(os.path.join(OUTPUT_DIR, "all_methods_f1_derivate_mean_std_superimposed.pdf"), format="pdf", dpi=150)
    plt.close(fig_mpl)
    print(f"[matplotlib] Sauvegardé → {os.path.join(OUTPUT_DIR, 'all_methods_f1_derivate_mean_std_superimposed.pdf')}")

if __name__ == "__main__":
    print("Chargement des données…")
    data = load_data()

    print("\n── Génération des figures matplotlib (PDF) ──")
    plot_matplotlib(data)

    print("\n── Génération des figures plotly (HTML) ──")
    plot_plotly(data)

    print("\n── Génération des figures comparaison méthodes F1 avec moyenne ± écart type ──")
    plot_method_f1_with_mean_std_band()

    print("\n── Génération du graphe superposé de toutes les méthodes F1 moyen ± écart type ──")
    plot_all_methods_superimposed()

    print("\n── Génération des figures comparaison méthodes dérivée F1 avec moyenne ± écart type ──")
    plot_method_f1_derivate_with_mean_std_band()

    print("\n── Génération du graphe superposé de toutes les méthodes dérivée F1 moyen ± écart type ──")
    plot_all_methods_superimposed_derivative()


    print(f"\n✓ Terminé. Figures dans : {os.path.abspath(OUTPUT_DIR)}/")