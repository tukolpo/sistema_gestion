/**
 * validaciones.js
 * ─────────────────────────────────────────────────────────────────
 * Integrante 1 — Subtarea 1.2 & 1.3
 * Validaciones del lado del cliente (frontend) para:
 *   - Formulario de Login (campos obligatorios, email, contraseña)
 *   - Gestión de Usuarios (asignación de roles vía AJAX)
 *   - Manejo de estados de error visuales
 * ─────────────────────────────────────────────────────────────────
 */

"use strict";

/* ════════════════════════════════════════════════════
   UTILIDADES GLOBALES
   ════════════════════════════════════════════════════ */

/**
 * Muestra un mensaje de error debajo de un campo.
 * @param {HTMLElement} input   - El campo de formulario
 * @param {string}      mensaje - El texto del error
 */
function mostrarError(input, mensaje) {
  input.classList.remove("input-valido");
  input.classList.add("input-invalido");

  let errElem = input.parentElement.querySelector(".form-error-msg");
  if (!errElem) {
    errElem = document.createElement("span");
    errElem.className = "form-error-msg";
    input.parentElement.appendChild(errElem);
  }
  errElem.textContent = mensaje;
  errElem.classList.add("visible");

  // Accesibilidad: marcar el input con aria-invalid
  input.setAttribute("aria-invalid", "true");
  input.setAttribute("aria-describedby", errElem.id || "err-" + input.id);
}

/**
 * Limpia el estado de error de un campo.
 * @param {HTMLElement} input - El campo de formulario
 */
function limpiarError(input) {
  input.classList.remove("input-invalido");
  input.classList.add("input-valido");

  const errElem = input.parentElement.querySelector(".form-error-msg");
  if (errElem) errElem.classList.remove("visible");

  input.setAttribute("aria-invalid", "false");
}

/**
 * Regex para validar formato de correo electrónico.
 */
const REGEX_EMAIL = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

/**
 * Valida el formato de un correo electrónico.
 * @param {string} valor
 * @returns {boolean}
 */
function esEmailValido(valor) {
  return REGEX_EMAIL.test(valor.trim());
}

/* ════════════════════════════════════════════════════
   MÓDULO: ALERTAS VISUALES
   ════════════════════════════════════════════════════ */

/**
 * Cierra una alerta al hacer click en su botón "×".
 * Inicializa todos los botones de cierre de alertas.
 */
function inicializarAlertas() {
  document.querySelectorAll(".alerta-cerrar").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const alerta = btn.closest(".alerta");
      if (alerta) {
        alerta.style.opacity = "0";
        alerta.style.transform = "translateY(-4px)";
        alerta.style.transition = "all .25s ease";
        setTimeout(function () { alerta.remove(); }, 250);
      }
    });
  });

  // Auto-ocultar alertas de éxito/info después de 5 segundos
  document.querySelectorAll(".alerta-exito, .alerta-info").forEach(function (alerta) {
    setTimeout(function () {
      alerta.style.opacity = "0";
      alerta.style.transform = "translateY(-4px)";
      alerta.style.transition = "all .25s ease";
      setTimeout(function () { alerta.remove(); }, 250);
    }, 5000);
  });
}

/* ════════════════════════════════════════════════════
   MÓDULO: FORMULARIO DE LOGIN
   ════════════════════════════════════════════════════ */

