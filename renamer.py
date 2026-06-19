"""
renamer.py - Módulo de renombrado masivo de archivos

Aplica reglas configurables para renombrar múltiples archivos a la vez.
"""

import os
import unicodedata
import re
from datetime import datetime
from typing import List, Dict


def _quitar_acentos(texto: str) -> str:
    """Elimina acentos y caracteres especiales de un texto."""
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def _aplicar_regla(nombre: str, regla: str, metadata: Dict = None) -> str:
    """
    Aplica una regla de renombrado a un nombre de archivo.

    Args:
        nombre: Nombre original del archivo
        regla: Regla a aplicar
        metadata: Metadatos del archivo (fecha, etc.)

    Returns:
        Nombre modificado
    """
    nombre_base, extension = os.path.splitext(nombre)

    if regla == 'minusculas':
        nombre_base = nombre_base.lower()
    elif regla == 'sin_espacios':
        nombre_base = nombre_base.replace(' ', '_')
    elif regla == 'sin_acentos':
        nombre_base = _quitar_acentos(nombre_base)
    elif regla == 'agregar_fecha_inicio' and metadata:
        fecha = metadata.get('fecha_modificacion', datetime.now())
        fecha_str = fecha.strftime('%Y-%m-%d') if hasattr(fecha, 'strftime') else str(fecha)[:10]
        nombre_base = f"{fecha_str}_{nombre_base}"
    elif regla == 'agregar_fecha_fin' and metadata:
        fecha = metadata.get('fecha_modificacion', datetime.now())
        fecha_str = fecha.strftime('%Y-%m-%d') if hasattr(fecha, 'strftime') else str(fecha)[:10]
        nombre_base = f"{nombre_base}_{fecha_str}"
    elif regla == 'quitar_caracteres_especiales':
        nombre_base = re.sub(r'[^\w\s.-]', '', nombre_base)

    return nombre_base + extension


def aplicar_reglas_renombrado(archivos: List[Dict], reglas: List[str]) -> List[Dict]:
    """
    Calcula los nuevos nombres aplicando las reglas especificadas.

    Args:
        archivos: Lista de archivos con 'ruta_origen' y 'nombre_original'
        reglas: Lista de reglas a aplicar en orden

    Returns:
        Lista con nombres originales y nuevos
    """
    resultados = []

    for archivo in archivos:
        nombre_original = archivo.get('nombre_original', '')
        nombre_nuevo = nombre_original

        for regla in reglas:
            nombre_nuevo = _aplicar_regla(nombre_nuevo, regla, archivo)

        resultados.append({
            'nombre_original': nombre_original,
            'nombre_nuevo': nombre_nuevo,
            'ruta_origen': archivo.get('ruta_origen', ''),
            'cambiara': nombre_original != nombre_nuevo
        })

    return resultados


def ejecutar_renombrado(archivos_con_nombres_nuevos: List[Dict]) -> Dict:
    """
    Ejecuta el renombrado de los archivos.

    Args:
        archivos_con_nombres_nuevos: Lista con 'ruta_origen' y 'nombre_nuevo'

    Returns:
        Diccionario con resultados: exitosos, fallidos
    """
    resultado = {
        'exitosos': [],
        'fallidos': [],
        'total_exitosos': 0,
        'total_fallidos': 0
    }

    for item in archivos_con_nombres_nuevos:
        try:
            ruta_origen = item.get('ruta_origen', '')
            nombre_nuevo = item.get('nombre_nuevo', '')

            if not os.path.exists(ruta_origen):
                resultado['fallidos'].append({
                    'ruta': ruta_origen,
                    'error': 'El archivo no existe'
                })
                resultado['total_fallidos'] += 1
                continue

            if not nombre_nuevo:
                resultado['fallidos'].append({
                    'ruta': ruta_origen,
                    'error': 'Nombre nuevo vacío'
                })
                resultado['total_fallidos'] += 1
                continue

            ruta_destino = os.path.join(os.path.dirname(ruta_origen), nombre_nuevo)

            if ruta_origen == ruta_destino:
                continue

            os.rename(ruta_origen, ruta_destino)
            resultado['exitosos'].append({
                'ruta_original': ruta_origen,
                'ruta_nueva': ruta_destino
            })
            resultado['total_exitosos'] += 1

        except Exception as e:
            resultado['fallidos'].append({
                'ruta': item.get('ruta_origen', ''),
                'error': str(e)
            })
            resultado['total_fallidos'] += 1

    return resultado
