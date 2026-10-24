#!/usr/bin/env python3
"""Genera el sitio del curso desde el Markdown de `contenido/`.

Uso:  python3 scripts/build.py
Salida: index.html y modulos/<slug>/index.html  (no se editan a mano)

Sin dependencias del proyecto salvo `markdown` (pip install markdown).
"""

from __future__ import annotations

import html
import re
import shutil
import unicodedata
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
CONTENIDO = RAIZ / "contenido"
SALIDA = RAIZ / "modulos"

AURORA = "https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0"
PACKS_BASE = [
    "p1-layout.css",
    "p2-navigation.css",
    "p3-typography.css",
    "p4-actions.css",
    "p6-feedback.css",
    "p12-system.css",
]
PACKS_CONDICIONALES = {
    "p5-forms.css": ("nz-field", "nz-input", "nz-checkbox", "nz-segmented"),
    "p8-data.css": ("nz-table", "nz-kpi", "nz-dl", "nz-arbol"),
    "p10-commerce.css": ("nz-cart", "nz-pricetable", "nz-checkout"),
    "p11-social.css": ("nz-quote", "nz-feed", "nz-activity"),
    "p13-charts.css": ("nz-chart", "nz-heatmap", "nz-bullet"),
    "p14-ai.css": ("nz-chat", "nz-msg", "nz-toolcall"),
    "p18-escenario.css": ("nz-escenario", "nz-esc-"),
}


def packs_para(html_: str) -> list[str]:
    """Solo los packs que la página usa de verdad (el auditor avisa del peso muerto)."""
    packs = list(PACKS_BASE)
    for pack, marcas in PACKS_CONDICIONALES.items():
        if any(m in html_ for m in marcas):
            packs.append(pack)
    return sorted(packs, key=lambda p: int(p.split("-")[0][1:]))

ATRIBUCION = "Hecho con ❤️ por David Antizar"


# --------------------------------------------------------------------------
# Lectura del contenido
# --------------------------------------------------------------------------


def leer_frontmatter(texto: str) -> tuple[dict, str]:
    if not texto.startswith("---"):
        return {}, texto
    _, bloque, resto = texto.split("---", 2)
    datos: dict = {}
    clave = None
    for linea in bloque.strip().splitlines():
        if not linea.strip():
            continue
        if linea.startswith("  - ") or linea.startswith("- "):
            if clave:
                datos.setdefault(clave, [])
                if isinstance(datos[clave], list):
                    datos[clave].append(linea.split("- ", 1)[1].strip())
            continue
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            clave = clave.strip()
            valor = valor.strip()
            if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                valor = valor[1:-1]
            datos[clave] = valor if valor else []
    return datos, resto.lstrip("\n")


def modulos() -> list[dict]:
    salida = []
    for ruta in sorted(CONTENIDO.glob("*.md")):
        crudo = ruta.read_text(encoding="utf-8")
        datos, cuerpo = leer_frontmatter(crudo)
        numero = datos.get("numero") or ruta.name[:2]
        slug = ruta.stem
        salida.append(
            {
                "numero": str(numero),
                "slug": slug,
                "titulo": datos.get("titulo", slug),
                "resumen": datos.get("resumen", ""),
                "duracion": datos.get("duracion", "30-40 min"),
                "nivel": datos.get("nivel", "Desde cero"),
                "objetivo": datos.get("objetivo", ""),
                "criterios": datos.get("criterios", []),
                "cuerpo": cuerpo,
                "ruta": ruta,
            }
        )
    return salida


# --------------------------------------------------------------------------
# Markdown -> HTML con objetos de Aurora
# --------------------------------------------------------------------------


def slug_id(texto: str) -> str:
    limpio = unicodedata.normalize("NFKD", texto)
    limpio = "".join(c for c in limpio if not unicodedata.combining(c))
    limpio = re.sub(r"<[^>]+>", "", limpio).lower()
    limpio = re.sub(r"[^a-z0-9]+", "-", limpio).strip("-")
    return limpio or "tramo"


