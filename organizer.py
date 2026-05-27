"""
organizer.py - Módulo de organización de archivos

Este módulo contiene la lógica principal para escanear, clasificar y organizar
archivos en carpetas según su tipo y fecha de modificación.
"""

import os
import shutil
from datetime import datetime
from typing import List, Dict, Tuple


# Mapeo de categorías por extensión
CATEGORIAS = {
    'documentos': ['.pdf', '.docx', '.doc', '.txt', '.pptx', '.xlsx', '.csv'],
    'imagenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'multimedia': ['.mp4', '.mp3', '.avi', '.mov', '.wav', '.mkv'],
    'otros': []
}

# Nombres de meses en español
MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}


def obtener_categoria(extension: str) -> str:
    """
    Determina la categoría de un archivo según su extensión.

    Args:
        extension: Extensión del archivo en minúsculas (ej: '.pdf')

    Returns:
        Nombre de la categoría: 'documentos', 'imagenes', 'multimedia' u 'otros'
    """
    ext = extension.lower()
    for categoria, extensiones in CATEGORIAS.items():
        if categoria == 'otros':
            continue
        if ext in extensiones:
            return categoria
    return 'otros'


def escanear_archivos(ruta_origen: str) -> List[Dict]:
    """
    Recorre recursivamente la carpeta origen y recopila información de todos los archivos.

    Args:
        ruta_origen: Ruta absoluta de la carpeta a escanear

    Returns:
        Lista de diccionarios con metadatos de cada archivo

    Raises:
        FileNotFoundError: Si la ruta origen no existe
        NotADirectoryError: Si la ruta no es un directorio
    """
    if not os.path.exists(ruta_origen):
        raise FileNotFoundError(f"La ruta no existe: {ruta_origen}")

    if not os.path.isdir(ruta_origen):
        raise NotADirectoryError(f"La ruta no es un directorio: {ruta_origen}")

    archivos = []

    for raiz, _, archivos_en_dir in os.walk(ruta_origen):
        for nombre_archivo in archivos_en_dir:
            ruta_completa = os.path.join(raiz, nombre_archivo)

            # Obtener información del archivo
            try:
                _, extension = os.path.splitext(nombre_archivo)
                tamaño = os.path.getsize(ruta_completa)
                fecha_mod = os.path.getmtime(ruta_completa)

                archivo_info = {
                    'nombre_original': nombre_archivo,
                    'nombre_base': os.path.splitext(nombre_archivo)[0],
                    'extension': extension.lower(),
                    'categoria': obtener_categoria(extension),
                    'tamaño_bytes': tamaño,
                    'fecha_modificacion': datetime.fromtimestamp(fecha_mod),
                    'ruta_origen': ruta_completa,
                    'ruta_relativa': os.path.relpath(ruta_completa, ruta_origen)
                }

                archivos.append(archivo_info)
            except (OSError, IOError) as e:
                # Si no se puede leer un archivo, lo ignoramos y continuamos
                continue

    return archivos


def generar_ruta_destino(archivo_info: Dict, ruta_base_destino: str,
                         organizar_por_fecha: bool = True) -> str:
    """
    Genera la ruta de destino para un archivo según su categoría y fecha.

    Args:
        archivo_info: Diccionario con metadatos del archivo
        ruta_base_destino: Ruta base donde se creará la estructura
        organizar_por_fecha: Si True, organiza en subcarpetas por año/mes

    Returns:
        Ruta completa de destino para el archivo
    """
    categoria = archivo_info['categoria'].capitalize()

    if organizar_por_fecha:
        fecha = archivo_info['fecha_modificacion']
        año = str(fecha.year)
        mes = MESES_ES[fecha.month]
        ruta_destino = os.path.join(ruta_base_destino, categoria, año, mes)
    else:
        ruta_destino = os.path.join(ruta_base_destino, categoria)

    return ruta_destino


def obtener_nombre_unico(ruta_destino: str, nombre_archivo: str) -> str:
    """
    Genera un nombre único si ya existe un archivo con el mismo nombre.

    Si el archivo ya existe, añade un sufijo numérico: archivo_1.pdf, archivo_2.pdf, etc.

    Args:
        ruta_destino: Ruta del directorio destino
        nombre_archivo: Nombre original del archivo

    Returns:
        Nombre único para el archivo
    """
    ruta_completa = os.path.join(ruta_destino, nombre_archivo)

    if not os.path.exists(ruta_completa):
        return nombre_archivo

    # Si ya existe, generar nombre con sufijo
    nombre_base, extension = os.path.splitext(nombre_archivo)
    contador = 1

    while True:
        nuevo_nombre = f"{nombre_base}_{contador}{extension}"
        ruta_nueva = os.path.join(ruta_destino, nuevo_nombre)

        if not os.path.exists(ruta_nueva):
            return nuevo_nombre

        contador += 1


