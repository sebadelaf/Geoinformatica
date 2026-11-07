"""Figura de la serie 2018-2024 del área total con NDSI >= 0,4 (informe, figura 2).

Uso:
    python src/figura_serie_ndsi.py
Entrada: resultados/ndsi_por_glaciar.csv (src/ndsi.py)
Salida:  figuras/serie_ndsi.png
"""
import matplotlib.pyplot as plt
import pandas as pd

import config as C


def main():
    d = pd.read_csv(C.RESULTADOS / "ndsi_por_glaciar.csv", dtype={C.ID_COL: str})
    s = d.groupby("anio")["area_nieve_m2"].sum() / 1e6
    secos = [y for y in s.index if y in (2020, 2022, 2023)]

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(s.index, s.values, color="#4a6fa5", lw=2, marker="o", zorder=2)
    ax.scatter(secos, s.loc[secos], s=70, facecolor="white", edgecolor="#c0392b", lw=2, zorder=3,
               label="Veranos tras inviernos secos")
    for y, v in s.items():
        ax.annotate(f"{v:.2f}".replace(".", ","), (y, v), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8)
    ax.set_xticks(s.index)
    ax.set_ylim(0, s.max() * 1.18)
    ax.set_ylabel("Área con NDSI ≥ 0,4 (km²)")
    ax.set_xlabel("Verano (febrero–marzo)")
    ax.set_title(f"Glaciaretes del Maipo alto (n = {d[C.ID_COL].nunique()}): área con nieve o hielo al fin del verano",
                 fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#dddddd", lw=0.6)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    fig.text(0.01, -0.02, "Fuente: Sentinel-2 L2A (Copernicus, Planetary Computer); IPG2022 (DGA). "
             "Script: src/figura_serie_ndsi.py", fontsize=7)
    C.FIGURAS.mkdir(exist_ok=True)
    fig.savefig(C.FIGURAS / "serie_ndsi.png", dpi=200, bbox_inches="tight")
    print("Guardado: figuras/serie_ndsi.png")


if __name__ == "__main__":
    main()
