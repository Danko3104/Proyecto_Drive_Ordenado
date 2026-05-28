# ✅ TODO - Tareas Pendientes Drive Ordenado

## 🚨 URGENTE - Arreglar Primero

### 1. Duplicados no aparecen en el Reporte
**Problema**: La sección de duplicados está documentada y en el código, pero no se muestra en la interfaz.

**Código involucrado**:
- `app.py` función `reporte()` (líneas ~281-320)
- `templates/report.html` (líneas ~52-77)
- `reporter.py` función `generar_reporte_csv()`

**Pasos para debuggear**:
1. Verificar que el CSV generado tenga la columna `es_duplicado`
2. Verificar que los valores sean "Si" o "No" (case sensitive)
3. Agregar prints en `reporte()` para ver si `duplicados_detalle` se está llenando
4. Revisar que el template reciba la variable correctamente

**Nota**: En la página de resultados sí aparecen los duplicados, el problema es específicamente en el reporte detallado.

---

## 🎨 Mejoras Visuales

### 2. Navegación del Reporte
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

### 3. Tarjetas Clickeables en Resultados
**Ubicación**: `templates/result.html`

**Estado**: ✅ Implementado

**Comportamiento**: 
- La tarjeta de "Categorías" es clickeable y abre el detalle abajo
- La tarjeta de "Duplicados" es clickeable (solo si hay duplicados)

**Nota**: Asegurar que el cursor cambie a pointer al pasar sobre ellas.

---

## ✨ Funcionalidades Futuras (Nice to Have)

### 4. Previsualización de Imágenes
- Mostrar miniaturas de imágenes en el preview
- Usar `send_file` con ruta temporal

### 5. Búsqueda/Filtro
- Campo de búsqueda en el reporte
- Filtrar por nombre, extensión, categoría

### 6. Exportar a Excel
- Usar librería `openpyxl` o `xlsxwriter`
- Agregar botón "Descargar Excel" junto al CSV

### 7. Programar Tareas
- Usar `APScheduler` para ejecutar organización automática
- Interfaz para seleccionar frecuencia (diario, semanal)

### 8. Undo/Deshacer
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
- [x] Este archivo de contexto creado
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

## 🐛 Bugs Conocidos

### Bug #1: Duplicados en Reporte
**Estado**: 🔴 Crítico
**Descripción**: La sección de duplicados no aparece en report.html aunque sí hay duplicados
**Asignado**: Por investigar

### Bug #2: Tema Oscuro en Gráficas
**Estado**: 🟡 Menor
**Descripción**: Al cambiar a modo oscuro, las gráficas necesitan recargar la página
**Solución**: Recargar página automáticamente o usar Chart.js con tema dinámico

---

**Última actualización**: 2026-05-28
**Próxima revisión**: Cuando se reporte el bug de duplicados como arreglado
