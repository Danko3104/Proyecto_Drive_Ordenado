"""
app.py - Aplicación Flask principal para Drive Ordenado

Este es el punto de entrada de la aplicación web que proporciona
la interfaz para organizar archivos en Google Drive.
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import os
import json
import threading
import shutil
from datetime import datetime
from typing import Dict, Any

# Importar módulos del proyecto
from organizer import organizar_archivos, obtener_estadisticas_adicionales, obtener_preview_organizacion, escanear_archivos
from duplicates import detectar_duplicados_en_carpeta, calcular_hash_archivos, encontrar_duplicados, eliminar_archivos_seleccionados
from reporter import (
    generar_reporte_csv, calcular_estadisticas_pandas,
    generar_resumen_texto, obtener_datos_para_tabla
)

app = Flask(__name__)
app.secret_key = 'drive_ordenado_secret_key_2024'

# Ruta del archivo de log para deshacer
UNDO_LOG_PATH = os.path.expanduser('/content/drive/MyDrive/drive_ordenado_undo.json')

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


def _guardar_undo_log(movimientos: list, metadata: dict):
    """Guarda el log de movimientos para deshacer."""
    try:
        carpeta_log = os.path.dirname(UNDO_LOG_PATH)
        if not os.path.exists(carpeta_log):
            os.makedirs(carpeta_log, exist_ok=True)

        log_data = {
            'metadata': metadata,
            'movimientos': movimientos
        }

        with open(UNDO_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando undo log: {e}")


def _cargar_undo_log():
    """Carga el log de movimientos para deshacer."""
    try:
        if not os.path.exists(UNDO_LOG_PATH):
            return None
        with open(UNDO_LOG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando undo log: {e}")
        return None


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

        # Guardar log para deshacer
        log_movimientos = []
        for archivo in archivos_procesados:
            if archivo.get('ruta_origen') and archivo.get('ruta_destino') and archivo.get('movido'):
                log_movimientos.append({
                    'ruta_origen_original': archivo['ruta_origen'],
                    'ruta_destino_actual': archivo['ruta_destino']
                })

        metadata_undo = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ruta_origen': ruta_origen,
            'ruta_destino': ruta_destino,
            'total_archivos': len(archivos_procesados),
            'criterio': criterio
        }
        _guardar_undo_log(log_movimientos, metadata_undo)

        # Guardar en historial de sesiones
        try:
            historial_path = os.path.join(ruta_destino, 'historial_sesiones.json')
            entrada_historial = {
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ruta_origen': ruta_origen,
                'ruta_destino': ruta_destino,
                'criterio': criterio,
                'total_archivos': len(archivos_procesados),
                'tamaño_total_mb': round(estadisticas_completas.get('resumen', {}).get('tamaño_total_mb', 0), 2),
                'duplicados_encontrados': estadisticas_duplicados.get('total_archivos_duplicados', 0) if estadisticas_duplicados else 0,
                'errores': estadisticas.get('errores', 0)
            }

            historial = []
            if os.path.exists(historial_path):
                try:
                    with open(historial_path, 'r', encoding='utf-8') as f:
                        historial = json.load(f)
                except Exception:
                    historial = []

            historial.insert(0, entrada_historial)
            historial = historial[:50]

            with open(historial_path, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

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


@app.route('/renombrar')
def renombrar():
    """Página de renombrado masivo."""
    return render_template('renamer.html')


@app.route('/renombrar/preview', methods=['POST'])
def renombrar_preview():
    """Endpoint para previsualizar renombrado masivo."""
    from renamer import aplicar_reglas_renombrado
    data = request.get_json()
    ruta = data.get('ruta', '').strip()
    reglas = data.get('reglas', [])

    if not ruta:
        return jsonify({'success': False, 'error': 'Debe especificar una ruta'}), 400
    if not reglas:
        return jsonify({'success': False, 'error': 'Debe seleccionar al menos una regla'}), 400

    ruta = os.path.expanduser(ruta)

    if not os.path.exists(ruta) or not os.path.isdir(ruta):
        return jsonify({'success': False, 'error': f'La ruta no existe: {ruta}'}), 400

    try:
        archivos = escanear_archivos(ruta)
        resultados = aplicar_reglas_renombrado(archivos, reglas)
        total_cambian = sum(1 for r in resultados if r['cambiara'])

        return jsonify({
            'success': True,
            'resultados': resultados,
            'total_archivos': len(resultados),
            'total_cambian': total_cambian,
            'no_cambian': len(resultados) - total_cambian
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/renombrar/ejecutar', methods=['POST'])
def renombrar_ejecutar():
    """Endpoint para ejecutar el renombrado masivo."""
    from renamer import ejecutar_renombrado
    data = request.get_json()
    archivos = data.get('archivos', [])

    if not archivos:
        return jsonify({'success': False, 'error': 'No hay archivos para renombrar'}), 400

    try:
        solo_cambiantes = [a for a in archivos if a.get('cambiara', False)]
        if not solo_cambiantes:
            return jsonify({'success': True, 'resultado': {'total_exitosos': 0, 'total_fallidos': 0, 'exitosos': [], 'fallidos': []}})

        resultado = ejecutar_renombrado(solo_cambiantes)
        return jsonify({'success': True, 'resultado': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    """Endpoint para obtener las categorías actuales."""
    from config import cargar_categorias
    categorias = cargar_categorias()
    return jsonify(categorias)


@app.route('/categorias', methods=['POST'])
def guardar_categorias():
    """Endpoint para guardar categorías personalizadas."""
    from config import guardar_categorias
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({'success': False, 'error': 'Datos inválidos'}), 400
    exito = guardar_categorias(data)
    if exito:
        return jsonify({'success': True, 'categorias': data})
    return jsonify({'success': False, 'error': 'Error al guardar categorías'}), 500


@app.route('/categorias/reset', methods=['POST'])
def resetear_categorias():
    """Endpoint para restaurar categorías por defecto."""
    from config import resetear_categorias
    categorias = resetear_categorias()
    return jsonify({'success': True, 'categorias': categorias})


@app.route('/basura')
def basura():
    """Página del limpiador de archivos basura."""
    return render_template('cleaner_temp.html')


@app.route('/basura/escanear', methods=['POST'])
def basura_escanear():
    """Endpoint para escanear archivos basura."""
    from cleaner_temp import escanear_archivos_basura
    data = request.get_json()
    ruta = data.get('ruta', '').strip()

    if not ruta:
        return jsonify({'success': False, 'error': 'Debe especificar una ruta'}), 400

    ruta = os.path.expanduser(ruta)

    if not os.path.exists(ruta) or not os.path.isdir(ruta):
        return jsonify({'success': False, 'error': f'La ruta no existe: {ruta}'}), 400

    try:
        resultado = escanear_archivos_basura(ruta)
        return jsonify({'success': True, **resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/basura/eliminar', methods=['POST'])
def basura_eliminar():
    """Endpoint para eliminar archivos basura."""
    from cleaner_temp import eliminar_basura
    data = request.get_json()
    rutas = data.get('rutas', [])

    if not rutas:
        return jsonify({'success': False, 'error': 'No se especificaron archivos'}), 400

    try:
        resultado = eliminar_basura(rutas)
        return jsonify({'success': True, 'resultado': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/historial')
def historial():
    """Página de historial de sesiones."""
    return render_template('historial.html')


@app.route('/historial/datos')
def historial_datos():
    """Endpoint para obtener los datos del historial."""
    ruta = request.args.get('ruta', '/content/drive/MyDrive')
    ruta = os.path.expanduser(ruta)
    historial_path = os.path.join(ruta, 'historial_sesiones.json')

    if not os.path.exists(historial_path):
        return jsonify({'success': True, 'historial': []})

    try:
        with open(historial_path, 'r', encoding='utf-8') as f:
            historial = json.load(f)
        return jsonify({'success': True, 'historial': historial})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/historial/limpiar', methods=['POST'])
def historial_limpiar():
    """Endpoint para limpiar el historial."""
    data = request.get_json()
    ruta = data.get('ruta', '/content/drive/MyDrive')
    ruta = os.path.expanduser(ruta)
    historial_path = os.path.join(ruta, 'historial_sesiones.json')

    try:
        if os.path.exists(historial_path):
            os.remove(historial_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/analizar', methods=['POST'])
def analizar_carpeta():
    """Endpoint para analizar una carpeta sin organizarla."""
    data = request.get_json()
    ruta = data.get('ruta', '').strip()

    if not ruta:
        return jsonify({'success': False, 'error': 'Debe especificar una ruta'}), 400

    ruta = os.path.expanduser(ruta)

    if not os.path.exists(ruta) or not os.path.isdir(ruta):
        return jsonify({'success': False, 'error': f'La ruta no existe o no es un directorio: {ruta}'}), 400

    try:
        archivos = escanear_archivos(ruta)

        if not archivos:
            return jsonify({
                'success': True,
                'total_archivos': 0,
                'tamaño_total_mb': 0,
                'por_categoria': {},
                'por_extension': {},
                'top_10_pesados': [],
                'archivos_vacios': 0,
                'archivo_mas_viejo': None,
                'archivo_mas_nuevo': None
            })

        total_archivos = len(archivos)
        tamaño_total_bytes = sum(a['tamaño_bytes'] for a in archivos)

        por_categoria = {}
        por_extension = {}
        archivos_vacios = 0
        mas_viejo = None
        mas_nuevo = None

        for a in archivos:
            cat = a['categoria']
            if cat not in por_categoria:
                por_categoria[cat] = {'cantidad': 0, 'tamaño_bytes': 0}
            por_categoria[cat]['cantidad'] += 1
            por_categoria[cat]['tamaño_bytes'] += a['tamaño_bytes']

            ext = a['extension'].lower() or 'sin_extension'
            if ext not in por_extension:
                por_extension[ext] = {'cantidad': 0, 'tamaño_bytes': 0}
            por_extension[ext]['cantidad'] += 1
            por_extension[ext]['tamaño_bytes'] += a['tamaño_bytes']

            if a['tamaño_bytes'] == 0:
                archivos_vacios += 1

            fecha = a['fecha_modificacion']
            if mas_viejo is None or fecha < mas_viejo['fecha']:
                mas_viejo = {'nombre': a['nombre_original'], 'fecha': fecha, 'ruta': a['ruta_origen']}
            if mas_nuevo is None or fecha > mas_nuevo['fecha']:
                mas_nuevo = {'nombre': a['nombre_original'], 'fecha': fecha, 'ruta': a['ruta_origen']}

        # Top 10 más pesados
        ordenados = sorted(archivos, key=lambda x: x['tamaño_bytes'], reverse=True)[:10]
        top_10 = []
        for a in ordenados:
            top_10.append({
                'nombre': a['nombre_original'],
                'ruta': a['ruta_origen'],
                'tamaño_mb': round(a['tamaño_bytes'] / (1024 * 1024), 2),
                'categoria': a['categoria']
            })

        # Top 10 extensiones más frecuentes
        ext_ordenadas = sorted(por_extension.items(), key=lambda x: x[1]['cantidad'], reverse=True)[:10]
        top_extensiones = {}
        for ext, datos in ext_ordenadas:
            top_extensiones[ext] = datos

        for cat, datos in por_categoria.items():
            datos['tamaño_mb'] = round(datos['tamaño_bytes'] / (1024 * 1024), 2)

        return jsonify({
            'success': True,
            'total_archivos': total_archivos,
            'tamaño_total_mb': round(tamaño_total_bytes / (1024 * 1024), 2),
            'por_categoria': por_categoria,
            'por_extension': top_extensiones,
            'top_10_pesados': top_10,
            'archivos_vacios': archivos_vacios,
            'archivo_mas_viejo': {
                'nombre': mas_viejo['nombre'],
                'fecha': mas_viejo['fecha'].strftime('%Y-%m-%d'),
                'ruta': mas_viejo['ruta']
            } if mas_viejo else None,
            'archivo_mas_nuevo': {
                'nombre': mas_nuevo['nombre'],
                'fecha': mas_nuevo['fecha'].strftime('%Y-%m-%d'),
                'ruta': mas_nuevo['ruta']
            } if mas_nuevo else None
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/subir', methods=['POST'])
def subir_archivos():
    """Endpoint para subir archivos desde el PC a Drive."""
    from organizer import obtener_nombre_unico

    archivos = request.files.getlist('archivos')
    ruta_destino = request.form.get('ruta_destino', '').strip()
    organizar_despues = request.form.get('organizar_despues', 'false').lower() == 'true'

    if not archivos:
        return jsonify({'success': False, 'error': 'No se enviaron archivos'}), 400

    if not ruta_destino:
        ruta_destino = '/content/drive/MyDrive'

    ruta_destino = os.path.expanduser(ruta_destino)

    if not os.path.exists(ruta_destino):
        try:
            os.makedirs(ruta_destino, exist_ok=True)
        except Exception as e:
            return jsonify({'success': False, 'error': f'No se pudo crear la carpeta destino: {e}'}), 500

    subidos = 0
    fallidos = 0
    errores = []

    for archivo in archivos:
        if archivo.filename == '':
            continue
        try:
            nombre_unico = obtener_nombre_unico(ruta_destino, archivo.filename)
            ruta_guardado = os.path.join(ruta_destino, nombre_unico)
            archivo.save(ruta_guardado)
            subidos += 1
        except Exception as e:
            fallidos += 1
            errores.append({'archivo': archivo.filename, 'error': str(e)})

    resultado = {
        'success': True,
        'subidos': subidos,
        'fallidos': fallidos,
        'errores': errores,
        'ruta': ruta_destino
    }

    if organizar_despues and subidos > 0:
        try:
            from organizer import organizar_archivos
            archivos_procesados, estadisticas = organizar_archivos(
                ruta_origen=ruta_destino,
                ruta_destino=ruta_destino,
                criterio='tipo',
                organizar_por_fecha=True,
                organizar_por_extension=True
            )
            resultado['organizado'] = True
            resultado['archivos_organizados'] = len(archivos_procesados)
        except Exception as e:
            resultado['organizado'] = False
            resultado['error_organizar'] = str(e)

    return jsonify(resultado)


@app.route('/explorador')
def explorador():
    """Endpoint para explorar carpetas de manera interactiva."""
    ruta = request.args.get('ruta', '/content/drive/MyDrive').strip()
    ruta = os.path.expanduser(ruta)

    if not os.path.exists(ruta) or not os.path.isdir(ruta):
        ruta = '/content/drive/MyDrive'

    try:
        ruta_padre = os.path.dirname(ruta) if ruta != os.path.dirname(ruta) else ruta
        contenido = os.listdir(ruta)
        carpetas = []
        for item in sorted(contenido):
            ruta_item = os.path.join(ruta, item)
            if os.path.isdir(ruta_item):
                try:
                    os.listdir(ruta_item)
                    carpetas.append({
                        'nombre': item,
                        'ruta': ruta_item
                    })
                except PermissionError:
                    carpetas.append({
                        'nombre': item + ' (sin acceso)',
                        'ruta': ruta_item,
                        'sin_acceso': True
                    })

        return jsonify({
            'ruta_actual': ruta,
            'ruta_padre': ruta_padre if ruta_padre != ruta else None,
            'carpetas': carpetas,
            'puede_seleccionar': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'ruta_actual': ruta, 'ruta_padre': None, 'carpetas': []}), 500


@app.route('/deshacer/estado')
def deshacer_estado():
    """Endpoint para verificar si hay un log de deshacer disponible."""
    try:
        log_data = _cargar_undo_log()
        if log_data is None:
            return jsonify({'disponible': False})

        metadata = log_data.get('metadata', {})
        return jsonify({
            'disponible': True,
            'total_archivos': metadata.get('total_archivos', 0),
            'fecha': metadata.get('fecha', ''),
            'ruta_origen': metadata.get('ruta_origen', ''),
            'ruta_destino': metadata.get('ruta_destino', '')
        })
    except Exception as e:
        return jsonify({'disponible': False, 'error': str(e)})


@app.route('/deshacer', methods=['POST'])
def deshacer():
    """Endpoint para revertir la última organización."""
    try:
        log_data = _cargar_undo_log()
        if log_data is None:
            return jsonify({'success': False, 'error': 'No hay operación para deshacer'}), 404

        movimientos = log_data.get('movimientos', [])
        metadata = log_data.get('metadata', {})
        ruta_destino = metadata.get('ruta_destino', '')

        revertidos = 0
        fallidos = 0

        for movimiento in reversed(movimientos):
            try:
                origen = movimiento.get('ruta_origen_original', '')
                destino = movimiento.get('ruta_destino_actual', '')

                if not os.path.exists(destino):
                    fallidos += 1
                    continue

                carpeta_origen = os.path.dirname(origen)
                if not os.path.exists(carpeta_origen):
                    os.makedirs(carpeta_origen, exist_ok=True)

                shutil.move(destino, origen)
                revertidos += 1

            except Exception:
                fallidos += 1

        # Eliminar carpetas vacías en destino
        carpetas_eliminadas = 0
        if ruta_destino and os.path.exists(ruta_destino):
            from organizer import eliminar_carpetas_vacias
            carpetas_eliminadas = eliminar_carpetas_vacias(ruta_destino)

        # Eliminar el archivo de log para evitar deshacer dos veces
        try:
            if os.path.exists(UNDO_LOG_PATH):
                os.remove(UNDO_LOG_PATH)
        except Exception:
            pass

        return jsonify({
            'success': True,
            'revertidos': revertidos,
            'fallidos': fallidos,
            'carpetas_eliminadas': carpetas_eliminadas,
            'mensaje': f'Se revirtieron {revertidos} archivos'
                       + (f' ({fallidos} fallos)' if fallidos > 0 else '')
                       + (f' y se eliminaron {carpetas_eliminadas} carpetas vacías' if carpetas_eliminadas > 0 else '')
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/buscar', methods=['POST'])
def buscar_archivos():
    """Endpoint para buscar archivos con filtros."""
    data = request.get_json()
    ruta = data.get('ruta', '').strip()
    nombre = data.get('nombre', '').strip().lower()
    extension = data.get('extension', '').strip().lower()
    categoria = data.get('categoria', '').strip().lower()
    tamaño_min_mb = data.get('tamaño_min_mb')
    tamaño_max_mb = data.get('tamaño_max_mb')

    if not ruta:
        return jsonify({'success': False, 'error': 'Debe especificar una ruta'}), 400

    ruta = os.path.expanduser(ruta)

    if not os.path.exists(ruta) or not os.path.isdir(ruta):
        return jsonify({'success': False, 'error': f'La ruta no existe o no es un directorio: {ruta}'}), 400

    try:
        archivos = escanear_archivos(ruta)

        if not archivos:
            return jsonify({'success': True, 'archivos': [], 'total': 0, 'mensaje': 'No se encontraron archivos'})

        filtrados = []
        for archivo in archivos:
            if nombre and nombre not in archivo['nombre_original'].lower():
                continue
            if extension:
                ext_clean = extension if extension.startswith('.') else '.' + extension
                if archivo['extension'].lower() != ext_clean:
                    continue
            if categoria and archivo['categoria'].lower() != categoria:
                continue
            tamaño_mb = archivo['tamaño_bytes'] / (1024 * 1024)
            if tamaño_min_mb is not None and tamaño_mb < float(tamaño_min_mb):
                continue
            if tamaño_max_mb is not None and tamaño_mb > float(tamaño_max_mb):
                continue

            filtrados.append({
                'nombre': archivo['nombre_original'],
                'ruta': archivo['ruta_origen'],
                'extension': archivo['extension'],
                'categoria': archivo['categoria'],
                'tamaño_mb': round(tamaño_mb, 2),
                'fecha_modificacion': archivo['fecha_modificacion'].strftime('%Y-%m-%d %H:%M')
            })

            if len(filtrados) >= 500:
                break

        return jsonify({
            'success': True,
            'archivos': filtrados,
            'total': len(filtrados),
            'mensaje': f'Se encontraron {len(filtrados)} archivos' + (' (máximo 500)' if len(filtrados) >= 500 else '')
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/limpiador')
def limpiador():
    """Página del limpiador de duplicados."""
    return render_template('cleaner.html')


@app.route('/limpiador/escanear', methods=['POST'])
def limpiador_escanear():
    """Endpoint para escanear duplicados desde el limpiador."""
    data = request.get_json()
    ruta = data.get('ruta', '').strip()

    if not ruta:
        return jsonify({'success': False, 'error': 'Debe especificar una ruta'}), 400

    ruta = os.path.expanduser(ruta)

    if not os.path.exists(ruta):
        return jsonify({'success': False, 'error': f'La ruta no existe: {ruta}'}), 400

    if not os.path.isdir(ruta):
        return jsonify({'success': False, 'error': f'La ruta no es un directorio: {ruta}'}), 400

    try:
        archivos_marcados, estadisticas = detectar_duplicados_en_carpeta(ruta)
        grupos = estadisticas.get('grupos_detalle', [])

        grupos_completos = []
        for grupo in grupos:
            grupo_id = grupo['grupo_id']
            hash_valor = grupo['hash']
            cantidad = grupo['cantidad']
            archivos = grupo['archivos']

            archivos_detalle = []
            for archivo_nombre in archivos:
                archivos_detalle.append({
                    'nombre': archivo_nombre,
                    'ruta': '',
                    'tamaño_mb': 0,
                    'fecha_modificacion': ''
                })

            grupos_completos.append({
                'grupo_id': grupo_id,
                'hash': hash_valor,
                'cantidad': cantidad,
                'archivos': archivos_detalle
            })

        return jsonify({
            'success': True,
            'grupos': grupos_completos,
            'total_grupos': estadisticas.get('total_grupos_duplicados', 0),
            'total_archivos': estadisticas.get('total_archivos_duplicados', 0),
            'espacio_mb': estadisticas.get('espacio_duplicado_mb', 0)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/limpiador/eliminar', methods=['POST'])
def limpiador_eliminar():
    """Endpoint para eliminar archivos duplicados seleccionados."""
    data = request.get_json()
    rutas = data.get('rutas', [])

    if not rutas:
        return jsonify({'success': False, 'error': 'No se especificaron archivos para eliminar'}), 400

    try:
        resultado = eliminar_archivos_seleccionados(rutas)
        return jsonify({
            'success': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
