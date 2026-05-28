# 📁 Drive Ordenado

Aplicación web que automatiza la organización de archivos en Google Drive montado en Google Colab. Organiza, clasifica, detecta duplicados y genera reportes completos de tus archivos.

---

## 👥 Integrantes

- **Mendoza Gomez Eleangie Valentina** (2242557)
- **Tavera Carreño Daniel José** (2243042)

---

## 📋 Descripción del Proyecto

**Drive Ordenado** es una aplicación web desarrollada en Python con Flask que permite organizar automáticamente archivos en Google Drive. El usuario interactúa desde el navegador sin necesidad de tocar código, indicando la ruta de Drive y configurando opciones según sus necesidades.

### ✨ Funcionalidades principales:

- **Escaneo recursivo** de archivos en cualquier carpeta
- **Clasificación automática** por tipo (documentos, imágenes, multimedia, otros)
- **Organización jerárquica** por fecha (año/mes) y extensión
- **Subcarpetas por extensión** dentro de cada mes (ej: `Documentos/2024/Marzo/pdf/`)
- **Preview antes de organizar** con resumen de archivos y estadísticas
- **Detección de duplicados** mediante hash MD5
- **Generación de reportes CSV** con estadísticas detalladas
- **Gráficas interactivas** en el reporte (dona y barras)
- **Lista de duplicados desplegable** con ubicaciones
- **Modo oscuro/claro** 🌙☀️ - elige tu tema preferido
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

## 🆕 ¿Nunca has usado Google Colab? Empieza aquí

Si es tu primera vez con Colab, sigue estos pasos para crear tu archivo:

### Paso A: Crear un nuevo notebook

