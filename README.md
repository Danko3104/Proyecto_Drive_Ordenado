# 📁 Drive Ordenado

Aplicación web que automatiza la organización de archivos en Google Drive montado en Google Colab. Organiza, clasifica, detecta duplicados y genera reportes completos de tus archivos.

---

## 👥 Integrantes

- **Mendoza Gomez Eleangie Valentina** (2242557)
- **Tavera Carreño Daniel José** (2243042)

---

## 📋 Descripción del Proyecto

**Drive Ordenado** es una aplicación web desarrollada en Python con Flask que permite organizar automáticamente archivos en Google Drive. El usuario interactúa desde el navegador sin necesidad de tocar código, indicando la ruta de Drive y configurando opciones según sus necesidades.

### Funcionalidades principales:

- **Escaneo recursivo** de archivos en cualquier carpeta
- **Clasificación automática** por tipo (documentos, imágenes, multimedia, otros)
- **Organización jerárquica** por fecha (año/mes) y extensión
- **Subcarpetas por extensión** dentro de cada mes (ej: `Documentos/2024/Marzo/pdf/`)
- **Preview antes de organizar** con resumen de archivos y estadísticas
- **Detección de duplicados** mediante hash MD5
- **Generación de reportes CSV** con estadísticas detalladas
- **Interfaz web moderna** y responsive
- **Acceso público** mediante tunneling con trycloudflare

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3 + Flask |
| Frontend | HTML5 + CSS3 + JavaScript (vanilla) |
| Procesamiento de datos | pandas, numpy |
| Tunneling | cloudflared (trycloudflare) |
| Entorno | Google Colab |

---

## ✅ Requisitos Previos

1. **Google Colab** con acceso a Google Drive montado
2. **Python 3.8** o superior
3. **Conexión a internet** para descargar dependencias

---

## 🚀 Instrucciones de Instalación y Uso en Google Colab

### Paso 1: Montar Google Drive

```python
# Conectar tu Google Drive a Colab
from google.colab import drive
drive.mount('/content/drive')
```

### Paso 2: Clonar el repositorio (SIEMPRE FRESH)

```bash
# Eliminar carpeta si existe de antes (para asegurar código actualizado)
!rm -rf Proyecto_Drive_Ordenado

# Descargar el código desde GitHub
!git clone https://github.com/Danko3104/Proyecto_Drive_Ordenado.git
```

### Paso 3: Entrar al directorio del proyecto

```bash
# Cambiar a la carpeta del proyecto
%cd Proyecto_Drive_Ordenado
```

### Paso 4: Instalar dependencias

```bash
# Instalar Flask y otras librerías necesarias
!pip install flask pandas numpy
```

### Paso 5: Descargar cloudflared (para crear el túnel)

```bash
# Descargar el programa que crea el enlace público
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# Dar permisos de ejecución
!chmod +x cloudflared-linux-amd64
```

### Paso 6: Iniciar el servidor Flask

```bash
# Iniciar el servidor web en segundo plano (no muestra logs aquí)
!nohup python3 app.py > flask.log 2>&1 &

# Esperar 3 segundos a que inicie
!sleep 3

# Verificar que está corriendo
!curl -s http://localhost:5000 > /dev/null && echo "✅ Servidor listo" || echo "❌ Error al iniciar"
```

### Paso 7: Crear túnel público

**IMPORTANTE:** Esta celda debe quedarse corriendo. No la detengas o el enlace dejará de funcionar.

```python
# Crear el enlace público para acceder desde cualquier navegador
# Esta celda se queda ejecutando para mantener el túnel activo
import subprocess
import time
import re
import sys

print("⏳ Iniciando túnel...")
print("="*60)

# Iniciar cloudflared y capturar output
process = subprocess.Popen(
    ['./cloudflared-linux-amd64', 'tunnel', '--url', 'http://localhost:5000'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

url_mostrada = False

# Leer output línea por línea
for line in process.stdout:
    line = line.strip()
    
    # Buscar y mostrar la URL cuando aparezca
    if not url_mostrada:
        match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
        if match:
            url = match.group(0)
            print("\n" + "🎉"*20)
            print("\n" + "="*60)
            print("  ✅ TÚNEL LISTO - ABRE ESTA URL EN TU NAVEGADOR:")
            print("="*60)
            print(f"\n       {url}\n")
            print("="*60)
            print("  ⚠️  NO CIERRES ESTA CELDA O EL ENLADO DEJARÁ DE FUNCIONAR")
            print("="*60 + "\n")
            url_mostrada = True
            continue
    
    # Mostrar solo mensajes importantes
    if 'INF' in line:
        if 'connection' in line.lower() or 'tunnel' in line.lower():
            print(f"  [OK] {line.split('INF')[-1].strip()}")
    elif 'error' in line.lower() or 'failed' in line.lower():
        print(f"  [ERROR] {line}")

try:
    process.wait()
except KeyboardInterrupt:
    print("\n🛑 Deteniendo túnel...")
    process.terminate()
    sys.exit(0)
```

