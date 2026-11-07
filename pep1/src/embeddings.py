"""Cambio de embedding AlphaEarth por glaciarete (Google Earth Engine).

Los vectores AlphaEarth (64 bandas A00-A63) tienen largo 1, así que el producto
punto entre dos años es el coseno de su ángulo. Cambio por píxel = 1 - coseno:
0 = sin cambio, 2 = opuesto. Por glaciar se promedia SIN ponderar sobre los
píxeles de 10 m cuyo centro cae en el polígono (EPSG:32719).

Requiere una cuenta de Earth Engine. Antes de correr:
    earthengine authenticate
    export EE_PROJECT=<id-de-tu-proyecto-de-cloud>
Las credenciales quedan en ~/.config/earthengine, fuera del repositorio.

Uso:
    python src/embeddings.py            # pares base 2018 vs cada año + años consecutivos
    python src/embeddings.py --fondo    # además, ruido de fondo fuera de los glaciares

Salidas:
    resultados/embedding_por_glaciar.csv   (glaciar, anio_a, anio_b, cambio, n_pix)
    resultados/embedding_fondo.csv         (percentiles del cambio en terreno sin glaciar)
"""
import argparse
import json
import os

import ee
import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping

import config as C


def iniciar():
    proyecto = os.environ.get("EE_PROJECT")
    if not proyecto:
        raise SystemExit("Definir EE_PROJECT con el id del proyecto de Google Cloud.")
    ee.Initialize(project=proyecto)


def a_ee(geom_wgs84):
    return ee.Geometry(mapping(geom_wgs84), "EPSG:4326", False)


def coleccion_glaciares(glac):
    g = glac.to_crs(4326)
    return ee.FeatureCollection([
        ee.Feature(a_ee(geom), {C.ID_COL: gid}) for gid, geom in zip(g[C.ID_COL], g.geometry)
    ])


def embedding(anio, region):
    return (ee.ImageCollection(C.EMB_COLECCION)
            .filterDate(f"{anio}-01-01", f"{anio + 1}-01-01")
            .filterBounds(region).mosaic())


def cambio(anio_a, anio_b, region):
    a, b = embedding(anio_a, region), embedding(anio_b, region)
    coseno = a.multiply(b).reduce(ee.Reducer.sum())
    return ee.Image(1).subtract(coseno).rename("cambio")


def pares():
    """Pares (año menor, año mayor): base 2018 contra cada año, consecutivos y el par principal."""
    base = [tuple(sorted((C.ANIO_BASE, y))) for y in C.ANIOS if y != C.ANIO_BASE]
    consecutivos = [(y - 1, y) for y in C.ANIOS[1:]]
    return sorted(set(base + consecutivos + [tuple(C.PAR_PRINCIPAL)]))


def cambio_por_glaciar(fc, region, anio_a, anio_b):
    red = ee.Reducer.mean().unweighted().combine(ee.Reducer.count(), sharedInputs=True)
    res = cambio(anio_a, anio_b, region).reduceRegions(
        collection=fc, reducer=red, scale=C.EMB_RES_M, crs=C.CRS_MEDIDA).getInfo()
    return pd.DataFrame([{
        C.ID_COL: f["properties"][C.ID_COL], "anio_a": anio_a, "anio_b": anio_b,
        "cambio": f["properties"].get("mean"), "n_pix": f["properties"].get("count", 0),
    } for f in res["features"]])


def region_fondo(glac):
    """Envolvente convexa de los glaciares + 2 km, menos los glaciares + 300 m."""
    region = glac.union_all().convex_hull.buffer(C.FONDO_REGION_M)
    excluir = glac.buffer(C.FONDO_EXCLUSION_M).union_all()
    return gpd.GeoSeries([region.difference(excluir)], crs=C.CRS_MEDIDA).to_crs(4326).iloc[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fondo", action="store_true")
    a = ap.parse_args()
    iniciar()

    glac = gpd.read_file(C.INVENTARIO, layer=C.CAPA)
    fc = coleccion_glaciares(glac)
    region = fc.geometry().bounds()

    filas = []
    for anio_a, anio_b in pares():
        print(f"cambio {anio_a}->{anio_b}")
        filas.append(cambio_por_glaciar(fc, region, anio_a, anio_b))
    df = pd.concat(filas)
    df["no_concluyente"] = df["n_pix"] < C.MIN_PIX_10M
    C.RESULTADOS.mkdir(exist_ok=True)
    df.to_csv(C.RESULTADOS / "embedding_por_glaciar.csv", index=False, float_format="%.5f")

    if a.fondo:
        geom = a_ee(region_fondo(glac))
        filas = []
        for anio_a, anio_b in pares():
            p = cambio(anio_a, anio_b, geom).reduceRegion(
                reducer=ee.Reducer.percentile([50, 90, 95, 99]), geometry=geom,
                scale=30, crs=C.CRS_MEDIDA, maxPixels=1e9, bestEffort=True).getInfo()
            filas.append({"anio_a": anio_a, "anio_b": anio_b, **p})
        pd.DataFrame(filas).to_csv(C.RESULTADOS / "embedding_fondo.csv", index=False, float_format="%.5f")
    print("Guardado: resultados/embedding_por_glaciar.csv")


if __name__ == "__main__":
    main()