1. **Abre tu navegador** y ve a: [https://colab.research.google.com](https://colab.research.google.com)
2. Haz clic en **"Nuevo cuaderno"** (o "New notebook" si está en inglés)
3. Se abrirá una página con una celda de código lista para usar

### Paso B: Agregar celdas de código

Las celdas son los cuadritos donde escribes los comandos. Para agregar más:

- **Método 1:** Haz clic en el botón **"+ Código"** (aparece arriba o en la barra lateral)
- **Método 2:** Presiona `Ctrl + M` y luego `B` (agrega celda debajo)

Verás un cuadrito gris donde puedes escribir. Eso es una celda de código.

### Paso C: Cambiar entre celdas de código y texto (opcional)

- Para escribir **código**: Deja como está (dice "Código" o "Code" arriba a la izquierda de la celda)
- Para escribir **texto explicativo**: Haz clic en el menú desplegable donde dice "Código" y cambia a "Texto"

### Paso D: Ejecutar una celda

Después de escribir o pegar código en una celda:

- **Haz clic en el ▶️ (botón de play)** a la izquierda de la celda
- **O presiona:** `Ctrl + Enter` (ejecuta y se queda) o `Shift + Enter` (ejecuta y pasa a la siguiente)

Cuando ejecutas, verás un círculo girando ⏳ mientras procesa, y luego el resultado abajo.

### Paso E: Guardar tu trabajo

- Colab guarda automáticamente en tu Google Drive
- O puedes ir a **Archivo → Guardar** (Ctrl + S)

---

## 🚀 Cómo usar Drive Ordenado en Google Colab (2 Opciones)

Ahora que sabes cómo usar Colab, elige una de estas dos formas:

### ⚡ OPCIÓN 1: RÁPIDA (Recomendada)

Perfecta si quieres empezar ya. Solo copia y pega:

**Celda 1 - Conectar Drive:**
```python
# 🔗 Conecta tu Google Drive a Colab
from google.colab import drive
drive.mount('/content/drive')
```

**Celda 2 - Descargar e iniciar todo automático:**
```bash
# 📥 Descargar el proyecto (código más reciente)
!rm -rf Proyecto_Drive_Ordenado  # Borra si existe
!git clone https://github.com/Danko3104/Proyecto_Drive_Ordenado.git

# 📂 Entrar a la carpeta
%cd Proyecto_Drive_Ordenado

# 🚀 Ejecutar setup automático (hace TODO por ti)
!python3 setup_colab.py
```

**Listo!** Espera unos segundos y verás la URL. Ábrela en tu navegador. ✅

---

### 🔧 OPCIÓN 2: PASO A PASO (Para entender qué pasa)

Si prefieres ver cada paso y entender qué está pasando:

#### Paso 1: Conectar tu Google Drive

Primero necesitamos que Colab pueda acceder a tus archivos de Drive.

```python
# 🔗 Esto abrirá una ventana para que autorices el acceso
from google.colab import drive
drive.mount('/content/drive')
```

Verás un link - haz clic, elige tu cuenta de Google y copia el código que te dan. Pégalo en Colab y presiona Enter.

#### Paso 2: Descargar el proyecto

Ahora vamos a bajar el código desde GitHub:

```bash
# 🗑️ Primero borramos si habías descargado algo antes
# (para asegurarnos de tener la última versión)
!rm -rf Proyecto_Drive_Ordenado

# 📥 Ahora sí, descargamos el proyecto
!git clone https://github.com/Danko3104/Proyecto_Drive_Ordenado.git

# 📂 Entramos a la carpeta que acabamos de crear
%cd Proyecto_Drive_Ordenado
```

#### Paso 3: Instalar lo que necesita la app

La aplicación necesita algunas librerías de Python para funcionar:

```bash
# 📦 Instalamos Flask (para el servidor web)
# Pandas y Numpy (para manejar los datos)
!pip install flask pandas numpy
```

Esto tomará unos segundos. Verás mucho texto - es normal, está instalando todo.

#### Paso 4: Descargar el "puente" a internet

Necesitamos un programa que cree un enlace público para tu app:

```bash
# 📥 Descargamos cloudflared (el programa que crea el enlace)
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# 🔓 Le damos permisos para ejecutarse
!chmod +x cloudflared-linux-amd64
```

#### Paso 5: Iniciar el servidor

Ahora arrancamos la aplicación web:

```bash
# 🚀 Iniciamos el servidor en segundo plano
# (nohup significa "no cuelgues cuando cierro" - técnico pero útil)
!nohup python3 app.py > flask.log 2>&1 &

# ⏳ Esperamos 3 segundos a que arranque
!sleep 3

# ✅ Verificamos que todo está OK
!curl -s http://localhost:5000 > /dev/null && echo "✅ Servidor listo!" || echo "❌ Algo salió mal"
```

Si ves "✅ Servidor listo!" todo va bien. Si ves error, intenta esperar un poco más y ejecutar de nuevo.

#### Paso 6: Crear el enlace público

**⚠️ IMPORTANTE:** Esta celda se debe quedar corriendo. No la detengas o el enlace morirá.

```python
# 🌐 Este código crea el túnel y muestra tu URL
import subprocess
import time
import re
import sys

print("⏳ Iniciando túnel...")
print("="*60)

# Iniciamos cloudflared
process = subprocess.Popen(
    ['./cloudflared-linux-amd64', 'tunnel', '--url', 'http://localhost:5000'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

url_mostrada = False

# Leemos el output hasta encontrar la URL
for line in process.stdout:
    line = line.strip()
    
    # Cuando encontramos la URL, la mostramos BONITO
    if not url_mostrada:
        match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
        if match:
            url = match.group(0)
            print("\n" + "🎉"*20)
            print("\n" + "="*60)
            print("  ✅ ¡TU ENLACE ESTÁ LISTO!")
            print("  Abre esta URL en tu navegador:")
            print("="*60)
            print(f"\n       {url}\n")
            print("="*60)
            print("  ⚠️  NO CIERRES ESTA CELDA")
            print("  O el enlace dejará de funcionar")
            print("="*60 + "\n")
            url_mostrada = True
            continue
    
    # Mostramos mensajes de estado
    if 'INF' in line and ('connection' in line.lower() or 'tunnel' in line.lower()):
        print(f"  [OK] {line.split('INF')[-1].strip()}")

# Mantenemos la celda viva
try:
    process.wait()
except KeyboardInterrupt:
    print("\n🛑 Deteniendo túnel...")
    process.terminate()
    sys.exit(0)
```

**Cuando veas la URL**, ábrela en tu navegador. La celda seguirá corriendo - eso es bueno, significa que el enlace sigue vivo.

---

## 🌓 Características de la interfaz

Una vez dentro de la app verás:

- **🌙☀️ Botón de tema**: En la esquina superior derecha, cambia entre claro y oscuro
- **📊 Preview**: Antes de mover archivos, ves cuántos hay y de qué tipo
- **⚠️ Advertencia de seguridad**: Si intentas organizar todo tu Drive, te avisa
- **📁 Organización inteligente**: Categoría → Año → Mes → Extensión

---

## 📖 Cómo usar la aplicación

### 1. Pantalla Principal

- **Ruta de la carpeta**: Dónde están los archivos a organizar (ej: `/content/drive/MyDrive/Descargas`)
  - Deja en blanco para organizar TODO tu Drive ⚠️
- **Carpeta destino**: Dónde quieres que vayan (deja vacío para misma ubicación)
- **Organizar por fecha**: Crea carpetas por año y mes ✅ Recomendado
- **Organizar por extensión**: Crea subcarpetas por tipo de archivo ✅ Recomendado
- **Detectar duplicados**: Encuentra archivos repetidos (más lento)

### 2. Proceso de organización

1. **Haz clic en "Organizar Archivos"**
2. **Revisa el preview** - te muestra:
   - Cuántos archivos encontró
   - Cuántos hay de cada categoría
   - Cuánto espacio ocupan
   - Cuántos duplicados hay (si activaste esa opción)
3. **Confirma** haciendo clic en "Confirmar y Organizar"
4. **Espera** la barra de progreso
5. **¡Listo!** Verás los resultados

### 3. Después de organizar

Puedes:
- **Ver el reporte detallado** en el navegador con:
  - 📊 **Gráficas** de distribución por categoría (dona) y por año (barras)
  - 🔍 **Sección de duplicados** desplegable con lista detallada y ubicaciones
  - 📈 Tablas de distribución por año y extensiones
  - 📋 Ejemplo del formato CSV
- **Descargar el archivo CSV** con todos los datos
- **Ver las estadísticas** de cuánto moviste

**Características del reporte detallado:**
- **Gráficas interactivas**: Visualiza la distribución de archivos
- **Modo oscuro/claro**: El reporte respeta tu tema elegido
- **Duplicados desplegables**: Haz clic en "Archivos Duplicados" para ver el listado completo con hash y ubicaciones

---

## 📁 Estructura de carpetas generada

Cuando organizas por **tipo**, **fecha** y **extensión**, queda así:

```
MiCarpeta_Organizada/
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
├── Imágenes/
│   ├── 2024/
│   │   └── Marzo/
│   │       ├── jpg/
│   │       │   └── foto.jpg
│   │       └── png/
│   │           └── imagen.png
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

---

## 📊 Categorías de archivos

| Categoría | Extensiones incluidas |
|-----------|----------------------|
| **Documentos** | .pdf, .docx, .doc, .txt, .pptx, .xlsx, .csv |
| **Imágenes** | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp |
| **Multimedia** | .mp4, .mp3, .avi, .mov, .wav, .mkv |
| **Otros** | Cualquier otra extensión |

---

## 🔧 Solución de problemas

### "La ruta no existe"
- Verifica que montaste Drive (Paso 1)
- Asegúrate de que la ruta empiece con `/content/drive/`

### "No se ve el modo oscuro"
- Presiona `Ctrl + Shift + R` en tu navegador (fuerza recarga sin caché)

### "El enlace no funciona"
- Verifica que la celda del Paso 6 sigue corriendo
- Si se detuvo, ejecútala de nuevo

### "No veo la URL"
- Espera 10-15 segundos, a veces tarda
- Si sigue sin salir, detén la celda (botón ■) y ejecútala otra vez

---

## 📝 Notas importantes

- ✅ Los archivos **nunca se eliminan**, solo se mueven
- 🔄 Si hay archivos con el mismo nombre, se renombran automáticamente
- ⏱️ La detección de duplicados puede ser lenta en carpetas grandes
- 🌐 El enlace cambia cada vez que reinicias (es temporal)

---

**¡Listo! Ahora sí, a organizar esos archivos!** 📁✨
