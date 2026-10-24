#!/usr/bin/env python3
"""Genera el JSON público del catálogo de tejidos desde negocio/tejidos.csv.

No publica coste, mínimo de stock ni proveedor: solo lo que el cliente debe ver.

Uso: python3 web/scripts/generar.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TEJIDOS = RAIZ / "negocio" / "tejidos.csv"
SALIDA = RAIZ / "web" / "datos-tejidos.json"


def num(valor: str) -> float:
    return float(str(valor).replace(",", ".") or 0)


def main() -> None:
    if not TEJIDOS.exists():
        raise SystemExit("No existe negocio/tejidos.csv")
    publicos = []
    with TEJIDOS.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            metros = num(fila["metros"])
            publicos.append(
                {
                    "ref": fila["ref"],
                    "nombre": fila["nombre"],
                    "composicion": fila["composicion"],
                    "color": fila["color"],
                    "metros": round(metros, 1),
                    "disponible": metros >= 3,
                }
            )
    SALIDA.write_text(json.dumps(publicos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(publicos)} tejidos publicados en {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