**Después de ver la URL, ábrela en tu navegador.**

⚠️ **IMPORTANTE:** Mantén esta celda ejecutándose. Si la detienes, el enlace dejará de funcionar.

---

## 🌓 Características de la interfaz

- **Modo Oscuro/Claro**: Botón 🌙/☀️ en la esquina superior derecha para cambiar tema
- **Preview antes de organizar**: Muestra estadísticas antes de mover archivos
- **Advertencia de seguridad**: Alerta si intentas organizar todo tu Drive

---

## 📝 Notas importantes

⚠️ **Si recargas la página y no ves los cambios:**
- Presiona `Ctrl + Shift + R` para forzar recarga sin caché
- O abre en una pestaña de incógnito

⚠️ **Para volver a ejecutar:**
- Si el túnel se cae, solo ejecuta el Paso 7 nuevamente
- Si quieres reiniciar todo, ejecuta desde el Paso 2

---

## 📖 Guía de Uso

### 1. Pantalla Principal

En la interfaz web encontrarás:

- **Ruta de la carpeta**: Ingresa la ruta completa (ej: `/content/drive/MyDrive/Descargas`)
- **Carpeta destino**: Opcional, dejar en blanco para organizar en la misma ubicación
- **Criterio principal**: Elegir entre organizar por tipo, fecha o tamaño
- **Organizar por fecha**: Checkbox para crear subcarpetas por año/mes
- **Organizar por extensión**: Checkbox para crear subcarpetas por extensión dentro de cada mes
- **Detectar duplicados**: Checkbox para identificar archivos duplicados (más lento)

### 2. Iniciar Organización

1. Completa los campos del formulario
2. Haz clic en "Organizar Archivos"
3. Revisa la **vista previa** que muestra:
   - Total de archivos encontrados
   - Cantidad por categoría
   - Número de duplicados detectados
   - Espacio total a mover
4. Confirma la organización haciendo clic en "Confirmar y Organizar"
5. Espera a que el proceso termine (verás una barra de progreso)

### 3. Ver Resultados

Una vez completado, podrás:
- Ver estadísticas en la pantalla de resultados
- Descargar el reporte CSV
- Ver el reporte detallado en el navegador

---

## 📁 Estructura de Carpetas Generada

Al organizar por **tipo**, **fecha** y **extensión**, la estructura resultante será:

```
Carpeta_Organizada/
├── Documentos/
│   ├── 2024/
│   │   ├── Enero/
│   │   │   └── pdf/
│   │   │       └── archivo.pdf
│   │   ├── Febrero/
│   │   └── Marzo/
│   │       ├── docx/
│   │       │   └── documento.docx
│   │       └── pdf/
│   │           └── otro.pdf
│   └── 2023/
│       ├── Diciembre/
│       └── Noviembre/
├── Imágenes/
│   ├── 2024/
│   │   └── Marzo/
│   │       ├── jpg/
│   │       │   └── foto.jpg
│   │       └── png/
│   │           └── imagen.png
│   └── 2023/
│       └── Diciembre/
│           └── jpg/
│               └── otra_foto.jpg
├── Multimedia/
│   └── 2024/
│       └── Febrero/
│           └── mp4/
│               └── video.mp4
└── Otros/
    └── 2024/
        └── zip/
            └── archivo.zip
```

> **Nota:** Las subcarpetas de extensión solo se crean cuando hay archivos con esa extensión. Si no deseas organizar por extensión, desmarca la opción "Organizar por extensión".

---

## 📊 Categorías de Archivos

| Categoría | Extensiones |
|-----------|-------------|
| **Documentos** | .pdf, .docx, .doc, .txt, .pptx, .xlsx, .csv |
| **Imágenes** | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp |
| **Multimedia** | .mp4, .mp3, .avi, .mov, .wav, .mkv |
| **Otros** | Cualquier otra extensión |

---

## 📄 Ejemplo de Reporte CSV

El archivo `reporte_organizacion.csv` contiene las siguientes columnas:

