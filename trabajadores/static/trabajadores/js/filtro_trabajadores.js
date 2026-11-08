/**
 * filtro_trabajadores.js
 * Módulo 3 — Tarea 1: filtros dinámicos y actualización en tiempo real.
 */
"use strict";

(function () {
  var DEBOUNCE_MS = 350;
  var debounceTimer = null;

  function obtenerElementos() {
    return {
      form: document.getElementById("form-filtros-trabajadores"),
      cargo: document.getElementById("filtro-cargo"),
      estatus: document.getElementById("filtro-estatus"),
      antiguedad: document.getElementById("filtro-antiguedad"),
      btnLimpiar: document.getElementById("btn-limpiar-filtros"),
      tbody: document.getElementById("tabla-trabajadores-body"),
      sinResultados: document.getElementById("mensaje-sin-resultados"),
      contenedor: document.getElementById("contenedor-tabla-trabajadores"),
      statsContenedor: document.getElementById("stats-trabajadores"),
      statTotal: document.getElementById("stat-total"),
      statActivos: document.getElementById("stat-activos"),
      statInactivos: document.getElementById("stat-inactivos"),
    };
  }

  function hayFiltrosActivos(els) {
    return (
      (els.cargo && els.cargo.value) ||
      (els.estatus && els.estatus.value) ||
      (els.antiguedad && els.antiguedad.value.trim() !== "")
    );
  }

  function construirParametros(els) {
    var params = new URLSearchParams();
    if (els.cargo && els.cargo.value) {
      params.set("cargo", els.cargo.value);
    }
    if (els.estatus && els.estatus.value) {
      params.set("estatus", els.estatus.value);
    }
    if (els.antiguedad && els.antiguedad.value.trim() !== "") {
      params.set("antiguedad", els.antiguedad.value.trim());
    }
    return params;
  }

  function urlDetalle(id) {
    return window.TRABAJADORES_URLS.detalle.replace("{id}", id);
  }

  function urlEditar(id) {
    return window.TRABAJADORES_URLS.editar.replace("{id}", id);
  }

  function urlEstado(id) {
    return window.TRABAJADORES_URLS.estado.replace("{id}", id);
  }

  function urlEliminar(id) {
    return window.TRABAJADORES_URLS.eliminar.replace("{id}", id);
  }

  function escaparHtml(texto) {
    var div = document.createElement("div");
    div.textContent = texto == null ? "" : String(texto);
    return div.innerHTML;
  }

  function renderizarFila(trabajador) {
    var nombreCompleto = escaparHtml(trabajador.nombre) + " " + escaparHtml(trabajador.apellido);
    var inicial = escaparHtml((trabajador.nombre || "?").charAt(0).toUpperCase());
    var badgeClase = trabajador.esta_activo ? "badge-estado badge-estado-activo" : "badge-estado badge-estado-inactivo";
    var btnAccionClase = trabajador.esta_activo ? "btn-fila btn-fila-desactivar" : "btn-fila btn-fila-activar";
    var btnAccionIcono = trabajador.esta_activo ? "fa-user-slash" : "fa-user-check";
    var btnTexto = trabajador.esta_activo ? "Desactivar" : "Activar";
    var antiguedad = escaparHtml(
      trabajador.antiguedad_texto ||
        (trabajador.antiguedad != null ? trabajador.antiguedad + " año(s)" : "—")
    );
    var btnEliminar = window.TRABAJADORES_URLS.puede_eliminar
      ? '<button type="button" class="btn-fila btn-fila-eliminar" data-id="' +
        trabajador.id +
        '" data-nombre="' +
        nombreCompleto +
        '" data-cedula="' +
        escaparHtml(trabajador.cedula) +
        '"><i class="fas fa-trash"></i> Eliminar</button>'
      : "";

    return (
      '<div class="tabla-fila" role="row" data-trabajador-id="' +
      trabajador.id +
      '">' +
      '<div class="celda-usuario">' +
      '<div class="avatar-mini">' +
      inicial +
      "</div>" +
      '<a href="' +
      urlDetalle(trabajador.id) +
      '" class="celda-nombre">' +
      nombreCompleto +
      "</a>" +
      "</div>" +
      '<div><span class="celda-email">' +
      escaparHtml(trabajador.cedula) +
      "</span></div>" +
      '<div><span class="celda-email">' +
      escaparHtml(trabajador.cargo_nombre) +
      "</span></div>" +
      '<div><span class="celda-email">' +
      antiguedad +
      "</span></div>" +
      '<div><span class="' +
      badgeClase +
      '">' +
      escaparHtml(trabajador.estado_display || trabajador.estado) +
      "</span></div>" +
      '<div class="acciones-fila">' +
      '<a href="' +
      urlDetalle(trabajador.id) +
      '" class="btn-fila btn-fila-perfil"><i class="fas fa-id-badge"></i> Perfil</a>' +
      '<a href="' +
      urlEditar(trabajador.id) +
      '" class="btn-fila btn-fila-editar"><i class="fas fa-pen"></i> Editar</a>' +
      '<form method="post" action="' +
      urlEstado(trabajador.id) +
      '" style="display:inline;">' +
      '<input type="hidden" name="csrfmiddlewaretoken" value="' +
      escaparHtml(window.TRABAJADORES_URLS.csrf) +
      '">' +
      '<button type="submit" class="' +
      btnAccionClase +
      '"><i class="fas ' +
      btnAccionIcono +
      '"></i> ' +
      btnTexto +
      "</button>" +
      "</form>" +
      btnEliminar +
      "</div>" +
      "</div>"
    );
  }

  function actualizarEstadisticas(els, trabajadores) {
    if (!els.statsContenedor) {
      return;
    }

    var lista = Array.isArray(trabajadores) ? trabajadores : [];
    var total = lista.length;
    var activos = lista.filter(function (t) {
      return t.esta_activo;
    }).length;
    var inactivos = total - activos;

    if (els.statTotal) els.statTotal.textContent = total;
    if (els.statActivos) els.statActivos.textContent = activos;
    if (els.statInactivos) els.statInactivos.textContent = inactivos;

    els.statsContenedor.hidden = false;
  }

  function mostrarCargando(els) {
    els.contenedor.setAttribute("aria-busy", "true");
    els.tbody.innerHTML =
      '<div class="tabla-vacia" id="estado-cargando-trabajadores"><p>Cargando trabajadores...</p></div>';
    els.sinResultados.hidden = true;
  }

  function mostrarError(els, mensaje) {
    els.contenedor.setAttribute("aria-busy", "false");
    els.tbody.innerHTML = "";
    els.sinResultados.hidden = false;
    els.sinResultados.querySelector("p").textContent = mensaje;
    if (els.statsContenedor) {
      els.statsContenedor.hidden = true;
    }
  }

  function renderizarResultados(els, trabajadores) {
    els.contenedor.setAttribute("aria-busy", "false");

    if (!Array.isArray(trabajadores) || trabajadores.length === 0) {
      els.tbody.innerHTML = "";
      els.sinResultados.hidden = false;
      els.sinResultados.querySelector("p").textContent = "No se encontraron resultados";
      actualizarEstadisticas(els, []);
      return;
    }

    els.sinResultados.hidden = true;
    els.tbody.innerHTML = trabajadores.map(renderizarFila).join("");
    actualizarEstadisticas(els, trabajadores);
  }

  function buscarTrabajadores(els) {
    var params = construirParametros(els);
    var url = window.TRABAJADORES_URLS.api;
    if (params.toString()) {
      url += "?" + params.toString();
    }

    if (els.btnLimpiar) {
      els.btnLimpiar.style.display = hayFiltrosActivos(els) ? "inline-flex" : "none";
    }

    mostrarCargando(els);

    fetch(url, {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    })
      .then(function (res) {
        if (!res.ok) {
          throw new Error("Error al obtener trabajadores.");
        }
        return res.json();
      })
      .then(function (data) {
        renderizarResultados(els, data);
      })
      .catch(function () {
        mostrarError(els, "No se pudo cargar la lista. Intenta de nuevo.");
      });
  }

  function programarBusqueda(els) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      buscarTrabajadores(els);
    }, DEBOUNCE_MS);
  }

  function limpiarFiltros(els) {
    if (els.cargo) els.cargo.value = "";
    if (els.estatus) els.estatus.value = "";
    if (els.antiguedad) els.antiguedad.value = "";
    buscarTrabajadores(els);
  }

  function inicializarModalEliminar(els) {
    var modal = document.getElementById("modal-eliminar");
    if (!modal || !window.TRABAJADORES_URLS.puede_eliminar) return;

    var form = document.getElementById("form-eliminar");
    var nombre = document.getElementById("eliminar-nombre");
    var cedula = document.getElementById("eliminar-cedula");
    var password = document.getElementById("eliminar-password");
    var ultimoBoton = null;

    function abrir(btn) {
      ultimoBoton = btn;
      form.action = urlEliminar(btn.dataset.id);
      nombre.innerHTML = btn.dataset.nombre;
      cedula.textContent = btn.dataset.cedula;
      password.value = "";
      modal.hidden = false;
      document.body.classList.add("menu-abierto");
      password.focus();
    }

    function cerrar() {
      modal.hidden = true;
      document.body.classList.remove("menu-abierto");
      password.value = "";
      if (ultimoBoton) ultimoBoton.focus();
    }

    els.tbody.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".btn-fila-eliminar");
      if (btn) abrir(btn);
    });
    modal.querySelectorAll("[data-cerrar]").forEach(function (el) {
      el.addEventListener("click", cerrar);
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && !modal.hidden) cerrar();
    });
    form.addEventListener("submit", function () {
      var enviar = form.querySelector("button[type=submit]");
      if (enviar) enviar.disabled = true;
    });
  }

  function inicializarFiltroTrabajadores() {
    var els = obtenerElementos();
    if (!els.form || !els.tbody || !window.TRABAJADORES_URLS) {
      return;
    }

    ["change", "input"].forEach(function (evento) {
      els.form.addEventListener(
        evento,
        function (ev) {
          if (ev.target && ev.target.id === "filtro-antiguedad" && evento === "change") {
            return;
          }
          programarBusqueda(els);
        },
        true
      );
    });

    if (els.antiguedad) {
      els.antiguedad.addEventListener("change", function () {
        programarBusqueda(els);
      });
    }

    if (els.btnLimpiar) {
      els.btnLimpiar.addEventListener("click", function () {
        limpiarFiltros(els);
      });
    }

    inicializarModalEliminar(els);
    buscarTrabajadores(els);
  }

  document.addEventListener("DOMContentLoaded", inicializarFiltroTrabajadores);
})();