def mover_archivo(archivo_info: Dict, ruta_destino: str, nuevo_nombre: str) -> Dict:
    """
    Mueve un archivo a su destino utilizando shutil.move.

    Args:
        archivo_info: Diccionario con metadatos del archivo
        ruta_destino: Ruta del directorio destino
        nuevo_nombre: Nombre del archivo en destino

    Returns:
        Diccionario actualizado con información del movimiento

    Raises:
        OSError: Si hay problemas al mover el archivo
    """
    # Crear directorio destino si no existe
    os.makedirs(ruta_destino, exist_ok=True)

    ruta_final = os.path.join(ruta_destino, nuevo_nombre)

    try:
        shutil.move(archivo_info['ruta_origen'], ruta_final)

        resultado = archivo_info.copy()
        resultado['ruta_destino'] = ruta_final
        resultado['nombre_destino'] = nuevo_nombre
        resultado['movido'] = True
        resultado['error'] = None

        return resultado

    except Exception as e:
        resultado = archivo_info.copy()
        resultado['ruta_destino'] = None
        resultado['nombre_destino'] = None
        resultado['movido'] = False
        resultado['error'] = str(e)

        return resultado


def organizar_archivos(ruta_origen: str, ruta_destino: str = None,
                       criterio: str = 'tipo', organizar_por_fecha: bool = True) -> Tuple[List[Dict], Dict]:
    """
    Función principal que organiza archivos según las configuraciones especificadas.

    Args:
        ruta_origen: Ruta de la carpeta a organizar
        ruta_destino: Ruta donde se moverán los archivos organizados
                      Si es None, se usa la misma ruta_origen
        criterio: Criterio principal ('tipo', 'fecha', 'tamaño')
        organizar_por_fecha: Si True, organiza en subcarpetas por año/mes

    Returns:
        Tupla con (lista de archivos procesados, estadísticas)

    Raises:
        FileNotFoundError: Si la ruta origen no existe
        ValueError: Si el criterio no es válido
    """
    if ruta_destino is None:
        ruta_destino = ruta_origen

    if criterio not in ['tipo', 'fecha', 'tamaño']:
        raise ValueError(f"Criterio no válido: {criterio}")

    # Escanear archivos
    archivos = escanear_archivos(ruta_origen)

    if not archivos:
        return [], {'total_archivos': 0, 'categorias': {}, 'errores': 0}

    # Procesar cada archivo
    archivos_procesados = []
    estadisticas = {
        'total_archivos': len(archivos),
        'categorias': {},
        'errores': 0,
        'tamaño_total_bytes': 0
    }

    for archivo in archivos:
        # Generar ruta de destino
        if criterio == 'tipo':
            ruta_cat_destino = generar_ruta_destino(archivo, ruta_destino, organizar_por_fecha)
        elif criterio == 'fecha':
            # Priorizar fecha sobre tipo
            fecha = archivo['fecha_modificacion']
            año = str(fecha.year)
            mes = MESES_ES[fecha.month]
            ruta_cat_destino = os.path.join(ruta_destino, año, mes, archivo['categoria'].capitalize())
        elif criterio == 'tamaño':
            # Clasificar por tamaño
            tamaño_mb = archivo['tamaño_bytes'] / (1024 * 1024)
            if tamaño_mb < 1:
                categoria_tamaño = 'Pequeños_1MB'
            elif tamaño_mb < 10:
                categoria_tamaño = 'Medianos_1-10MB'
            elif tamaño_mb < 100:
                categoria_tamaño = 'Grandes_10-100MB'
            else:
                categoria_tamaño = 'Muy_Grandes_100MB+'
            ruta_cat_destino = os.path.join(ruta_destino, categoria_tamaño, archivo['categoria'].capitalize())

        # Obtener nombre único
        nuevo_nombre = obtener_nombre_unico(ruta_cat_destino, archivo['nombre_original'])

        # Mover archivo
        resultado = mover_archivo(archivo, ruta_cat_destino, nuevo_nombre)
        archivos_procesados.append(resultado)

        # Actualizar estadísticas
        cat = archivo['categoria']
        if cat not in estadisticas['categorias']:
            estadisticas['categorias'][cat] = {'cantidad': 0, 'tamaño_bytes': 0}
        estadisticas['categorias'][cat]['cantidad'] += 1
        estadisticas['categorias'][cat]['tamaño_bytes'] += archivo['tamaño_bytes']
        estadisticas['tamaño_total_bytes'] += archivo['tamaño_bytes']

        if resultado.get('error'):
            estadisticas['errores'] += 1

    return archivos_procesados, estadisticas


def obtener_estadisticas_adicionales(archivos_procesados: List[Dict]) -> Dict:
    """
    Calcula estadísticas adicionales de los archivos procesados.

    Args:
        archivos_procesados: Lista de archivos con información de procesamiento

    Returns:
        Diccionario con estadísticas calculadas
    """
    if not archivos_procesados:
        return {}

    extensiones = {}
    fechas_años = {}
    tamaño_total = 0
    movidos = 0
    errores = 0

    for archivo in archivos_procesados:
        # Contar extensiones
        ext = archivo['extension'] or 'sin_extension'
        extensiones[ext] = extensiones.get(ext, 0) + 1

        # Contar por año
        año = archivo['fecha_modificacion'].year
        fechas_años[año] = fechas_años.get(año, 0) + 1

        # Tamaño total
        tamaño_total += archivo['tamaño_bytes']

        # Contar movimientos y errores
        if archivo.get('movido'):
            movidos += 1
        if archivo.get('error'):
            errores += 1

    return {
        'extensiones_unicas': len(extensiones),
        'conteo_por_extension': extensiones,
        'años_encontrados': sorted(fechas_años.keys()),
        'conteo_por_año': fechas_años,
        'tamaño_total_mb': round(tamaño_total / (1024 * 1024), 2),
        'archivos_movidos': movidos,
        'archivos_con_error': errores
    }
