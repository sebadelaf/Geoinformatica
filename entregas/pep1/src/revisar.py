"""Revisiones rápidas de los resultados, para no escribir comandos largos en la terminal.

Uso:
    python src/revisar.py ndsi         # resumen del NDSI por año
    python src/revisar.py perdida      # 5 glaciares con mayor pérdida de nieve/hielo (par principal)
    python src/revisar.py embeddings   # resumen del cambio de embedding por par de años
    python src/revisar.py umbral       # glaciares cuyo cambio supera el p95 del ruido de fondo
    python src/revisar.py correlacion  # ¿el embedding cambia más donde el NDSI pierde más? (Spearman)
    python src/revisar.py ee           # prueba la conexión a Earth Engine
"""
import os
import sys

import pandas as pd

import config as C


def ndsi():
    d = pd.read_csv(C.RESULTADOS / "ndsi_por_glaciar.csv", dtype={C.ID_COL: str})
    print(f"Filas: {len(d)} (esperado: 322 x número de años)\n")
    r = d.groupby("anio").agg(
        frac_nieve_mediana=("frac_nieve", "median"),
        area_nieve_km2_total=("area_nieve_m2", lambda s: s.sum() / 1e6),
        pix_validos_mediana=("n_pix_validos", "median"),
        no_concluyentes=("no_concluyente", "sum"),
        fechas=("n_fechas", "first"),
    )
    print(r.round(3).to_string())


def perdida():
    a, b = C.PAR_PRINCIPAL
    d = pd.read_csv(C.RESULTADOS / "ndsi_por_glaciar.csv", dtype={C.ID_COL: str})
    d = d[~d.no_concluyente]
    w = d.pivot(index=C.ID_COL, columns="anio", values="area_nieve_m2")
    if a not in w or b not in w:
        sys.exit(f"Faltan los años {a} y {b} en ndsi_por_glaciar.csv")
    top = (w[a] - w[b]).sort_values(ascending=False).head(5).rename(f"perdida_m2_{a}_{b}")
    print(pd.concat([w.loc[top.index, [a, b]], top], axis=1).to_string())


def embeddings():
    d = pd.read_csv(C.RESULTADOS / "embedding_por_glaciar.csv", dtype={C.ID_COL: str})
    print(f"Filas: {len(d)}\n")
    r = d.groupby(["anio_a", "anio_b"]).agg(
        cambio_mediana=("cambio", "median"), cambio_max=("cambio", "max"),
        sin_dato=("cambio", lambda s: int(s.isna().sum())), no_concluyentes=("no_concluyente", "sum"))
    print(r.round(4).to_string())
    f = C.RESULTADOS / "embedding_fondo.csv"
    if f.exists():
        print("\nRuido de fondo (terreno sin glaciar):")
        print(pd.read_csv(f).round(4).to_string(index=False))


def umbral():
    d = pd.read_csv(C.RESULTADOS / "embedding_por_glaciar.csv", dtype={C.ID_COL: str})
    f = pd.read_csv(C.RESULTADOS / "embedding_fondo.csv")[["anio_a", "anio_b", "cambio_p95"]]
    d = d[~d.no_concluyente].merge(f, on=["anio_a", "anio_b"])
    d["supera_p95"] = d["cambio"] > d["cambio_p95"]
    r = d.groupby(["anio_a", "anio_b"]).agg(
        glaciares=("supera_p95", "size"), supera_p95=("supera_p95", "sum"),
        umbral_p95=("cambio_p95", "first"), cambio_mediana=("cambio", "median"))
    r["pct_supera"] = 100 * r["supera_p95"] / r["glaciares"]
    print("Glaciares concluyentes cuyo cambio de embedding supera el p95 del terreno sin glaciar:\n")
    print(r.round(4).to_string())


def correlacion():
    a, b = C.PAR_PRINCIPAL
    t = pd.read_csv(C.RESULTADOS / "por_glaciar.csv", dtype={C.ID_COL: str})
    t = t[~t.no_concluyente].copy()
    emb = f"cambio_emb_{a}_{b}"
    ini = f"area_nieve_m2_{a}"
    t["perdida_abs_m2"] = t[ini] - t[f"area_nieve_m2_{b}"]
    t["perdida_rel"] = t["perdida_abs_m2"] / t[ini].where(t[ini] > 0)
    print(f"Glaciares concluyentes: {len(t)}. Par {a}-{b}. Correlación de Spearman (Pearson sobre rangos) con {emb}:\n")
    for col in ["perdida_abs_m2", "perdida_rel", "perdida_min_m2", "area_km2"]:
        if col in t:
            sub = t[[col, emb]].dropna()
            print(f"  {col:16s} rho = {sub[col].rank().corr(sub[emb].rank()):+.3f}  (n = {len(sub)})")
    print("\nrho cerca de 0: el embedding no sigue la pérdida que mide el NDSI.")


def probar_ee():
    import ee
    proyecto = os.environ.get("EE_PROJECT")
    if not proyecto:
        sys.exit("Falta EE_PROJECT. En PowerShell:  $env:EE_PROJECT=\"tu-proyecto\"")
    ee.Initialize(project=proyecto)
    n = ee.ImageCollection(C.EMB_COLECCION).filterDate("2023-01-01", "2024-01-01").size().getInfo()
    print(f"Conexión OK con el proyecto {proyecto}. Teselas AlphaEarth 2023 en el mundo: {n}")


if __name__ == "__main__":
    ops = {"ndsi": ndsi, "perdida": perdida, "embeddings": embeddings, "umbral": umbral, "correlacion": correlacion, "ee": probar_ee}
    if len(sys.argv) != 2 or sys.argv[1] not in ops:
        sys.exit(__doc__)
    ops[sys.argv[1]]()
