/**
 * Drive Ordenado - Script de Frontend
 * Maneja la interacción del usuario y comunicación con el backend
 */

// Estado global
let intervaloEstado = null;
let procesoIniciado = false;
let previewData = null;
let formDataGuardado = null;

// Elementos del DOM
document.addEventListener('DOMContentLoaded', function() {
    inicializarEventos();
    inicializarTema();
});

/**
 * Inicializa todos los eventos de la aplicación
 */
function inicializarEventos() {
    const form = document.getElementById('organizeForm');

    if (form) {
        form.addEventListener('submit', manejarSubmit);
    }

    // Validación en tiempo real de la ruta
    const inputRuta = document.getElementById('ruta_origen');
    if (inputRuta) {
        inputRuta.addEventListener('blur', validarRuta);
    }

    // Botón de cambio de tema
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTema);
    }
}

/**
 * Inicializa el tema según preferencia guardada o del sistema
 */
function inicializarTema() {
    const temaGuardado = localStorage.getItem('tema');
    const themeToggle = document.getElementById('themeToggle');

    if (temaGuardado) {
        document.documentElement.setAttribute('data-theme', temaGuardado);
        actualizarIconoTema(themeToggle, temaGuardado);
    } else {
        // Detectar preferencia del sistema
        const prefiereOscuro = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const tema = prefiereOscuro ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', tema);
        actualizarIconoTema(themeToggle, tema);
    }
}

/**
 * Cambia entre tema claro y oscuro
 */
function toggleTema() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    const temaActual = html.getAttribute('data-theme');
    const nuevoTema = temaActual === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-theme', nuevoTema);
    localStorage.setItem('tema', nuevoTema);
    actualizarIconoTema(themeToggle, nuevoTema);
}

/**
 * Actualiza el icono del botón de tema
 */
function actualizarIconoTema(boton, tema) {
    if (boton) {
        boton.textContent = tema === 'dark' ? '☀️' : '🌙';
        boton.title = tema === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
    }
}

/**
 * Maneja el envío del formulario - ahora obtiene preview primero
 */
function manejarSubmit(e) {
    e.preventDefault();

    if (procesoIniciado) {
        return;
    }

    // Obtener datos del formulario
    formDataGuardado = {
        ruta_origen: document.getElementById('ruta_origen').value.trim(),
        ruta_destino: document.getElementById('ruta_destino').value.trim(),
        criterio: document.getElementById('criterio').value,
        organizar_por_fecha: document.getElementById('organizar_por_fecha').checked,
        organizar_por_extension: document.getElementById('organizar_por_extension').checked,
        detectar_duplicados: document.getElementById('detectar_duplicados').checked
    };

    // Si no se especifica ruta, usar MyDrive por defecto
    if (!formDataGuardado.ruta_origen) {
        formDataGuardado.ruta_origen = '/content/drive/MyDrive';
    }

    // Mostrar sección de progreso mientras se carga el preview
    mostrarSeccion('progressSection');
    ocultarSeccion('resultSection');
    ocultarSeccion('errorSection');
    ocultarSeccion('previewSection');

    const mensaje = document.getElementById('progressMessage');
    if (mensaje) {
        mensaje.textContent = 'Analizando archivos...';
    }

    // Obtener preview
    obtenerPreview();
}

/**
 * Obtiene el preview de la organización desde el servidor
 */
async function obtenerPreview() {
    try {
        const respuesta = await fetch('/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ruta_origen: formDataGuardado.ruta_origen,
                detectar_duplicados: formDataGuardado.detectar_duplicados
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || 'Error al obtener preview');
        }

        previewData = datos.preview;

        // Ocultar progreso y mostrar preview
        ocultarSeccion('progressSection');
        mostrarPreview(datos.preview);

    } catch (error) {
        mostrarError(error.message);
    }
}

/**
 * Muestra el preview en la interfaz
 */
