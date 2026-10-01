# Diplomatura en Data Analytics — UNNE

Este repositorio contiene el Trabajo Práctico Integrador para el Módulo II.

El proyecto implementa un pipeline automatizado, donde se procesan datos en Python, respectivamente de información de exportaciones provinciales del Nordestes Argentino.

## Estructura del Pipeline

1. **Extract (`src/extract.py`):** Consulta la API de Datos Abiertos del Estado Argentino (`datos.gob.ar`) para obtener los conjuntos de datos históricos de exportaciones por provincia.
2. **Transform (`src/transform.py`):** Realiza la limpieza, tipología de datos y el cálculo de métricas clave:
   - Participación porcentual de exportación por provincia (`participacion_pct`).
   - Variación interanual (`interanual_pct`).
   - Clasificación por décadas y ranking de destinos principales por año.
   - Cruce de información con rubros principales y productos primarios.
3. **Load (`src/load.py`):** Aplica validaciones de calidad de datos (Quality Checks de cantidad de filas, columnas requeridas y unicidad) y guarda los productos finales:
   - `data/processed/exportaciones_nea.csv` (Dataset consolidado de 13 columnas y ~1408 filas).
   - `data/processed/resumen.json` (Métricas del proceso y ficha técnica).
   - `logs/pipeline.log` (Bitácora de ejecuciones del sistema).

   El repositorio se puede conseguir clonandolo:

git clone [https://github.com/MarceGonza1/diplo_data-analytics_unne-TP2.git](https://github.com/MarceGonza1/diplo_data-analytics_unne-TP2.git)
cd diplo_data-analytics_unne-TP2

Análisis y Hallazgos sobre los Datos:
Luego de probar los diferentes "TODOS", evidenciamos mucha exportación de la región del NEA hacia todo lo referido al sector agropecuario. Socios comerciales como Brasil (dentro del Mercosur) y China se mantienen de forma constante entre los principales destinos del volumen exportado a lo largo de las décadas analizadas, mostrando una dependencia clara de la demanda de commodities en mercados clave.


*Diplomatura en Data Analytics — Universidad Nacional del Nordeste (UNNE)*
