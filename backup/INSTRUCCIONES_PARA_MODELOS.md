# 🤖 Instrucciones para Modelos de IA

Si eres un modelo de IA (Claude, GPT, etc.) y vas a trabajar en este proyecto, lee esto primero.

## 📖 Debes Leer Primero

1. **`CONTEXT.md`** - Entender qué es el proyecto y qué se ha hecho
2. **`TODO.md`** - Ver qué tareas están pendientes
3. **`README.md`** (en raíz) - Ver instrucciones de uso

## 🎯 Reglas Importantes

### Antes de hacer cambios
- [ ] Verificar que estás en el directorio correcto: `proyecto_drive_ordenado/`
- [ ] Hacer `git pull origin master` para tener la última versión
- [ ] Leer el archivo que vas a modificar completamente antes de editar

### Al hacer cambios
- [ ] Preferir `Edit` sobre `Write` para no borrar código existente
- [ ] Mantener consistencia con el estilo de código existente
- [ ] Usar las mismas variables CSS que ya están definidas
- [ ] Si agregas funcionalidades, actualizar CONTEXT.md y TODO.md

### Después de hacer cambios
- [ ] Probar en modo claro y oscuro
- [ ] Probar en móvil (responsive)
- [ ] Hacer commit con mensaje descriptivo
- [ ] Hacer push a GitHub

## 🚫 No Hagas Esto

1. **No cambies la arquitectura base** (Flask + Jinja2 + CSS vanilla)
2. **No agregues frameworks pesados** sin consultar (React, Vue, etc.)
3. **No elimines funcionalidades** marcadas como ✅ en CONTEXT.md
4. **No modifiques el comportamiento de organización de archivos** sin pruebas exhaustivas
5. **No uses imágenes externas** - todo debe ser texto/iconos o emojis

## ✅ Sí Puedes Hacer Esto

1. Arreglar bugs visuales
2. Mejorar el CSS (más limpio, no más complejo)
3. Agregar gráficas con Chart.js
4. Agregar secciones desplegables
5. Mejorar textos y documentación
6. Optimizar consultas/performance

## 🔍 Cómo Debuggear

### Si algo no se ve en la interfaz:
```python
# Agregar en app.py para ver qué datos llegan al template
print(f"Datos: {variable}")
```

### Si el modo oscuro no funciona:
- Verificar que `localStorage.getItem('tema')` esté en el script
- Verificar que las variables CSS `--color-*` estén definidas

### Si las gráficas no cargan:
- Abrir consola del navegador (F12)
- Verificar que Chart.js se cargó: `typeof Chart !== 'undefined'`
- Verificar que el canvas existe: `document.getElementById('chartId')`

## 📁 Estructura de Archivos Clave

```
app.py              → Rutas Flask, lógica principal
organizer.py        → Funciones de organización de archivos
duplicates.py       → Lógica de hash y detección de duplicados
reporter.py         → Generación de CSV

templates/
  index.html        → Formulario principal
  result.html       → Resultados tras organizar
  report.html       → Reporte detallado con gráficas

static/
  style.css         → Variables CSS, tema oscuro/claro
  script.js         → JavaScript de index.html
```

## 🎨 Guía de Estilos

### Colores
- Siempre usar variables CSS: `var(--color-primary)`
- Nunca hardcodear colores hex directamente

### Espaciado
- Usar variables: `var(--spacing)`, `var(--spacing-sm)`, etc.
- Unidades consistentes: rem para texto, px para bordes/radios

### Nomenclatura
- Clases CSS: kebab-case (ej: `.expandable-header`)
- Variables: camelCase en JS, snake_case en Python
- IDs: descriptivos y únicos (ej: `#duplicadosSection`)

## 🆘 ¿Necesitas Ayuda?

Si no entiendes algo:
1. Lee los comentarios en el código
2. Revisa CONTEXT.md para entender el contexto
3. Prueba la aplicación ejecutándola localmente
4. Pregunta al usuario por aclaraciones

---

**Recuerda**: Este es un proyecto académico. La prioridad es que funcione bien y sea fácil de entender, no que tenga la arquitectura más avanzada.
