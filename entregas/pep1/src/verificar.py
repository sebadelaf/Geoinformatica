"""Verificación independiente de tres cifras del informe (criterio A, 3 puntos).

1. Área total de los glaciaretes: área en UTM 19S (GeoPandas) frente al área
   geodésica sobre el elipsoide WGS84 (pyproj.Geod), sin proyectar.
2. NDSI de un glaciar: Planetary Computer (src/ndsi.py) frente a Earth Engine
   (COPERNICUS/S2_SR_HARMONIZED, que ya trae corregido el desfase del baseline 04.00).
3. Cambio de embedding de un glaciar: Earth Engine reduceRegions (src/embeddings.py)
   frente a NumPy sobre los píxeles exportados uno a uno.

Uso:
    python src/verificar.py --glaciar <id> --anio 2023 
    python src/verificar.py --solo-area      # no requiere Earth Engine
Salida:
    resultados/verificacion.csv
"""
import argparse

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Geod

import config as C


def area_geodesica_km2(glac):
    geod = Geod(ellps="WGS84")
    return sum(abs(geod.geometry_area_perimeter(g)[0]) for g in glac.to_crs(4326).geometry) / 1e6


def ndsi_ee(geom, anio):
    import ee
    ini, fin = C.NDSI_MESES

    def preparar(img):
        scl = img.select("SCL")
        mala = scl.remap(list(C.SCL_DESCARTAR), [1] * len(C.SCL_DESCARTAR), 0)
        return img.normalizedDifference(["B3", "B11"]).rename("ndsi").updateMask(mala.Not())

    col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
           .filterBounds(geom).filterDate(f"{anio}-{ini}", f"{anio}-{fin}T23:59:59")
           .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", C.NUBES_MAX)).map(preparar))
    med = col.median()
    nieve = med.gte(C.NDSI_UMBRAL).rename("nieve")
    r = med.addBands(nieve).reduceRegion(
        reducer=ee.Reducer.mean().unweighted().combine(ee.Reducer.count(), sharedInputs=True),
        geometry=geom, scale=C.NDSI_RES_M, crs=C.CRS_MEDIDA).getInfo()
    return r.get("nieve_mean"), r.get("ndsi_count")


def cambio_numpy(geom, anio_a, anio_b):
    import ee
    from embeddings import embedding
    bandas = [f"A{i:02d}" for i in range(64)]
    a = embedding(anio_a, geom).select(bandas)
    b = embedding(anio_b, geom).select(bandas, [f"B{i:02d}" for i in range(64)])
    pix = a.addBands(b).sample(region=geom, scale=C.EMB_RES_M, projection=C.CRS_MEDIDA,
                               geometries=False).getInfo()["features"]
    if not pix:
        return None, 0
    va = np.array([[p["properties"][f"A{i:02d}"] for i in range(64)] for p in pix])
    vb = np.array([[p["properties"][f"B{i:02d}"] for i in range(64)] for p in pix])
    return float(np.mean(1 - np.sum(va * vb, axis=1))), len(pix)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glaciar")
    ap.add_argument("--anio", type=int, default=2023)
    ap.add_argument("--anio-a", type=int, default=C.PAR_PRINCIPAL[0])
    ap.add_argument("--anio-b", type=int, default=C.PAR_PRINCIPAL[1])
    ap.add_argument("--solo-area", action="store_true")
    a = ap.parse_args()

    glac = gpd.read_file(C.INVENTARIO, layer=C.CAPA)
    filas = []
    utm = glac.geometry.area.sum() / 1e6
    geo = area_geodesica_km2(glac)
    filas.append({"cifra": "area_total_km2", "camino_1": "GeoPandas EPSG:32719", "valor_1": utm,
                  "camino_2": "pyproj.Geod WGS84", "valor_2": geo,
                  "dif_relativa_pct": 100 * (utm - geo) / geo})

    if "area_dga_km2" in glac.columns:
        dga = glac["area_dga_km2"].sum()
        filas.append({"cifra": "area_total_km2", "camino_1": "GeoPandas EPSG:32719", "valor_1": utm,
                      "camino_2": "Atributo AREA_KM2 del IPG2022 (DGA)", "valor_2": dga,
                      "dif_relativa_pct": 100 * (utm - dga) / dga})

    if not a.solo_area:
        if not a.glaciar:
            raise SystemExit("Indicar --glaciar <id> (elegir uno grande, con > 50 píxeles).")
        from embeddings import a_ee, iniciar
        iniciar()
        g = glac[glac[C.ID_COL] == a.glaciar]
        if g.empty:
            raise SystemExit(f"No existe el glaciar {a.glaciar}. Copia el id tal cual desde: python src/revisar.py perdida")
        geom = a_ee(g.to_crs(4326).geometry.iloc[0])

        pc = pd.read_csv(C.RESULTADOS / "ndsi_por_glaciar.csv", dtype={C.ID_COL: str})
        f = pc[(pc[C.ID_COL] == a.glaciar) & (pc.anio == a.anio)].iloc[0]
        frac_ee, n_ee = ndsi_ee(geom, a.anio)
        filas.append({"cifra": f"frac_nieve {a.glaciar} {a.anio}",
                      "camino_1": f"Planetary Computer (n={int(f.n_pix_validos)})", "valor_1": f.frac_nieve,
                      "camino_2": f"Earth Engine (n={n_ee})", "valor_2": frac_ee,
                      "dif_relativa_pct": None if not frac_ee else 100 * (f.frac_nieve - frac_ee) / frac_ee})

        em = pd.read_csv(C.RESULTADOS / "embedding_por_glaciar.csv", dtype={C.ID_COL: str})
        e = em[(em[C.ID_COL] == a.glaciar) & (em.anio_a == a.anio_a) & (em.anio_b == a.anio_b)].iloc[0]
        v_np, n_np = cambio_numpy(geom, a.anio_a, a.anio_b)
        filas.append({"cifra": f"cambio_emb {a.glaciar} {a.anio_a}-{a.anio_b}",
                      "camino_1": f"reduceRegions (n={int(e.n_pix)})", "valor_1": e.cambio,
                      "camino_2": f"NumPy por píxel (n={n_np})", "valor_2": v_np,
                      "dif_relativa_pct": None if not v_np else 100 * (e.cambio - v_np) / v_np})

    df = pd.DataFrame(filas)
    C.RESULTADOS.mkdir(exist_ok=True)
    df.to_csv(C.RESULTADOS / "verificacion.csv", index=False, float_format="%.5f")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
