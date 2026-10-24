/* Curso Mastermind — comportamiento propio. Sin dependencias.
   Regla de la casa: nada de contenido oculto por defecto ni animaciones que
   condicionen que el dato se lea. Sin JS, la página se lee entera igual. */

(function () {
  "use strict";

  /* ---------- Copiar bloques de código ---------- */

  function prepararCopiar() {
    document.querySelectorAll(".curso-codigo").forEach(function (bloque) {
      var boton = document.createElement("button");
      boton.type = "button";
      boton.className = "curso-copiar";
      boton.textContent = "Copiar";
      boton.setAttribute("aria-label", "Copiar el código de este bloque");
      boton.addEventListener("click", function () {
        var texto = bloque.querySelector("code") ? bloque.querySelector("code").innerText : "";
        var marcar = function () {
          boton.textContent = "Copiado";
          boton.classList.add("is-hecho");
          window.setTimeout(function () {
            boton.textContent = "Copiar";
            boton.classList.remove("is-hecho");
          }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(texto).then(marcar, function () { seleccionar(bloque, marcar); });
        } else {
          seleccionar(bloque, marcar);
        }
      });
      bloque.appendChild(boton);
    });
  }

  function seleccionar(bloque, cb) {
    var rango = document.createRange();
    rango.selectNodeContents(bloque.querySelector("code") || bloque);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(rango);
    try { document.execCommand("copy"); } catch (e) { /* sin permiso: queda seleccionado */ }
    cb();
  }

  /* ---------- Modo presentación (tramos) ---------- */

  var tramos = [];
  var indice = 0;
  var cuenta, anterior, siguiente;

  function activo() {
    return document.body.classList.contains("curso-presentando");
  }

  function pintarCuenta() {
    if (!cuenta) return;
    cuenta.textContent = tramos.length ? (indice + 1) + " / " + tramos.length : "0 / 0";
    if (anterior) anterior.disabled = indice <= 0;
    if (siguiente) siguiente.disabled = indice >= tramos.length - 1;
  }

  function ir(i, suave) {
    if (!tramos.length) return;
    indice = Math.max(0, Math.min(tramos.length - 1, i));
    tramos[indice].scrollIntoView({ behavior: suave === false ? "auto" : "smooth", block: "start" });
    pintarCuenta();
  }

  function entrar() {
    document.body.classList.add("curso-presentando");
    document.documentElement.classList.add("curso-presentando");
    var boton = document.querySelector("[data-curso-presentar]");
    if (boton) boton.setAttribute("aria-pressed", "true");
    ir(0, false);
    if (cuenta) cuenta.focus({ preventScroll: true });
  }

  function salir() {
    document.body.classList.remove("curso-presentando");
    document.documentElement.classList.remove("curso-presentando");
    var boton = document.querySelector("[data-curso-presentar]");
    if (boton) { boton.setAttribute("aria-pressed", "false"); boton.focus({ preventScroll: true }); }
    if (tramos[indice]) tramos[indice].scrollIntoView({ behavior: "auto", block: "start" });
  }

  function prepararPresentacion() {
    tramos = Array.prototype.slice.call(document.querySelectorAll(".curso-tramo"));
    cuenta = document.querySelector(".curso-hud__cuenta");
    anterior = document.querySelector("[data-curso-anterior]");
    siguiente = document.querySelector("[data-curso-siguiente]");

    var boton = document.querySelector("[data-curso-presentar]");
    if (boton) {
      boton.addEventListener("click", function () { activo() ? salir() : entrar(); });
    }
    if (anterior) anterior.addEventListener("click", function () { ir(indice - 1); });
    if (siguiente) siguiente.addEventListener("click", function () { ir(indice + 1); });
    var botonSalir = document.querySelector("[data-curso-salir]");
    if (botonSalir) botonSalir.addEventListener("click", salir);

    document.addEventListener("keydown", function (e) {
      if (!activo()) {
        if (e.key === "p" && (e.metaKey || e.ctrlKey) === false && e.target === document.body) entrar();
        return;
      }
      if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") { e.preventDefault(); ir(indice + 1); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); ir(indice - 1); }
      else if (e.key === "Home") { e.preventDefault(); ir(0); }
      else if (e.key === "End") { e.preventDefault(); ir(tramos.length - 1); }
      else if (e.key === "Escape") { e.preventDefault(); salir(); }
    });

    if (cuenta) {
      cuenta.setAttribute("tabindex", "-1");
      cuenta.setAttribute("role", "status");
      cuenta.setAttribute("aria-live", "polite");
    }
    pintarCuenta();
  }

  document.addEventListener("DOMContentLoaded", function () {
    prepararCopiar();
    prepararPresentacion();
  });
})();