function inicializarFormularioLogin() {
  const form      = document.getElementById("form-login");
  if (!form) return;

  const inputEmail = document.getElementById("id_email");
  const inputPass  = document.getElementById("id_password");
  const btnLogin   = document.getElementById("btn-login");

  // ─── Validación en tiempo real (al escribir) ──────────────

  if (inputEmail) {
    inputEmail.addEventListener("input", function () {
      validarEmail(inputEmail);
    });

    inputEmail.addEventListener("blur", function () {
      validarEmail(inputEmail);
    });
  }

  if (inputPass) {
    inputPass.addEventListener("input", function () {
      validarPassword(inputPass);
    });

    inputPass.addEventListener("blur", function () {
      validarPassword(inputPass);
    });
  }

  // ─── Validación al hacer submit ───────────────────────────

  form.addEventListener("submit", function (e) {
    const emailOk = validarEmail(inputEmail);
    const passOk  = validarPassword(inputPass);

    if (!emailOk || !passOk) {
      e.preventDefault(); // Bloquear envío si hay errores

      // Hacer foco en el primer campo con error
      if (!emailOk && inputEmail) inputEmail.focus();
      else if (!passOk && inputPass) inputPass.focus();
      return;
    }

    // ─── Subtarea 1.3: Indicador de carga en el botón ────────
    if (btnLogin) {
      btnLogin.classList.add("cargando");
      btnLogin.disabled = true;
    }
  });

  // ─── Funciones de validación individuales ────────────────

  function validarEmail(input) {
    if (!input) return false;
    const valor = input.value.trim();

    if (valor === "") {
      mostrarError(input, "El correo electrónico es obligatorio.");
      return false;
    }
    if (!esEmailValido(valor)) {
      mostrarError(input, "Ingresa un correo electrónico válido (ej: usuario@correo.com).");
      return false;
    }
    limpiarError(input);
    return true;
  }

  function validarPassword(input) {
    if (!input) return false;
    const valor = input.value;

    if (valor === "") {
      mostrarError(input, "La contraseña es obligatoria.");
      return false;
    }
    if (valor.length < 8) {
      mostrarError(input, "La contraseña debe tener al menos 8 caracteres.");
      return false;
    }
    limpiarError(input);
    return true;
  }
}

/* ════════════════════════════════════════════════════
   MÓDULO: GESTIÓN DE USUARIOS — ASIGNACIÓN DE ROL (AJAX)
   ════════════════════════════════════════════════════ */

function inicializarGestionUsuarios() {
  // Inicializar todos los botones "Guardar Rol"
  document.querySelectorAll(".btn-guardar-rol").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const usuarioId = btn.dataset.usuarioId;
      const select    = document.querySelector('.select-rol[data-usuario-id="' + usuarioId + '"]');

      if (!select) return;

      const rolId    = select.value;
      const csrfToken = obtenerCsrfToken();

      // Deshabilitar botón mientras procesa
      btn.disabled = true;
      btn.textContent = "...";

      fetch("/usuarios/" + usuarioId + "/asignar-rol/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body: "rol_id=" + encodeURIComponent(rolId),
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data.success) {
            mostrarToast(data.mensaje, "exito");

            // Actualizar badge del rol en la fila
            const fila  = btn.closest(".tabla-fila");
            if (fila) {
              const badge = fila.querySelector(".badge-rol");
              if (badge) {
                badge.textContent = data.rol_nombre;
                if (data.rol_nombre === "Sin Rol") {
                  badge.classList.add("badge-sin-rol");
                } else {
                  badge.classList.remove("badge-sin-rol");
                }
              }
            }
          } else {
            mostrarToast(data.error || "Error al asignar rol.", "error");
          }
        })
        .catch(function () {
          mostrarToast("Error de conexión. Intenta de nuevo.", "error");
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = "Guardar";
        });
    });
  });
}

/* ════════════════════════════════════════════════════
   MÓDULO: TOAST / NOTIFICACIONES AJAX
   ════════════════════════════════════════════════════ */

/**
 * Muestra una notificación temporal tipo "toast".
 * @param {string} mensaje - Texto a mostrar
 * @param {string} tipo    - 'exito' | 'error'
 */
function mostrarToast(mensaje, tipo) {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = "toast toast-" + tipo;

  const icono = tipo === "exito" ? "✓" : "✕";
  toast.innerHTML = '<span style="font-weight:700">' + icono + '</span> ' + mensaje;

  container.appendChild(toast);

  // Auto-eliminar después de 3.5 segundos
  setTimeout(function () {
    toast.classList.add("toast-salir");
    setTimeout(function () { toast.remove(); }, 300);
  }, 3500);
}

/* ════════════════════════════════════════════════════
   UTILIDAD: CSRF TOKEN
   ════════════════════════════════════════════════════ */

/**
 * Obtiene el CSRF Token desde las cookies de Django.
 * @returns {string}
 */
function obtenerCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : "";
}

/* ════════════════════════════════════════════════════
   INICIALIZACIÓN AL CARGAR LA PÁGINA
   ════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
  inicializarAlertas();
  inicializarFormularioLogin();
  inicializarGestionUsuarios();
});
