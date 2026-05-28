# ✅ TODO - Tareas Pendientes Drive Ordenado

## 🚨 URGENTE - Arreglar Primero

### 1. Duplicados no aparecen en el Reporte
**Estado**: ✅ RESUELTO - 2026-05-28
**Nota**: El bug fue corregido en la versión actual del código. La sección de duplicados ahora se muestra correctamente en `report.html` cuando existen duplicados.

---

## ✅ Completado

### 1. Carpetas vacías después de organizar
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Se agregó función `eliminar_carpetas_vacias()` en `organizer.py`
- Elimina carpetas vacías recursivamente después de mover archivos
- Se muestra contador en resultados con sección desplegable

### 2. Layout de tarjetas en resultados
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Grid CSS con `auto-fit` para distribuir las 5 tarjetas uniformemente
- Las tarjetas ocupan toda la fila sin dejar espacios vacíos
- Padding y gap reducidos para que quepan las 5 tarjetas arriba

### 3. Gráficas del reporte
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Gráficas apiladas en una sola columna para mejor visualización
- Altura ajustada a 320px para que se vean grandes
- Pie chart con leyenda en posición `bottom`
- Título "Visualización de Datos" centrado y agrandado

### 4. Badges informativos
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Badge "X tipos" en Extensiones Encontradas
- Badge "X años" en Distribución por Año

### 5. Iconos de colapsar/elargar
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Se eliminaron los iconos ⌄/⌃ de todos los templates (`result.html` y `report.html`)
- JavaScript simplificado para no manipular iconos de toggle

### 6. Theme toggle posicionado
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Botón de tema movido a esquina superior derecha (`top: 8px; right: 8px`)
- Ya no interfiere con el título centrado

### 7. Favicon
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Agregado favicon con emoji 📁 en las 3 páginas (`index.html`, `result.html`, `report.html`)
- Usa SVG data URI para no depender de archivos externos

### 8. Botón de acceso directo a Google Drive
**Estado**: ✅ RESUELTO - 2026-05-28
**Solución**:
- Botón 🚀 Abrir Drive en el footer de `result.html`
- Botón 🚀 Abrir Drive en el footer de `report.html`
- Botón 🚀 Abrir Drive en la pantalla de éxito de `index.html`
- Abre Google Drive en una nueva pestaña

---

## 🎨 Mejoras Visuales Pendientes

### Navegación del Reporte
**Ubicación**: `templates/report.html`, línea ~18-21

**Problema**: Los enlaces "← Inicio" y "Resultados" están muy pegados.

**Solución actual**: Se agregó un span con margen entre ellos.

**Mejora ideal**: Usar Flexbox con gap:
```css
.nav {
    display: flex;
    gap: var(--spacing);
}
```

---

## ✨ Funcionalidades Futuras (Nice to Have)

### 1. Previsualización de Imágenes
- Mostrar miniaturas de imágenes en el preview
- Usar `send_file` con ruta temporal

### 2. Búsqueda/Filtro
- Campo de búsqueda en el reporte
- Filtrar por nombre, extensión, categoría

### 3. Exportar a Excel
- Usar librería `openpyxl` o `xlsxwriter`
- Agregar botón "Descargar Excel" junto al CSV

### 4. Programar Tareas
- Usar `APScheduler` para ejecutar organización automática
- Interfaz para seleccionar frecuencia (diario, semanal)

### 5. Undo/Deshacer
- Guardar log de movimientos
- Botón "Deshacer última organización"
- Revertir archivos a su ubicación original

---

## 🧪 Testing Pendiente

- [ ] Probar con carpeta vacía
- [ ] Probar con 1000+ archivos
- [ ] Probar con nombres de archivo con caracteres especiales
- [ ] Probar modo oscuro en todos los navegadores
- [ ] Probar responsive en móvil
- [ ] Verificar que el CSV se descarga correctamente

---

## 📝 Documentación

- [x] README principal actualizado
- [x] CONTEXT.md actualizado
- [x] TODO.md actualizado
- [ ] Agregar screenshots/gifs al README
- [ ] Crear video tutorial de uso

---

## 🔧 Optimizaciones Técnicas

### Performance
- [ ] Paginar la lista de duplicados (si son muchos)
- [ ] Lazy loading de gráficas
- [ ] Comprimir imágenes si se implementa preview

### Código
- [ ] Refactorizar CSS (es muy grande)
- [ ] Separar JavaScript en archivos por página
- [ ] Agregar type hints faltantes
- [ ] Agregar docstrings completas

---

**Última actualización**: 2026-05-28
**Próxima revisión**: Al completar testing pendiente o agregar nueva funcionalidad
