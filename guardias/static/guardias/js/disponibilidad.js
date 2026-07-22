/**
 * disponibilidad.js
 * Módulo 4 — Tarea 2: consulta y visualización de disponibilidad de funcionarios.
 */
"use strict";

(function () {
  var BADGE_CLASES = {
    DISPONIBLE: "badge-rol badge-disponible",
    VACACIONES: "badge-rol badge-vacaciones",
    PERMISO: "badge-rol badge-permiso",
    INACTIVO: "badge-rol badge-inactivo",
  };

  function obtenerElementos() {
    return {
      tbody: document.getElementById("tabla-disponibilidad-body"),
      sinResultados: document.getElementById("mensaje-sin-funcionarios"),
      selectFuncionario: document.getElementById("id_funcionario"),
      inputFecha: document.getElementById("filtro-fecha-disponibilidad"),
      btnRecargar: document.getElementById("btn-recargar-disponibilidad"),
    };
  }

  function escaparHtml(texto) {
    var div = document.createElement("div");
    div.textContent = texto == null ? "" : String(texto);
    return div.innerHTML;
  }

  function fechaHoyISO() {
    var hoy = new Date();
    var mes = String(hoy.getMonth() + 1).padStart(2, "0");
    var dia = String(hoy.getDate()).padStart(2, "0");
    return hoy.getFullYear() + "-" + mes + "-" + dia;
  }

  function construirUrl(fecha) {
    var url = window.GUARDIAS_URLS.disponibilidad;
    if (fecha) {
      url += "?fecha=" + encodeURIComponent(fecha);
    }
    return url;
  }

  function renderizarFila(funcionario) {
    var inicial = escaparHtml((funcionario.nombre || "?").charAt(0).toUpperCase());
    var badgeClase =
      BADGE_CLASES[funcionario.estado_disponibilidad] || "badge-rol badge-inactivo";
    var motivoHtml = funcionario.motivo
      ? '<span class="disponibilidad-motivo">' + escaparHtml(funcionario.motivo) + "</span>"
      : "";

    return (
      '<div class="tabla-fila disponibilidad-fila" role="row" data-funcionario-id="' +
      funcionario.id +
      '" data-disponible="' +
      (funcionario.disponible ? "1" : "0") +
      '">' +
      '<div class="celda-usuario" role="cell">' +
      '<div class="avatar-mini" aria-hidden="true">' +
      inicial +
      "</div>" +
      '<span class="celda-nombre">' +
      escaparHtml(funcionario.nombre_completo) +
      "</span>" +
      "</div>" +
      '<div role="cell"><span class="celda-email">' +
      escaparHtml(funcionario.cedula) +
      "</span></div>" +
      '<div role="cell"><span class="celda-email">' +
      escaparHtml(funcionario.cargo || "—") +
      "</span></div>" +
      '<div role="cell">' +
      '<span class="' +
      badgeClase +
      '">' +
      escaparHtml(funcionario.estado_disponibilidad_display) +
      "</span>" +
      motivoHtml +
      "</div>" +
      "</div>"
    );
  }

  function actualizarSelectFuncionarios(funcionarios) {
    var select = document.getElementById("id_funcionario");
    if (!select) {
      return;
    }

    var disponibles = funcionarios.filter(function (f) {
      return f.disponible;
    });

    select.innerHTML = "";

    if (disponibles.length === 0) {
      select.disabled = true;
      var optVacio = document.createElement("option");
      optVacio.value = "";
      optVacio.textContent = "— No hay funcionarios disponibles —";
      select.appendChild(optVacio);
      return;
    }

    select.disabled = false;
    var optDefault = document.createElement("option");
    optDefault.value = "";
    optDefault.textContent = "— Seleccione un funcionario disponible —";
    select.appendChild(optDefault);

    disponibles.forEach(function (f) {
      var opt = document.createElement("option");
      opt.value = String(f.id);
      opt.textContent = f.nombre_completo;
      select.appendChild(opt);
    });
  }

  function mostrarCargando(els) {
    if (!els.tbody) {
      return;
    }
    els.tbody.innerHTML =
      '<div class="tabla-fila disponibilidad-cargando" role="row">' +
      '<div role="cell" style="grid-column: 1 / -1; text-align:center; padding:16px;">' +
      "Cargando disponibilidad…" +
      "</div></div>";
    if (els.sinResultados) {
      els.sinResultados.hidden = true;
    }
  }

  function mostrarError(els, mensaje) {
    if (!els.tbody) {
      return;
    }
    els.tbody.innerHTML =
      '<div class="tabla-fila" role="row">' +
      '<div role="cell" class="disponibilidad-error" style="grid-column: 1 / -1;">' +
      escaparHtml(mensaje) +
      "</div></div>";
  }

  function cargarDisponibilidad() {
    var els = obtenerElementos();
    if (!els.tbody) {
      return;
    }

    var fecha = els.inputFecha && els.inputFecha.value ? els.inputFecha.value : fechaHoyISO();
    if (els.inputFecha && !els.inputFecha.value) {
      els.inputFecha.value = fecha;
    }

    mostrarCargando(els);

    fetch(construirUrl(fecha), {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    })
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error("No se pudo cargar la disponibilidad (HTTP " + resp.status + ").");
        }
        return resp.json();
      })
      .then(function (datos) {
        if (!Array.isArray(datos) || datos.length === 0) {
          els.tbody.innerHTML = "";
          if (els.sinResultados) {
            els.sinResultados.hidden = false;
          }
          actualizarSelectFuncionarios([]);
          return;
        }

        if (els.sinResultados) {
          els.sinResultados.hidden = true;
        }

        els.tbody.innerHTML = datos.map(renderizarFila).join("");
        actualizarSelectFuncionarios(datos);
      })
      .catch(function (err) {
        mostrarError(els, err.message || "Error al consultar disponibilidad.");
        actualizarSelectFuncionarios([]);
      });
  }

  function inicializar() {
    var els = obtenerElementos();
    if (!els.tbody) {
      return;
    }

    if (els.inputFecha) {
      els.inputFecha.value = fechaHoyISO();
      els.inputFecha.addEventListener("change", cargarDisponibilidad);
    }

    if (els.btnRecargar) {
      els.btnRecargar.addEventListener("click", cargarDisponibilidad);
    }

    cargarDisponibilidad();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializar);
  } else {
    inicializar();
  }
})();
