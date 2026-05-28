# 📋 Contexto del Proyecto - Drive Ordenado

## 🎯 Descripción General

**Drive Ordenado** es una aplicación web Flask que organiza automáticamente archivos en Google Drive. Está diseñada para ejecutarse en Google Colab y proporciona una interfaz web moderna con modo oscuro/claro.

**Integrantes:**
- Mendoza Gomez Eleangie Valentina (2242557)
- Tavera Carreño Daniel José (2243042)

---

## ✅ Funcionalidades Implementadas

### Funcionalidades Core
- [x] Escaneo recursivo de archivos
- [x] Clasificación automática por tipo (documentos, imágenes, multimedia, otros)
- [x] Organización jerárquica por fecha (año/mes) y extensión
- [x] Subcarpetas por extensión dentro de cada mes
- [x] Preview antes de organizar con estadísticas
- [x] Detección de duplicados mediante hash MD5
- [x] Generación de reportes CSV
- [x] Modo oscuro/claro con persistencia en localStorage
- [x] Interfaz web responsive
- [x] Eliminación automática de carpetas vacías
- [x] Botón de acceso directo a Google Drive
- [x] Favicon en todas las páginas

### Gráficas en Reporte
- [x] Distribución por Categoría (doughnut)
- [x] Archivos por Año (barras) - se oculta si solo hay 1 año
- [x] Extensiones Principales (pie) - leyenda abajo
- [x] Gráficas apiladas en una sola columna para mejor visualización
- [ ] ~~Distribución de Tamaños~~ (eliminada por solicitud del usuario)

### Secciones Desplegables en Reporte
- [x] Archivos Duplicados (con lista detallada)
- [x] Distribución por Año (tabla) - con badge "X años"
- [x] Extensiones Encontradas (badges) - con badge "X tipos"
- [x] Resumen Estadístico

### Secciones Desplegables en Resultados
- [x] Archivos procesados → Estadísticas Adicionales
- [x] Distribución por Categoría (desde tarjeta clickeable)
- [x] Archivos Duplicados (desde tarjeta clickeable, si existen)
- [x] Carpetas Vacías Eliminadas (desde tarjeta clickeable)

### UI/UX
- [x] Lupa 🔍 en esquina superior derecha de tarjetas desplegables
- [x] Grid CSS flexible para tarjetas de resultados (5 tarjetas en fila)
- [x] Badges informativos en headers desplegables
- [x] Theme toggle en esquina superior derecha
- [x] Título de visualización centrado y agrandado
- [x] Iconos de flecha (⌄/⌃) eliminados de secciones desplegables

---

## 🔧 Problemas Conocidos / Pendientes

### 🔴 Críticos
*Todos los bugs críticos han sido resueltos.*

### 🟡 Mejoras Visuales
1. **Navegación del Reporte**
   - Los enlaces "← Inicio" y "Resultados" están muy pegados
   - **Solución actual**: Se agregó un span con margen entre ellos
   - **Mejora ideal**: Usar Flexbox con gap en el CSS

### 🟢 Funcionalidades Futuras Sugeridas
2. **Previsualización de archivos** - Ver miniaturas de imágenes antes de organizar
3. **Búsqueda en tiempo real** - Filtrar archivos por nombre/categoría
4. **Exportar a Excel** - Además de CSV, opción de Excel
5. **Programar organización** - Ejecutar automáticamente cada cierto tiempo
6. **Undo/Deshacer** - Revertir la última organización

---

## 🏗️ Estructura del Proyecto

```
proyecto_drive_ordenado/
├── app.py                  # Servidor Flask principal
├── organizer.py            # Lógica de organización de archivos
├── duplicates.py           # Detección de duplicados con hash MD5
├── reporter.py             # Generación de reportes CSV
├── requirements.txt        # Dependencias Python
├── setup_colab.py          # Script de setup automático para Colab
├── start.sh                # Script de inicio legacy
├── start_tunnel.sh         # Script para túnel Cloudflare
├── tunnel.py               # Script alternativo para túnel
├── README.md               # Documentación principal
├── backup/
│   ├── CONTEXT.md          # Este archivo
│   ├── TODO.md             # Tareas pendientes y completadas
│   └── fotos_referencias/  # Carpeta para capturas (actualmente vacía)
├── templates/
│   ├── index.html          # Página principal (formulario)
│   ├── result.html         # Página de resultados
│   └── report.html         # Página de reporte detallado
└── static/
    ├── style.css           # Estilos CSS con variables para tema oscuro
    └── script.js           # JavaScript frontend
```

