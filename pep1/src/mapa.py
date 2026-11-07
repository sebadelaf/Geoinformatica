"""Mapa de resultados: glaciaretes del Maipo alto coloreados por cambio de embedding.

Cumple la norma del curso: título, leyenda, escala, norte, fuente y CRS (EPSG:32719).

Uso:
    python src/mapa.py 
Salida:
    figuras/mapa_cambio_embedding.png
"""
import argparse

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

import config as C


def barra_escala(ax, largo_m=5000):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x, y = x0 + 0.06 * (x1 - x0), y0 + 0.05 * (y1 - y0)
    ax.plot([x, x + largo_m], [y, y], color="black", lw=3)
    ax.text(x + largo_m / 2, y + 0.012 * (y1 - y0), f"{largo_m / 1000:.0f} km", ha="center", fontsize=8)


def norte(ax):
    ax.annotate("N", xy=(0.94, 0.95), xytext=(0.94, 0.86), xycoords="axes fraction",
                ha="center", fontsize=11, fontweight="bold",
                arrowprops=dict(facecolor="black", width=3, headwidth=9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anio-a", type=int, default=C.PAR_PRINCIPAL[0])
    ap.add_argument("--anio-b", type=int, default=C.PAR_PRINCIPAL[1])
    a = ap.parse_args()
    col = f"cambio_emb_{a.anio_a}_{a.anio_b}"

    glac = gpd.read_file(C.INVENTARIO, layer=C.CAPA)
    t = pd.read_csv(C.RESULTADOS / "por_glaciar.csv", dtype={C.ID_COL: str})
    g = glac[[C.ID_COL, "geometry"]].merge(t[[C.ID_COL, col, "no_concluyente"]], on=C.ID_COL)
    # Los glaciaretes son chicos: se dibujan como puntos de tamaño fijo para que se vean
    p = g.copy()
    p["geometry"] = g.geometry.representative_point()

    fig, ax = plt.subplots(figsize=(7, 10))
    p[~p.no_concluyente].plot(ax=ax, column=col, cmap="viridis", markersize=14, legend=True,
                              legend_kwds={"label": f"Cambio de embedding {a.anio_a}-{a.anio_b} (1 - coseno)",
                                           "shrink": 0.6})
    p[p.no_concluyente].plot(ax=ax, color="lightgrey", markersize=8, marker="x",
                             label=f"No concluyente (< {C.MIN_PIX_20M} píxeles de 20 m)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title(f"Glaciaretes del Maipo alto (subcuenca {C.COD_SCUEN}):\n"
                 f"cambio de embedding AlphaEarth {a.anio_a}-{a.anio_b}")
    ax.set_xlabel("Este (m)")
    ax.set_ylabel("Norte (m)")
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.tick_params(axis="x", labelrotation=45, labelsize=7)
    ax.tick_params(axis="y", labelsize=7)
    barra_escala(ax)
    norte(ax)
    fig.text(0.01, 0.01, "Fuente: IPG2022 (DGA); Satellite Embedding V1 (Google). "
             f"CRS: {C.CRS_MEDIDA} (WGS84 / UTM 19S). Script: src/mapa.py", fontsize=7)
    C.FIGURAS.mkdir(exist_ok=True)
    fig.savefig(C.FIGURAS / "mapa_cambio_embedding.png", dpi=200, bbox_inches="tight")
    print("Guardado: figuras/mapa_cambio_embedding.png")


if __name__ == "__main__":
    main()
