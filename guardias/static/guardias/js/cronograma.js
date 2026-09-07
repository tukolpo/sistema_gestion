"use strict";

(function () {
  function getCSRFToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  function cargarCronograma() {
    fetch(window.GUARDIAS_URLS.cronograma, {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    })
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        document.querySelectorAll('[id^="celda-"]').forEach(function (celda) {
          celda.textContent = "—";
        });
        data.guardias.forEach(function (g) {
          var celda = document.getElementById("celda-" + g.turno + "-" + g.fecha);
          if (celda) {
            celda.textContent = g.trabajador + (g.aprobado ? " ✓" : "");
          }
        });
      })
      .catch(function (err) {
        console.error("Error al cargar cronograma:", err);
      });
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
        alert("Selecciona funcionario y fecha.");
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
            alert(result.data.detail || "No se pudo asignar el turno.");
            return;
          }
          form.reset();
          cargarCronograma();
        })
        .catch(function () {
          alert("Error de conexión al asignar el turno.");
        });
    });
  }

  function inicializarAprobacion() {
    var btn = document.getElementById("btn-aprobar");
    if (!btn) return;

    btn.addEventListener("click", function () {
      fetch(window.GUARDIAS_URLS.cronograma, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ aprobado: true }),
      })
        .then(function (resp) { return resp.json(); })
        .then(function () { cargarCronograma(); })
        .catch(function () {
          alert("Error al aprobar el cronograma.");
        });
    });
  }

  function inicializar() {
    inicializarAsignacion();
    inicializarAprobacion();
    cargarCronograma();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializar);
  } else {
    inicializar();
  }
})();