"""
duplicates.py - Módulo de detección de archivos duplicados

Este módulo proporciona funciones para detectar archivos duplicados
mediante el cálculo de hashes MD5.
"""

import hashlib
import os
from typing import List, Dict, Tuple
from collections import defaultdict


def calcular_hash_md5(ruta_archivo: str, tamaño_bloque: int = 8192) -> str:
    """
    Calcula el hash MD5 de un archivo.

    Lee el archivo en bloques para manejar archivos grandes de forma eficiente
    sin cargarlos completamente en memoria.

    Args:
        ruta_archivo: Ruta absoluta del archivo
        tamaño_bloque: Tamaño del bloque para lectura (default: 8192 bytes)

    Returns:
        Hash MD5 del archivo como string hexadecimal

    Raises:
        FileNotFoundError: Si el archivo no existe
        PermissionError: Si no hay permisos para leer el archivo
        OSError: Si ocurre un error de E/S
    """
    hash_md5 = hashlib.md5()

    try:
        with open(ruta_archivo, 'rb') as f:
            for bloque in iter(lambda: f.read(tamaño_bloque), b''):
                hash_md5.update(bloque)
        return hash_md5.hexdigest()

    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
    except PermissionError:
        raise PermissionError(f"Sin permisos para leer: {ruta_archivo}")
    except OSError as e:
        raise OSError(f"Error leyendo archivo {ruta_archivo}: {e}")


def calcular_hash_archivos(archivos_info: List[Dict],
                           tamano_maximo: int = 500 * 1024 * 1024) -> List[Dict]:
    """
    Calcula el hash MD5 para una lista de archivos.

    Para archivos muy grandes (mayores a tamano_maximo), se calcula un hash
    parcial usando solo el inicio y final del archivo.

    Args:
        archivos_info: Lista de diccionarios con información de archivos
        tamano_maximo: Tamaño máximo en bytes para hash completo (default: 500MB)

    Returns:
        Lista de diccionarios actualizada con el campo 'hash_md5'
    """
    archivos_con_hash = []

    for archivo in archivos_info:
        try:
            ruta = archivo.get('ruta_origen') or archivo.get('ruta_destino')

            if not ruta or not os.path.exists(ruta):
                archivo['hash_md5'] = None
                archivo['error_hash'] = 'Ruta no disponible'
                archivos_con_hash.append(archivo)
                continue

            tamano = archivo.get('tamaño_bytes', 0)

            # Para archivos muy grandes, usar hash parcial
            if tamano > tamano_maximo:
                archivo['hash_md5'] = calcular_hash_parcial(ruta)
                archivo['hash_parcial'] = True
            else:
                archivo['hash_md5'] = calcular_hash_md5(ruta)
                archivo['hash_parcial'] = False

            archivo['error_hash'] = None

        except Exception as e:
            archivo['hash_md5'] = None
            archivo['error_hash'] = str(e)
            archivo['hash_parcial'] = False

        archivos_con_hash.append(archivo)

    return archivos_con_hash


def calcular_hash_parcial(ruta_archivo: str, bytes_inicio: int = 4096,
                          bytes_final: int = 4096) -> str:
    """
    Calcula un hash parcial usando el inicio y final del archivo.

    Esta técnica es más rápida para archivos grandes manteniendo buena
    probabilidad de detectar duplicados.

    Args:
        ruta_archivo: Ruta absoluta del archivo
        bytes_inicio: Bytes a leer desde el inicio
        bytes_final: Bytes a leer desde el final

    Returns:
        Hash MD5 del contenido leído
    """
    hash_md5 = hashlib.md5()

    with open(ruta_archivo, 'rb') as f:
        # Leer inicio
        hash_md5.update(f.read(bytes_inicio))

        # Obtener tamaño y posicionarse para leer el final
        f.seek(0, 2)  # Ir al final
        tamano = f.tell()

        if tamano > bytes_inicio + bytes_final:
            f.seek(-bytes_final, 2)  # Retroceder bytes_final desde el final
            hash_md5.update(f.read(bytes_final))

        # Añadir tamaño como parte del hash para diferenciar
        hash_md5.update(str(tamano).encode())

    return hash_md5.hexdigest()


