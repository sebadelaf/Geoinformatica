# Diseño del agente: C1 Glaciaretes que desaparecen

## 1. Qué hace el agente y qué se pierde sin él

El agente recorre los 322 glaciaretes del Maipo alto uno por uno. Para cada uno decide qué años y qué señales consultar (NDSI de fin de verano y cambio de embedding AlphaEarth), revisa si la evidencia alcanza (píxeles válidos, nubes, tamaño) y redacta una ficha con la cifra de cada herramienta y su traza. Cuando las señales se contradicen o el glaciar es demasiado chico, lo dice en la ficha en vez de clasificarlo.

Tarea de punta a punta: «Redacta la ficha del glaciarete X». El agente llama `ndsi_por_glaciar` para 2018 a 2024, `cambio_embedding` contra 2018, compara con el umbral de ruido de fondo, consulta `estado_segun_ugalde` y escribe la ficha.

Sin el agente queda una tabla de 322 filas y unas 40 columnas. Nadie la lee glaciar por glaciar ni explica qué significa cada caso. El agente es lo que convierte la tabla en 322 fichas revisables con evidencia, y detecta cuáles no se pueden concluir.

## 2. Herramientas

Todas son deterministas: el modelo decide qué llamar y las herramientas calculan. El código está en `src/herramientas.py`.

| Herramienta | Qué hace | Entradas | Salida | Decisión espacial dentro | Estado |
| --- | --- | --- | --- | --- | --- |
| `contar_glaciares` | Cuenta glaciares y suma su área | `cod_scuen: str` (código BNA de 4 dígitos), `clase: str` | `n: int`, `area_km2: float` | Selección por atributo `COD_SCUEN`, no por caja; área en EPSG:32719 | Implementada y probada (`tests/`) |
| `ndsi_por_glaciar` | Nieve o hielo de fin de verano en un glaciar | `id_glaciar: str`, `anio: int` (2018-2024) | `frac_nieve` (0-1), `area_nieve_m2` (m²), `n_pix_validos`, `no_concluyente` | Sentinel-2 L2A feb-mar, nubes < 10 %, máscara SCL; grilla 20 m EPSG:32719; píxel cuenta si su centro cae en el polígono; NDSI ≥ 0,4 | Implementada y probada (`tests/`) |
| `cambio_embedding` | Cambio del embedding AlphaEarth entre dos años | `id_glaciar: str`, `anio_a: int`, `anio_b: int` (2017-2024) | `cambio` (1 − coseno, 0 a 2), `n_pix`, `no_concluyente` | Grilla 10 m EPSG:32719; media no ponderada de píxeles con centro en el polígono | Implementada (lee `resultados/embedding_por_glaciar.csv`) |
| `umbral_fondo` | Ruido del embedding en terreno sin glaciar | `anio_a: int`, `anio_b: int`, `percentil: int` | umbral (adimensional) | Región = envolvente convexa + 2 km menos glaciares + 300 m; muestreo a 30 m | Diseñada (datos en `resultados/embedding_fondo.csv`) |
| `contexto_topografico` | Altura, pendiente y orientación | `id_glaciar: str` | `altura_m`, `pendiente_grados`, `orientacion_grados` | Copernicus DEM GLO-30, media sobre el polígono en EPSG:32719 | Diseñada |
| `estado_segun_ugalde` | Estado del glaciar en Ugalde et al. (2026) | `id_glaciar: str` | `vanishment` (`Entirely vanished` o `Presumably vanished`) o `no_listado` | Cruce por atributo `COD_GLA` con el material suplementario, sin cruce espacial; los 17 registros de la subcuenca 0570 cruzan con el inventario | Diseñada (lógica en `src/validar_ugalde.py`) |

Reglas comunes: toda herramienta devuelve `resultado` y `traza`; si los datos no alcanzan devuelve `no_se_puede: true` con la razón. El agente no puede escribir una cifra que no esté en el `resultado` de alguna llamada.

## 3. Ejemplo de traza

Pregunta: «¿Cuánta nieve o hielo perdió el glaciarete CL105706051@ entre 2020 y 2023?»

```json
[
  {"herramienta": "ndsi_por_glaciar",
   "parametros": {"id_glaciar": "CL105706051@", "anio": 2020},
   "fuente": "resultados/ndsi_por_glaciar.csv",
   "resultado": {"frac_nieve": 0.7303, "area_nieve_m2": 182000.0, "n_pix_validos": 623, "no_concluyente": false}},
  {"herramienta": "ndsi_por_glaciar",
   "parametros": {"id_glaciar": "CL105706051@", "anio": 2023},
   "fuente": "resultados/ndsi_por_glaciar.csv",
   "resultado": {"frac_nieve": 0.509, "area_nieve_m2": 126800.0, "n_pix_validos": 623, "no_concluyente": false}}
]
```

Respuesta del agente: «Entre 2020 y 2023 la superficie con NDSI ≥ 0,4 del glaciarete CL105706051@ pasó de 182.000 a 126.800 m², una pérdida de 55.200 m² (ndsi_por_glaciar, llamadas 1 y 2).» La resta la hace una herramienta o queda explícita con los dos valores citados.

> Los dos `<cifra>` de 2020 se llenan con la salida real de la herramienta (cada traza trae también el campo `hora`):
>
> ```powershell
> python -c "import sys; sys.path.insert(0,'src'); import herramientas as h, json; print(json.dumps(h.ndsi_por_glaciar('CL105706051@', 2020), indent=1, ensure_ascii=False))"
> ```

## 4. Set de control

El borrador está en `control/preguntas_control.csv`: 27 preguntas, 5 imposibles y 2 trampas (selección por caja y CRS). Las respuestas se calculan sin agente con los scripts de `src/`; las marcadas «PENDIENTE» se llenan al correr el análisis.
