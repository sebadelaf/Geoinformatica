"""Pruebas de las herramientas con datos sintéticos (no requieren red ni Earth Engine).

Correr con:  pytest -q
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from rasterio.transform import from_origin
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as C  # noqa: E402
import herramientas as H  # noqa: E402
from inventario import filtrar  # noqa: E402
from ndsi import zonal  # noqa: E402

# Dos cuadrados de 200 m x 200 m (0,04 km²) en UTM 19S, cerca de El Yeso
X0, Y0 = 390000, 6260000


@pytest.fixture
def ipg(tmp_path):
    utm = gpd.GeoDataFrame({
        "COD_GLA": ["A", "B", "C", "D"],
        "CLASIFICA": ["GLACIARETE", "glaciarete ", "GLACIAR DE MONTAÑA", "GLACIARETE"],
        "COD_SCUEN": [570, "0570", "0570", "0571"],
        "AREA_KM2": [0.04, 0.04, 0.04, 0.04],         # como en el IPG real: choca con area_km2 en GPKG   # número y texto: ambos deben servir
        "geometry": [box(X0, Y0, X0 + 200, Y0 + 200), box(X0 + 1000, Y0, X0 + 1200, Y0 + 200),
                     box(X0, Y0 + 1000, X0 + 200, Y0 + 1200), box(X0 + 5000, Y0, X0 + 5200, Y0 + 200)],
    }, crs=C.CRS_MEDIDA)
    ruta = tmp_path / "ipg.gpkg"
    utm.to_crs(5360).to_file(ruta)   # como viene de la DGA: SIRGAS-Chile geográfico
    return ruta


def test_filtrar_por_codigo_y_clase(ipg):
    sel = filtrar(gpd.read_file(ipg), id_col="COD_GLA")
    assert sorted(sel[C.ID_COL]) == ["A", "B"]
    assert sel.crs.to_string() == C.CRS_MEDIDA
    assert sel["area_m2"].sum() == pytest.approx(80000, rel=1e-3)


def test_inventario_se_guarda_en_gpkg(ipg, tmp_path):
    sel = filtrar(gpd.read_file(ipg), id_col="COD_GLA")
    sel.to_file(tmp_path / "out.gpkg", layer="g", driver="GPKG")
    assert "area_dga_km2" in gpd.read_file(tmp_path / "out.gpkg").columns


def test_contar_glaciares_y_traza(ipg):
    out = H.contar_glaciares("570", "GLACIARETE", ruta_ipg=ipg)
    assert out["resultado"]["n"] == 2
    assert out["resultado"]["area_km2"] == pytest.approx(0.08, abs=0.005)
    assert out["traza"]["herramienta"] == "contar_glaciares"
    assert out["traza"]["parametros"] == {"cod_scuen": "570", "clase": "GLACIARETE"}


def test_contar_glaciares_subcuenca_vacia(ipg):
    out = H.contar_glaciares("9999", "GLACIARETE", ruta_ipg=ipg)
    assert out["resultado"]["no_se_puede"]


def test_zonal_cuenta_pixeles_por_centro():
    # Grilla de 20 m: el glaciar A (200 m) contiene 10 x 10 = 100 centros de píxel
    glac = gpd.GeoDataFrame({C.ID_COL: ["A"], "geometry": [box(X0, Y0, X0 + 200, Y0 + 200)]},
                            crs=C.CRS_MEDIDA)
    ndsi = np.full((20, 20), 0.6, dtype="float32")
    t = from_origin(X0, Y0 + 400, 20, 20)   # la grilla cubre 400 m x 400 m
    # El glaciar ocupa filas 10-19 y columnas 0-9 de la grilla
    ndsi[10:15, 0:10] = 0.1    # mitad del glaciar sin nieve: 50 píxeles
    ndsi[10, 0] = np.nan       # un píxel con nube
    r = zonal(ndsi, t, glac).iloc[0]
    assert r.n_pix_total == 100
    assert r.n_pix_validos == 99
    assert r.area_nieve_m2 == 50 * 400
    assert not r.no_concluyente


def test_ndsi_anio_imposible(tmp_path):
    ruta = tmp_path / "n.csv"
    pd.DataFrame({C.ID_COL: ["A"], "anio": [2023], "frac_nieve": [0.5], "area_nieve_m2": [400.0],
                  "n_pix_validos": [30], "no_concluyente": [False]}).to_csv(ruta, index=False)
    assert H.ndsi_por_glaciar("A", 2010, ruta=ruta)["resultado"]["no_se_puede"]
    assert H.ndsi_por_glaciar("ZZ", 2023, ruta=ruta)["resultado"]["no_se_puede"]
    ok = H.ndsi_por_glaciar("A", 2023, ruta=ruta)
    assert ok["resultado"]["area_nieve_m2"] == 400.0
    assert ok["traza"]["fuente"] == str(ruta)


def test_embedding_fuera_de_rango(tmp_path):
    out = H.cambio_embedding("A", 2016, 2023, ruta=tmp_path / "no_existe.csv")
    assert out["resultado"]["no_se_puede"]
