"""Filtra el IPG2022 (DGA) a los glaciaretes del Maipo alto y los guarda en EPSG:32719.

Uso:
    python src/inventario.py --ipg datos/crudos/IPG2022.shp [--id-col COD_GLA]

Salida:
    datos/glaciaretes_maipo_32719.gpkg  (capa "glaciaretes")
    resultados/inventario_resumen.csv   (n y área total; respuesta conocida: 322 y 20,32 km²)
"""
import argparse
import sys

import geopandas as gpd
import pandas as pd

import config as C


def normalizar_cod(serie: pd.Series) -> pd.Series:
    """COD_SCUEN puede venir como texto '0570' o como número 570: se lleva a 4 dígitos."""
    s = serie.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return s.where(~s.str.isdigit(), s.str.zfill(4))


def filtrar(ipg: gpd.GeoDataFrame, cod_scuen=C.COD_SCUEN, clase=C.CLASE, id_col=None) -> gpd.GeoDataFrame:
    for col in ("CLASIFICA", "COD_SCUEN"):
        if col not in ipg.columns:
            sys.exit(f"Falta la columna {col}. Columnas disponibles: {list(ipg.columns)}")
    if ipg.crs is None:
        sys.exit("El inventario no trae CRS: revisar el .prj antes de seguir.")

    cod = normalizar_cod(ipg["COD_SCUEN"])
    clas = ipg["CLASIFICA"].astype(str).str.strip().str.upper()
    sel = ipg[(cod == cod_scuen) & (clas == clase.upper())].copy()

    if id_col and id_col in sel.columns:
        sel[C.ID_COL] = sel[id_col].astype(str)
    else:
        if id_col:
            print(f"AVISO: no existe la columna {id_col}; se crea un id correlativo.")
        sel[C.ID_COL] = [f"MA{i:04d}" for i in range(1, len(sel) + 1)]
    if sel[C.ID_COL].duplicated().any():
        sys.exit("Hay identificadores repetidos: elegir otra --id-col.")

    # GeoPackage no distingue mayúsculas: AREA_KM2 (DGA) chocaría con area_km2 (nuestra)
    if "AREA_KM2" in sel.columns:
        sel = sel.rename(columns={"AREA_KM2": "area_dga_km2"})

    sel = sel.to_crs(C.CRS_MEDIDA)
    # Geometrías inválidas (autointersecciones) darían áreas erróneas
    invalidas = int((~sel.geometry.is_valid).sum())
    if invalidas:
        print(f"AVISO: {invalidas} geometrías inválidas; se reparan con make_valid().")
        sel["geometry"] = sel.geometry.make_valid()
    sel["area_m2"] = sel.geometry.area
    sel["area_km2"] = sel["area_m2"] / 1e6
    # Número teórico de píxeles de 20 m que caben en el polígono (para el riesgo de tamaño)
    sel["pix20_teoricos"] = sel["area_m2"] / (C.NDSI_RES_M ** 2)
    return sel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ipg", required=True, help="Shapefile o GPKG del IPG2022")
    ap.add_argument("--id-col", default="COD_GLA", help="Columna con el código del glaciar en el IPG")
    a = ap.parse_args()

    ipg = gpd.read_file(a.ipg)
    print(f"IPG leído: {len(ipg)} polígonos, CRS {ipg.crs}")
    sel = filtrar(ipg, id_col=a.id_col)

    C.DATOS.mkdir(exist_ok=True)
    C.RESULTADOS.mkdir(exist_ok=True)
    sel.to_file(C.INVENTARIO, layer=C.CAPA, driver="GPKG")

    resumen = pd.DataFrame([{
        "cod_scuen": C.COD_SCUEN, "clase": C.CLASE, "crs_medida": C.CRS_MEDIDA,
        "n_glaciaretes": len(sel),
        "area_total_km2": round(sel["area_km2"].sum(), 2),
        "area_total_dga_km2": round(sel["area_dga_km2"].sum(), 2) if "area_dga_km2" in sel else None,
        "area_mediana_km2": round(sel["area_km2"].median(), 4),
        "n_menores_10pix20m": int((sel["pix20_teoricos"] < C.MIN_PIX_20M).sum()),
    }])
    resumen.to_csv(C.RESULTADOS / "inventario_resumen.csv", index=False)
    print(resumen.T.to_string(header=False))
    print(f"Guardado: {C.INVENTARIO}")


if __name__ == "__main__":
    main()
