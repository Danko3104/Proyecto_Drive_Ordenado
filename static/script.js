/**
 * Drive Ordenado - Script de Frontend
 * Maneja la interacción del usuario y comunicación con el backend
 */

// Estado global
let intervaloEstado = null;
let procesoIniciado = false;

// Elementos del DOM
document.addEventListener('DOMContentLoaded', function() {
    inicializarEventos();
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
}

/**
 * Maneja el envío del formulario
 */
function manejarSubmit(e) {
    e.preventDefault();

    // Confirmación antes de iniciar
    if (!confirm('¿Estás seguro de que deseas organizar los archivos?\n\nEsta acción moverá los archivos a nuevas ubicaciones.')) {
        return;
    }

    iniciarOrganizacion();
}

/**
 * Valida que la ruta ingresada tenga formato correcto
 */
function validarRuta() {
    const input = document.getElementById('ruta_origen');
    const ruta = input.value.trim();

    if (!ruta) {
        return;
    }

    // Expansión de ~ a ruta home
    if (ruta.startsWith('~')) {
        input.value = ruta.replace('~', '/root');
    }

    // Verificar que parezca una ruta válida
    if (!ruta.startsWith('/') && !ruta.startsWith('~')) {
        mostrarAdvertencia(input, 'La ruta debe comenzar con / o ~');
    } else {
        limpiarAdvertencia(input);
    }
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
 * Inicia el proceso de organización
 */
async function iniciarOrganizacion() {
    if (procesoIniciado) {
        return;
    }

    procesoIniciado = true;

    // Obtener datos del formulario
    const formData = {
        ruta_origen: document.getElementById('ruta_origen').value.trim(),
        ruta_destino: document.getElementById('ruta_destino').value.trim(),
        criterio: document.getElementById('criterio').value,
        organizar_por_fecha: document.getElementById('organizar_por_fecha').checked,
        detectar_duplicados: document.getElementById('detectar_duplicados').checked
    };

    // Mostrar sección de progreso
    mostrarSeccion('progressSection');
    ocultarSeccion('resultSection');
    ocultarSeccion('errorSection');

    // Deshabilitar botón
    const btn = document.getElementById('btnOrganizar');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Procesando...';
    }

    try {
        // Enviar petición al servidor
        const respuesta = await fetch('/organizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
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
