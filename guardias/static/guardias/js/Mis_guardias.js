"use strict";

(function () {
  var MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
  ];

  var DIAS_SEMANA = [
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo",
  ];

  var ICONO_TURNO = {
    MANANA: "fa-sun",
    TARDE: "fa-cloud-sun",
    NOCHE: "fa-moon",
  };

  var estado = {
    anio: window.MIS_GUARDIAS_INICIAL.anio,
    mes: window.MIS_GUARDIAS_INICIAL.mes, // 1-12
  };

  // Guardias del mes visible, guardadas por fecha ISO para poder mostrar el detalle al hacer clic
  var guardiasDelMes = {};
  var diaSeleccionado = null;

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function isoDeFecha(anio, mes, dia) {
    return anio + "-" + pad2(mes) + "-" + pad2(dia);
  }

  function diasEnMes(anio, mes) {
    return new Date(anio, mes, 0).getDate();
  }

  // Día de la semana del 1° del mes, con lunes=0 ... domingo=6
  function primerDiaSemanaLunes(anio, mes) {
    var jsDay = new Date(anio, mes - 1, 1).getDay();
    return jsDay === 0 ? 6 : jsDay - 1;
  }

  function formatearFechaLarga(iso) {
    var partes = iso.split("-").map(Number);
    var fecha = new Date(partes[0], partes[1] - 1, partes[2]);
    var diaSemana = DIAS_SEMANA[fecha.getDay() === 0 ? 6 : fecha.getDay() - 1];
    return diaSemana + " " + fecha.getDate() + " de " + MESES[fecha.getMonth()] + " de " + fecha.getFullYear();
  }

  function construirCalendario() {
    var grid = document.getElementById("mini-calendario-grid");
    var etiquetaMes = document.getElementById("mis-guardias-mes");
    if (!grid) return;

    etiquetaMes.textContent = MESES[estado.mes - 1] + " " + estado.anio;

    var hoy = new Date();
    var isoHoy = isoDeFecha(hoy.getFullYear(), hoy.getMonth() + 1, hoy.getDate());

    var totalDias = diasEnMes(estado.anio, estado.mes);
    var offsetInicial = primerDiaSemanaLunes(estado.anio, estado.mes);

    var html = "";

    for (var i = 0; i < offsetInicial; i++) {
      html += '<div class="mini-calendario-dia mini-calendario-dia-otro-mes"></div>';
    }

    for (var dia = 1; dia <= totalDias; dia++) {
      var iso = isoDeFecha(estado.anio, estado.mes, dia);
      var esHoy = iso === isoHoy;
      html += '<div class="mini-calendario-dia' + (esHoy ? " mini-calendario-dia-hoy" : "") + '" id="dia-' + iso + '" data-fecha="' + iso + '">';
      html += '<span class="mini-calendario-numero">' + dia + "</span>";
      html += '<div class="mini-calendario-badges" id="badges-' + iso + '"></div>';
      html += "</div>";
    }

    grid.innerHTML = html;
  }

  function calcularProximaGuardia() {
    var hoy = new Date();
    var isoHoy = isoDeFecha(hoy.getFullYear(), hoy.getMonth() + 1, hoy.getDate());
    var fechas = Object.keys(guardiasDelMes).filter(function (iso) {
      return iso >= isoHoy;
    }).sort();
    return fechas.length ? guardiasDelMes[fechas[0]] : null;
  }

  function mostrarProximaGuardia() {
    var contenedor = document.getElementById("proxima-guardia");
    var texto = document.getElementById("proxima-guardia-texto");
    if (!contenedor || !texto) return;

    var proxima = calcularProximaGuardia();
    if (!proxima) {
      contenedor.hidden = true;
      return;
    }

    var estadoTexto = proxima.aprobado ? "aprobado" : "pendiente de aprobación";
    texto.textContent = formatearFechaLarga(proxima.fecha) + " — Turno " + proxima.turno_display + " (" + estadoTexto + ")";
    contenedor.hidden = false;
  }

  function mostrarDetalleDia(iso) {
    var panel = document.getElementById("detalle-dia");
    var fechaEl = document.getElementById("detalle-dia-fecha");
    var infoEl = document.getElementById("detalle-dia-info");
    var g = guardiasDelMes[iso];
    if (!panel || !g) return;

    fechaEl.textContent = formatearFechaLarga(iso);
    var estadoTexto = g.aprobado ? "Aprobado ✓" : "Pendiente de aprobación";
    infoEl.textContent = "Turno " + g.turno_display + " — " + estadoTexto;
    panel.hidden = false;

    document.querySelectorAll(".mini-calendario-dia-seleccionado").forEach(function (el) {
      el.classList.remove("mini-calendario-dia-seleccionado");
    });
    var celda = document.getElementById("dia-" + iso);
    if (celda) celda.classList.add("mini-calendario-dia-seleccionado");
    diaSeleccionado = iso;
  }

  function ocultarDetalleDia() {
    var panel = document.getElementById("detalle-dia");
    if (panel) panel.hidden = true;
    document.querySelectorAll(".mini-calendario-dia-seleccionado").forEach(function (el) {
      el.classList.remove("mini-calendario-dia-seleccionado");
    });
    diaSeleccionado = null;
  }

  function cargarGuardias() {
    var mesParam = estado.anio + "-" + pad2(estado.mes);
    var url = window.MIS_GUARDIAS_URL + "?mes=" + mesParam;

    guardiasDelMes = {};
    ocultarDetalleDia();

    fetch(url, {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    })
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        (data.guardias || []).forEach(function (g) {
          guardiasDelMes[g.fecha] = g;

          var contenedor = document.getElementById("badges-" + g.fecha);
          if (!contenedor) return;

          var celda = document.getElementById("dia-" + g.fecha);
          if (celda) {
            celda.classList.add("mini-calendario-dia-con-guardia");
            celda.addEventListener("click", function () {
              mostrarDetalleDia(g.fecha);
            });
          }

          var icono = ICONO_TURNO[g.turno] || "fa-clock";
          var badge = document.createElement("div");
          badge.className = "mini-calendario-badge " +
            (g.aprobado ? "mini-calendario-badge-aprobado" : "mini-calendario-badge-pendiente");
          badge.innerHTML = '<i class="fas ' + icono + '"></i> ' + g.turno_display;
          contenedor.appendChild(badge);
        });

        mostrarProximaGuardia();
      })
      .catch(function (err) {
        console.error("Error al cargar mis guardias:", err);
      });
  }

  function renderizarMesActual() {
    construirCalendario();
    cargarGuardias();
  }

  function inicializar() {
    var btnAnterior = document.getElementById("btn-mes-anterior");
    var btnSiguiente = document.getElementById("btn-mes-siguiente");
    var btnHoy = document.getElementById("btn-mes-hoy");
    var btnCerrarDetalle = document.getElementById("cerrar-detalle-dia");

    if (btnAnterior) {
      btnAnterior.addEventListener("click", function () {
        estado.mes -= 1;
        if (estado.mes < 1) {
          estado.mes = 12;
          estado.anio -= 1;
        }
        renderizarMesActual();
      });
    }

    if (btnSiguiente) {
      btnSiguiente.addEventListener("click", function () {
        estado.mes += 1;
        if (estado.mes > 12) {
          estado.mes = 1;
          estado.anio += 1;
        }
        renderizarMesActual();
      });
    }

    if (btnHoy) {
      btnHoy.addEventListener("click", function () {
        var hoy = new Date();
        estado.anio = hoy.getFullYear();
        estado.mes = hoy.getMonth() + 1;
        renderizarMesActual();
      });
    }

    if (btnCerrarDetalle) {
      btnCerrarDetalle.addEventListener("click", ocultarDetalleDia);
    }

    renderizarMesActual();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializar);
  } else {
    inicializar();
  }
})();