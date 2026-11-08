/**
 * sidebar.js — menú lateral tipo cajón (drawer) con acordeón interno.
 * Reemplaza el <script> en línea del final de base.html.
 */
(function () {
  "use strict";

  var sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  var grupos = sidebar.querySelectorAll(".nav-grupo");

  function establecer(grupo, abierto) {
    var btn = grupo.querySelector(":scope > .nav-item-padre");
    grupo.classList.toggle("abierto", abierto);
    if (btn) btn.setAttribute("aria-expanded", abierto ? "true" : "false");
  }

  // Acordeón: al abrir un grupo se cierran los demás.
  grupos.forEach(function (grupo) {
    var btn = grupo.querySelector(":scope > .nav-item-padre");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var abrir = !grupo.classList.contains("abierto");
      if (abrir) {
        grupos.forEach(function (otro) {
          if (otro !== grupo) establecer(otro, false);
        });
      }
      establecer(grupo, abrir);
    });
  });

  // ── Cajón: fondo difuminado + botón de apertura + botón de cierre ──
  var topbar = document.querySelector(".topbar");

  var overlay = document.createElement("div");
  overlay.className = "sidebar-overlay";
  document.body.appendChild(overlay);

  var boton = document.createElement("button");
  boton.type = "button";
  boton.className = "btn-menu";
  boton.setAttribute("aria-label", "Abrir menú");
  boton.setAttribute("aria-controls", "sidebar");
  boton.setAttribute("aria-expanded", "false");
  boton.innerHTML = '<i class="fas fa-bars" aria-hidden="true"></i>';
  if (topbar) topbar.appendChild(boton);

  var cerrar = document.createElement("button");
  cerrar.type = "button";
  cerrar.className = "btn-cerrar-menu";
  cerrar.setAttribute("aria-label", "Cerrar menú");
  cerrar.innerHTML = '<i class="fas fa-xmark" aria-hidden="true"></i>';
  var cabecera = sidebar.querySelector(".sidebar-header");
  if (cabecera) cabecera.appendChild(cerrar);

  function menu(abrir) {
    sidebar.classList.toggle("abierto", abrir);
    overlay.classList.toggle("visible", abrir);
    document.body.classList.toggle("menu-abierto", abrir);
    boton.setAttribute("aria-expanded", abrir ? "true" : "false");
    (abrir ? cerrar : boton).focus({ preventScroll: true });
  }

  boton.addEventListener("click", function () {
    menu(!sidebar.classList.contains("abierto"));
  });
  cerrar.addEventListener("click", function () { menu(false); });
  overlay.addEventListener("click", function () { menu(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && sidebar.classList.contains("abierto")) menu(false);
  });
  sidebar.querySelectorAll("a[href]").forEach(function (a) {
    a.addEventListener("click", function () { menu(false); });
  });

  // Limpia el estado guardado por la versión anterior (menú minimizable).
  try { localStorage.removeItem("sidebarMinimizado"); } catch (e) {}
})();