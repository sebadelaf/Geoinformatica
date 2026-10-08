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
  - [Copernicus DEM, Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/catalog).
  - [Ugalde et al. (2025), *Ice loss detection of glacierets in the Desert and Central Andes of Chile between 2018 and 2023*](https://doi.org/10.3389/feart.2025.1565290).
  - **Muestra descargada:** no; se debe registrar al iniciar la PEP 1.
- **Qué hará el agente:** Recorrerá el inventario polígono por polígono y calculará el cambio interanual en los embeddings y en el NDSI. Comparará ambas señales con los glaciaretes reportados como desaparecidos por Ugalde et al. (2025). Redactará una ficha por glaciarete con cifras, evidencia, fuentes, herramientas y advertencias de calidad.
- **Versión mínima para la PEP 1:** Una cuenca de prueba, preferentemente Maipo alto: cálculo de NDSI y cambio en embeddings por glaciarete, sin agente autónomo. La entrega es el 12 de noviembre.
- **Riesgo principal y cómo lo vamos a enfrentar:** Los glaciaretes pequeños pueden ocupar sólo unos pocos píxeles de 10 m y no producir una señal robusta. Se registrará el número de píxeles válidos, se definirá un umbral mínimo y los casos insuficientes se marcarán como no concluyentes, sin clasificarlos automáticamente como desaparecidos.

## Plan de entregas

- **PEP 1 — 12 de noviembre:** una cuenca, NDSI y cambio en embeddings por glaciarete, sin agente.
- **PEP 2 — 7 de enero:** agente que procesa el inventario completo de la cuenca, genera fichas por glaciarete y compara los resultados con el estudio publicado.

## Verificación y herramientas del curso

La verificación comparará los resultados con los glaciaretes que Ugalde et al. (2025) reportan como desaparecidos. Cada ficha deberá citar las herramientas que produjeron sus cifras. El proyecto aplica ráster, interacciones ráster-vector, estadística zonal y Google Earth Engine.