---

## 🎨 Sistema de Diseño

### Variables CSS para Temas
```css
/* Tema Claro (default) */
--color-primary: #2563eb
--color-bg: #f8fafc
--color-card: #ffffff
--color-text: #1e293b
--color-border: #e2e8f0

/* Tema Oscuro */
--color-primary: #3b82f6
--color-bg: #0f172a
--color-card: #1e293b
--color-text: #f1f5f9
--color-border: #334155
```

### Componentes Desplegables
- Clase: `.expandable-header`, `.expandable-content`
- Transición: 0.3s ease
- **Nota**: Los iconos ⌄/⌃ fueron eliminados por solicitud del usuario

### Tarjetas Desplegables
- Lupa 🔍 en esquina superior derecha (position: absolute)
- Solo en tarjetas con clase `.expandable-card`
- Opacidad aumenta al hover

---

## 📊 Estado de las Gráficas

| Gráfica | Tipo | Estado | Ubicación |
|---------|------|--------|-----------|
| Distribución por Categoría | Doughnut | ✅ Activa | Primera, ancho completo |
| Archivos por Año | Bar | ✅ Activa | Segunda, ancho completo (oculta si 1 año) |
| Extensiones Principales | Pie | ✅ Activa | Tercera, ancho completo, leyenda abajo |
| Distribución de Tamaños | Bar | ❌ Eliminada | N/A |

---

## 🌓 Modo Oscuro

- Implementado en: `index.html`, `result.html`, `report.html`
- Persistencia: `localStorage` con clave `'tema'`
- Valores: `'dark'` o `'light'`
- Toggle: Botón 🌙/☀️ en header (esquina superior derecha)
- Las gráficas Chart.js se recargan al cambiar tema para aplicar nuevos colores

---

## 🚀 Cómo Ejecutar (Resumen)

### Opción Rápida (2 celdas en Colab)
```python
# Celda 1
from google.colab import drive
drive.mount('/content/drive')

# Celda 2
!rm -rf Proyecto_Drive_Ordenado
!git clone https://github.com/Danko3104/Proyecto_Drive_Ordenado.git
%cd Proyecto_Drive_Ordenado
!python3 setup_colab.py
```

---

## 📝 Notas Técnicas Importantes

1. **Versión de CSS**: Se usa `?v=2.0` o `?v=3.0` para evitar caché del navegador
2. **Chart.js**: Cargado desde CDN `https://cdn.jsdelivr.net/npm/chart.js`
3. **Túnel**: Usa `cloudflared` con trycloudflare (URLs temporales)
4. **CSV**: Columnas: nombre_original, extension, categoria, tamaño_bytes, fecha_modificacion, ruta_destino, es_duplicado
5. **Gráfica de años**: No se renderiza si `estadisticas.resumen.años_cubiertos|length <= 1`
6. **Favicon**: Emoji 📁 como SVG data URI (sin dependencias externas)
7. **Theme toggle**: Posicionado con `position: absolute; top: 8px; right: 8px`

---

## 🔗 URLs Importantes

- Repositorio: https://github.com/Danko3104/Proyecto_Drive_Ordenado.git
- Túnel se genera automáticamente al ejecutar
- Google Drive: https://drive.google.com (acceso directo desde botones de la app)

---

## ⚠️ Decisiones de Diseño

1. **No se eliminan archivos**: Solo se mueven, nunca se borran
2. **Duplicados marcados, no eliminados**: El usuario decide qué hacer
3. **Sin base de datos**: Todo se maneja con archivos CSV y variables en memoria
4. **Sesión única**: No hay persistencia entre reinicios del servidor
5. **Lupa en tarjetas**: Indica visualmente que la tarjeta es desplegable
6. **Gráficas apiladas**: Distribución vertical en una columna para mejor legibilidad
7. **Favicon emoji**: Evita depender de archivos externos que puedan romperse

---

## 🐛 Último Error Conocido

**Fecha**: 2026-05-28
**Estado**: ✅ Todos los bugs críticos resueltos
**Últimos cambios**:
- Layout de tarjetas corregido a grid CSS
- Gráficas del reporte reorganizadas en columna única
- Iconos de flecha eliminados de secciones desplegables
- Theme toggle reposicionado
- Botón de acceso a Drive agregado

---

**Para cualquier modelo que revise esto**: Revisa los issues abiertos en TODO.md y verifica que las funcionalidades marcadas con ✅ funcionen correctamente antes de agregar nuevas features.
