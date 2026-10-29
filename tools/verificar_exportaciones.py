# -*- coding: utf-8 -*-
"""Verificador de exportaciones del patron IAModa (H1).

Comprueba que las muestras generadas desde el probador real (gancho
window.__patronTest) sean ficheros validos:
  - SVG 1:1   -> XML valido, unidades en cm, regla de 10 cm, piezas
  - PDF A4    -> estructura %PDF correcta, xref coherente, paginas >= 2
  - DXF R12   -> AC1009, pares codigo/valor, POLYLINE/VERTEX/TEXT
  - dom.json  -> conteo de elementos dibujados y sin overflow horizontal

Uso:  python tools/verificar_exportaciones.py [carpeta]
      (por defecto tools/exportaciones-muestra junto a este script)
Las muestras se generan con tools/probar_en_navegador.md (receta) o
automaticamente durante la sesion de pruebas del patron.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CARPETA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "exportaciones-muestra"
fallos = []


def check(nombre, cond, detalle=""):
    estado = "ok " if cond else "FALLO"
    print(f"  [{estado}] {nombre}" + (f" — {detalle}" if detalle else ""))
    if not cond:
        fallos.append(nombre)


def verificar_svg(ruta):
    print("SVG 1:1")
    texto = ruta.read_text(encoding="utf-8")
    raiz = ET.fromstring(texto)  # XML bien formado
    NS = "{http://www.w3.org/2000/svg}"
    w, h = raiz.get("width", ""), raiz.get("height", "")
    check("unidades en cm", w.endswith("cm") and h.endswith("cm"), f"{w} x {h}")
    check("tiene regla de verificacion", raiz.find(f".//{NS}g[@id='regla']") is not None)
    check("texto 10 cm", "10 cm" in texto)
    check("etiqueta 1:1", "ESCALA 1:1" in texto)
    piezas = len(raiz.findall(f".//{NS}g[@transform]"))
    check("piezas >= 2", piezas >= 2, f"{piezas} grupos")
    lineas = len(raiz.findall(f".//{NS}line"))
    check("rejilla dibujada", lineas > 50, f"{lineas} lineas")
    check("piquetes naranjas", 'stroke="#ff6a00"' in texto)
    check("lineas de costura discontinuas", 'stroke-dasharray="0.9 1.1"' in texto)


def verificar_pdf(ruta):
    print("PDF A4")
    bruto = ruta.read_bytes()
    check("cabecera %PDF-1.4", bruto.startswith(b"%PDF-1.4"))
    check("marca %%EOF", bruto.rstrip().endswith(b"%%EOF"))
    texto = bruto.decode("latin-1")
    n_paginas = len(re.findall(r"/Type /Page[^s]", texto))
    check("paginas >= 2", n_paginas >= 2, f"{n_paginas} paginas")
    m = re.search(r"/Type /Pages .*?/Count (\d+)", texto, re.S)
    check("/Count coincide", bool(m) and int(m.group(1)) == n_paginas, m.group(1) if m else "?")
    check("MediaBox A4", "/MediaBox [0 0 595.28 841.89]" in texto)
    check("portada con titulo", "IAModa - patron" in texto)
    check("regla de impresion", "10 cm - imprime al 100" in texto)
    check("solape declarado", "solape 1.5 cm" in texto)
    # xref: cada offset debe apuntar a "N 0 obj"
    sx = int(re.search(r"startxref\s+(\d+)", texto).group(1))
    check("startxref apunta a xref", texto[sx:sx + 4] == "xref")
    entradas = re.findall(r"(\d{10}) 00000 n", texto[sx:])
    correctos = sum(1 for i, v in enumerate(entradas, start=1)
                    if texto[int(v):].startswith(f"{i} 0 obj"))
    check("xref coherente", correctos == len(entradas), f"{correctos}/{len(entradas)} offsets")
    # cada stream declara su Length exacta
    ok_len, total = True, 0
    for m2 in re.finditer(r"/Length (\d+) >>\nstream\n", texto):
        total += 1
        ini = m2.end()
        if not texto[ini + int(m2.group(1)):].startswith("\nendstream"):
            ok_len = False
    check("streams con Length exacta", ok_len and total >= 1, f"{total} streams")


def verificar_dxf(ruta):
    print("DXF R12")
    lineas = ruta.read_text(encoding="ascii").splitlines()
    check("pares codigo/valor", len(lineas) % 2 == 0, f"{len(lineas)} lineas")
    check("AC1009 (R12)", "AC1009" in lineas)
    check("marca EOF", lineas[-1] == "EOF")
    check("POLYLINE >= 2", lineas.count("POLYLINE") >= 2, str(lineas.count("POLYLINE")))
    check("VERTEX >= 20", lineas.count("VERTEX") >= 20, str(lineas.count("VERTEX")))
    check("capa PINZAS", "PINZAS" in lineas)
    check("capa PIQUETES", "PIQUETES" in lineas)
    check("capa ETIQUETAS", "ETIQUETAS" in lineas)
    textos = [lineas[i + 1] for i, v in enumerate(lineas) if v == "1" and i + 1 < len(lineas)]
    check("titulo de patron", any("PATRON" in t for t in textos))
    # codigos de grupo validos (numeros)
    codigos = [int(x) for i, x in enumerate(lineas) if i % 2 == 0]
    check("codigos de grupo numericos", all(c >= 0 for c in codigos))


def verificar_dom(ruta):
    print("DOM del probador")
    dom = json.loads(ruta.read_text(encoding="utf-8"))
    check("piezas >= 2", dom["piezas"] >= 2, str(dom))
    check("margen de costura dibujado", dom["margen"] >= 2)
    check("lineas de costura >= 2", dom["costura"] >= 2)
    check("pinzas >= 1", dom["pinza"] >= 1)
    check("piquetes >= 4", dom["piquete"] >= 4)
    check("hilos >= 2", dom["hilo"] >= 2)
    check("sin overflow horizontal", dom["overflow"] is False)


def main():
    print(f"Verificador de exportaciones — carpeta: {CARPETA}\n")
    esperados = {
        "patron-1a1.svg": verificar_svg,
        "patron-a4.pdf": verificar_pdf,
        "patron-r12.dxf": verificar_dxf,
        "dom.json": verificar_dom,
    }
    if not CARPETA.exists() or not any((CARPETA / n).exists() for n in esperados):
        print("Faltan muestras: abre el probador y ejecuta el gancho")
        print("window.__patronTest() (receta en tools/probar_en_navegador.md),")
        print("guarda los ficheros en esta carpeta y vuelve a lanzar este script.")
        return 1
    for nombre, fn in esperados.items():
        ruta = CARPETA / nombre
        if not ruta.exists():
            print(f"{nombre}: FALLO — no existe\n")
            fallos.append(nombre)
            continue
        try:
            fn(ruta)
        except Exception as e:  # noqa: BLE001
            fallos.append(nombre)
            print(f"  [FALLO] excepcion: {type(e).__name__}: {e}")
        print()
    if fallos:
        print(f"RESULTADO: {len(fallos)} fallo(s): {', '.join(fallos)}")
        return 1
    print("RESULTADO: todas las exportaciones son validas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