function mostrarPreview(preview) {
    // Actualizar estadísticas principales
    const totalEl = document.getElementById('previewTotal');
    const sizeEl = document.getElementById('previewSize');
    const dupSectionEl = document.getElementById('previewDupSection');
    const dupCountEl = document.getElementById('previewDupCount');

    if (totalEl) totalEl.textContent = preview.total_archivos;
    if (sizeEl) sizeEl.textContent = preview.tamaño_total_mb + ' MB';

    // Mostrar sección de duplicados si hay
    if (preview.duplicados && preview.duplicados.cantidad > 0) {
        if (dupSectionEl) dupSectionEl.classList.remove('hidden');
        if (dupCountEl) dupCountEl.textContent = preview.duplicados.cantidad;
    } else {
        if (dupSectionEl) dupSectionEl.classList.add('hidden');
    }

    // Generar lista de categorías
    const categoriesContainer = document.getElementById('previewCategories');
    if (categoriesContainer) {
        categoriesContainer.innerHTML = '';

        const categorias = preview.categorias || {};
        const porExtension = preview.por_extension || {};

        // Renderizar categorías
        for (const [categoria, datos] of Object.entries(categorias)) {
            const catCard = document.createElement('div');
            catCard.className = 'preview-category-card';

            const icono = obtenerIconoCategoria(categoria);
            const tamañoMB = (datos.tamaño_bytes / (1024 * 1024)).toFixed(2);

            catCard.innerHTML = `
                <div class="preview-category-header">
                    <span class="preview-category-icon">${icono}</span>
                    <span class="preview-category-name">${capitalizar(categoria)}</span>
                </div>
                <div class="preview-category-stats">
                    <span class="preview-category-count">${datos.cantidad} archivos</span>
                    <span class="preview-category-size">${tamañoMB} MB</span>
                </div>
            `;

            categoriesContainer.appendChild(catCard);
        }

        // Renderizar extensiones si hay
        if (Object.keys(porExtension).length > 0) {
            const extContainer = document.createElement('div');
            extContainer.className = 'preview-extensions-container';
            extContainer.innerHTML = `
                <h4 class="preview-section-title">📎 Extensiones Encontradas</h4>
                <div class="preview-extensions-grid" id="previewExtensions"></div>
            `;
            categoriesContainer.appendChild(extContainer);

            const extensionsGrid = extContainer.querySelector('#previewExtensions');

            // Ordenar extensiones por cantidad (mayor a menor)
            const extensionesOrdenadas = Object.entries(porExtension)
                .sort((a, b) => b[1].cantidad - a[1].cantidad);

            for (const [ext, datos] of extensionesOrdenadas) {
                const extBadge = document.createElement('div');
                extBadge.className = 'preview-extension-badge';
                extBadge.innerHTML = `
                    <span class="extension-name">${ext}</span>
                    <span class="extension-count">${datos.cantidad}</span>
                `;
                extensionsGrid.appendChild(extBadge);
            }
        }
    }

    // Mostrar sección de preview
    mostrarSeccion('previewSection');
}

/**
 * Obtiene el icono correspondiente a una categoría
 */
function obtenerIconoCategoria(categoria) {
    const iconos = {
        'documentos': '📄',
        'imagenes': '🖼️',
        'multimedia': '🎬',
        'otros': '📦'
    };
    return iconos[categoria.toLowerCase()] || '📁';
}

/**
 * Capitaliza la primera letra de un string
 */
function capitalizar(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Cancela el preview y vuelve al formulario
 */
function cancelarPreview() {
    ocultarSeccion('previewSection');
    previewData = null;
    formDataGuardado = null;
}

/**
 * Confirma la organización y la ejecuta
 */
function confirmarOrganizacion() {
    // Ocultar preview
    ocultarSeccion('previewSection');

    // Mostrar progreso
    mostrarSeccion('progressSection');

    // Iniciar organización
    iniciarOrganizacion();
}

/**
 * Inicia el proceso de organización
 */
async function iniciarOrganizacion() {
    if (procesoIniciado) {
        return;
    }

    procesoIniciado = true;

    // Deshabilitar botón
    const btn = document.getElementById('btnOrganizar');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Procesando...';
    }

    try {
        // Agregar flag de confirmado
        const dataToSend = {
            ...formDataGuardado,
            confirmado: true
        };

        // Enviar petición al servidor
        const respuesta = await fetch('/organizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSend)
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || 'Error al iniciar el proceso');
        }

        // Iniciar polling del estado
        iniciarPollingEstado();

    } catch (error) {
        mostrarError(error.message);
        procesoIniciado = false;

        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🚀</span> Organizar Archivos';
        }
    }
}

