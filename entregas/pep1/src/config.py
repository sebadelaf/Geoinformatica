"""Parámetros del proyecto en un solo lugar.

Toda decisión espacial que aparece en el informe sale de aquí, para que el
informe y el código no se contradigan. 
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
RESULTADOS = RAIZ / "resultados"
FIGURAS = RAIZ / "figuras"

# Área de estudio: subcuenca BNA del Maipo alto en el IPG2022.
# Se selecciona por atributo, no por caja: la caja trae glaciares de cuencas vecinas.
COD_SCUEN = "0570"
CLASE = "GLACIARETE"

# CRS de medición: WGS84 / UTM 19S. Áreas en m², distancias en m.
CRS_MEDIDA = "EPSG:32719"

# IPG2022 completo, tal como se baja de la DGA (no va al repositorio)
IPG_CRUDO = DATOS / "crudos" / "IPG2022.shp"

# Inventario filtrado (salida de inventario.py)
INVENTARIO = DATOS / "glaciaretes_maipo_32719.gpkg"
CAPA = "glaciaretes"
ID_COL = "id_glaciar"  # columna de identificador que crea inventario.py

# NDSI con Sentinel-2 L2A
NDSI_UMBRAL = 0.4          # nieve/hielo si NDSI >= 0,4 (umbral clásico de Dozier/Hall)
NDSI_RES_M = 20            # B11 es de 20 m: el NDSI se calcula en grilla de 20 m
NDSI_MESES = ("02-01", "03-31")  # fin del verano austral: mínima nieve estacional
NUBES_MAX = 10             # % de nubes de la escena (eo:cloud_cover)
# Clases SCL que se descartan: 0 sin dato, 1 saturado, 3 sombra de nube,
# 8 y 9 nube, 10 cirro. La nieve (11) se conserva.
SCL_DESCARTAR = (0, 1, 3, 8, 9, 10)
MARGEN_M = 500             # margen alrededor de los glaciares al bajar imágenes

# Embeddings AlphaEarth
EMB_COLECCION = "GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL"
EMB_RES_M = 10
ANIO_BASE = 2018
ANIOS = list(range(2017, 2025))       # disponibilidad de AlphaEarth: 2017-2024
ANIOS_NDSI = list(range(2018, 2025))  # veranos (feb-mar) 2018-2024
# El NDSI de fin de verano sigue a la nieve del invierno anterior: 2019, 2021 y 2024
# salen altos y 2020, 2022 y 2023 bajos (tras los inviernos de hipersequía 2019 y 2021).
# Por eso se comparan años de POCA nieve, donde lo que queda con NDSI alto es hielo.
# Par principal (tabla, mapa y verificación): dos años de poca nieve, 3 años aparte.
PAR_PRINCIPAL = (2020, 2023)
# Métrica robusta: área mínima de cada glaciar en una ventana inicial y una final.
VENTANA_INICIAL = (2018, 2019, 2020)
VENTANA_FINAL = (2022, 2023, 2024)

# Validación: material suplementario de Ugalde et al. (2026), glaciares muy pequeños desaparecidos
UGALDE_XLSX = DATOS / "crudos" / "ugalde_2026_sup001.xlsx"

# Riesgo principal: glaciaretes con pocos píxeles
MIN_PIX_20M = 10   # < 10 píxeles válidos de 20 m (4.000 m²) => no concluyente
MIN_PIX_10M = 40   # equivalente en la grilla de 10 m

# Ruido de fondo de los embeddings: terreno fuera de los glaciares
FONDO_EXCLUSION_M = 300   # se excluye este margen alrededor de cada glaciar
FONDO_REGION_M = 2000     # región = envolvente convexa de los glaciares + 2 km.
