/**
 * efectos-tema.js — nieve cayendo sutil en el login (tema Navidad).
 * Solo se activa si <body data-efectos-tema> existe.
 * Respeta prefers-reduced-motion y se pausa con la pestaña oculta.
 */
(function () {
  "use strict";
  if (!document.body.hasAttribute("data-efectos-tema")) return;
  if (document.documentElement.getAttribute("data-tema") !== "navidad") return;
  if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var canvas = document.createElement("canvas");
  canvas.className = "efecto-tema-canvas";
  canvas.setAttribute("aria-hidden", "true");
  document.body.appendChild(canvas);
  var ctx = canvas.getContext("2d");
  var w = 0, h = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);

  function ajustar() {
    w = window.innerWidth; h = window.innerHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  ajustar();
  window.addEventListener("resize", ajustar);

  function copo(arriba) {
    return {
      x: Math.random() * w,
      y: arriba ? -10 : Math.random() * h,
      r: 1 + Math.random() * 2.6,
      v: 0.4 + Math.random() * 1.1,
      fase: Math.random() * Math.PI * 2
    };
  }
  var copos = [], total = w < 600 ? 40 : 80;
  for (var i = 0; i < total; i++) copos.push(copo(false));

  var activo = true, t = 0;
  function frame() {
    if (!activo) return;
    t += 0.01;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "rgba(255,255,255,.85)";
    for (var i = 0; i < copos.length; i++) {
      var p = copos[i];
      p.x += Math.sin(t + p.fase) * 0.5;
      p.y += p.v;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, 6.2832);
      ctx.fill();
      if (p.y > h + 10) copos[i] = copo(true);
    }
    requestAnimationFrame(frame);
  }
  document.addEventListener("visibilitychange", function () {
    activo = !document.hidden;
    if (activo) requestAnimationFrame(frame);
  });
  requestAnimationFrame(frame);
})();