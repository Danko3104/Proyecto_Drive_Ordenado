"""
reporter.py - Módulo de generación de reportes CSV

Este módulo genera reportes CSV de la organización de archivos
y calcula estadísticas usando pandas.
"""

import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
import json


def generar_reporte_csv(archivos_procesados: List[Dict],
                        ruta_salida: str = 'reporte_organizacion.csv') -> str:
    """
    Genera un archivo CSV con el reporte de organización de archivos.

    Args:
        archivos_procesados: Lista de diccionarios con información de archivos
        ruta_salida: Ruta donde se guardará el CSV

    Returns:
        Ruta completa del archivo CSV generado
    """
    if not archivos_procesados:
        # Crear CSV vacío con encabezados
        df_vacio = pd.DataFrame(columns=[
            'nombre_original', 'extension', 'categoria', 'tamaño_bytes',
            'fecha_modificacion', 'ruta_destino', 'es_duplicado'
        ])
        df_vacio.to_csv(ruta_salida, index=False, encoding='utf-8')
        return os.path.abspath(ruta_salida)

    # Preparar datos para el DataFrame
    datos = []
    for archivo in archivos_procesados:
        fila = {
            'nombre_original': archivo.get('nombre_original', ''),
            'extension': archivo.get('extension', ''),
            'categoria': archivo.get('categoria', ''),
            'tamaño_bytes': archivo.get('tamaño_bytes', 0),
            'fecha_modificacion': archivo['fecha_modificacion'].strftime('%Y-%m-%d %H:%M:%S')
                if isinstance(archivo.get('fecha_modificacion'), datetime)
                else str(archivo.get('fecha_modificacion', '')),
            'ruta_destino': archivo.get('ruta_destino', ''),
            'es_duplicado': 'Si' if archivo.get('es_duplicado') else 'No'
        }
        datos.append(fila)

    # Crear DataFrame
    df = pd.DataFrame(datos)

    # Guardar CSV
    df.to_csv(ruta_salida, index=False, encoding='utf-8')

    return os.path.abspath(ruta_salida)


def calcular_estadisticas_pandas(archivos_procesados: List[Dict],
                                  estadisticas_base: Optional[Dict] = None) -> Dict:
    """
    Calcula estadísticas avanzadas usando pandas.

    Args:
        archivos_procesados: Lista de archivos procesados
        estadisticas_base: Estadísticas base calculadas previamente

    Returns:
        Diccionario con estadísticas detalladas
    """
    if not archivos_procesados:
        return {
            'resumen': {
                'total_archivos': 0,
                'tamaño_total_mb': 0,
                'total_categorias': 0
            },
            'por_categoria': {},
            'por_extension': {},
            'por_año': {},
            'duplicados': {'cantidad': 0, 'espacio_ocupado_mb': 0}
        }

    # Preparar datos
    datos = []
    for archivo in archivos_procesados:
        datos.append({
            'nombre': archivo.get('nombre_original', ''),
            'extension': archivo.get('extension', '').lower() or 'sin_ext',
            'categoria': archivo.get('categoria', 'otros'),
            'tamaño_bytes': archivo.get('tamaño_bytes', 0),
            'tamaño_mb': round(archivo.get('tamaño_bytes', 0) / (1024 * 1024), 2),
            'año': archivo['fecha_modificacion'].year
                if isinstance(archivo.get('fecha_modificacion'), datetime)
                else datetime.now().year,
            'es_duplicado': archivo.get('es_duplicado', False)
        })

    df = pd.DataFrame(datos)

    # Estadísticas por categoría
    por_categoria = df.groupby('categoria').agg({
        'nombre': 'count',
        'tamaño_mb': 'sum',
        'tamaño_bytes': 'sum'
    }).rename(columns={'nombre': 'cantidad'}).to_dict('index')

    # Estadísticas por extensión
    por_extension = df.groupby('extension').agg({
        'nombre': 'count',
        'tamaño_mb': 'sum'
    }).rename(columns={'nombre': 'cantidad'}).to_dict('index')

    # Estadísticas por año
    por_año = df.groupby('año').agg({
        'nombre': 'count',
        'tamaño_mb': 'sum'
    }).rename(columns={'nombre': 'cantidad'}).to_dict('index')

    # Estadísticas de duplicados
    duplicados_df = df[df['es_duplicado'] == True]
    duplicados_info = {
        'cantidad': len(duplicados_df),
        'espacio_ocupado_mb': round(duplicados_df['tamaño_mb'].sum(), 2)
    }

    # Tamaños estadísticos
    tamaño_stats = {
        'promedio_mb': round(df['tamaño_mb'].mean(), 2),
        'mediana_mb': round(df['tamaño_mb'].median(), 2),
        'maximo_mb': round(df['tamaño_mb'].max(), 2),
        'minimo_mb': round(df['tamaño_mb'].min(), 2)
    }

    return {
        'resumen': {
            'total_archivos': len(df),
            'tamaño_total_mb': round(df['tamaño_mb'].sum(), 2),
            'total_categorias': df['categoria'].nunique(),
            'total_extensiones': df['extension'].nunique(),
            'años_cubiertos': sorted(df['año'].unique().tolist())
        },
        'tamaño_stats': tamaño_stats,
        'por_categoria': por_categoria,
        'por_extension': por_extension,
        'por_año': por_año,
        'duplicados': duplicados_info
    }


