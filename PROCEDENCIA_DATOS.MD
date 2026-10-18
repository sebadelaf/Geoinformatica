# Procedencia de datos: C1 Glaciaretes que desaparecen

Marquen cada fuente como abierta (fecha ). Lo que diga «verificar» se completa con lo que muestre el archivo.

## 1. Inventario Público de Glaciares 2022 (IPG2022), DGA

- **Dónde:** https://dga.mop.gob.cl/inventario-publico-glaciares/ → «Descargar Shape» (https://dga.mop.gob.cl/uploads/sites/13/2024/07/Glaciares-1.zip). Informe en PDF en la misma página.
- **Archivo:** `Glaciares/IPG_2022_v2/INV_PG_2022_v2.shp` (versión 2, `FECHA_ACTU` 2023-07-15). El zip trae además la metodología y el LEEME en `Glaciares/Documentos/`.
- **Qué es:** 26.180 polígonos para todo Chile, de los cuales 18.211 son `GLACIARETE`. Los demás son 3.844 de montaña, 3.598 rocosos, 310 de valle y 217 efluentes.
- **Campos útiles:** `COD_GLA` (identificador), `NOMBRE`, `CLASIFICA`, `COD_CUEN`/`COD_SCUEN`/`COD_SSCUEN`, `AREA_KM2`, `HMIN`/`HMEDIA`/`HMAX`, `ORIENTA`, `PENDIENTE`, `FUENTE_DIG`, `FUEN_FECHA`, `INVE_FECHA`, `RESOL_IMG`, `ERROR`. También trae `ESP_MED`, `VOL_KM3` y `EQ_AGUAKM3` (estimados con Chen y Ohmura 1990).
- **Maipo alto (`COD_SCUEN = 0570`):**
  - 1.103 polígonos, de los cuales 322 son glaciaretes, con 20,32 km² en total.
  - 43 glaciaretes miden menos de 0,01 km². El más chico tiene 1.106 m², o sea 2,8 píxeles de 20 m.
  - La mediana es 97 píxeles de 20 m.
  - La altura media va de 3.070 a 6.036 m.
- **Fechas:** las imágenes base de los glaciaretes del Maipo alto (`FUEN_FECHA`) van de 2013 a 2022; la mayoría es de 2015, 2018 y 2019. La fecha de inventario (`INVE_FECHA`) es 2019–2023.
- **Resolución:** vectorial. La imagen base de cada polígono (`FUENTE_DIG`/`RESOL_IMG`) va de LiDAR a Landsat (15 m); en el Maipo alto, 114 glaciaretes se digitalizaron sobre Sentinel-2.
- **CRS:** **EPSG:5360 (SIRGAS-Chile, geográfico)**, según el `.prj`. Los campos `DATUM`/`HUSO` dicen «WGS 84» y «19 SUR», pero esos campos describen las coordenadas `UTM_NORTE`/`UTM_ESTE`, no la geometría. Para medir se reproyecta a EPSG:32719.
- **Abierto:** [x] 18-oct-2026 · 

## 2. Embeddings satelitales AlphaEarth (Satellite Embedding V1 Annual)

- **Dónde:** Google Earth Engine, `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL` (requiere cuenta y proyecto de Earth Engine).
- **Fechas:** una imagen por año calendario, de 2017 a 2024. La versión 1.1 (nov. 2025) regeneró la capa 2017.
- **Resolución:** 10 m; 64 bandas (A00–A63), vector de largo 1 → el cambio entre años se mide con el producto punto.
- **CRS:** UTM local de cada tesela (propiedad `UTM_ZONE`); Maipo alto → 19S.
- **Licencia:** CC-BY 4.0 (hay que citar).
- **Ojo:** el embedding es anual, así que mezcla la nieve de invierno con la superficie de verano. No es un «fin de temporada de ablación» como el NDSI.
- **Abierto:** [ ] fecha: ____ 

## 3. Sentinel-2 L2A (reflectancia de superficie)

- **Dónde:** Microsoft Planetary Computer, colección `sentinel-2-l2a` (STAC). Alternativa en Earth Engine: `COPERNICUS/S2_SR_HARMONIZED`.
- **Teselas:** 19HCC, 19HCD, 19HDC, 19HDD.
- **Fechas:** fin del verano austral (dic–mar) de 2019 y de 2023, igual que Ugalde et al. Anotar aquí las escenas sin nubes que encuentren: ____
- **Resolución:** B3 (verde) a 10 m; **B11 (SWIR) a 20 m** → el NDSI queda efectivamente a 20 m.
- **CRS:** EPSG:32719.
- **Abierto:** [ ] fecha: ____ 
## 4. Copernicus DEM GLO-30

- **Dónde:** Planetary Computer, colección `cop-dem-glo-30`.
- **Fecha:** adquisición TanDEM-X 2011–2015 (modelo estático).
- **Resolución:** 30 m. **CRS:** EPSG:4326 (reproyectar a 32719).
- **Uso:** altitud, pendiente, orientación y sombras por glaciarete (Ugalde encontró que los que desaparecieron están concentrados bajo 3.700 m).
- **Abierto:** [ ] fecha: ____ 

## 5. Cuencas y subcuencas BNA, DGA

- **Dónde:** IDE Chile (https://www.ide.cl) o el servicio de la SMA (`Recursos_hidricos_glaciares`, capas 9 «Subcuencas - BNA» y 10 «Cuencas - DGA»).
- **Uso:** definir el polígono «Maipo alto» y la caja del README.
- **CRS:** EPSG:4326 en el servicio de la SMA; verificar si se descarga de otro lado.
- **Abierto:** [ ] fecha: ____ 

## 6. Estudio de referencia (verificación)

- Ugalde, F. et al. (2025). *Ice loss detection of glacierets in the Desert and Central Andes of Chile between 2018 and 2023.* Frontiers in Earth Science, 13. doi:10.3389/feart.2025.1565290
- **Qué da:** inspección visual de los 588 glaciaretes de 0,001–0,01 km² del área de estudio (77 «entirely vanished», 244 «presumably vanished»). Usa NDSI de Sentinel-2 con umbral 0,4, dic–mar de 2019–2020 y de 2022–2023, en Earth Engine.
- **Región Metropolitana según el artículo:**
  - Tabla 3: 45 glaciaretes de menos de 0,01 km²; 18 sin hielo visible (40 %) y 27 con hielo visible.
  - Tabla 4: 20,65 km² de glaciaretes; 6,09 km² de hielo limpio; cambio de −1,65 km² (−27,1 %) entre 2019 y 2023.
- **Cruce con el IPG2022 (hecho):** el shapefile da exactamente 327 glaciaretes, 20,65 km² y 45 menores de 0,01 km² en la Región Metropolitana, así que el estudio usó esta misma versión del inventario. De esos 45, 43 están en el Maipo alto.

## Pendientes

- [ ] **Lista de glaciaretes desaparecidos por `COD_GLA`.** El artículo publica totales por región, no la lista por glaciar («los datos se entregarán a pedido»). Hay que revisar el material suplementario en frontiersin.org; si no está, escribir al autor de correspondencia (felipe.ugalde@ug.uchile.cl). Sin esta lista, la verificación queda en comparar totales regionales.
- [ ] (Opcional) RGI 7.0 / GLIMS como segundo juego de contornos.
