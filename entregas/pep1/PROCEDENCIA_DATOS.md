# Procedencia de datos: C1 Glaciaretes que desaparecen

Todos los datos de este proyecto son **reales**. No hay datos simulados en los resultados. Los únicos datos sintéticos están en `tests/` y sirven solo para probar el código; no aparecen en el informe.

> Completar las fechas de descarga (AAAA-MM-DD) el día que se baje cada dato. Las licencias marcadas «verificar» hay que confirmarlas en la página de la fuente.

## 1. Inventario Público de Glaciares 2022 (IPG2022), DGA

- **Dónde:** https://dga.mop.gob.cl/inventario-publico-glaciares/ (archivo guardado en `datos/crudos/IPG2022.shp`, fuera del repositorio).
- **Fecha de descarga:** AAAA-MM-DD
- **Fechas del dato:** imágenes base de 2013 a 2022 en el área de estudio; inventario publicado en 2022 (v2 de 2023).
- **Resolución:** vectorial, digitalizado sobre imágenes de 1 a 15 m.
- **Licencia:** dato público de la Dirección General de Aguas, MOP (verificar condiciones de uso en el portal).
- **CRS:** EPSG:5360 (SIRGAS-Chile, geográfico). Se reproyecta a EPSG:32719 en `src/inventario.py`.
- **Real o simulado:** real.

## 2. Embeddings satelitales AlphaEarth (Satellite Embedding V1 Annual)

- **Dónde:** Google Earth Engine, `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`. Se consulta en línea desde `src/embeddings.py`; no se descarga el ráster.
- **Fecha de consulta:** AAAA-MM-DD
- **Fechas del dato:** anual, 2017 a 2024.
- **Resolución:** 10 m, 64 bandas (`A00`–`A63`), vectores de largo 1.
- **Licencia:** CC BY 4.0, con atribución a Google y Google DeepMind (verificar en la ficha del catálogo de Earth Engine).
- **CRS:** UTM de cada zona; en el área de estudio, EPSG:32719. Las reducciones se piden en EPSG:32719 a 10 m.
- **Real o simulado:** real.

## 3. Sentinel-2 L2A (reflectancia de superficie)

- **Dónde:** Microsoft Planetary Computer, colección `sentinel-2-l2a`, teselas 19HCC, 19HCD, 19HDC y 19HDD. La lista exacta de escenas usadas queda en `resultados/ndsi_escenas.csv`.
- **Fecha de consulta:** AAAA-MM-DD
- **Fechas del dato:** 1 de febrero al 31 de marzo de 2018 a 2024, escenas con menos de 10 % de nubes.
- **Resolución:** B03 a 10 m y B11 a 20 m; el NDSI se calcula a 20 m.
- **Licencia:** datos Copernicus Sentinel, uso libre y abierto (Copernicus Sentinel Data Terms).
- **CRS:** EPSG:32719.
- **Procesamiento:** desde el baseline 04.00 (enero de 2022) los valores traen un desfase de −1000; `src/ndsi.py` lo corrige antes de calcular el NDSI.
- **Real o simulado:** real.

## 4. Sentinel-2 L2A armonizado en Earth Engine (solo verificación)

- **Dónde:** `COPERNICUS/S2_SR_HARMONIZED`, usado en `src/verificar.py` como segundo camino para el NDSI de un glaciar.
- **Licencia y CRS:** como el punto 3.
- **Real o simulado:** real.

## 5. Copernicus DEM GLO-30

- **Dónde:** Microsoft Planetary Computer, colección `cop-dem-glo-30`.
- **Fecha de descarga:** AAAA-MM-DD
- **Resolución:** 30 m.
- **Licencia:** licencia Copernicus DEM de ESA (uso libre con atribución; verificar).
- **CRS:** EPSG:4326 (geográfico, alturas EGM2008); se remuestrea a EPSG:32719 para el contexto topográfico.
- **Real o simulado:** real. Se usa en la PEP 2 (`contexto_topografico`).

## 6. Ugalde et al. (2026), material suplementario: dato de validación

- **Qué es:** planilla del material suplementario del artículo de Ugalde et al. (2026) sobre glaciares muy pequeños desaparecidos en Chile (hoja `Ugalde_etal_2026_Very_small_gla`), publicada por Cambridge University Press (archivo `S0260305526100524sup001.xlsx`). Completar con el título, la revista y el DOI exactos del artículo.
- **Dónde queda:** `datos/crudos/ugalde_2026_sup001.xlsx`, fuera del repositorio.
- **Fecha de descarga:** AAAA-MM-DD
- **Contenido:** 321 glaciares desaparecidos de Antofagasta al Ñuble, con los atributos del IPG2022 (incluido `COD_GLA`), la clase de desaparición (`Entirely vanished` / `Presumably vanished`), la imagen de alta resolución usada para confirmarlo, el lecho (`Gl_bed`) y la comparación con el IPG2014 y el RGI 7.0. En la subcuenca 0570 hay 17.
- **Cruce:** por atributo `COD_GLA` (sin operación espacial), en `src/validar_ugalde.py`.
- **Licencia:** la del material suplementario de la revista (verificar).
- **CRS:** no aplica (tabla); trae latitud y longitud WGS84 de cada glaciar.
- **Real o simulado:** real.
- **Nota:** el catálogo del curso cita Ugalde et al. (2025) en *Frontiers in Earth Science* (doi:10.3389/feart.2025.1565290). Este suplementario es de un artículo distinto, de 2026; citar ambos en el informe.

## Fuente descartada

- **MODIS MCD43A4 NDSI (Earth Engine):** se descartó porque su píxel de 500 m es más grande que el glaciarete típico del Maipo alto (área mediana en `resultados/inventario_resumen.csv`).
