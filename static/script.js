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
    const dupStatEl = document.getElementById('previewDupStat');
    const dupCountEl = document.getElementById('previewDupCount');

    if (totalEl) totalEl.textContent = preview.total_archivos;
    if (sizeEl) sizeEl.textContent = preview.tamaño_total_mb + ' MB';

    // Mostrar duplicados si hay
    if (preview.duplicados && preview.duplicados.cantidad > 0) {
        if (dupStatEl) dupStatEl.style.display = 'flex';
        if (dupCountEl) dupCountEl.textContent = preview.duplicados.cantidad;
    } else {
        if (dupStatEl) dupStatEl.style.display = 'none';
    }

    // Generar lista de categorías
    const categoriesContainer = document.getElementById('previewCategories');
    if (categoriesContainer) {
        categoriesContainer.innerHTML = '';

        const categorias = preview.categorias || {};

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

// Exportar funciones para uso global
window.resetForm = resetForm;
window.formatearBytes = formatearBytes;
window.formatearFecha = formatearFecha;
window.cancelarPreview = cancelarPreview;
window.confirmarOrganizacion = confirmarOrganizacion;