/**
 * Valida que la ruta ingresada tenga formato correcto
 * y detecta rutas peligrosas (todo el Drive)
 */
function validarRuta() {
    const input = document.getElementById('ruta_origen');
    const ruta = input.value.trim();
    const securityWarning = document.getElementById('securityWarning');

    if (!ruta) {
        if (securityWarning) securityWarning.classList.add('hidden');
        return;
    }

    // Expansión de ~ a ruta home
    if (ruta.startsWith('~')) {
        input.value = ruta.replace('~', '/root');
    }

    // Verificar que parezca una ruta válida
    if (!ruta.startsWith('/') && !ruta.startsWith('~')) {
        mostrarAdvertencia(input, 'La ruta debe comenzar con / o ~');
        if (securityWarning) securityWarning.classList.add('hidden');
    } else {
        limpiarAdvertencia(input);
    }

    // Detectar rutas peligrosas (todo el Drive o carpetas raíz sensibles)
    if (esRutaPeligrosa(ruta)) {
        if (securityWarning) {
            securityWarning.classList.remove('hidden');
        }
    } else {
        if (securityWarning) {
            securityWarning.classList.add('hidden');
        }
    }
}

/**
 * Detecta si una ruta es peligrosa (todo el Drive o carpetas sensibles)
 */
function esRutaPeligrosa(ruta) {
    // Normalizar la ruta (quitar trailing slash)
    const rutaNormalizada = ruta.replace(/\/$/, '');

    // Patrones de rutas peligrosas
    const patronesPeligrosos = [
        /^\/content\/drive\/?$/i,                           // /content/drive
        /^\/content\/drive\/MyDrive\/?$/i,                  // /content/drive/MyDrive
        /^\/content\/drive\/Shareddrives\/?$/i,             // /content/drive/Shareddrives
        /^\/content\/drive\/.*\/(Google\s*Drive|Mi\s*unidad)\/?$/i,  // Carpetas raíz con otros nombres
        /^~\/drive\/?$/i,                                   // ~/drive
        /^~\/GoogleDrive\/?$/i,                             // ~/GoogleDrive
    ];

    // Verificar si coincide con algún patrón peligroso
    for (const patron of patronesPeligrosos) {
        if (patron.test(rutaNormalizada)) {
            return true;
        }
    }

    // Detectar rutas que parecen ser la raíz del Drive sin subcarpeta específica
    // Ejemplo: /content/drive/MyDrive/ (termina en MyDrive/)
    if (rutaNormalizada.match(/\/content\/drive\/[^\/]+\/?$/i)) {
        return true;
    }

    return false;
}

/**
 * Muestra una advertencia debajo de un campo
 */
function mostrarAdvertencia(elemento, mensaje) {
    limpiarAdvertencia(elemento);

    const advertencia = document.createElement('span');
    advertencia.className = 'help-text error-text';
    advertencia.style.color = 'var(--color-error)';
    advertencia.textContent = mensaje;

    elemento.parentNode.appendChild(advertencia);
}

/**
 * Limpia las advertencias de un campo
 */
function limpiarAdvertencia(elemento) {
    const grupo = elemento.parentNode;
    const advertencias = grupo.querySelectorAll('.error-text');
    advertencias.forEach(adv => adv.remove());
}

/**
 * Inicia el polling para consultar el estado del proceso
 */
function iniciarPollingEstado() {
    // Consultar estado cada 1 segundo
    intervaloEstado = setInterval(consultarEstado, 1000);
}

/**
 * Consulta el estado actual del proceso
 */
