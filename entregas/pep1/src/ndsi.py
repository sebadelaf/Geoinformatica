"""NDSI de fin de verano por glaciarete con Sentinel-2 L2A (Microsoft Planetary Computer).

Para cada año: escenas del 1 de febrero al 31 de marzo con menos de 10 % de nubes,
máscara SCL, NDSI = (B03 - B11) / (B03 + B11) en grilla de 20 m (EPSG:32719),
mediana temporal y estadística zonal por polígono.

Regla de pertenencia de un píxel: el píxel cuenta si su CENTRO cae dentro del
polígono (rasterize con all_touched=False). Es la misma regla que usa Earth Engine
con reductores no ponderados, lo que permite la verificación cruzada.

Uso:
    python src/ndsi.py                 # todos los años de config.ANIOS_NDSI
    python src/ndsi.py --anios 2019 2023

Salidas:
    resultados/ndsi_por_glaciar.csv   (una fila por glaciar y año)
    resultados/ndsi_escenas.csv       (qué escenas se usaron: trazabilidad)
    datos/cache/ndsi_<año>.tif        (mediana de NDSI, para mapas y verificación)
"""
import argparse

import geopandas as gpd
import numpy as np
import odc.stac
import pandas as pd
import planetary_computer
import pystac_client
import rasterio
import xarray as xr
from rasterio.features import rasterize

import config as C

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"


def buscar_escenas(bbox_wgs84, anio):
    cat = pystac_client.Client.open(STAC, modifier=planetary_computer.sign_inplace)
    ini, fin = C.NDSI_MESES
    items = cat.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox_wgs84,
        datetime=f"{anio}-{ini}/{anio}-{fin}",
        query={"eo:cloud_cover": {"lt": C.NUBES_MAX}},
    ).item_collection()
    return list(items)


def cargar_ndsi(items, bbox_wgs84):
    """Devuelve (ndsi por fecha, geobox). Corrige el desfase de -1000 del baseline 04.00."""
    viejos = [i for i in items if float(i.properties.get("s2:processing_baseline", "0")) < 4.0]
    nuevos = [i for i in items if float(i.properties.get("s2:processing_baseline", "0")) >= 4.0]
    partes = []
    for grupo, desfase in ((viejos, 0), (nuevos, -1000)):
        if not grupo:
            continue
        ds = odc.stac.load(
            grupo, bands=["B03", "B11", "SCL"], crs=C.CRS_MEDIDA, resolution=C.NDSI_RES_M,
            bbox=bbox_wgs84, groupby="solar_day", chunks={"x": 2048, "y": 2048},
            resampling={"B03": "average", "B11": "nearest", "SCL": "nearest"},
        )
        mala = ds.SCL.isin(list(C.SCL_DESCARTAR)) | (ds.B03 == 0) | (ds.B11 == 0)
        verde = (ds.B03.astype("float32") + desfase) / 10000
        swir = (ds.B11.astype("float32") + desfase) / 10000
        ndsi = ((verde - swir) / (verde + swir)).where(~mala)
        partes.append(ndsi.clip(-1, 1))
    ndsi = xr.concat(partes, dim="time").sortby("time")
    return ndsi, ndsi.odc.geobox


def zonal(ndsi2d, transform, glaciares):
    """Estadística zonal con etiquetas: un entero por glaciar, 0 fuera."""
    etiquetas = rasterize(
        ((g, i + 1) for i, g in enumerate(glaciares.geometry)),
        out_shape=ndsi2d.shape, transform=transform, fill=0, all_touched=False, dtype="int32",
    )
    n = len(glaciares) + 1
    valido = np.isfinite(ndsi2d)
    total = np.bincount(etiquetas.ravel(), minlength=n)
    validos = np.bincount(etiquetas[valido], minlength=n)
    nieve = np.bincount(etiquetas[valido & (ndsi2d >= C.NDSI_UMBRAL)], minlength=n)
    suma = np.bincount(etiquetas[valido], weights=ndsi2d[valido], minlength=n)
    with np.errstate(invalid="ignore", divide="ignore"):
        df = pd.DataFrame({
            C.ID_COL: glaciares[C.ID_COL].values,
            "n_pix_total": total[1:],
            "n_pix_validos": validos[1:],
            "ndsi_medio": suma[1:] / validos[1:],
            "frac_nieve": nieve[1:] / validos[1:],
            "area_nieve_m2": nieve[1:] * C.NDSI_RES_M ** 2,
        })
    df["no_concluyente"] = df["n_pix_validos"] < C.MIN_PIX_20M
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anios", type=int, nargs="+", default=C.ANIOS_NDSI)
    a = ap.parse_args()

    glac = gpd.read_file(C.INVENTARIO, layer=C.CAPA)
    caja = glac.total_bounds + np.array([-1, -1, 1, 1]) * C.MARGEN_M
    bbox_wgs84 = list(gpd.GeoSeries.from_xy([caja[0], caja[2]], [caja[1], caja[3]], crs=C.CRS_MEDIDA)
                      .to_crs(4326).total_bounds)

    (C.DATOS / "cache").mkdir(parents=True, exist_ok=True)
    filas, escenas = [], []
    for anio in a.anios:
        items = buscar_escenas(bbox_wgs84, anio)
        print(f"{anio}: {len(items)} escenas con < {C.NUBES_MAX} % de nubes")
        if not items:
            continue
        escenas += [{"anio": anio, "id": i.id, "fecha": i.properties["datetime"],
                     "nubes_pct": i.properties.get("eo:cloud_cover"),
                     "baseline": i.properties.get("s2:processing_baseline")} for i in items]
        ndsi, geobox = cargar_ndsi(items, bbox_wgs84)
        mediana = ndsi.median("time", skipna=True).compute().values.astype("float32")
        n_obs = int(ndsi.sizes["time"])

        with rasterio.open(C.DATOS / "cache" / f"ndsi_{anio}.tif", "w", driver="GTiff",
                           height=mediana.shape[0], width=mediana.shape[1], count=1,
                           dtype="float32", crs=C.CRS_MEDIDA, transform=geobox.affine,
                           nodata=np.nan, compress="deflate") as dst:
            dst.write(mediana, 1)

        df = zonal(mediana, geobox.affine, glac)
        df.insert(1, "anio", anio)
        df["n_fechas"] = n_obs
        filas.append(df)

    C.RESULTADOS.mkdir(exist_ok=True)
    pd.concat(filas).to_csv(C.RESULTADOS / "ndsi_por_glaciar.csv", index=False, float_format="%.4f")
    pd.DataFrame(escenas).to_csv(C.RESULTADOS / "ndsi_escenas.csv", index=False)
    print("Guardado: resultados/ndsi_por_glaciar.csv y resultados/ndsi_escenas.csv")


if __name__ == "__main__":
    main()
