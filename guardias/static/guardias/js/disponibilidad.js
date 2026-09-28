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

    // 1) Select real (oculto): sigue siendo la fuente del valor que se envía
    select.innerHTML = "";

    if (disponibles.length === 0) {
      select.disabled = true;
      var optVacio = document.createElement("option");
      optVacio.value = "";
      optVacio.textContent = "— No hay funcionarios disponibles —";
      select.appendChild(optVacio);
    } else {
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

    // 2) Menú visual: se ve moderno y controla el select real al elegir
    actualizarMenuFuncionarios(disponibles, select);
  }

  function actualizarMenuFuncionarios(disponibles, select) {
    var boton = document.getElementById("btn-dropdown-funcionario");
    var texto = document.getElementById("texto-dropdown-funcionario");
    var lista = document.getElementById("lista-dropdown-funcionario");
    if (!boton || !texto || !lista) {
      return;
    }

    lista.innerHTML = "";
    lista.hidden = true;
    boton.setAttribute("aria-expanded", "false");

    if (disponibles.length === 0) {
      boton.disabled = true;
      texto.textContent = "— No hay funcionarios disponibles —";
      return;
    }

    boton.disabled = false;
    texto.textContent = "— Seleccione un funcionario disponible —";

    disponibles.forEach(function (f) {
      var li = document.createElement("li");
      li.className = "dropdown-opcion";
      li.setAttribute("role", "option");
      li.textContent = f.nombre_completo;
      li.addEventListener("click", function () {
        select.value = String(f.id);
        texto.textContent = f.nombre_completo;
        lista.querySelectorAll(".dropdown-opcion-activa").forEach(function (o) {
          o.classList.remove("dropdown-opcion-activa");
        });
        li.classList.add("dropdown-opcion-activa");
        cerrarMenuFuncionarios();
      });
      lista.appendChild(li);
    });
  }

  function abrirMenuFuncionarios() {
    var boton = document.getElementById("btn-dropdown-funcionario");
    var lista = document.getElementById("lista-dropdown-funcionario");
    if (!boton || !lista || boton.disabled) return;
    lista.hidden = false;
    boton.setAttribute("aria-expanded", "true");
  }

  function cerrarMenuFuncionarios() {
    var boton = document.getElementById("btn-dropdown-funcionario");
    var lista = document.getElementById("lista-dropdown-funcionario");
    if (!boton || !lista) return;
    lista.hidden = true;
    boton.setAttribute("aria-expanded", "false");
  }

  function inicializarMenuFuncionarios() {
    var boton = document.getElementById("btn-dropdown-funcionario");
    var lista = document.getElementById("lista-dropdown-funcionario");
    if (!boton || !lista) return;

    boton.addEventListener("click", function (e) {
      e.stopPropagation();
      if (lista.hidden) {
        abrirMenuFuncionarios();
      } else {
        cerrarMenuFuncionarios();
      }
    });

    document.addEventListener("click", function (e) {
      if (!lista.hidden && !lista.contains(e.target) && e.target !== boton) {
        cerrarMenuFuncionarios();
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        cerrarMenuFuncionarios();
      }
    });

    // Cuando cronograma.js hace form.reset() tras asignar, el <select> oculto
    // vuelve a "", pero el botón visual no se entera solo: lo sincronizamos aquí.
    var form = document.getElementById("form-asignacion");
    if (form) {
      form.addEventListener("reset", function () {
        setTimeout(function () {
          texto.textContent = boton.disabled
            ? "— No hay funcionarios disponibles —"
            : "— Seleccione un funcionario disponible —";
          lista.querySelectorAll(".dropdown-opcion-activa").forEach(function (o) {
            o.classList.remove("dropdown-opcion-activa");
          });
          cerrarMenuFuncionarios();
        }, 0);
      });
    }
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

    inicializarMenuFuncionarios();
    cargarDisponibilidad();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializar);
  } else {
    inicializar();
  }
})();