```csv
nombre_original,extension,categoria,tamaño_bytes,fecha_modificacion,ruta_destino,es_duplicado
informe_anual.pdf,.pdf,documentos,1543200,2024-03-15 10:30:00,/ruta/destino/Documentos/2024/Marzo/informe_anual.pdf,No
foto_vacaciones.jpg,.jpg,imagenes,2048560,2023-12-20 14:45:00,/ruta/destino/Imagenes/2023/Diciembre/foto_vacaciones.jpg,No
presentacion.pptx,.pptx,documentos,4520000,2024-01-10 09:15:00,/ruta/destino/Documentos/2024/Enero/presentacion.pptx,Si
cancion_favorita.mp3,.mp3,multimedia,5242880,2024-05-22 16:20:00,/ruta/destino/Multimedia/2024/Mayo/cancion_favorita.mp3,No
```

### Columnas del CSV:

| Columna | Descripción |
|---------|-------------|
| `nombre_original` | Nombre del archivo antes de organizar |
| `extension` | Extensión del archivo |
| `categoria` | Categoría asignada (documentos, imagenes, multimedia, otros) |
| `tamaño_bytes` | Tamaño del archivo en bytes |
| `fecha_modificacion` | Fecha de última modificación (YYYY-MM-DD HH:MM:SS) |
| `ruta_destino` | Ruta final donde fue movido el archivo |
| `es_duplicado` | "Si" si es duplicado, "No" en caso contrario |

---

## 🔍 Detección de Duplicados

El sistema detecta archivos duplicados calculando el **hash MD5** de cada archivo:

- Archivos con el mismo contenido tienen el mismo hash
- Los duplicados son marcados en el CSV pero **NO se eliminan**
- Se reporta el espacio ocupado por duplicados

Para archivos grandes (>500MB), se usa un hash parcial (inicio + final + tamaño) para optimizar el rendimiento.

---

## 🏗️ Estructura del Proyecto

```
proyecto_drive_ordenado/
├── app.py                  # Servidor Flask principal
├── organizer.py            # Lógica de organización
├── reporter.py             # Generación de reportes CSV
├── duplicates.py           # Detección de duplicados
├── requirements.txt        # Dependencias Python
├── start.sh                # Script de inicio
├── README.md               # Documentación
├── templates/
│   ├── index.html          # Página principal
│   ├── result.html         # Pantalla de resultados
│   └── report.html         # Vista del reporte
└── static/
    ├── style.css           # Estilos CSS
    └── script.js           # JavaScript frontend
```

---

## ⚙️ API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Página principal con formulario |
| `/preview` | POST | Obtiene preview de organización sin mover archivos |
| `/organizar` | POST | Inicia el proceso de organización |
| `/estado` | GET | Consulta el estado del proceso en curso |
| `/resultados` | GET | Muestra los resultados del último proceso |
| `/reporte` | GET | Vista detallada del reporte CSV |
| `/descargar_reporte` | GET | Descarga el archivo CSV |
| `/api/estadisticas` | GET | API JSON con estadísticas |

---

## ⚠️ Notas Importantes

1. **Los archivos originales nunca se eliminan**, solo se mueven a nuevas ubicaciones
2. Si un archivo con el mismo nombre existe en destino, se renombra automáticamente (`archivo_1.pdf`, `archivo_2.pdf`, etc.)
3. La detección de duplicados puede ser lenta en carpetas con muchos archivos grandes
4. El túnel de trycloudflare es temporal y cambia cada vez que reinicias la aplicación

---

## 🔧 Solución de Problemas

### Error: "La ruta no existe"
- Verifica que Google Drive esté montado correctamente
- Asegúrate de que la ruta comience con `/content/drive/`

### Error: "Permission denied" al mover archivos
- Algunos archivos de sistema de Google Drive pueden tener restricciones
- Los archivos afectados se reportan en el CSV con el error correspondiente

### El túnel no se genera
- Verifica que cloudflared se descargó correctamente
- Ejecuta `chmod +x cloudflared-linux-amd64` manualmente
- Intenta reiniciar el runtime de Colab

---

## 📜 Licencia

Proyecto académico desarrollado para fines educativos.

---

## 🙏 Créditos

Desarrollado como proyecto de programación en Python.

- **Backend**: Python, Flask, pandas
- **Frontend**: HTML5, CSS3, JavaScript
- **Tunneling**: Cloudflare Tunnel

---

**¡Gracias por usar Drive Ordenado!** 📁✨
