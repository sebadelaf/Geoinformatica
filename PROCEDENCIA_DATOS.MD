# Procedencia de datos: C1 Glaciaretes que desaparecen

## 1. Inventario Público de Glaciares 2022 (IPG2022), DGA

- **Dónde:** Portal DGA (https://dga.mop.gob.cl/inventario-publico-glaciares/)
- **Fechas:** Imágenes base de 2013 a 2022 en el área de estudio (2016–2020 a nivel nacional); inventario publicado en 2022 (v2 de 2023).
- **Resolución:** Vectorial (polígonos digitalizados a partir de imágenes base de entre 1 y 15 m).
- **CRS:** EPSG:5360 (SIRGAS-Chile, geográfico); se reproyecta a EPSG:32719 (UTM 19S) para mediciones zonales.

## 2. Embeddings satelitales AlphaEarth (Satellite Embedding V1 Annual)

- **Dónde:** Google Earth Engine, colección `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`.
- **Fechas:** Anual, de 2017 a 2024 (versión 1.1).
- **Resolución:** 10 m (64 bandas: `A00`–`A63`).
- **CRS:** EPSG:32719 (UTM zona 19S en el área de estudio).

## 3. Sentinel-2 L2A (reflectancia de superficie)

- **Dónde:** Microsoft Planetary Computer, colección `sentinel-2-l2a`, teselas 19HCC, 19HCD, 19HDC y 19HDD.
- **Fechas:** Fin del verano austral (dic–mar) de 2019 y 2023.
- **Resolución:** 10 m en banda B3 (verde) y 20 m en banda B11 (SWIR), quedando el NDSI a 20 m.
- **CRS:** EPSG:32719 (UTM zona 19S).
