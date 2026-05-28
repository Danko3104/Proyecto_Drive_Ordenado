"""
app.py - Aplicación Flask principal para Drive Ordenado

Este es el punto de entrada de la aplicación web que proporciona
la interfaz para organizar archivos en Google Drive.
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import os
import json
import threading
from datetime import datetime
from typing import Dict, Any

# Importar módulos del proyecto
from organizer import organizar_archivos, obtener_estadisticas_adicionales, obtener_preview_organizacion
from duplicates import detectar_duplicados_en_carpeta, calcular_hash_archivos, encontrar_duplicados
from reporter import (
    generar_reporte_csv, calcular_estadisticas_pandas,
    generar_resumen_texto, obtener_datos_para_tabla
)

app = Flask(__name__)
app.secret_key = 'drive_ordenado_secret_key_2024'

# Variable global para el estado del proceso
estado_proceso = {
    'en_progreso': False,
    'progreso': 0,
    'mensaje': '',
    'resultado': None,
    'error': None
}


@app.route('/')
def index():
    """Página principal con el formulario de configuración."""
    return render_template('index.html')


@app.route('/preview', methods=['POST'])
def preview():
    """Endpoint para obtener un preview de la organización sin mover archivos."""
    # Obtener datos del formulario
    data = request.get_json()

    ruta_origen = data.get('ruta_origen', '').strip()
    detectar_duplicados = data.get('detectar_duplicados', False)

    # Validaciones
    if not ruta_origen:
        return jsonify({
            'success': False,
            'error': 'Debe especificar una ruta de origen'
        }), 400

    # Expandir ~ a la ruta home
    ruta_origen = os.path.expanduser(ruta_origen)

    # Verificar que la ruta existe
    if not os.path.exists(ruta_origen):
        return jsonify({
            'success': False,
            'error': f'La ruta no existe: {ruta_origen}'
        }), 400

    if not os.path.isdir(ruta_origen):
        return jsonify({
            'success': False,
            'error': f'La ruta no es un directorio: {ruta_origen}'
        }), 400

    try:
        # Obtener preview de la organización
        preview_data = obtener_preview_organizacion(ruta_origen, detectar_duplicados)

        return jsonify({
            'success': True,
            'preview': preview_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/organizar', methods=['POST'])
def organizar():
    """Endpoint para iniciar el proceso de organización."""
    global estado_proceso

    # Verificar si ya hay un proceso en curso
    if estado_proceso['en_progreso']:
        return jsonify({
            'success': False,
            'error': 'Ya hay un proceso en curso. Por favor espere.'
        }), 409

    # Obtener datos del formulario
    data = request.get_json()

    ruta_origen = data.get('ruta_origen', '').strip()
    ruta_destino = data.get('ruta_destino', '').strip() or ruta_origen
    criterio = data.get('criterio', 'tipo')
    organizar_por_fecha = data.get('organizar_por_fecha', True)
    organizar_por_extension = data.get('organizar_por_extension', True)
    detectar_duplicados = data.get('detectar_duplicados', False)
    confirmado = data.get('confirmado', False)

    # Validaciones
    if not ruta_origen:
        return jsonify({
            'success': False,
            'error': 'Debe especificar una ruta de origen'
        }), 400

    # Expandir ~ a la ruta home
    ruta_origen = os.path.expanduser(ruta_origen)
    ruta_destino = os.path.expanduser(ruta_destino)

    # Verificar que la ruta existe
    if not os.path.exists(ruta_origen):
        return jsonify({
            'success': False,
            'error': f'La ruta no existe: {ruta_origen}'
        }), 400

    if not os.path.isdir(ruta_origen):
        return jsonify({
            'success': False,
            'error': f'La ruta no es un directorio: {ruta_origen}'
        }), 400

    # Guardar configuración en sesión
    session['config'] = {
        'ruta_origen': ruta_origen,
        'ruta_destino': ruta_destino,
        'criterio': criterio,
        'organizar_por_fecha': organizar_por_fecha,
        'organizar_por_extension': organizar_por_extension,
        'detectar_duplicados': detectar_duplicados
    }

    # Iniciar proceso en segundo plano
    estado_proceso = {
        'en_progreso': True,
        'progreso': 0,
        'mensaje': 'Iniciando proceso...',
        'resultado': None,
        'error': None
    }

    thread = threading.Thread(
        target=ejecutar_organizacion,
        args=(ruta_origen, ruta_destino, criterio, organizar_por_fecha, organizar_por_extension, detectar_duplicados)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'Proceso iniciado'})


def ejecutar_organizacion(ruta_origen: str, ruta_destino: str,
                         criterio: str, organizar_por_fecha: bool,
                         organizar_por_extension: bool, detectar_duplicados: bool):
    """
    Función que ejecuta la organización en un hilo separado.

    Args:
        ruta_origen: Ruta de la carpeta origen
        ruta_destino: Ruta de la carpeta destino
        criterio: Criterio de organización
        organizar_por_fecha: Si organizar por fecha
        organizar_por_extension: Si organizar por extensión
        detectar_duplicados: Si detectar duplicados
    """
    global estado_proceso

    try:
        # Fase 1: Escaneo
        estado_proceso['mensaje'] = 'Escaneando archivos...'
        estado_proceso['progreso'] = 10

        # Fase 2: Detección de duplicados (si está activado)
        archivos_con_duplicados = None
        estadisticas_duplicados = None

        if detectar_duplicados:
            estado_proceso['mensaje'] = 'Detectando archivos duplicados...'
            estado_proceso['progreso'] = 30

            archivos_con_duplicados, estadisticas_duplicados = detectar_duplicados_en_carpeta(ruta_origen)

        # Fase 3: Organización
        estado_proceso['mensaje'] = 'Organizando archivos...'
        estado_proceso['progreso'] = 50

        archivos_procesados, estadisticas = organizar_archivos(
            ruta_origen=ruta_origen,
            ruta_destino=ruta_destino,
            criterio=criterio,
            organizar_por_fecha=organizar_por_fecha,
            organizar_por_extension=organizar_por_extension
        )

        # Si hay información de duplicados, combinarla
        if archivos_con_duplicados and detectar_duplicados:
            # Crear diccionario de duplicados por ruta
            duplicados_por_ruta = {
                a['ruta_origen']: a for a in archivos_con_duplicados
            }

            for archivo in archivos_procesados:
                ruta = archivo.get('ruta_destino') or archivo.get('ruta_origen')
                if ruta in duplicados_por_ruta:
                    archivo['es_duplicado'] = duplicados_por_ruta[ruta].get('es_duplicado', False)
                    archivo['hash_md5'] = duplicados_por_ruta[ruta].get('hash_md5', '')

        # Fase 4: Generar reporte CSV
        estado_proceso['mensaje'] = 'Generando reporte CSV...'
        estado_proceso['progreso'] = 75

        ruta_reporte = os.path.join(ruta_destino, 'reporte_organizacion.csv')
        generar_reporte_csv(archivos_procesados, ruta_reporte)

        # Fase 5: Calcular estadísticas adicionales
        estado_proceso['mensaje'] = 'Calculando estadísticas...'
        estado_proceso['progreso'] = 90

        estadisticas_adicionales = obtener_estadisticas_adicionales(archivos_procesados)
        estadisticas_completas = calcular_estadisticas_pandas(archivos_procesados, estadisticas)

        # Combinar estadísticas
        if estadisticas_duplicados:
            estadisticas_completas['duplicados'] = {
                'cantidad': estadisticas_duplicados.get('total_archivos_duplicados', 0),
                'espacio_ocupado_mb': estadisticas_duplicados.get('espacio_duplicado_mb', 0),
                'grupos': estadisticas_duplicados.get('total_grupos_duplicados', 0)
            }

        # Agregar información de carpetas eliminadas
        if 'carpetas_vacias_eliminadas' in estadisticas:
            estadisticas_completas['carpetas_eliminadas'] = {
                'total': estadisticas.get('carpetas_vacias_eliminadas', 0),
                'origen': estadisticas.get('carpetas_eliminadas_origen', 0),
                'destino': estadisticas.get('carpetas_eliminadas_destino', 0)
            }

        # Guardar resultado (usando variables del ámbito de la función)
        estado_proceso['resultado'] = {
            'archivos_procesados': len(archivos_procesados),
            'estadisticas': estadisticas_completas,
            'estadisticas_adicionales': estadisticas_adicionales,
            'ruta_reporte': ruta_reporte,
            'ruta_destino': ruta_destino,
            'criterio': criterio,
            'organizar_por_fecha': organizar_por_fecha,
            'organizar_por_extension': organizar_por_extension,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        estado_proceso['mensaje'] = 'Proceso completado exitosamente'
        estado_proceso['progreso'] = 100
        estado_proceso['en_progreso'] = False

    except Exception as e:
        estado_proceso['error'] = str(e)
        estado_proceso['mensaje'] = f'Error: {str(e)}'
        estado_proceso['en_progreso'] = False


@app.route('/estado')
def obtener_estado():
    """Endpoint para consultar el estado del proceso."""
    return jsonify(estado_proceso)


@app.route('/resultados')
def resultados():
    """Página de resultados del proceso."""
    if not estado_proceso['resultado'] and not estado_proceso['error']:
        return render_template('index.html', mensaje='No hay resultados disponibles')

    return render_template('result.html',
                          resultado=estado_proceso.get('resultado'),
                          error=estado_proceso.get('error'))


@app.route('/reporte')
def reporte():
    """Página de visualización del reporte CSV."""
    resultado = estado_proceso.get('resultado')

    if not resultado:
        return render_template('index.html', mensaje='No hay reporte disponible')

    # Cargar datos de duplicados desde el CSV si existe
    duplicados_detalle = []
    ruta_reporte = resultado.get('ruta_reporte')

    if ruta_reporte and os.path.exists(ruta_reporte):
        try:
            import csv
            from collections import defaultdict

            # Agrupar archivos por hash para encontrar duplicados
            grupos_por_hash = defaultdict(list)

            with open(ruta_reporte, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('es_duplicado', '').lower() == 'si':
                        # Usar ruta_destino como identificador único
                        hash_key = row.get('ruta_destino', '') + row.get('tamaño_bytes', '')
                        grupos_por_hash[hash_key].append({
                            'nombre': row.get('nombre_original', ''),
                            'ruta': row.get('ruta_destino', ''),
                            'tamaño': row.get('tamaño_bytes', '')
                        })

            # Crear lista de duplicados con sus ubicaciones
            for hash_key, archivos in grupos_por_hash.items():
                if len(archivos) > 1:
                    duplicados_detalle.append({
                        'nombre': archivos[0]['nombre'],
                        'hash': hash_key[:32],
                        'ubicaciones': [a['ruta'] for a in archivos],
                        'cantidad': len(archivos)
                    })

        except Exception as e:
            print(f"Error al leer duplicados del CSV: {e}")

    return render_template('report.html',
                          estadisticas=resultado.get('estadisticas') if resultado else None,
                          timestamp=resultado.get('timestamp') if resultado else None,
                          duplicados_detalle=duplicados_detalle)


@app.route('/descargar_reporte')
def descargar_reporte():
    """Endpoint para descargar el archivo CSV."""
    resultado = estado_proceso.get('resultado')

    if not resultado or not resultado.get('ruta_reporte'):
        return jsonify({'error': 'No hay reporte disponible'}), 404

    ruta_reporte = resultado['ruta_reporte']

    if not os.path.exists(ruta_reporte):
        return jsonify({'error': 'El archivo de reporte no existe'}), 404

    return send_file(ruta_reporte,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='reporte_organizacion.csv')


@app.route('/api/estadisticas')
def api_estadisticas():
    """API endpoint para obtener estadísticas en formato JSON."""
    resultado = estado_proceso.get('resultado')

    if not resultado:
        return jsonify({'error': 'No hay datos disponibles'}), 404

    return jsonify(resultado.get('estadisticas', {}))


@app.route('/api/datos_tabla')
def api_datos_tabla():
    """API endpoint para obtener datos de archivos en formato JSON."""
    resultado = estado_proceso.get('resultado')

    if not resultado:
        return jsonify([])

    # Simular datos de tabla desde las estadísticas
    # En producción, guardaríamos la lista completa de archivos
    datos = []
    stats = resultado.get('estadisticas', {})

    # Generar datos de ejemplo basados en las estadísticas
    por_categoria = stats.get('por_categoria', {})
    for categoria, datos_cat in por_categoria.items():
        datos.append({
            'categoria': categoria,
            'cantidad': datos_cat.get('cantidad', 0),
            'tamaño_mb': round(datos_cat.get('tamaño_bytes', 0) / (1024*1024), 2)
        })

    return jsonify(datos)


@app.errorhandler(404)
def not_found(error):
    """Manejador de error 404."""
    return render_template('index.html', mensaje='Página no encontrada'), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejador de error 500."""
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500


if __name__ == '__main__':
    # Configuración para desarrollo local
    # En producción (Colab), usar start.sh para lanzar
    app.run(host='0.0.0.0', port=5000, debug=True)