def arreglar_tablas(html_: str) -> str:
    def una(match: re.Match) -> str:
        tabla = match.group(0)
        cabeceras = re.findall(r"<th[^>]*>(.*?)</th>", tabla, flags=re.S)
        etiquetas = [re.sub(r"<[^>]+>", "", c).strip() for c in cabeceras]

        def fila(m: re.Match) -> str:
            celdas = re.findall(r"<td[^>]*>.*?</td>", m.group(0), flags=re.S)
            nuevas = []
            for i, celda in enumerate(celdas):
                etiqueta = etiquetas[i] if i < len(etiquetas) else ""
                nuevas.append(
                    re.sub(r"<td", f'<td data-etiqueta="{html.escape(etiqueta, quote=True)}"', celda, count=1)
                )
            return "<tr>" + "".join(nuevas) + "</tr>"

        tabla = re.sub(r"<tr>(?:(?!</tr>).)*?<td.*?</tr>", fila, tabla, flags=re.S)
        tabla = tabla.replace("<table>", '<table class="nz-table nz-table--apilable">')
        return (
            '<div class="nz-table-wrap nz-table-wrap--apilable">' + tabla + "</div>"
        )

    return re.sub(r"<table>.*?</table>", una, html_, flags=re.S)


def arreglar_html(html_: str) -> str:
    # Código inline (los bloques ya traen class="language-x")
    html_ = html_.replace("<code>", '<code class="nz-code nz-code--inline">')

    # Bloques de código con botón de copiar
    html_ = re.sub(
        r'<pre><code class="language-([\w+-]+)">',
        lambda m: f'<pre class="nz-code nz-code--block curso-codigo" data-lenguaje="{m.group(1)}"><code>',
        html_,
    )
    html_ = html_.replace("<pre><code>", '<pre class="nz-code nz-code--block curso-codigo"><code>')

    # Citas -> callout del sistema
    html_ = html_.replace("<blockquote>", '<div class="nz-callout nz-callout--tip">')
    html_ = html_.replace("</blockquote>", "</div>")

    # Checklists
    html_ = re.sub(r"<li>\[ \]\s*", '<li class="curso-tarea">', html_)
    html_ = re.sub(r"<li>\[[xX]\]\s*", '<li class="curso-tarea is-hecha">', html_)

    # Enlaces externos con rel seguro
    html_ = html_.replace('<a href="http', '<a rel="noopener" href="http')

    return arreglar_tablas(html_)


def tramos(cuerpo: str) -> tuple[str, list[dict]]:
    md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists", "attr_list"])
    crudo = arreglar_html(md.convert(cuerpo))
    trozos = [t for t in re.split(r"(?=<h2)", crudo) if t.strip()]
    indice = []
    salida = []
    for trozo in trozos:
        m = re.match(r"<h2>(.*?)</h2>", trozo, flags=re.S)
        if m:
            titulo = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            ident = slug_id(titulo)
            trozo = trozo.replace(m.group(0), f'<h2 id="{ident}">{m.group(1)}</h2>', 1)
            indice.append({"titulo": titulo, "id": ident})
        salida.append(f'<section class="curso-tramo nz-prose">\n{trozo}\n</section>')
    return "\n".join(salida), indice


# --------------------------------------------------------------------------
# Plantillas
# --------------------------------------------------------------------------


def cabeza(titulo: str, descripcion: str, prefijo: str, packs: list[str], extra: str = "") -> str:
    enlaces = "\n".join(
        f'  <link rel="stylesheet" href="{AURORA}/packs/{p}">' for p in packs
    )
    return f"""<!DOCTYPE html>
<html lang="es" data-nz-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(titulo)}</title>
  <meta name="description" content="{html.escape(descripcion)}">
  <link rel="icon" type="image/svg+xml" href="{prefijo}favicon.svg">
  <link rel="stylesheet" href="{AURORA}/tokens.css">
{enlaces}
  <link rel="stylesheet" href="{prefijo}assets/curso.css">
{extra}
</head>"""


