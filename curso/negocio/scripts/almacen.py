#!/usr/bin/env python3
"""Almacén de tejidos: lista, aviso de mínimo, consumo y ajuste de inventario.

Ejemplos:
    python3 negocio/scripts/almacen.py lista
    python3 negocio/scripts/almacen.py bajo-minimo        # sale con código 1 si hay aviso
    python3 negocio/scripts/almacen.py consumir LANA-AZUL-01 3.46 --pedido P-2026-014
    python3 negocio/scripts/almacen.py ajustar LANA-AZUL-01 6.0 --motivo "inventario mensual"
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NEGOCIO = RAIZ / "negocio"
TEJIDOS = NEGOCIO / "tejidos.csv"
MOVIMIENTOS = NEGOCIO / "movimientos.csv"

CAMPOS_TEJIDO = [
    "ref", "nombre", "composicion", "color", "metros", "metros_minimos",
    "precio_m", "proveedor", "plazo_dias",
]
CAMPOS_MOVIMIENTO = ["fecha", "ref", "metros", "tipo", "pedido", "motivo"]


def leer(ruta: Path, campos: list[str]) -> list[dict]:
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8", newline="") as f:
        return [dict(fila) for fila in csv.DictReader(f)]


def escribir(ruta: Path, campos: list[str], filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({c: fila.get(c, "") for c in campos})


def num(valor: str) -> float:
    return float(str(valor).replace(",", ".") or 0)


def bajo_minimo(t: dict) -> bool:
    return num(t["metros"]) < num(t["metros_minimos"])


def apuntar(ref: str, metros: float, tipo: str, pedido: str = "", motivo: str = "") -> None:
    filas = leer(MOVIMIENTOS, CAMPOS_MOVIMIENTO)
    filas.append(
        {
            "fecha": date.today().isoformat(),
            "ref": ref,
            "metros": f"{metros:+g}",
            "tipo": tipo,
            "pedido": pedido,
            "motivo": motivo,
        }
    )
    escribir(MOVIMIENTOS, CAMPOS_MOVIMIENTO, filas)


def cmd_lista(args: argparse.Namespace) -> int:
    tejidos = leer(TEJIDOS, CAMPOS_TEJIDO)
    if not tejidos:
        print("No hay tejidos. Crea negocio/tejidos.csv")
        return 1
    print(f"{'REF':<16}{'TEJIDO':<24}{'METROS':>8}{'MÍNIMO':>9}   ESTADO")
    for t in sorted(tejidos, key=lambda x: (not bajo_minimo(x), x["ref"])):
        estado = "PEDIR" if bajo_minimo(t) else "ok"
        print(f"{t['ref']:<16}{t['nombre'][:23]:<24}{num(t['metros']):>8.2f}{num(t['metros_minimos']):>9.1f}   {estado}")
    return 0


def cmd_bajo_minimo(args: argparse.Namespace) -> int:
    tejidos = [t for t in leer(TEJIDOS, CAMPOS_TEJIDO) if bajo_minimo(t)]
    if not tejidos:
        print("Sin tejidos bajo mínimo.")
        return 0
    total = 0.0
    print("TEJIDOS BAJO MÍNIMO")
    for t in tejidos:
        faltan = num(t["metros_minimos"]) - num(t["metros"])
        coste = faltan * num(t["precio_m"])
        total += coste
        print(
            f"{t['ref']:<16}{t['nombre'][:22]:<23} quedan {num(t['metros']):.2f} m "
            f"· faltan {faltan:.2f} m · {coste:.2f} € · {t['proveedor']} ({t['plazo_dias']} días)"
        )
    print(f"Coste de reposición hasta mínimo: {total:.2f} €")
    return 1


def cmd_consumir(args: argparse.Namespace) -> int:
    if args.metros <= 0:
        print("ERROR: los metros deben ser mayores que cero.")
        return 2
    tejidos = leer(TEJIDOS, CAMPOS_TEJIDO)
    tejido = next((t for t in tejidos if t["ref"] == args.ref), None)
    if not tejido:
        print(f"No existe el tejido {args.ref}")
        return 1
    disponibles = num(tejido["metros"])
    if args.metros > disponibles:
        print(
            f"ERROR: no hay suficiente {args.ref}. Disponibles {disponibles:.2f} m, "
            f"pedidos {args.metros:.2f} m. No se descuenta nada."
        )
        return 2
    tejido["metros"] = f"{disponibles - args.metros:.2f}"
    escribir(TEJIDOS, CAMPOS_TEJIDO, tejidos)
    apuntar(args.ref, -args.metros, "consumo", args.pedido or "", "")
    print(f"{args.ref}: {-args.metros:+.2f} m · quedan {tejido['metros']} m")
    if num(tejido["metros"]) < num(tejido["metros_minimos"]):
        print(f"AVISO: {args.ref} está por debajo del mínimo ({tejido['metros_minimos']} m).")
    return 0


def cmd_ajustar(args: argparse.Namespace) -> int:
    if args.metros < 0:
        print("ERROR: el stock no puede ser negativo.")
        return 2
    tejidos = leer(TEJIDOS, CAMPOS_TEJIDO)
    tejido = next((t for t in tejidos if t["ref"] == args.ref), None)
    if not tejido:
        print(f"No existe el tejido {args.ref}")
        return 1
    antes = num(tejido["metros"])
    tejido["metros"] = f"{args.metros:.2f}"
    escribir(TEJIDOS, CAMPOS_TEJIDO, tejidos)
    apuntar(args.ref, args.metros - antes, "ajuste", "", args.motivo or "inventario")
    print(f"{args.ref}: ajuste {args.metros - antes:+.2f} m (antes {antes:.2f}, ahora {args.metros:.2f})")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Almacén de tejidos")
    sub = p.add_subparsers(dest="comando", required=True)

    sub.add_parser("lista").set_defaults(func=cmd_lista)
    sub.add_parser("bajo-minimo").set_defaults(func=cmd_bajo_minimo)

    c = sub.add_parser("consumir")
    c.add_argument("ref")
    c.add_argument("metros", type=float)
    c.add_argument("--pedido", default="")
    c.set_defaults(func=cmd_consumir)

    a = sub.add_parser("ajustar")
    a.add_argument("ref")
    a.add_argument("metros", type=float)
    a.add_argument("--motivo", default="")
    a.set_defaults(func=cmd_ajustar)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
