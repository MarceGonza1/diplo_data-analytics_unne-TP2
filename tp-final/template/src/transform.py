"""
TRANSFORM — De datos crudos a un dataset analítico   *** ACÁ TRABAJÁS VOS ***
=============================================================================

Este es el corazón del TP. El Extract ya te trae los datos y el Load ya
sabe guardarlos: lo que falta es convertir lo crudo en algo analizable.

El recorrido es:

    formato ANCHO (como llega de la API)
        fecha        China   Brasil   ...   __TOTAL__
        1993-01-01    12.3     45.6   ...      120.0

              |  ancho_a_largo()          <- TODO 1
              v

    formato LARGO / "tidy" (una fila por observación)
        anio  provincia  destino  valor_musd  total_provincia_musd
        1993  Chaco      China          12.3                 120.0
        1993  Chaco      Brasil         45.6                 120.0

              |  + columnas derivadas     <- TODO 2, 3, 4, 5, 6
              |  + join con rubros        <- TODO 7, 8
              v

    dataset final de 13 columnas

CÓMO TRABAJAR
-------------
Hay 8 TODOs numerados. Hacelos EN ORDEN: cada uno usa el anterior.
Después de cada TODO corré los tests para ver si vas bien:

    python tests/test_transform.py

Las funciones ya tienen su docstring con el CONTRATO (qué recibe, qué
devuelve). Respetalo: el resto del pipeline cuenta con eso.
"""

import logging

import config

# Nombre reservado que usa extract.py para la serie del total provincial
CLAVE_TOTAL = "__TOTAL__"

# Orden final de las columnas del CSV. Es un contrato: el Load lo respeta
# y la consigna del TP lo exige. NO lo modifiques.
COLUMNAS = [
    "anio",
    "provincia",
    "destino",
    "region_destino",
    "valor_musd",
    "total_provincia_musd",
    "participacion_pct",
    "var_interanual_pct",
    "decada",
    "ranking_destino",
    "es_top3",
    "rubro_principal",
    "pp_participacion_pct",
]


# ======================================================================
# 1) ANCHO -> LARGO
# ======================================================================
def extraer_anio(fecha_texto):
    """Convierte '1993-01-01' en el entero 1993.

    Esta te la dejamos resuelta como ejemplo del estilo que esperamos:
    una función corta, con nombre de verbo y un solo trabajo.
    """
    return int(fecha_texto[:4])


def ancho_a_largo(paquetes_destino):
    """CONTRATO: recibe los paquetes crudos de destino; devuelve una lista
    de dicts con una fila por (año, provincia, destino).

    Cada dict debe tener exactamente estas 5 claves:
        anio                  (int)
        provincia             (str)
        destino               (str)
        valor_musd            (float, redondeado a 2 decimales)
        total_provincia_musd  (float, redondeado a 2 decimales)

    Cada paquete tiene esta forma:
        {
          "provincia": "Chaco",
          "orden_columnas": ["China", "Brasil", ..., "__TOTAL__"],
          "data": [["1993-01-01", 12.3, 45.6, ..., 120.0], ...]
        }

    En cada fila de 'data', el elemento 0 es la fecha y los siguientes
    son los valores, EN EL MISMO ORDEN que 'orden_columnas'.

    Ojo con tres cosas:
      - La columna CLAVE_TOTAL no es un destino: no genera fila propia,
        pero su valor va en 'total_provincia_musd' de todas las filas
        de ese año.
      - Si un valor es None, salteá esa observación (patrón 'continue').
      - Redondeá los valores a 2 decimales con round().
    """
    filas = []

    # TODO 1 --------------------------------------------------------------
    # Recorré cada paquete, y dentro de cada uno cada fila de 'data'.
    #
    # Pistas:
    #   - Para separar fecha y valores:   fecha = fila_cruda[0]
    #                                     valores = fila_cruda[1:]
    #   - Para saber en qué posición está el total:
    #                                     columnas.index(CLAVE_TOTAL)
    #   - Para recorrer nombre y posición a la vez:
    #                                     for i, nombre in enumerate(columnas)
    #   - Usá extraer_anio() para el año.
    #
    # Estructura sugerida (bucles anidados, como en la Clase 3):
    #   for paquete in paquetes_destino:
    #       ... leer provincia y orden_columnas ...
    #       for fila_cruda in paquete["data"]:
    #           ... calcular anio y total ...
    #           for posicion, nombre in enumerate(columnas):
    #               ... saltear el total y los None, y hacer filas.append({...})
    for paquete in paquetes_destino:
        provincia = paquete["provincia"]
        columnas = paquete["orden_columnas"]
        posicion_total = columnas.index(CLAVE_TOTAL)

        for fila_cruda in paquete["data"]:
            fecha = fila_cruda[0]
            anio = extraer_anio(fecha)
            
            # El valor total provincial viene en la posición del __TOTAL__
            val_total = fila_cruda[1:][posicion_total]
            total_provincia_musd = round(val_total, 2) if val_total is not None else None

            # Recorremos cada destino individual
            for posicion, nombre_destino in enumerate(columnas):
                if nombre_destino == CLAVE_TOTAL:
                    continue  # El total no es un país/destino individual
                
                valor = fila_cruda[1:][posicion]
                if valor is None:
                    continue  # Descartamos valores nulos
                
                filas.append({
                    "anio": anio,
                    "provincia": provincia,
                    "destino": nombre_destino,
                    "valor_musd": round(float(valor), 2),
                    "total_provincia_musd": total_provincia_musd
                })
    # ---------------------------------------------------------------------

    logging.info("  ancho_a_largo: %s filas", len(filas))
    return filas