def barra(prefijo: str, raiz: str = "../index.html") -> str:
    return f"""<a class="curso-skip" href="#contenido">Saltar al contenido</a>
<header class="nz-navbar nz-navbar--bordered curso-barra">
  <div class="nz-container nz-navbar__brand">
    <a class="nz-navbar__link" href="{prefijo}index.html"><strong>Curso Mastermind</strong></a>
    <a class="nz-navbar__link" href="{raiz}">IAModa</a>
  </div>
  <nav class="nz-container nz-navbar__links" aria-label="Navegación principal">
    <a class="nz-navbar__link" href="{prefijo}index.html#programa">Programa</a>
    <a class="nz-navbar__link" href="{prefijo}index.html#requisitos">Requisitos</a>
    <a class="nz-navbar__link" href="{prefijo}modulos/01-que-es-un-agente/index.html">Empezar</a>
    <a class="nz-navbar__link" href="https://github.com/Ntizar/IAModa" rel="noopener">GitHub</a>
  </nav>
</header>"""


def pie(prefijo: str) -> str:
    return f"""<footer class="curso-pie">
  <div class="nz-container">
    <p><strong>Curso Mastermind</strong> · tu agente de IA para llevar el negocio.</p>
    <p>{ATRIBUCION} · contenido abierto para aprender, copiar y adaptar.</p>
  </div>
</footer>
<div class="curso-hud" role="group" aria-label="Controles de la presentación">
  <button class="nz-btn nz-btn--ghost nz-btn--icon" type="button" data-curso-anterior aria-label="Tramo anterior">←</button>
  <span class="curso-hud__cuenta">0 / 0</span>
  <button class="nz-btn nz-btn--ghost nz-btn--icon" type="button" data-curso-siguiente aria-label="Tramo siguiente">→</button>
  <button class="nz-btn nz-btn--soft nz-btn--sm" type="button" data-curso-salir="1">Salir</button>
</div>
<script src="{prefijo}assets/curso.js" defer></script>"""


def pagina_modulo(mod: dict, anterior: dict | None, siguiente: dict | None, total: int) -> str:
    cuerpo, indice = tramos(mod["cuerpo"])
    lista_indice = "\n".join(
        f'      <li><a href="#{i["id"]}">{html.escape(i["titulo"])}</a></li>' for i in indice
    )
    criterios = "\n".join(f"      <li>{html.escape(str(c))}</li>" for c in mod["criterios"])
    bloque_criterios = (
        f"""  <div class="curso-criterios">
    <p class="nz-eyebrow">Criterios de aceptación</p>
    <p>Al terminar este módulo, esto tiene que estar en verde:</p>
    <ol>
{criterios}
    </ol>
  </div>"""
        if criterios
        else ""
    )

    nav = []
    if anterior:
        nav.append(
            f"""    <a class="curso-navpie__enlace" href="../{anterior['slug']}/index.html">
      <span class="curso-navpie__rotulo">Anterior · {anterior['numero']}</span>
      <span>{html.escape(anterior['titulo'])}</span>
    </a>"""
        )
    if siguiente:
        nav.append(
            f"""    <a class="curso-navpie__enlace curso-navpie__enlace--siguiente" href="../{siguiente['slug']}/index.html">
      <span class="curso-navpie__rotulo">Siguiente · {siguiente['numero']}</span>
      <span>{html.escape(siguiente['titulo'])}</span>
    </a>"""
        )
    nav_html = "\n".join(nav) if nav else ""

    return f"""{cabeza(mod['titulo'] + ' · Curso Mastermind', mod['resumen'], '../../', packs_para(cuerpo + bloque_criterios))}
<body class="nz">
{barra('../../', '../../../index.html')}
<main class="curso-main nz-container" id="contenido">
  <nav class="nz-breadcrumb" aria-label="Migas de pan">
    <a href="../../index.html">Curso</a>
    <span class="nz-breadcrumb__sep">/</span>
    <span aria-current="page">Módulo {mod['numero']}</span>
  </nav>

  <header class="curso-cabecera">
    <p class="nz-eyebrow">Módulo {mod['numero']} de {total} · {html.escape(mod['nivel'])}</p>
    <h1 class="nz-h1">{html.escape(mod['titulo'])}</h1>
    <p class="nz-lead">{html.escape(mod['resumen'])}</p>
    <div class="curso-cabecera__meta">
      <span class="nz-badge nz-badge--neutral">{html.escape(mod['duracion'])}</span>
      <span class="nz-badge nz-badge--brand">{len(indice)} tramos</span>
      <button class="nz-btn nz-btn--accent nz-btn--sm" type="button" data-curso-presentar aria-pressed="false">Presentar</button>
    </div>
    <p class="curso-aviso-lectura nz-text--muted">Con <kbd class="nz-atajo-teclado">←</kbd> y <kbd class="nz-atajo-teclado">→</kbd> pasas de tramo; <kbd class="nz-atajo-teclado">Esc</kbd> vuelve a la lectura.</p>
  </header>

{bloque_criterios}

  <nav class="curso-indice" aria-label="Índice del módulo">
    <p class="nz-eyebrow">En este módulo</p>
    <ol>
{lista_indice}
    </ol>
  </nav>

{cuerpo}

  <nav class="curso-navpie" aria-label="Navegación entre módulos">
{nav_html}
  </nav>
</main>
{pie('../../')}
</body>
</html>
"""


