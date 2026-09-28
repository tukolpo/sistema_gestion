"use strict";

(function () {
  var MESES_CORTOS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

  // Lunes de la semana que contiene "fecha" (0=domingo..6=sábado en JS)
  function lunesDeSemana(fecha) {
    var dia = fecha.getDay();
    var diff = dia === 0 ? -6 : 1 - dia;
    var lunes = new Date(fecha);
    lunes.setDate(fecha.getDate() + diff);
    lunes.setHours(0, 0, 0, 0);
    return lunes;
  }

  function formatearISO(fecha) {
    var mes = String(fecha.getMonth() + 1).padStart(2, "0");
    var dia = String(fecha.getDate()).padStart(2, "0");
    return fecha.getFullYear() + "-" + mes + "-" + dia;
  }

  function formatearCorto(fecha) {
    return String(fecha.getDate()).padStart(2, "0") + " " + MESES_CORTOS[fecha.getMonth()];
  }

  function sumarDias(fecha, cantidad) {
    var nueva = new Date(fecha);
    nueva.setDate(fecha.getDate() + cantidad);
    return nueva;
  }

  // Estado: lunes de la semana que se está viendo actualmente
  var semanaInicio = lunesDeSemana(new Date());

  function getCSRFToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  function mostrarMensaje(contenedorId, texto, tipo) {
    var contenedor = document.getElementById(contenedorId);
    if (!contenedor) return;
    contenedor.textContent = texto;
    contenedor.className = tipo === "error" ? "alerta alerta-error" : "alerta alerta-exito";
    contenedor.hidden = false;
    clearTimeout(contenedor._timeout);
    contenedor._timeout = setTimeout(function () {
      contenedor.hidden = true;
    }, 5000);
  }

  // Construye las 7 filas de la semana actual (solo la estructura, sin datos aún)
  function construirEstructuraSemana() {
    var contenedor = document.getElementById("cronograma-dias");
    if (!contenedor) return;

    var turnos = window.GUARDIAS_TURNOS || [];
    var html = "";

    for (var i = 0; i < 7; i++) {
      var fecha = sumarDias(semanaInicio, i);
      var iso = formatearISO(fecha);
      var esUltimo = i === 6;

      html += '<div class="cronograma-fila' + (esUltimo ? "" : " cronograma-fila-borde") + '">';
      html += '<button type="button" class="btn-dia-cronograma" data-fecha="' + iso + '" ' +
        'title="Usar esta fecha en el formulario de asignación">' +
        String(fecha.getDate()).padStart(2, "0") + "<br>" +
        String(fecha.getMonth() + 1).padStart(2, "0") +
        "</button>";

      html += '<div class="cronograma-turnos">';
      turnos.forEach(function (par) {
        var codigo = par[0];
        var texto = par[1];
        html += '<div class="cronograma-turno-pill">' +
          '<span class="cronograma-turno-nombre">' + texto + '</span>' +
          '<span id="celda-' + codigo + '-' + iso + '" class="cronograma-turno-valor">—</span>' +
          '</div>';
      });
      html += "</div></div>";
    }

    contenedor.innerHTML = html;

    // Cada círculo con la fecha lleva a "Asignar Turno" con esa fecha ya escrita
    contenedor.querySelectorAll(".btn-dia-cronograma").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var inputFecha = document.getElementById("id_fecha");
        if (inputFecha) {
          inputFecha.value = btn.dataset.fecha;
        }
        var tabAsignar = document.querySelector('.tab-btn[data-tab="asignar"]');
        if (tabAsignar) {
          tabAsignar.click();
        }
      });
    });
  }

  function actualizarNavegacion() {
    var fin = sumarDias(semanaInicio, 6);
    var rango = document.getElementById("cronograma-rango");
    if (rango) {
      rango.textContent = formatearCorto(semanaInicio) + " – " + formatearCorto(fin) + " " + fin.getFullYear();
    }
    var btnReporte = document.getElementById("btn-reporte");
    if (btnReporte && window.GUARDIAS_URLS.reporte) {
      btnReporte.href = window.GUARDIAS_URLS.reporte + "?fecha=" + formatearISO(semanaInicio);
    }
  }

  function cargarCronograma() {
    var url = window.GUARDIAS_URLS.cronograma + "?fecha=" + formatearISO(semanaInicio);

    fetch(url, {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    })
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        document.querySelectorAll('[id^="celda-"]').forEach(function (celda) {
          celda.textContent = "—";
          celda.classList.remove("cronograma-turno-valor-asignado");
          var pill = celda.closest(".cronograma-turno-pill");
          if (pill) pill.classList.remove("cronograma-turno-pill-asignado");
        });
        data.guardias.forEach(function (g) {
          var celda = document.getElementById("celda-" + g.turno + "-" + g.fecha);
          if (celda) {
            celda.textContent = g.trabajador + (g.aprobado ? " ✓" : "");
            celda.classList.add("cronograma-turno-valor-asignado");
            var pill = celda.closest(".cronograma-turno-pill");
            if (pill) pill.classList.add("cronograma-turno-pill-asignado");
          }
        });
      })
      .catch(function (err) {
        console.error("Error al cargar cronograma:", err);
      });
  }

  function renderizarSemanaActual() {
    construirEstructuraSemana();
    actualizarNavegacion();
    cargarCronograma();
  }

  function inicializarNavegacionSemanas() {
    var btnAnterior = document.getElementById("btn-semana-anterior");
    var btnSiguiente = document.getElementById("btn-semana-siguiente");
    var btnHoy = document.getElementById("btn-semana-hoy");

    if (btnAnterior) {
      btnAnterior.addEventListener("click", function () {
        semanaInicio = sumarDias(semanaInicio, -7);
        renderizarSemanaActual();
      });
    }
    if (btnSiguiente) {
      btnSiguiente.addEventListener("click", function () {
        semanaInicio = sumarDias(semanaInicio, 7);
        renderizarSemanaActual();
      });
    }
    if (btnHoy) {
      btnHoy.addEventListener("click", function () {
        semanaInicio = lunesDeSemana(new Date());
        renderizarSemanaActual();
      });
    }
  }

  function inicializarAsignacion() {
    var form = document.getElementById("form-asignacion");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var body = {
        turno: document.getElementById("id_turno").value,
        funcionario: document.getElementById("id_funcionario").value,
        fecha: document.getElementById("id_fecha").value,
      };

      if (!body.funcionario || !body.fecha) {
        mostrarMensaje("mensaje-asignacion", "Selecciona funcionario y fecha.", "error");
        return;
      }

      fetch(window.GUARDIAS_URLS.asignar, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(body),
      })
        .then(function (resp) { return resp.json().then(function (data) { return { ok: resp.ok, data: data }; }); })
        .then(function (result) {
          if (!result.ok) {
            mostrarMensaje("mensaje-asignacion", result.data.detail || "No se pudo asignar el turno.", "error");
            return;
          }
          mostrarMensaje("mensaje-asignacion", result.data.detail || "Turno asignado correctamente.", "exito");
          form.reset();
          cargarCronograma();
        })
        .catch(function () {
          mostrarMensaje("mensaje-asignacion", "Error de conexión al asignar el turno.", "error");
        });
    });
  }

  function inicializarAprobacion() {
    var btn = document.getElementById("btn-aprobar");
    if (!btn) return;

    btn.addEventListener("click", function () {
      // Se aprueba la semana que se está viendo en este momento, no la de hoy.
      fetch(window.GUARDIAS_URLS.cronograma, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ aprobado: true, fecha: formatearISO(semanaInicio) }),
      })
        .then(function (resp) { return resp.json(); })
        .then(function (data) {
          mostrarMensaje("mensaje-cronograma", data.detail || "Cronograma aprobado.", "exito");
          cargarCronograma();
        })
        .catch(function () {
          mostrarMensaje("mensaje-cronograma", "Error al aprobar el cronograma.", "error");
        });
    });
  }

  function inicializar() {
    inicializarNavegacionSemanas();
    inicializarAsignacion();
    inicializarAprobacion();
    renderizarSemanaActual();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializar);
  } else {
    inicializar();
  }
})();