def encontrar_duplicados(archivos_con_hash: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Identifica archivos duplicados basándose en sus hashes MD5.

    Args:
        archivos_con_hash: Lista de archivos con campo 'hash_md5' calculado

    Returns:
        Tupla con:
        - Lista de archivos marcados con 'es_duplicado' y 'grupo_duplicados'
        - Diccionario con estadísticas de duplicados
    """
    # Agrupar por hash
    grupos_por_hash = defaultdict(list)

    for archivo in archivos_con_hash:
        hash_valor = archivo.get('hash_md5')
        if hash_valor:
            grupos_por_hash[hash_valor].append(archivo)

    # Marcar duplicados
    archivos_marcados = []
    grupos_duplicados = []
    total_duplicados = 0
    espacio_duplicado = 0

    grupo_id = 1
    for hash_valor, archivos_grupo in grupos_por_hash.items():
        if len(archivos_grupo) > 1:
            # Es un grupo de duplicados
            es_original = True
            for archivo in archivos_grupo:
                archivo_copia = archivo.copy()
                archivo_copia['es_duplicado'] = not es_original
                archivo_copia['grupo_duplicados'] = grupo_id
                archivo_copia['hash_duplicado'] = hash_valor

                if not es_original:
                    total_duplicados += 1
                    espacio_duplicado += archivo.get('tamaño_bytes', 0)

                es_original = False
                archivos_marcados.append(archivo_copia)

            grupos_duplicados.append({
                'grupo_id': grupo_id,
                'hash': hash_valor[:16] + '...',
                'cantidad': len(archivos_grupo),
                'archivos': [a['nombre_original'] for a in archivos_grupo]
            })
            grupo_id += 1
        else:
            # No es duplicado
            archivo_copia = archivos_grupo[0].copy()
            archivo_copia['es_duplicado'] = False
            archivo_copia['grupo_duplicados'] = None
            archivo_copia['hash_duplicado'] = hash_valor
            archivos_marcados.append(archivo_copia)

    # Calcular espacio potencialmente ahorrable
    estadisticas = {
        'total_archivos_escaneados': len(archivos_con_hash),
        'archivos_con_hash_valido': len([a for a in archivos_con_hash if a.get('hash_md5')]),
        'total_grupos_duplicados': len(grupos_duplicados),
        'total_archivos_duplicados': total_duplicados,
        'espacio_duplicado_mb': round(espacio_duplicado / (1024 * 1024), 2),
        'grupos_detalle': grupos_duplicados
    }

    return archivos_marcados, estadisticas


def detectar_duplicados_en_carpeta(ruta_carpeta: str) -> Tuple[List[Dict], Dict]:
    """
    Función principal que detecta duplicados en una carpeta.

    Realiza el escaneo completo: lista archivos, calcula hashes y encuentra duplicados.

    Args:
        ruta_carpeta: Ruta de la carpeta a analizar

    Returns:
        Tupla con (archivos marcados, estadísticas)
    """
    from organizer import escanear_archivos

    # Escanear archivos
    archivos = escanear_archivos(ruta_carpeta)

    if not archivos:
        return [], {
            'total_archivos_escaneados': 0,
            'archivos_con_hash_valido': 0,
            'total_grupos_duplicados': 0,
            'total_archivos_duplicados': 0,
            'espacio_duplicado_mb': 0,
            'grupos_detalle': []
        }

    # Calcular hashes
    archivos_con_hash = calcular_hash_archivos(archivos)

    # Encontrar duplicados
    return encontrar_duplicados(archivos_con_hash)


def obtener_resumen_duplicados_para_reporte(archivos_marcados: List[Dict]) -> str:
    """
    Genera un resumen en texto de los duplicados encontrados.

    Args:
        archivos_marcados: Lista de archivos con información de duplicados

    Returns:
        String con resumen formateado
    """
    duplicados = [a for a in archivos_marcados if a.get('es_duplicado')]

    if not duplicados:
        return "No se encontraron archivos duplicados."

    lineas = ["ARCHIVOS DUPLICADOS ENCONTRADOS:", "=" * 40, ""]

    for archivo in duplicados:
        lineas.append(f"  • {archivo['nombre_original']}")
        lineas.append(f"    Hash: {archivo.get('hash_duplicado', 'N/A')[:20]}...")
        lineas.append(f"    Grupo: {archivo.get('grupo_duplicados')}")
        lineas.append("")

    return "\n".join(lineas)