def tarjeta(mod: dict) -> str:
    return f"""      <a class="nz-article nz-article--interactive curso-modulo" href="modulos/{mod['slug']}/index.html">
        <span class="curso-modulo__num">Módulo {mod['numero']}</span>
        <span class="nz-h3">{html.escape(mod['titulo'])}</span>
        <span class="nz-text--muted">{html.escape(mod['resumen'])}</span>
        <span class="curso-modulo__pie">
          <span class="nz-badge nz-badge--neutral">{html.escape(mod['duracion'])}</span>
          <span class="nz-badge nz-badge--outline">{len(mod['criterios'])} criterios</span>
        </span>
      </a>"""


def portada(lista: list[dict]) -> str:
    total = len(lista)
    tarjetas = "\n".join(tarjeta(m) for m in lista)
    fundamentos = [m for m in lista if int(m["numero"]) <= 6]
    negocio = [m for m in lista if 7 <= int(m["numero"]) <= 10]
    resto = [m for m in lista if int(m["numero"]) >= 11]

    def bloque_mods(mods: list[dict]) -> str:
        return ", ".join(f"{m['numero']} · {m['titulo']}" for m in mods)

    return f"""{cabeza('Curso Mastermind — tu agente de IA para llevar el negocio', 'Curso práctico desde cero: instala Hermes, monta tu repositorio, dale memoria y skills, y pon tu agente a llevar clientes, almacén, pedidos, redes y tu web.', '', packs_para('nz-kpi nz-article nz-stepper'))}
<body class="nz">
{barra('')}
<main id="contenido">
  <section class="nz-container curso-hero">
    <p class="nz-eyebrow">Curso práctico · castellano · desde cero</p>
    <h1 class="nz-display">Tu agente de IA,<br>trabajando en tu negocio</h1>
    <p class="nz-lead">No es un chat que responde preguntas: es un agente que tiene tu repositorio, tu
    memoria y tu oficio escrito en skills. En {total} módulos montas el tuyo y lo pones a llevar
    una sastrería de verdad: clientes con medidas, tejidos en almacén, encargos con plazos,
    contenido para redes y una web propia publicada.</p>
    <div class="curso-hero__acciones">
      <a class="nz-btn nz-btn--primary nz-btn--lg" href="modulos/01-que-es-un-agente/index.html">Empezar por el módulo 01</a>
      <a class="nz-btn nz-btn--outline" href="#programa">Ver el programa</a>
      <a class="nz-btn nz-btn--ghost" href="https://github.com/Ntizar/IAModa" rel="noopener">Ver el repositorio</a>
    </div>
    <div class="curso-hero__datos">
      <div class="nz-kpi nz-kpi--bordered">
        <span class="nz-kpi__label">Módulos</span>
        <span class="nz-kpi__value">{total}</span>
        <span class="nz-kpi__target">de 30 a 40 minutos cada uno</span>
      </div>
      <div class="nz-kpi nz-kpi--bordered">
        <span class="nz-kpi__label">Casos de negocio reales</span>
        <span class="nz-kpi__value nz-kpi__value--accent">5</span>
        <span class="nz-kpi__target">clientes, almacén, pedidos, redes y web</span>
      </div>
      <div class="nz-kpi nz-kpi--bordered">
        <span class="nz-kpi__label">Requisitos</span>
        <span class="nz-kpi__value">0</span>
        <span class="nz-kpi__target">de programación: copiar, pegar y pensar</span>
      </div>
    </div>
  </section>

  <section class="nz-container" aria-labelledby="que-consigues">
    <h2 class="nz-h2" id="que-consigues">Qué tienes al terminar</h2>
    <div class="nz-grid-auto nz-grid-auto--spacious">
      <article class="nz-article">
        <h3 class="nz-h3">Un agente con identidad</h3>
        <p>Instalado en tu ordenador, con un modelo elegido, un <code class="nz-code nz-code--inline">SOUL.md</code> que le dice cómo trabajar y una memoria que no se pierde al cerrar la sesión.</p>
      </article>
      <article class="nz-article">
        <h3 class="nz-h3">Un repositorio que es la verdad</h3>
        <p>Tu negocio en GitHub: identidad, skills, datos y scripts versionados. Si cambias de ordenador, clonas y sigues donde lo dejaste.</p>
      </article>
      <article class="nz-article">
        <h3 class="nz-h3">El oficio escrito en skills</h3>
        <p>El conocimiento de tu taller deja de estar en tu cabeza: queda en ficheros que el agente carga cuando toca, y que puedes vender, heredar o mejorar.</p>
      </article>
      <article class="nz-article">
        <h3 class="nz-h3">Rutinas que trabajan solas</h3>
        <p>Un informe cada mañana, aviso de stock bajo, recordatorio de pruebas y borradores de redes. Tú apruebas; él hace el trabajo pesado.</p>
      </article>
      <article class="nz-article">
        <h3 class="nz-h3">Tu web publicada</h3>
        <p>Catálogo de tejidos leído de tus datos reales y formulario de encargo, con Aurora y GitHub Pages. Sin cuotas y sin depender de nadie.</p>
      </article>
      <article class="nz-article">
        <h3 class="nz-h3">Criterio, no fe</h3>
        <p>Límites, permisos, coste y human loop: sabes qué puede tocar el agente y qué no, y cómo comprobar que lo que dice es verdad.</p>
      </article>
    </div>
  </section>

  <section class="nz-container" id="programa" aria-labelledby="titulo-programa">
    <h2 class="nz-h2" id="titulo-programa">Programa</h2>
    <p class="nz-lead">Tres bloques. En el primero montas el agente; en el segundo le enseñas el negocio;
    en el tercero lo pones a volar con web, rutinas y límites.</p>
    <div class="nz-bento">
      <div class="nz-article">
        <p class="nz-eyebrow">Bloque 1 · Fundamentos</p>
        <p>{html.escape(bloque_mods(fundamentos))}</p>
      </div>
      <div class="nz-article">
        <p class="nz-eyebrow">Bloque 2 · El negocio</p>
        <p>{html.escape(bloque_mods(negocio))}</p>
      </div>
      <div class="nz-article">
        <p class="nz-eyebrow">Bloque 3 · Web y autonomía</p>
        <p>{html.escape(bloque_mods(resto))}</p>
      </div>
    </div>
    <div class="nz-grid-auto nz-grid-auto--spacious" style="margin-block-start: var(--nz-space-6)">
{tarjetas}
    </div>
  </section>

  <section class="nz-container" id="requisitos" aria-labelledby="titulo-requisitos">
    <h2 class="nz-h2" id="titulo-requisitos">Antes de empezar</h2>
    <div class="nz-split">
      <div>
        <h3 class="nz-h3">Necesitas</h3>
        <ul class="nz-list nz-list--check">
          <li class="nz-list__item">Un ordenador con Windows, macOS o Linux (8 GB de RAM bastan).</li>
          <li class="nz-list__item">Conexión a internet y una cuenta de GitHub gratuita.</li>
          <li class="nz-list__item">Telegram en el móvil: es la forma más cómoda de hablar con tu agente.</li>
          <li class="nz-list__item">Una cuenta de modelo: <strong>NaN</strong> (recomendado en este curso), Nous Portal u OpenRouter.</li>
          <li class="nz-list__item">Los datos de tu negocio, aunque sea en un CSV hecho a mano.</li>
        </ul>
      </div>
      <div>
        <h3 class="nz-h3">No necesitas</h3>
        <ul class="nz-list">
          <li class="nz-list__item">Saber programar. Los scripts del curso se copian y se ejecutan.</li>
          <li class="nz-list__item">Un servidor ni pagar hosting: GitHub Pages es gratis.</li>
          <li class="nz-list__item">Contratar a nadie. El agente es el becario que no duerme.</li>
        </ul>
        <div class="nz-callout nz-callout--warn">
          <p><strong>Ojo con los datos personales.</strong> Los clientes reales se quedan en tu ordenador,
          fuera de git. En el repositorio van ejemplos inventados.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="nz-container" aria-labelledby="como-usar">
    <h2 class="nz-h2" id="como-usar">Cómo se usa el curso</h2>
    <div class="nz-grid-auto">
      <article class="nz-article">
        <p class="nz-eyebrow">1 · Lee</p>
        <p>Cada módulo abre con lo que vas a conseguir y los criterios que tienen que quedar en verde.</p>
      </article>
      <article class="nz-article">
        <p class="nz-eyebrow">2 · Ejecuta</p>
        <p>Los comandos están en bloques con botón de copiar. Si algo falla, el módulo trae los errores típicos.</p>
      </article>
      <article class="nz-article">
        <p class="nz-eyebrow">3 · Comprueba</p>
        <p>Checklist final. Si no está entera marcada, el módulo no está terminado: no se pasa al siguiente.</p>
      </article>
      <article class="nz-article">
        <p class="nz-eyebrow">4 · Preséntalo</p>
        <p>El botón «Presentar» convierte el módulo en tramos a pantalla completa, para clase o para repasar.</p>
      </article>
    </div>
  </section>
</main>
{pie('')}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def main() -> None:
    lista = modulos()
    if not lista:
        raise SystemExit("No hay módulos en contenido/")

    (RAIZ / "index.html").write_text(portada(lista), encoding="utf-8")
    (RAIZ / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Curso Mastermind">'
        '<rect width="64" height="64" rx="14" fill="#0b4fd9"/>'
        '<path d="M16 46V18h7l9 14 9-14h7v28h-7V30l-9 13-9-13v16z" fill="#ffffff"/>'
        "</svg>\n",
        encoding="utf-8",
    )

    if SALIDA.exists():
        shutil.rmtree(SALIDA)

    for i, mod in enumerate(lista):
        anterior = lista[i - 1] if i > 0 else None
        siguiente = lista[i + 1] if i + 1 < len(lista) else None
        destino = SALIDA / mod["slug"]
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "index.html").write_text(
            pagina_modulo(mod, anterior, siguiente, len(lista)), encoding="utf-8"
        )

    print(f"OK · {len(lista)} módulos · portada + modulos/ generados")
    for mod in lista:
        print(f"  {mod['numero']} · {mod['titulo']} → modulos/{mod['slug']}/index.html")


if __name__ == "__main__":
    main()
