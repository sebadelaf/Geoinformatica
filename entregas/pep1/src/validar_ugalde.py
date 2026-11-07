"""Contraste con Ugalde et al. (2026): glaciares muy pequeños desaparecidos en Chile.

El suplementario trae una fila por glaciar desaparecido, con el código COD_GLA del
IPG2022, así que el cruce es por atributo (no espacial). Clases: "Entirely vanished"
y "Presumably vanished".

Uso:
    python src/validar_ugalde.py
Requiere: datos/crudos/ugalde_2026_sup001.xlsx y resultados/por_glaciar.csv (src/tabla.py)

Salidas:
    resultados/validacion_ugalde.csv          (los desaparecidos del Maipo alto con nuestras cifras)
    resultados/validacion_ugalde_resumen.csv  (tabla de contingencia de cada señal)
"""
import pandas as pd

import config as C


def leer_ugalde(ruta=C.UGALDE_XLSX):
    # La fila 0 es el origen de cada columna (IPG2022, This_work, ...); los nombres están en la fila 1
    u = pd.read_excel(ruta, header=1, dtype=str)
    u["COD_SCUEN"] = u["COD_SCUEN"].str.strip().str.zfill(4)
    return u[u["COD_SCUEN"] == C.COD_SCUEN][
        ["COD_GLA", "AREA_KM2", "Vanishment", "Comparison", "Gl_bed", "IMAG_First", "Fecha_IMAG"]
    ].rename(columns={"COD_GLA": C.ID_COL, "AREA_KM2": "area_ipg_km2_ugalde"})


def contingencia(df, columna_senal, nombre):
    obs = df["desaparecido_ugalde"]
    pred = df[columna_senal]
    vp, fp = int((pred & obs).sum()), int((pred & ~obs).sum())
    fn, vn = int((~pred & obs).sum()), int((~pred & ~obs).sum())
    return {
        "senal": nombre, "glaciares": len(df), "VP": vp, "FP": fp, "FN": fn, "VN": vn,
        "sensibilidad": vp / (vp + fn) if vp + fn else None,
        "precision": vp / (vp + fp) if vp + fp else None,
    }


def main():
    a, b = C.PAR_PRINCIPAL
    u = leer_ugalde()
    t = pd.read_csv(C.RESULTADOS / "por_glaciar.csv", dtype={C.ID_COL: str})
    faltan = sorted(set(u[C.ID_COL]) - set(t[C.ID_COL]))
    print(f"Ugalde et al.: {len(u)} glaciares desaparecidos en la subcuenca {C.COD_SCUEN}; "
          f"{len(u) - len(faltan)} cruzan con nuestro inventario por COD_GLA.")
    if faltan:
        print(f"  Sin cruce: {faltan}")

    t["desaparecido_ugalde"] = t[C.ID_COL].isin(u[C.ID_COL])
    v = u.merge(t, on=C.ID_COL, how="left")
    v.to_csv(C.RESULTADOS / "validacion_ugalde.csv", index=False, float_format="%.4f")

    print("\nDesaparecidos según Ugalde, con nuestras cifras:")
    cols = [C.ID_COL, "area_km2", "pix20_teoricos", "Vanishment", "no_concluyente",
            f"area_nieve_m2_{a}", f"area_nieve_m2_{b}", f"cambio_emb_{a}_{b}"]
    print(v[[c for c in cols if c in v]].round(4).to_string(index=False))

    print(f"\nNo concluyentes por tamaño: {int(v['no_concluyente'].sum())} de {len(v)} desaparecidos, "
          f"{int(t.loc[~t.desaparecido_ugalde, 'no_concluyente'].sum())} de "
          f"{int((~t.desaparecido_ugalde).sum())} no desaparecidos.")
    print("Área mediana (km²): desaparecidos "
          f"{t.loc[t.desaparecido_ugalde, 'area_km2'].median():.4f}, "
          f"resto {t.loc[~t.desaparecido_ugalde, 'area_km2'].median():.4f}")

    # Señales binarias, evaluadas sobre TODOS los glaciares (también los no concluyentes,
    # para mostrar qué pasa si se ignora el umbral de píxeles) y sobre los concluyentes.
    filas = []
    fondo = pd.read_csv(C.RESULTADOS / "embedding_fondo.csv")
    p95 = fondo[(fondo.anio_a == a) & (fondo.anio_b == b)]["cambio_p95"].iloc[0]
    t["ndsi_sin_hielo_final"] = t.get("area_min_final_m2", t[f"area_nieve_m2_{b}"]).fillna(0) == 0
    t["emb_supera_p95"] = t[f"cambio_emb_{a}_{b}"] > p95
    for sub, etiqueta in ((t, "todos"), (t[~t.no_concluyente], "concluyentes")):
        filas.append(contingencia(sub, "ndsi_sin_hielo_final",
                                  f"NDSI: área mínima {C.VENTANA_FINAL[0]}-{C.VENTANA_FINAL[-1]} = 0 ({etiqueta})"))
        filas.append(contingencia(sub, "emb_supera_p95",
                                  f"Embedding {a}-{b} > p95 fondo = {p95:.4f} ({etiqueta})"))
    # Falsos positivos del NDSI: ¿pérdida reciente o glaciares que nunca se ven como nieve/hielo?
    import geopandas as gpd
    glac = gpd.read_file(C.INVENTARIO, layer=C.CAPA, ignore_geometry=True)
    extra = [c for c in ("CUBIERTO", "HMEDIA", "ORIENTA") if c in glac.columns]
    t = t.merge(glac[[C.ID_COL] + extra], on=C.ID_COL, how="left")
    fp = t[t.ndsi_sin_hielo_final & ~t.desaparecido_ugalde]
    if "area_min_inicial_m2" in fp:
        nunca = fp[[c for c in fp.columns if c.startswith("area_nieve_m2_")]].fillna(0).max(axis=1) == 0
        print(f"\nFalsos positivos del NDSI: {len(fp)}")
        print(f"  sin NDSI >= {C.NDSI_UMBRAL} en NINGÚN año 2018-2024 (ni en veranos nevados): {int(nunca.sum())}")
        print(f"  con hielo en {C.VENTANA_INICIAL[0]}-{C.VENTANA_INICIAL[-1]} y sin hielo al final (candidatos a "
              f"pérdida no listada): {int((fp['area_min_inicial_m2'].fillna(0) > 0).sum())}")
        if "CUBIERTO" in fp:
            print("  CUBIERTO (IPG) en los falsos positivos:", fp["CUBIERTO"].fillna("vacío").value_counts().to_dict())
            print("  CUBIERTO (IPG) en el resto:", t.loc[~t.index.isin(fp.index), "CUBIERTO"].fillna("vacío").value_counts().to_dict())
        if "HMEDIA" in fp:
            print(f"  Altura media (m): falsos positivos {pd.to_numeric(fp.HMEDIA).median():.0f}, "
                  f"resto {pd.to_numeric(t.loc[~t.index.isin(fp.index), 'HMEDIA']).median():.0f}")
        fp.assign(nunca_visible=nunca).to_csv(C.RESULTADOS / "validacion_falsos_positivos_ndsi.csv",
                                             index=False, float_format="%.4f")

    r = pd.DataFrame(filas)
    r.to_csv(C.RESULTADOS / "validacion_ugalde_resumen.csv", index=False, float_format="%.3f")
    print("\nContingencia (VP = desaparecido en Ugalde y detectado por la señal):")
    print(r.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
