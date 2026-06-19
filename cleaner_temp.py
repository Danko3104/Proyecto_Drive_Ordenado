"""
cleaner_temp.py - Módulo de limpieza de archivos temporales y basura

Detecta y elimina archivos basura comunes como temporales de Windows/Mac,
logs, cachés, etc.
"""

import os
import fnmatch
from typing import List, Dict


PATRONES_BASURA = {
    'Windows temporales': ['*.tmp', '~$*', 'Thumbs.db', 'desktop.ini'],
    'Mac basura': ['.DS_Store', '._*', '.Spotlight-V100', '.Trashes'],
    'Logs': ['*.log', '*.log.*'],
    'Caché': ['*.cache', '*.bak', '*.old'],
    'Office temporales': ['~$*.docx', '~$*.xlsx', '~$*.pptx']
}


def _coincide_con_patron(nombre_archivo: str, patron: str) -> bool:
    """Verifica si un nombre de archivo coincide con un patrón glob."""
    return fnmatch.fnmatch(nombre_archivo, patron)


def escanear_archivos_basura(ruta: str) -> Dict:
    """
    Escanea una carpeta en busca de archivos basura.

    Args:
        ruta: Ruta de la carpeta a escanear

    Returns:
        Diccionario con archivos encontrados y estadísticas
    """
    if not os.path.exists(ruta) or not os.path.isdir(ruta):
        return {'archivos': [], 'total_encontrados': 0, 'total_mb': 0, 'por_categoria': {}}

    archivos_encontrados = []
    por_categoria = {}

    for raiz, _, archivos in os.walk(ruta):
        for nombre in archivos:
            for categoria, patrones in PATRONES_BASURA.items():
                for patron in patrones:
                    if _coincide_con_patron(nombre, patron):
                        ruta_completa = os.path.join(raiz, nombre)
                        try:
                            tamaño = os.path.getsize(ruta_completa)
                            archivos_encontrados.append({
                                'nombre': nombre,
                                'ruta': ruta_completa,
                                'tamaño_bytes': tamaño,
                                'categoria_basura': categoria
                            })

                            if categoria not in por_categoria:
                                por_categoria[categoria] = {'cantidad': 0, 'tamaño_bytes': 0}
                            por_categoria[categoria]['cantidad'] += 1
                            por_categoria[categoria]['tamaño_bytes'] += tamaño
                        except (OSError, IOError):
                            pass
                        break

    total_bytes = sum(a['tamaño_bytes'] for a in archivos_encontrados)

    for cat in por_categoria:
        por_categoria[cat]['tamaño_mb'] = round(por_categoria[cat]['tamaño_bytes'] / (1024 * 1024), 2)

    return {
        'archivos': archivos_encontrados,
        'total_encontrados': len(archivos_encontrados),
        'total_mb': round(total_bytes / (1024 * 1024), 2),
        'por_categoria': por_categoria
    }


def eliminar_basura(rutas: List[str]) -> Dict:
    """
    Elimina los archivos basura especificados.

    Args:
        rutas: Lista de rutas de archivos a eliminar

    Returns:
        Diccionario con resultados de la eliminación
    """
    resultado = {
        'eliminados': [],
        'fallidos': [],
        'espacio_liberado_mb': 0,
        'total_eliminados': 0
    }

    for ruta in rutas:
        try:
            if not os.path.exists(ruta):
                resultado['fallidos'].append({'ruta': ruta, 'error': 'No existe'})
                continue
            if not os.path.isfile(ruta):
                resultado['fallidos'].append({'ruta': ruta, 'error': 'No es un archivo'})
                continue

            tamaño = os.path.getsize(ruta)
            os.remove(ruta)
            resultado['eliminados'].append(ruta)
            resultado['espacio_liberado_mb'] += tamaño / (1024 * 1024)
            resultado['total_eliminados'] += 1

        except Exception as e:
            resultado['fallidos'].append({'ruta': ruta, 'error': str(e)})

    resultado['espacio_liberado_mb'] = round(resultado['espacio_liberado_mb'], 2)
    return resultado
