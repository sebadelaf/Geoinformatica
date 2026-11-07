## Cómo ejecutar (PEP 1)

Sección para pegar en el `README.md` del repositorio.

### 1. Entorno (≈ 5 min)

```bash
conda env create -f environment.yml
conda activate glaciaretes
pytest -q                      # 6 pruebas con datos sintéticos, sin red
```

### 2. Datos que no van en el repositorio

1. Bajar el IPG2022 desde https://dga.mop.gob.cl/inventario-publico-glaciares/ y dejar el shapefile en `datos/crudos/IPG2022.shp`.
2. Earth Engine (solo una vez por persona; las credenciales quedan en `~/.config/earthengine`, fuera del repositorio):

```bash
earthengine authenticate
export EE_PROJECT=<id-de-tu-proyecto-de-google-cloud>
```

Sentinel-2 se lee en línea desde Planetary Computer, sin cuenta.

### 3. Análisis de punta a punta

Correr desde la raíz del repositorio:

| Paso | Comando | Produce | Tiempo aprox. |
| --- | --- | --- | --- |
| Inventario | `python src/inventario.py --ipg datos/crudos/IPG2022.shp --id-col COD_GLA` | `datos/glaciaretes_maipo_32719.gpkg`, `resultados/inventario_resumen.csv` | < 1 min |
| NDSI | `python src/ndsi.py` | `resultados/ndsi_por_glaciar.csv`, `resultados/ndsi_escenas.csv`, `datos/cache/ndsi_<año>.tif` | 10–40 min (depende de la red) |
| Embeddings | `python src/embeddings.py --fondo` | `resultados/embedding_por_glaciar.csv`, `resultados/embedding_fondo.csv` | 5–15 min |
| Tabla | `python src/tabla.py --anio-a 2019 --anio-b 2023` | `resultados/por_glaciar.csv`, `resultados/top10_perdida_ndsi.csv` | < 1 min |
| Mapa | `python src/mapa.py --anio-a 2019 --anio-b 2023` | `figuras/mapa_cambio_embedding.png` | < 1 min |
| Verificación | `python src/verificar.py --glaciar <id> --anio 2023` | `resultados/verificacion.csv` | 2–5 min |

Para una prueba rápida: `python src/ndsi.py --anios 2019 2023`.

Todas las decisiones espaciales (CRS, umbral NDSI, meses, nubes, mínimo de píxeles) están en `src/config.py`.
