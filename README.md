# Geoinformática

## Proyecto

- **Código del catálogo:** C1
- **Título:** Detección temprana de la desaparición de glaciaretes en los Andes centrales
- **Ruta:** científica
- **Pregunta o propuesta de valor:** ¿Detectan los embeddings satelitales la desaparición de glaciaretes antes que el índice de nieve (NDSI)? Google publicó en 2025 embeddings anuales de 10 m para todo el planeta (AlphaEarth), y Ugalde et al. (2025) identificaron glaciaretes del Desierto y los Andes Centrales que desaparecieron entre 2018 y 2023, por lo que existe una referencia independiente contra la cual comparar.
- **Datos:**
  - [Inventario Público de Glaciares 2022, DGA](https://dga.mop.gob.cl/inventario-publico-glaciares/).
  - [Satellite Embedding V1 / AlphaEarth, Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL) (requiere cuenta de Earth Engine y acceso habilitado).
  - [Sentinel-2 L2A, Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/catalog) (colección disponible en el catálogo).
  - [MODIS MCD43A4 NDSI, Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/MODIS_MCD43A4_006_NDSI?hl=es-419) (fuente de referencia para el índice de nieve).
  - [Copernicus DEM, Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/catalog).
  - [Ugalde et al. (2025), *Ice loss detection of glacierets in the Desert and Central Andes of Chile between 2018 and 2023*](https://doi.org/10.3389/feart.2025.1565290).
  - **Muestra descargada:** no.
- **Qué hará el agente:** Recorrerá el inventario polígono por polígono y calculará el cambio interanual en los embeddings y en el NDSI. Comparará ambas señales con los glaciaretes reportados como desaparecidos por Ugalde et al. (2025). Redactará una ficha por glaciarete con cifras, evidencia, fuentes, herramientas y advertencias de calidad.
- **Versión mínima para la PEP 1:** Una cuenca de prueba: cálculo de NDSI y cambio en embeddings por glaciarete, sin agente autónomo. La entrega es el 12 de noviembre.
- **Riesgo principal y cómo lo vamos a enfrentar:** Los glaciaretes pequeños pueden ocupar sólo unos pocos píxeles de 10 m y no producir una señal robusta. Se registrará el número de píxeles válidos, se definirá un umbral mínimo y los casos insuficientes se marcarán como no concluyentes, sin clasificarlos automáticamente como desaparecidos.

- ## Área de estudio y CRS
**Cuenca:** Maipo alto, subcuenca BNA `0570` (campo `COD_SCUEN` del IPG2022), Región Metropolitana. Tiene 322 glaciaretes con 20,32 km² en total, que son 322 de los 327 glaciaretes de la región.

**Caja (oeste, sur, este, norte; grados):** −70,38; −34,30; −69,77; −33,05
La caja es la extensión de todos los glaciares del IPG2022 con `COD_SCUEN = 0570`, redondeada hacia afuera. Para seleccionar glaciares no se usa la caja, se usa el código de subcuenca: la caja también toma glaciares de cuencas vecinas (438 glaciaretes en vez de 322).

**CRS de medición:** EPSG:32719 (WGS84 / UTM zona 19S).
Medimos superficies de hielo en m² y km², y el Maipo alto (≈ 70,4° O a 69,8° O) cae entero en la zona UTM 19 (72° O a 66° O). Sentinel-2 se distribuye en esas mismas teselas UTM 19S (19HCC, 19HCD, 19HDC, 19HDD), así que no se remuestrea el ráster para medir.

## Preguntas que el agente debe responder

1) ¿Cuántos glaciaretes del IPG2022 hay en el Maipo alto y cuánta superficie suman (km²)?
`contar_glaciares`: GeoPandas; filtra `CLASIFICA == "GLACIARETE"` y `COD_SCUEN == "0570"` y calcula el área en EPSG:32719. Respuesta conocida: 322 glaciaretes, 20,32 km²

2) ¿Qué superficie con NDSI ≥ 0,4 tenía el glaciarete *X* al final del verano de 2019 y al de 2023, y cuánto cambió?
`ndsi_por_glaciar`: compuesto Sentinel-2 L2A de dic–mar, nubes < 10 %, NDSI = (B3 − B11)/(B3 + B11), estadística zonal sobre el polígono

3) ¿Cuánto cambió el embedding AlphaEarth del glaciarete *X* entre 2018 y 2023?
`cambio_embedding`: producto punto entre los vectores de 64 dimensiones de ambos años, promediado sobre los píxeles del polígono (Earth Engine)

## Preguntas imposibles
1) ¿Qué glaciaretes del Maipo alto habrán desaparecido en 2030?
Ninguna. No tenemos proyecciones, el agente debe responder "no hay datos para eso"

2) ¿Cuál era el NDSI del glaciarete *X* en 2010?
Con nuestras fuentes no se puede, ya que los embeddings parten en 2017 y Sentinel-2 en 2015.
