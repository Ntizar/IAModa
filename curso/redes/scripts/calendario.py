#!/usr/bin/env python3
"""Calendario editorial: qué toca esta semana, qué espera aprobación y cambio de estado.

Ejemplos:
    python3 redes/scripts/calendario.py semana
    python3 redes/scripts/calendario.py pendientes
    python3 redes/scripts/calendario.py estado 2026-10-28 aprobado
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CALENDARIO = RAIZ / "redes" / "calendario.csv"
CAMPOS = ["fecha", "red", "pilar", "formato", "estado", "texto", "notas"]
ESTADOS = ["idea", "borrador", "aprobado", "publicado", "descartado"]


def leer() -> list[dict]:
    if not CALENDARIO.exists():
        return []
    with CALENDARIO.open(encoding="utf-8", newline="") as f:
        return [dict(fila) for fila in csv.DictReader(f)]


def escribir(filas: list[dict]) -> None:
    CALENDARIO.parent.mkdir(parents=True, exist_ok=True)
    with CALENDARIO.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({c: fila.get(c, "") for c in CAMPOS})


def fecha(valor: str):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def linea(f: dict) -> str:
    return f"{f['fecha']}  {f['red']:<11}{f['pilar']:<10}{f['estado']:<11}{f.get('texto','')[:60]}"


def cmd_semana(args: argparse.Namespace) -> int:
    hoy = date.today()
    limite = hoy + timedelta(days=7)
    filas = [f for f in leer() if (d := fecha(f.get("fecha", ""))) and hoy <= d <= limite]
    if not filas:
        print("Nada programado en los próximos 7 días. Toca rellenar el calendario.")
        return 0
    print("ESTA SEMANA")
    for f in sorted(filas, key=lambda x: x["fecha"]):
        print(linea(f))
    huecos = 7 - len({f["fecha"] for f in filas})
    print(f"\nHuecos sin contenido: {max(huecos, 0)} día(s)")
    return 0


def cmd_pendientes(args: argparse.Namespace) -> int:
    filas = [f for f in leer() if f["estado"] in {"borrador", "idea"}]
    if not filas:
        print("Nada pendiente de aprobar. O vas sobrado o el calendario está vacío.")
        return 0
    print("PENDIENTES DE APROBACIÓN")
    for f in sorted(filas, key=lambda x: x["fecha"]):
        print(linea(f))
        if f.get("texto"):
            print(f"    «{f['texto']}»")
    return 0


def cmd_estado(args: argparse.Namespace) -> int:
    if args.nuevo not in ESTADOS:
        print(f"ERROR: estado desconocido. Válidos: {', '.join(ESTADOS)}")
        return 2
    if not fecha(args.fecha):
        print("ERROR: la fecha va en formato AAAA-MM-DD.")
        return 2
    filas = leer()
    tocadas = 0
    for f in filas:
        if f["fecha"] == args.fecha and (not args.red or f["red"] == args.red):
            f["estado"] = args.nuevo
            tocadas += 1
    if not tocadas:
        print("No hay ninguna publicación con esa fecha.")
        return 1
    escribir(filas)
    print(f"{tocadas} publicación(es) del {args.fecha} → {args.nuevo}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Calendario de contenido")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("semana").set_defaults(func=cmd_semana)
    sub.add_parser("pendientes").set_defaults(func=cmd_pendientes)
    e = sub.add_parser("estado")
    e.add_argument("fecha")
    e.add_argument("nuevo")
    e.add_argument("--red", default="")
    e.set_defaults(func=cmd_estado)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