async function consultarEstado() {
    try {
        const respuesta = await fetch('/estado');
        const estado = await respuesta.json();

        // Actualizar UI
        actualizarProgreso(estado);

        // Verificar si el proceso terminó
        if (!estado.en_progreso) {
            clearInterval(intervaloEstado);

            if (estado.error) {
                mostrarError(estado.error);
            } else if (estado.resultado) {
                mostrarResultado();
            }

            procesoIniciado = false;
        }

    } catch (error) {
        console.error('Error consultando estado:', error);
    }
}

/**
 * Actualiza la barra de progreso y mensajes
 */
function actualizarProgreso(estado) {
    const fill = document.getElementById('progressFill');
    const porcentaje = document.getElementById('progressPercentage');
    const mensaje = document.getElementById('progressMessage');
    const status = document.getElementById('progressStatus');

    if (fill) {
        fill.style.width = estado.progreso + '%';
    }

    if (porcentaje) {
        porcentaje.textContent = estado.progreso + '%';
    }

    if (mensaje) {
        mensaje.textContent = estado.mensaje;
    }

    if (status) {
        status.textContent = estado.en_progreso ? 'Procesando...' : 'Completado';
    }
}

/**
 * Muestra la sección de resultados exitosos
 */
function mostrarResultado() {
    ocultarSeccion('progressSection');
    mostrarSeccion('resultSection');

    const btn = document.getElementById('btnOrganizar');
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🚀</span> Organizar Archivos';
    }

    // Redirigir automáticamente a resultados después de 3 segundos
    setTimeout(() => {
        window.location.href = '/resultados';
    }, 3000);
}

/**
 * Muestra un mensaje de error
 */
function mostrarError(mensaje) {
    ocultarSeccion('progressSection');
    ocultarSeccion('previewSection');
    mostrarSeccion('errorSection');

    const errorMsg = document.getElementById('errorMessage');
    if (errorMsg) {
        errorMsg.textContent = mensaje;
    }

    const btn = document.getElementById('btnOrganizar');
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🚀</span> Organizar Archivos';
    }
}

/**
 * Resetea el formulario para un nuevo intento
 */
function resetForm() {
    ocultarSeccion('errorSection');
    ocultarSeccion('resultSection');
    ocultarSeccion('progressSection');
    ocultarSeccion('previewSection');

    previewData = null;
    formDataGuardado = null;

    const btn = document.getElementById('btnOrganizar');
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🚀</span> Organizar Archivos';
    }
}

/**
 * Muestra una sección del DOM
 */
function mostrarSeccion(id) {
    const seccion = document.getElementById(id);
    if (seccion) {
        seccion.classList.remove('hidden');
    }
}

/**
 * Oculta una sección del DOM
 */
function ocultarSeccion(id) {
    const seccion = document.getElementById(id);
    if (seccion) {
        seccion.classList.add('hidden');
    }
}

/**
 * Formatea bytes a unidades legibles
 */
