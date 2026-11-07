"""Une NDSI y embeddings en una tabla por glaciar y arma la tabla de resultados del informe.

Uso:
    python src/tabla.py            # usa config.PAR_PRINCIPAL

Salidas:
    resultados/por_glaciar.csv        (una fila por glaciar; producida por src/tabla.py)
    resultados/top10_perdida_ndsi.csv (los 10 con mayor pérdida de superficie con NDSI >= 0,4)
"""
import argparse

import geopandas as gpd
import pandas as pd

import config as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anio-a", type=int, default=C.PAR_PRINCIPAL[0])
    ap.add_argument("--anio-b", type=int, default=C.PAR_PRINCIPAL[1])
    a = ap.parse_args()

    glac = gpd.read_file(C.INVENTARIO, layer=C.CAPA)
    base = pd.DataFrame(glac.drop(columns="geometry"))[[C.ID_COL, "area_km2", "pix20_teoricos"]]

    ndsi = pd.read_csv(C.RESULTADOS / "ndsi_por_glaciar.csv", dtype={C.ID_COL: str})
    ancho = ndsi.pivot(index=C.ID_COL, columns="anio", values=["area_nieve_m2", "n_pix_validos"])
    ancho.columns = [f"{v}_{y}" for v, y in ancho.columns]
    ancho = ancho.reset_index()

    emb = pd.read_csv(C.RESULTADOS / "embedding_por_glaciar.csv", dtype={C.ID_COL: str})
    par = emb[(emb.anio_a == a.anio_a) & (emb.anio_b == a.anio_b)][[C.ID_COL, "cambio", "n_pix"]]
    par = par.rename(columns={"cambio": f"cambio_emb_{a.anio_a}_{a.anio_b}", "n_pix": "n_pix10_emb"})

    t = base.merge(ancho, on=C.ID_COL, how="left").merge(par, on=C.ID_COL, how="left")
    ca, cb = f"area_nieve_m2_{a.anio_a}", f"area_nieve_m2_{a.anio_b}"
    t[f"perdida_nieve_m2_{a.anio_a}_{a.anio_b}"] = t[ca] - t[cb]
    # Métrica robusta a la nieve estacional: mínimo de cada ventana
    ini = [f"area_nieve_m2_{y}" for y in C.VENTANA_INICIAL if f"area_nieve_m2_{y}" in t]
    fin = [f"area_nieve_m2_{y}" for y in C.VENTANA_FINAL if f"area_nieve_m2_{y}" in t]
    if ini and fin:
        t["area_min_inicial_m2"] = t[ini].min(axis=1)
        t["area_min_final_m2"] = t[fin].min(axis=1)
        t["perdida_min_m2"] = t["area_min_inicial_m2"] - t["area_min_final_m2"]
    t["no_concluyente"] = (
        (t[f"n_pix_validos_{a.anio_a}"].fillna(0) < C.MIN_PIX_20M)
        | (t[f"n_pix_validos_{a.anio_b}"].fillna(0) < C.MIN_PIX_20M)
        | (t["n_pix10_emb"].fillna(0) < C.MIN_PIX_10M)
    )
    print(f"Glaciares en inventario: {len(base)}; con NDSI: {ancho[C.ID_COL].nunique()}; "
          f"con embedding: {par[C.ID_COL].nunique()}; no concluyentes: {int(t.no_concluyente.sum())}")

    t.to_csv(C.RESULTADOS / "por_glaciar.csv", index=False, float_format="%.4f")
    top = (t[~t.no_concluyente]
           .sort_values(f"perdida_nieve_m2_{a.anio_a}_{a.anio_b}", ascending=False).head(10))
    top.to_csv(C.RESULTADOS / "top10_perdida_ndsi.csv", index=False, float_format="%.4f")
    print(top[[C.ID_COL, "area_km2", ca, cb, f"cambio_emb_{a.anio_a}_{a.anio_b}"]].to_string(index=False))


if __name__ == "__main__":
    main()
