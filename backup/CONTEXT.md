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

### Gráficas en Reporte
- [x] Distribución por Categoría (doughnut)
- [x] Archivos por Año (barras)
- [x] Extensiones Principales (pie) - centrada
- [ ] ~~Distribución de Tamaños~~ (eliminada por solicitud del usuario)

### Secciones Desplegables en Reporte
- [x] Archivos Duplicados (con lista detallada)
- [x] Distribución por Año (tabla)
- [x] Extensiones Encontradas (badges)
- [x] Resumen Estadístico

### Secciones Desplegables en Resultados
- [x] Distribución por Categoría (desde tarjeta clickeable)
- [x] Archivos Duplicados (desde tarjeta clickeable, si existen)

---

## 🔧 Problemas Conocidos / Pendientes

### 🔴 Críticos
1. **Sección de Duplicados en Reporte no aparece**
   - El template `report.html` verifica `{% if duplicados_detalle and duplicados_detalle|length > 0 %}`
   - La función `reporte()` en `app.py` carga los duplicados desde el CSV
   - **Problema**: Los duplicados no se están mostrando aunque existan en el CSV
   - **Posible causa**: El CSV no tiene la columna `es_duplicado` correctamente poblada o el hash no está generándose bien
   - **Ubicación**: Revisar `reporter.py` función `generar_reporte_csv()`

### 🟡 Mejoras Visuales
2. **Navegación en Reporte**
   - Los enlaces "← Inicio" y "Resultados" están muy pegados
   - Se agregó un `span` con margen entre ellos como solución temporal
   - **Podría mejorarse**: Con flexbox y gap en el CSS

3. **Responsive de Gráficas**
   - Las gráficas se adaptan pero podrían optimizarse mejor para móviles

### 🟢 Funcionalidades Futuras Sugeridas
4. **Previsualización de archivos** - Ver miniaturas de imágenes antes de organizar
5. **Búsqueda en tiempo real** - Filtrar archivos por nombre/categoría
6. **Exportar a Excel** - Además de CSV, opción de Excel
7. **Programar organización** - Ejecutar automáticamente cada cierto tiempo
8. **Undo/Deshacer** - Revertir la última organización

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
│   └── CONTEXT.md          # Este archivo
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
- Iconos: ▼ (cerrado), ▲ (abierto)
- Transición: 0.3s ease

---

## 📊 Estado de las Gráficas

| Gráfica | Tipo | Estado | Ubicación |
|---------|------|--------|-----------|
| Distribución por Categoría | Doughnut | ✅ Activa | Arriba, izquierda |
| Archivos por Año | Bar | ✅ Activa | Arriba, derecha |
| Extensiones Principales | Pie | ✅ Activa | Abajo, centrada |
| Distribución de Tamaños | Bar | ❌ Eliminada | N/A |

---

## 🌓 Modo Oscuro

- Implementado en: `index.html`, `result.html`, `report.html`
- Persistencia: `localStorage` con clave `'tema'`
- Valores: `'dark'` o `'light'`
- Toggle: Botón 🌙/☀️ en header
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
3. **Túnel**: Usa `cloudflared` con trycloudflare ( URLs temporales )
4. **CSV**: Columnas: nombre_original, extension, categoria, tamaño_bytes, fecha_modificacion, ruta_destino, es_duplicado

---

## 🔗 URLs Importantes

- Repositorio: https://github.com/Danko3104/Proyecto_Drive_Ordenado.git
- Túnel se genera automáticamente al ejecutar

---

## ⚠️ Decisiones de Diseño

1. **No se eliminan archivos**: Solo se mueven, nunca se borran
2. **Duplicados marcados, no eliminados**: El usuario decide qué hacer
3. **Sin base de datos**: Todo se maneja con archivos CSV y variables en memoria
4. **Sesión única**: No hay persistencia entre reinicios del servidor

---

## 🐛 Último Error Conocido

**Fecha**: 2026-05-28
**Problema**: Los duplicados aparecen en el resultado pero no se muestra el detalle en el reporte
**Estado**: Investigar función `generar_reporte_csv()` en `reporter.py`

---

**Para cualquier modelo que revise esto**: Revisa los issues abiertos en el README.md principal y verifica que las funcionalidades marcadas con ✅ funcionen correctamente antes de agregar nuevas features.