function formatearBytes(bytes) {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Formatea una fecha
 */
function formatearFecha(fechaStr) {
    const fecha = new Date(fechaStr);

    return fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================
// BUSCADOR DE ARCHIVOS
// ============================================
let searchOrdenColumna = -1;
let searchOrdenAsc = true;

function toggleSearchSection() {
    const section = document.getElementById('searchSection');
    if (section) section.classList.toggle('hidden');
}

async function buscarArchivos() {
    const ruta = document.getElementById('searchRuta').value.trim() || '/content/drive/MyDrive';
    const nombre = document.getElementById('searchNombre').value.trim();
    const extension = document.getElementById('searchExtension').value.trim();
    const categoria = document.getElementById('searchCategoria').value;
    const tamañoMin = document.getElementById('searchSizeMin').value;
    const tamañoMax = document.getElementById('searchSizeMax').value;

    try {
        const resp = await fetch('/buscar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ruta, nombre, extension, categoria,
                tamaño_min_mb: tamañoMin || null,
                tamaño_max_mb: tamañoMax || null
            })
        });
        const data = await resp.json();

        if (!resp.ok) { alert('Error: ' + data.error); return; }

        const resultsDiv = document.getElementById('searchResults');
        const count = document.getElementById('searchCount');
        const tbody = document.getElementById('searchTableBody');

        count.textContent = data.mensaje;
        tbody.innerHTML = '';

        data.archivos.forEach(a => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td title="${a.ruta}">${a.nombre}</td>
                <td>${capitalizar(a.categoria)}</td>
                <td>${a.extension}</td>
                <td>${a.tamaño_mb} MB</td>
                <td>${a.fecha_modificacion}</td>
            `;
            tbody.appendChild(tr);
        });

        resultsDiv.classList.remove('hidden');
        searchOrdenColumna = -1;
        searchOrdenAsc = true;
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

function ordenarTablaBusqueda(columna) {
    const tbody = document.getElementById('searchTableBody');
    const filas = Array.from(tbody.querySelectorAll('tr'));

    if (searchOrdenColumna === columna) {
        searchOrdenAsc = !searchOrdenAsc;
    } else {
        searchOrdenColumna = columna;
        searchOrdenAsc = true;
    }

    filas.sort((a, b) => {
        const valA = a.children[columna].textContent.trim();
        const valB = b.children[columna].textContent.trim();
        const numA = parseFloat(valA);
        const numB = parseFloat(valB);
        if (!isNaN(numA) && !isNaN(numB)) {
            return searchOrdenAsc ? numA - numB : numB - numA;
        }
        return searchOrdenAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
    });

    filas.forEach(f => tbody.appendChild(f));
}

// ============================================
// SUBIDA DE ARCHIVOS
// ============================================
let uploadArchivos = [];

function toggleUploadSection() {
    const section = document.getElementById('uploadSection');
    if (section) section.classList.toggle('hidden');
}

function manejarDrop(event) {
    const archivos = Array.from(event.dataTransfer.files);
    prepararSubida(archivos);
}

function manejarSeleccionArchivos(event) {
    const archivos = Array.from(event.target.files);
    prepararSubida(archivos);
    event.target.value = '';
}

function prepararSubida(archivos) {
    uploadArchivos = archivos;
    const lista = document.getElementById('uploadItems');
    const count = document.getElementById('uploadCount');
    const divLista = document.getElementById('uploadLista');

    if (archivos.length === 0) {
        divLista.classList.add('hidden');
        return;
    }

    count.textContent = `${archivos.length} archivo(s) seleccionados`;
    lista.innerHTML = '';
    let totalSize = 0;

    archivos.forEach((f, i) => {
        totalSize += f.size;
        const item = document.createElement('div');
        item.style.cssText = 'display:flex; justify-content:space-between; padding:var(--spacing-xs) var(--spacing); border-bottom:1px solid var(--color-border); font-size:0.9rem;';
        item.innerHTML = `<span>${i + 1}. ${f.name}</span><span style="color:var(--color-text-light);">${formatearBytes(f.size)}</span>`;
        lista.appendChild(item);
    });

    const totalItem = document.createElement('div');
    totalItem.style.cssText = 'display:flex; justify-content:space-between; padding:var(--spacing-xs) var(--spacing); font-weight:600; font-size:0.9rem;';
    totalItem.innerHTML = `<span>Total:</span><span>${formatearBytes(totalSize)}</span>`;
    lista.appendChild(totalItem);

    divLista.classList.remove('hidden');
}

async function subirArchivos() {
    if (uploadArchivos.length === 0) {
        alert('Selecciona archivos primero');
        return;
    }

    const ruta = document.getElementById('uploadRuta').value.trim() || '/content/drive/MyDrive';
    const organizar = document.getElementById('organizarAuto').checked;

    document.getElementById('uploadProgress').classList.remove('hidden');
    document.getElementById('uploadResult').classList.add('hidden');

    const fill = document.getElementById('uploadProgressFill');
    const pct = document.getElementById('uploadProgressPct');
    const msg = document.getElementById('uploadProgressMsg');

    const formData = new FormData();
    uploadArchivos.forEach(f => formData.append('archivos', f));
    formData.append('ruta_destino', ruta);
    formData.append('organizar_despues', organizar ? 'true' : 'false');

    try {
        pct.textContent = '50%';
        fill.style.width = '50%';
        msg.textContent = 'Subiendo archivos...';

        const resp = await fetch('/subir', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();

        fill.style.width = '100%';
        pct.textContent = '100%';

        const resultDiv = document.getElementById('uploadResult');
        const resultMsg = document.getElementById('uploadResultMsg');

        if (!resp.ok) {
            resultMsg.style.color = 'var(--color-error)';
            resultMsg.textContent = 'Error: ' + data.error;
        } else {
            let texto = `✅ ${data.subidos} archivo(s) subidos exitosamente`;
            if (data.fallidos > 0) texto += `, ${data.fallidos} fallaron`;
            if (data.organizado) texto += ` y ${data.archivos_organizados} organizados automáticamente`;
            resultMsg.style.color = 'var(--color-success)';
            resultMsg.textContent = texto;
        }

        resultDiv.classList.remove('hidden');
        uploadArchivos = [];
        document.getElementById('uploadLista').classList.add('hidden');

    } catch (e) {
        msg.textContent = 'Error: ' + e.message;
    }
}

// ============================================
// CATEGORÍAS PERSONALIZADAS
// ============================================
let categoriasEditables = {};

function toggleCategoriasSection() {
    const s = document.getElementById('categoriasSection');
    if (s) {
        s.classList.toggle('hidden');
        if (!s.classList.contains('hidden')) cargarCategoriasEdit();
    }
}

async function cargarCategoriasEdit() {
    try {
        const resp = await fetch('/categorias');
        categoriasEditables = await resp.json();
        renderizarCategoriasEdit();
    } catch (e) { console.error(e); }
}

function renderizarCategoriasEdit() {
    const container = document.getElementById('categoriasLista');
    container.innerHTML = '';
    for (const [cat, exts] of Object.entries(categoriasEditables)) {
        if (cat === 'otros') continue;
        const div = document.createElement('div');
        div.style.cssText = 'background:var(--color-bg); border:1px solid var(--color-border); border-radius:var(--radius); padding:var(--spacing); margin-bottom:var(--spacing-sm);';
        div.innerHTML = `
            <div style="display:flex; align-items:center; gap:var(--spacing-sm); margin-bottom:var(--spacing-sm);">
                <input type="text" value="${cat}" class="cat-nombre" style="flex:1; font-weight:600; padding:var(--spacing-xs) var(--spacing-sm); border:2px solid var(--color-border); border-radius:var(--radius-sm); background:var(--color-input-bg); color:var(--color-text);">
                <button class="btn btn-outline" onclick="this.closest('div').parentElement.remove()" style="padding:var(--spacing-xs) var(--spacing-sm); font-size:0.85rem;">✕</button>
            </div>
            <div class="cat-extensiones" style="display:flex; flex-wrap:wrap; gap:var(--spacing-xs);">
                ${exts.map(e => `
                    <span style="display:inline-flex; align-items:center; gap:4px; background:var(--color-card); border:1px solid var(--color-border); border-radius:var(--radius-sm); padding:2px 8px; font-size:0.85rem; font-family:monospace;">
                        ${e}
                        <span style="cursor:pointer; color:var(--color-error);" onclick="this.parentElement.remove()">✕</span>
                    </span>
                `).join('')}
                <button class="btn btn-outline" onclick="agregarExtension(this)" style="padding:2px 8px; font-size:0.85rem;">+</button>
            </div>
        `;
        container.appendChild(div);
    }
}

function agregarExtension(btn) {
    const ext = prompt('Ingresa la extensión (ej: .json):');
    if (!ext) return;
    const extFormateada = ext.startsWith('.') ? ext.toLowerCase() : '.' + ext.toLowerCase();
    const span = document.createElement('span');
    span.style.cssText = 'display:inline-flex; align-items:center; gap:4px; background:var(--color-card); border:1px solid var(--color-border); border-radius:var(--radius-sm); padding:2px 8px; font-size:0.85rem; font-family:monospace;';
    span.innerHTML = `${extFormateada} <span style="cursor:pointer;color:var(--color-error);" onclick="this.parentElement.remove()">✕</span>`;
    btn.parentElement.insertBefore(span, btn);
}

function agregarCategoriaVacia() {
    const container = document.getElementById('categoriasLista');
    const div = document.createElement('div');
    div.style.cssText = 'background:var(--color-bg); border:1px solid var(--color-border); border-radius:var(--radius); padding:var(--spacing); margin-bottom:var(--spacing-sm);';
    div.innerHTML = `
        <div style="display:flex; align-items:center; gap:var(--spacing-sm); margin-bottom:var(--spacing-sm);">
            <input type="text" value="nueva_categoria" class="cat-nombre" style="flex:1; font-weight:600; padding:var(--spacing-xs) var(--spacing-sm); border:2px solid var(--color-border); border-radius:var(--radius-sm); background:var(--color-input-bg); color:var(--color-text);">
            <button class="btn btn-outline" onclick="this.closest('div').parentElement.remove()" style="padding:var(--spacing-xs) var(--spacing-sm); font-size:0.85rem;">✕</button>
        </div>
        <div class="cat-extensiones" style="display:flex; flex-wrap:wrap; gap:var(--spacing-xs);">
            <button class="btn btn-outline" onclick="agregarExtension(this)" style="padding:2px 8px; font-size:0.85rem;">+ Extensión</button>
        </div>
    `;
    container.appendChild(div);
}

async function guardarCategorias() {
    const categorias = {};
    const divs = document.querySelectorAll('#categoriasLista > div');
    divs.forEach(div => {
        const nombreInput = div.querySelector('.cat-nombre');
        const nombre = nombreInput.value.trim().toLowerCase();
        if (!nombre) return;
        const exts = [];
        div.querySelectorAll('.cat-extensiones > span').forEach(span => {
            const txt = span.textContent.replace('✕', '').trim();
            if (txt) exts.push(txt);
        });
        categorias[nombre] = exts;
    });
    categorias['otros'] = [];

    try {
        const resp = await fetch('/categorias', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(categorias)
        });
        const data = await resp.json();
        const msg = document.getElementById('categoriasMsg');
        if (data.success) {
            msg.textContent = '✅ Categorías guardadas exitosamente';
            msg.style.color = 'var(--color-success)';
            categoriasEditables = data.categorias;
        } else {
            msg.textContent = '❌ ' + (data.error || 'Error al guardar');
            msg.style.color = 'var(--color-error)';
        }
        msg.classList.remove('hidden');
        setTimeout(() => msg.classList.add('hidden'), 3000);
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

async function resetearCategorias() {
    if (!confirm('¿Restaurar categorías por defecto? Se perderán los cambios.')) return;
    try {
        const resp = await fetch('/categorias/reset', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            categoriasEditables = data.categorias;
            renderizarCategoriasEdit();
            const msg = document.getElementById('categoriasMsg');
            msg.textContent = '✅ Categorías restauradas a valores por defecto';
            msg.style.color = 'var(--color-success)';
            msg.classList.remove('hidden');
            setTimeout(() => msg.classList.add('hidden'), 3000);
        }
    } catch (e) { alert('Error: ' + e.message); }
}

// ============================================
// ANÁLISIS DE CARPETA
// ============================================
function toggleAnalisisSection() {
    const section = document.getElementById('analisisSection');
    if (section) section.classList.toggle('hidden');
}

async function analizarCarpeta() {
    const ruta = document.getElementById('analisisRuta').value.trim() || '/content/drive/MyDrive';

    document.getElementById('analisisProgress').classList.remove('hidden');
    document.getElementById('analisisResultados').classList.add('hidden');

    try {
        const resp = await fetch('/analizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ruta })
        });
        const data = await resp.json();

        document.getElementById('analisisProgress').classList.add('hidden');

        if (!resp.ok) { alert('Error: ' + data.error); return; }

        // Cards de resumen
        const cards = document.getElementById('analisisCards');
        cards.innerHTML = `
            <div class="stat-card stat-primary"><div class="stat-icon">📄</div><div class="stat-value">${data.total_archivos}</div><div class="stat-label">Archivos totales</div></div>
            <div class="stat-card stat-info"><div class="stat-icon">💾</div><div class="stat-value">${data.tamaño_total_mb}</div><div class="stat-label">MB totales</div></div>
            <div class="stat-card stat-success"><div class="stat-icon">📂</div><div class="stat-value">${Object.keys(data.por_categoria).length}</div><div class="stat-label">Categorías</div></div>
            <div class="stat-card stat-warning"><div class="stat-icon">⚠️</div><div class="stat-value">${data.archivos_vacios}</div><div class="stat-label">Archivos vacíos</div></div>
        `;

        // Categorías con barra de progreso
        let catHtml = '<h4 class="section-title" style="margin-bottom:var(--spacing-sm);">📁 Distribución por categoría</h4>';
        for (const [cat, d] of Object.entries(data.por_categoria)) {
            const pct = data.total_archivos > 0 ? (d.cantidad / data.total_archivos * 100).toFixed(1) : 0;
            catHtml += `
                <div style="margin-bottom:var(--spacing-sm);">
                    <div style="display:flex; justify-content:space-between; font-size:0.9rem; margin-bottom:4px;">
                        <span>${capitalizar(cat)}</span>
                        <span>${d.cantidad} archivos (${d.tamaño_mb} MB / ${pct}%)</span>
                    </div>
                    <div style="height:8px; background:var(--color-border); border-radius:4px; overflow:hidden;">
                        <div style="height:100%; width:${pct}%; background:var(--color-primary); border-radius:4px;"></div>
                    </div>
                </div>
            `;
        }

        // Top 10
        const topBody = document.getElementById('analisisTopBody');
        topBody.innerHTML = '';
        data.top_10_pesados.forEach((a, i) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${i + 1}</td><td title="${a.ruta}">${a.nombre}</td><td>${a.tamaño_mb} MB</td><td>${capitalizar(a.categoria)}</td>`;
            topBody.appendChild(tr);
        });

        // Datos curiosos
        const datosDiv = document.getElementById('analisisDatos');
        let datosHtml = '<h4 class="section-title">📎 Datos adicionales</h4><div class="info-grid">';
        datosHtml += `
            <div class="info-item"><span class="info-label">📅 Archivo más antiguo:</span><span class="info-value">${data.archivo_mas_viejo ? data.archivo_mas_viejo.nombre + ' (' + data.archivo_mas_viejo.fecha + ')' : 'N/A'}</span></div>
            <div class="info-item"><span class="info-label">🆕 Archivo más reciente:</span><span class="info-value">${data.archivo_mas_nuevo ? data.archivo_mas_nuevo.nombre + ' (' + data.archivo_mas_nuevo.fecha + ')' : 'N/A'}</span></div>
            <div class="info-item"><span class="info-label">📎 Extensiones distintas:</span><span class="info-value">${Object.keys(data.por_extension).length}</span></div>
        `;
        datosHtml += '</div>';
        datosDiv.innerHTML = catHtml + datosHtml;

        document.getElementById('analisisResultados').classList.remove('hidden');
    } catch (e) {
        document.getElementById('analisisProgress').classList.add('hidden');
        alert('Error: ' + e.message);
    }
}

// Exportar funciones para uso global
window.resetForm = resetForm;
window.formatearBytes = formatearBytes;
window.formatearFecha = formatearFecha;
window.cancelarPreview = cancelarPreview;
window.confirmarOrganizacion = confirmarOrganizacion;
window.toggleSearchSection = toggleSearchSection;
window.buscarArchivos = buscarArchivos;
window.ordenarTablaBusqueda = ordenarTablaBusqueda;
window.toggleUploadSection = toggleUploadSection;
window.manejarDrop = manejarDrop;
window.manejarSeleccionArchivos = manejarSeleccionArchivos;
window.subirArchivos = subirArchivos;
window.toggleAnalisisSection = toggleAnalisisSection;
window.analizarCarpeta = analizarCarpeta;
window.toggleCategoriasSection = toggleCategoriasSection;
window.agregarCategoriaVacia = agregarCategoriaVacia;
window.guardarCategorias = guardarCategorias;
window.resetearCategorias = resetearCategorias;
window.agregarExtension = agregarExtension;