def generar_resumen_texto(archivos_procesados: List[Dict],
                          estadisticas: Dict) -> str:
    """
    Genera un resumen en formato texto plano.

    Args:
        archivos_procesados: Lista de archivos procesados
        estadisticas: Diccionario con estadísticas

    Returns:
        String con resumen formateado
    """
    lineas = []
    lineas.append("=" * 60)
    lineas.append("REPORTE DE ORGANIZACIÓN DE ARCHIVOS")
    lineas.append("=" * 60)
    lineas.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lineas.append("")

    # Resumen general
    lineas.append("RESUMEN GENERAL")
    lineas.append("-" * 60)
    lineas.append(f"Total de archivos procesados: {estadisticas.get('total_archivos', 0)}")
    lineas.append(f"Tamaño total: {estadisticas.get('tamaño_total_bytes', 0) / (1024*1024):.2f} MB")
    lineas.append(f"Errores: {estadisticas.get('errores', 0)}")
    lineas.append("")

    # Por categoría
    lineas.append("DISTRIBUCIÓN POR CATEGORÍA")
    lineas.append("-" * 60)
    for categoria, datos in estadisticas.get('categorias', {}).items():
        cantidad = datos.get('cantidad', 0)
        tamaño_mb = datos.get('tamaño_bytes', 0) / (1024 * 1024)
        lineas.append(f"  {categoria.capitalize():15} : {cantidad:5d} archivos ({tamaño_mb:8.2f} MB)")
    lineas.append("")

    # Duplicados
    duplicados = [a for a in archivos_procesados if a.get('es_duplicado')]
    lineas.append("ARCHIVOS DUPLICADOS")
    lineas.append("-" * 60)
    lineas.append(f"Total de duplicados: {len(duplicados)}")
    if duplicados:
        espacio_duplicado = sum(d.get('tamaño_bytes', 0) for d in duplicados) / (1024 * 1024)
        lineas.append(f"Espacio ocupado por duplicados: {espacio_duplicado:.2f} MB")
    lineas.append("")

    lineas.append("=" * 60)

    return "\n".join(lineas)


def obtener_datos_para_tabla(archivos_procesados: List[Dict],
                              limite: int = 100) -> List[Dict]:
    """
    Prepara los datos para mostrar en tabla HTML.

    Args:
        archivos_procesados: Lista de archivos
        limite: Número máximo de registros a retornar

    Returns:
        Lista de diccionarios simplificados para la tabla
    """
    datos = []
    for archivo in archivos_procesados[:limite]:
        datos.append({
            'nombre': archivo.get('nombre_original', ''),
            'extension': archivo.get('extension', ''),
            'categoria': archivo.get('categoria', '').capitalize(),
            'tamaño': formatear_tamaño(archivo.get('tamaño_bytes', 0)),
            'fecha': formatear_fecha(archivo.get('fecha_modificacion')),
            'duplicado': 'Sí' if archivo.get('es_duplicado') else 'No',
            'movido': 'Sí' if archivo.get('movido') else 'No',
            'error': archivo.get('error', '') or '-'
        })
    return datos


def formatear_tamaño(bytes_valor: int) -> str:
    """Formatea bytes a formato legible."""
    if bytes_valor < 1024:
        return f"{bytes_valor} B"
    elif bytes_valor < 1024 * 1024:
        return f"{bytes_valor / 1024:.1f} KB"
    elif bytes_valor < 1024 * 1024 * 1024:
        return f"{bytes_valor / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_valor / (1024 * 1024 * 1024):.2f} GB"


def formatear_fecha(fecha_valor) -> str:
    """Formatea fecha a string."""
    if isinstance(fecha_valor, datetime):
        return fecha_valor.strftime('%d/%m/%Y %H:%M')
    return str(fecha_valor)[:16] if fecha_valor else '-'


def exportar_estadisticas_json(estadisticas: Dict, ruta_salida: str = 'estadisticas.json') -> str:
    """
    Exporta las estadísticas a formato JSON.

    Args:
        estadisticas: Diccionario con estadísticas
        ruta_salida: Ruta del archivo JSON

    Returns:
        Ruta del archivo generado
    """
    # Convertir objetos datetime a string
    def convertir_a_serializable(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, dict):
            return {k: convertir_a_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convertir_a_serializable(i) for i in obj]
        return obj

    stats_serializable = convertir_a_serializable(estadisticas)

    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(stats_serializable, f, indent=2, ensure_ascii=False)

    return os.path.abspath(ruta_salida)
