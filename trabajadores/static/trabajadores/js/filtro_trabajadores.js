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
      departamento: document.getElementById("filtro-departamento"),
      estatus: document.getElementById("filtro-estatus"),
      antiguedad: document.getElementById("filtro-antiguedad"),
      btnLimpiar: document.getElementById("btn-limpiar-filtros"),
      tbody: document.getElementById("tabla-trabajadores-body"),
      sinResultados: document.getElementById("mensaje-sin-resultados"),
      contenedor: document.getElementById("contenedor-tabla-trabajadores"),
    };
  }

  function hayFiltrosActivos(els) {
    return (
      (els.cargo && els.cargo.value) ||
      (els.departamento && els.departamento.value) ||
      (els.estatus && els.estatus.value) ||
      (els.antiguedad && els.antiguedad.value.trim() !== "")
    );
  }

  function construirParametros(els) {
    var params = new URLSearchParams();
    if (els.cargo && els.cargo.value) {
      params.set("cargo", els.cargo.value);
    }
    if (els.departamento && els.departamento.value) {
      params.set("departamento", els.departamento.value);
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

  function escaparHtml(texto) {
    var div = document.createElement("div");
    div.textContent = texto == null ? "" : String(texto);
    return div.innerHTML;
  }

  function renderizarFila(trabajador) {
    var nombreCompleto = escaparHtml(trabajador.nombre) + " " + escaparHtml(trabajador.apellido);
    var inicial = escaparHtml((trabajador.nombre || "?").charAt(0).toUpperCase());
    var badgeClase = trabajador.esta_activo ? "badge-rol" : "badge-rol badge-sin-rol";
    var btnColor = trabajador.esta_activo ? "#8b1a2b" : "#2b6b3a";
    var btnTexto = trabajador.esta_activo ? "Desactivar" : "Activar";
    var antiguedad =
      trabajador.antiguedad != null
        ? escaparHtml(trabajador.antiguedad) + " año(s)"
        : "—";

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
      escaparHtml(trabajador.departamento) +
      "</span></div>" +
      '<div><span class="celda-email">' +
      antiguedad +
      "</span></div>" +
      '<div><span class="' +
      badgeClase +
      '">' +
      escaparHtml(trabajador.estado_display || trabajador.estado) +
      "</span></div>" +
      '<div style="display:flex; gap:8px; flex-wrap:wrap;">' +
      '<a href="' +
      urlDetalle(trabajador.id) +
      '" class="btn-accion">Perfil</a>' +
      '<a href="' +
      urlEditar(trabajador.id) +
      '" class="btn-accion btn-guardar">Editar</a>' +
      '<form method="post" action="' +
      urlEstado(trabajador.id) +
      '">' +
      '<input type="hidden" name="csrfmiddlewaretoken" value="' +
      escaparHtml(window.TRABAJADORES_URLS.csrf) +
      '">' +
      '<button type="submit" class="btn-accion" style="background:' +
      btnColor +
      '; color:white;">' +
      btnTexto +
      "</button>" +
      "</form>" +
      "</div>" +
      "</div>"
    );
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
  }

  function renderizarResultados(els, trabajadores) {
    els.contenedor.setAttribute("aria-busy", "false");

    if (!Array.isArray(trabajadores) || trabajadores.length === 0) {
      els.tbody.innerHTML = "";
      els.sinResultados.hidden = false;
      els.sinResultados.querySelector("p").textContent = "No se encontraron resultados";
      return;
    }

    els.sinResultados.hidden = true;
    els.tbody.innerHTML = trabajadores.map(renderizarFila).join("");
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
    if (els.departamento) els.departamento.value = "";
    if (els.estatus) els.estatus.value = "";
    if (els.antiguedad) els.antiguedad.value = "";
    buscarTrabajadores(els);
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

    buscarTrabajadores(els);
  }

  document.addEventListener("DOMContentLoaded", inicializarFiltroTrabajadores);
})();