# ======================================================================
# 2) COLUMNAS DERIVADAS SIMPLES
# ======================================================================
def clasificar_region(destino):
    """Devuelve la región geoeconómica de un país de destino.

    Ejemplos:  'Brasil' -> 'Mercosur'   |   'China' -> 'Asia'

    El mapeo está en config.REGIONES. Si el país NO está en el
    diccionario, devolvé config.REGION_POR_DEFECTO en lugar de romper.
    """
    # TODO 2 --------------------------------------------------------------
    return config.REGIONES.get(destino, config.REGION_POR_DEFECTO)
    # ---------------------------------------------------------------------


def calcular_decada(anio):
    """Devuelve la década de un año como texto."""
    inicio_decada = (anio // 10) * 10
    return f"{inicio_decada}s"
def calcular_participacion(valor, total):
    """Qué porcentaje del total exportado representa este destino.

    Ejemplo:  valor=110.93, total=401.74  ->  27.61

    Devolvé None si el total es cero o None: dividir por cero rompe el
    programa, y un dato ausente es más honesto que un cero inventado.
    Redondeá a 2 decimales.
    """
    # TODO 4 --------------------------------------------------------------
    if not total or total == 0 or valor is None:
        return None
    return round((valor / total) * 100, 2)
    # ---------------------------------------------------------------------


def agregar_derivadas_simples(filas):
    """Agrega region_destino, decada y participacion_pct a cada fila.

    CONTRATO: modifica y devuelve la misma lista de filas.
    """
    for fila in filas:
        fila["region_destino"] = clasificar_region(fila["destino"])
        fila["decada"] = calcular_decada(fila["anio"])
        fila["participacion_pct"] = calcular_participacion(
            fila["valor_musd"], fila["total_provincia_musd"]
        )
    return filas


# ======================================================================
# 3) VARIACIÓN INTERANUAL
# ======================================================================
def calcular_variacion(actual, anterior):
    """Variación porcentual entre dos valores.

    Fórmula:  (actual - anterior) / anterior * 100
    Ejemplo:  actual=110.93, anterior=75.79  ->  46.36

    Devolvé None si 'anterior' es None o cero. Redondeá a 2 decimales.
    """
    # TODO 5 --------------------------------------------------------------
    if actual is None or anterior is None or anterior == 0:
        return None
    return round(((actual - anterior) / anterior) * 100, 2)
    # ---------------------------------------------------------------------


def agregar_variacion_interanual(filas):
    """Agrega var_interanual_pct comparando cada fila con el año previo
    del MISMO destino y la MISMA provincia.

    CONTRATO: modifica y devuelve la misma lista de filas. La primera
    observación de cada serie queda con None (no hay año anterior).
    """
    # TODO 6 --------------------------------------------------------------
    # Estrategia recomendada (dos pasadas, sin ordenar nada):
    #
    #   1. Primera pasada: armá un diccionario 'indice' donde la clave sea
    #      la tupla (provincia, destino, anio) y el valor sea valor_musd.
    #
    #   2. Segunda pasada: para cada fila, buscá en ese índice la clave
    #      (provincia, destino, anio - 1). Si no está, .get() devuelve None
    #      y calcular_variacion() ya sabe qué hacer con eso.
    #
    # Usar un dict como índice evita recorrer toda la lista por cada fila.
    grupos = {}
    for fila in filas:
        clave = (fila["provincia"], fila["anio"])
        grupos.setdefault(clave, []).append(fila)

    for clave, grupo in grupos.items():
        grupo_ordenado = sorted(grupo, key=lambda f: f.get("valor_musd") or 0, reverse=True)
        for i, fila in enumerate(grupo_ordenado, start=1):
            fila["ranking_destino"] = i

    return filas
    # ---------------------------------------------------------------------


# ======================================================================
# 4) RANKING DE DESTINOS
# ======================================================================
def agregar_ranking(filas, top_n=None):
    """Agrega ranking_destino (1 = el que más exportó) y es_top3 (bool).

    El ranking se calcula DENTRO de cada grupo (provincia, año): ser el
    destino #1 de Chaco en 2024 no dice nada sobre Misiones en 1998.

    CONTRATO: modifica y devuelve la misma lista de filas.
    """
    if top_n is None:
        top_n = config.TOP_N

    # TODO 7 --------------------------------------------------------------
    # Estrategia sugerida:
    #   1. Agrupá las filas en un dict cuya clave sea (provincia, anio).
    #      Pista: dict.setdefault(clave, []).append(fila)
    #   2. Para cada grupo, ordenalo por valor_musd de mayor a menor:
    #      sorted(grupo, key=lambda f: f["valor_musd"], reverse=True)
    #   3. Recorré el grupo ordenado con enumerate(..., start=1) y asigná
    #      'ranking_destino' y 'es_top3' (un booleano: posición <= top_n).
    
    def agregar_ranking(filas, top_n=3):
        """Agrega a cada fila la clave ranking_destino y es_top3 para esa provincia y año."""
    grupos = {}
    for fila in filas:
        clave = (fila["provincia"], fila["anio"])
        grupos.setdefault(clave, []).append(fila)

    for clave, grupo in grupos.items():
        grupo_ordenado = sorted(grupo, key=lambda f: f.get("valor_musd") or 0, reverse=True)
        for i, fila in enumerate(grupo_ordenado, start=1):
            fila["ranking_destino"] = i
            fila["es_top3"] = (i <= 3)

    return filas


# ======================================================================
# 5) JOIN CON LOS RUBROS
# ======================================================================
def construir_indice_rubros(paquetes_rubro):
    indice = {}
    
    for paquete in paquetes_rubro:
        provincia = paquete.get("provincia")
        columnas = paquete.get("orden_columnas", [])
        
        for fila in paquete.get("data", []):
            fecha = fila[0]
            anio = extraer_anio(fecha)
            
            # Los valores de los rubros van desde el índice 1 en adelante
            valores = fila[1:]
            
            # Mapeamos cada columna con su valor numérico
            rubros = {}
            for i, nombre_rubro in enumerate(columnas):
                if i < len(valores) and valores[i] is not None:
                    rubros[nombre_rubro] = valores[i]
            
            # 1. Rubro principal (el de mayor valor)
            rubro_principal = max(rubros, key=rubros.get) if rubros else None
            
            # 2. Porcentaje de Productos primarios sobre el total
            total = sum(rubros.values()) if rubros else 0
            pp_val = rubros.get("Productos primarios", 0)
            pp_participacion_pct = round((pp_val / total) * 100, 1) if total > 0 else 0.0
            
            datos = {
                "rubro_principal": rubro_principal,
                "pp_participacion_pct": pp_participacion_pct
            }
            
            # Guardamos la clave en formato int
            if anio is not None:
                indice[(provincia, int(anio))] = datos

    logging.info(" Índice de rubros: %s claves (provincia, año)", len(indice))
    return indice

def unir_con_rubros(filas, indice_rubros):
    """Join por clave compuesta (provincia, anio)."""
    for fila in filas:
        prov = fila.get("provincia")
        anio_val = fila.get("anio") if fila.get("anio") is not None else fila.get("año")
        
        try:
            anio_key = int(str(anio_val).strip())
        except (ValueError, TypeError):
            anio_key = anio_val

        # Busca primero por clave int y luego por valor crudo
        info = indice_rubros.get((prov, anio_key))
        if info is None:
            info = indice_rubros.get((prov, anio_val), {})

        # Asigna las columnas; si no hubo match, quedan en None
        fila["rubro_principal"] = info.get("rubro_principal")
        fila["pp_participacion_pct"] = info.get("pp_participacion_pct")

    return filas
    # ---------------------------------------------------------------------


# ======================================================================
# ORQUESTACIÓN DEL TRANSFORM  (ya resuelta: no hace falta tocarla)
# ======================================================================
def ordenar_columnas(filas):
    """Devuelve las filas con las claves en el orden definido por COLUMNAS."""
    return [{columna: fila.get(columna) for columna in COLUMNAS} for fila in filas]


def transformar(datos_crudos):
    """CONTRATO: recibe {'destino': [...], 'rubro': [...]} crudos;
    devuelve la lista de filas finales, ordenadas y con las 13 columnas.

    Fijate cómo esta función 'directora' solo llama a las otras en orden.
    Eso es diseño modular: si mañana cambia una regla, tocás una función.
    """
    logging.info("TRANSFORM: iniciando")

    filas = ancho_a_largo(datos_crudos["destino"])
    filas = agregar_derivadas_simples(filas)
    filas = agregar_variacion_interanual(filas)
    filas = agregar_ranking(filas)

    indice = construir_indice_rubros(datos_crudos["rubro"])
    filas = unir_con_rubros(filas, indice)

    filas.sort(key=lambda f: (f["provincia"], f["anio"], f["ranking_destino"]))
    filas = ordenar_columnas(filas)

    logging.info("TRANSFORM OK: %s filas x %s columnas", len(filas), len(COLUMNAS))
    return filas
