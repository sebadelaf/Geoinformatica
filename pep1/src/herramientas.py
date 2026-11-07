"""Herramientas deterministas que el agente podrá llamar (PEP 2).

Cada herramienta devuelve un dict con "resultado" y "traza". La traza dice qué
herramienta se llamó, con qué parámetros, de qué archivo salió la cifra y qué
devolvió. Si la pregunta no se puede responder con los datos, la herramienta lo
dice ("no_se_puede": True y la razón) en vez de devolver un número.

Implementadas y probadas para la PEP 1: contar_glaciares, ndsi_por_glaciar.
"""
from datetime import datetime, timezone

import geopandas as gpd
import pandas as pd

import config as C
from inventario import filtrar


def _traza(nombre, parametros, fuente, resultado):
    return {
        "herramienta": nombre, "parametros": parametros, "fuente": str(fuente),
        "resultado": resultado, "hora": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _no_se_puede(nombre, parametros, razon):
    r = {"no_se_puede": True, "razon": razon}
    return {"resultado": r, "traza": _traza(nombre, parametros, "-", r)}


def contar_glaciares(cod_scuen: str = C.COD_SCUEN, clase: str = C.CLASE, ruta_ipg=C.IPG_CRUDO):
    """Número y área (km², EPSG:32719) de glaciares de una clase en una subcuenca BNA.

    Decisión espacial: selección por atributo COD_SCUEN (no por caja) y área en UTM 19S.
    """
    params = {"cod_scuen": cod_scuen, "clase": clase}
    ipg = gpd.read_file(ruta_ipg)
    sel = filtrar(ipg, cod_scuen=str(cod_scuen).zfill(4), clase=clase)
    if sel.empty:
        return _no_se_puede("contar_glaciares", params,
                            f"No hay glaciares de clase {clase} en la subcuenca {cod_scuen} del IPG2022.")
    r = {"n": int(len(sel)), "area_km2": round(float(sel["area_km2"].sum()), 2), "crs": C.CRS_MEDIDA}
    return {"resultado": r, "traza": _traza("contar_glaciares", params, ruta_ipg, r)}


def ndsi_por_glaciar(id_glaciar: str, anio: int, ruta=C.RESULTADOS / "ndsi_por_glaciar.csv"):
    """NDSI de fin de verano (feb-mar) de un glaciar: fracción con NDSI >= 0,4, m² y píxeles.

    Decisiones espaciales: grilla de 20 m en EPSG:32719, píxel cuenta si su centro
    cae en el polígono, nubes < 10 %, máscara SCL, umbral NDSI 0,4.
    """
    params = {"id_glaciar": id_glaciar, "anio": anio}
    if anio not in C.ANIOS_NDSI:
        return _no_se_puede("ndsi_por_glaciar", params,
                            "Solo hay NDSI calculado para los veranos con Sentinel-2 L2A "
                            f"({min(C.ANIOS_NDSI)}-{max(C.ANIOS_NDSI)}).")
    df = pd.read_csv(ruta, dtype={C.ID_COL: str})
    fila = df[(df[C.ID_COL] == str(id_glaciar)) & (df["anio"] == anio)]
    if fila.empty:
        razon = (f"El glaciar {id_glaciar} no está en el inventario del Maipo alto."
                 if str(id_glaciar) not in set(df[C.ID_COL])
                 else f"No hay NDSI calculado para {anio}.")
        return _no_se_puede("ndsi_por_glaciar", params, razon)
    f = fila.iloc[0]
    r = {
        "frac_nieve": None if pd.isna(f["frac_nieve"]) else round(float(f["frac_nieve"]), 3),
        "area_nieve_m2": float(f["area_nieve_m2"]),
        "n_pix_validos": int(f["n_pix_validos"]),
        "no_concluyente": bool(f["no_concluyente"]),
    }
    return {"resultado": r, "traza": _traza("ndsi_por_glaciar", params, ruta, r)}


def cambio_embedding(id_glaciar: str, anio_a: int, anio_b: int,
                     ruta=C.RESULTADOS / "embedding_por_glaciar.csv"):
    """1 - coseno medio entre los embeddings AlphaEarth de dos años, sobre el polígono (10 m)."""
    params = {"id_glaciar": id_glaciar, "anio_a": anio_a, "anio_b": anio_b}
    fuera = [y for y in (anio_a, anio_b) if y not in C.ANIOS]
    if fuera:
        return _no_se_puede("cambio_embedding", params,
                            f"AlphaEarth cubre {min(C.ANIOS)}-{max(C.ANIOS)}; no hay embedding para {fuera}.")
    df = pd.read_csv(ruta, dtype={C.ID_COL: str})
    a, b = sorted((anio_a, anio_b))  # el coseno es simétrico
    fila = df[(df[C.ID_COL] == str(id_glaciar)) & (df["anio_a"] == a) & (df["anio_b"] == b)]
    if fila.empty:
        return _no_se_puede("cambio_embedding", params,
                            "Ese par de años o ese glaciar no está calculado; correr embeddings.py.")
    f = fila.iloc[0]
    r = {"cambio": None if pd.isna(f["cambio"]) else round(float(f["cambio"]), 4),
         "n_pix": int(f["n_pix"]), "no_concluyente": bool(f["no_concluyente"])}
    return {"resultado": r, "traza": _traza("cambio_embedding", params, ruta, r)}
