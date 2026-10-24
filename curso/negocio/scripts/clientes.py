#!/usr/bin/env python3
"""Clientes y medidas de una sastrería. Solo biblioteca estándar.

Ejemplos:
    python3 negocio/scripts/clientes.py buscar ruiz
    python3 negocio/scripts/clientes.py ficha C-2026-002
    python3 negocio/scripts/clientes.py alta --nombre "Marta Ruiz" --telefono 600000000
    python3 negocio/scripts/clientes.py medidas C-2026-002 --pecho 96 --cintura 78 --cadera 100
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NEGOCIO = RAIZ / "negocio"
CLIENTES = NEGOCIO / "clientes.csv"
MEDIDAS = NEGOCIO / "medidas.csv"

CAMPOS_CLIENTE = ["id", "nombre", "telefono", "email", "alta", "notas"]
CAMPOS_MEDIDA = [
    "cliente_id", "fecha", "pecho", "cintura", "cadera", "cuello", "hombro", "manga", "notas",
]


def leer(ruta: Path, campos: list[str]) -> list[dict]:
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        if lector.fieldnames != campos:
            print(f"AVISO: {ruta.name} tiene cabeceras distintas de las esperadas: {lector.fieldnames}")
        return [dict(fila) for fila in lector]


def escribir(ruta: Path, campos: list[str], filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({c: fila.get(c, "") for c in campos})


def normalizar_telefono(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor or "")
    if len(digitos) == 9:
        return digitos
    if len(digitos) == 11 and digitos.startswith("34"):
        return digitos[2:]
    return digitos


def buscar(clientes: list[dict], texto: str) -> list[dict]:
    t = texto.strip().lower()
    return [
        c for c in clientes
        if t in (c.get("nombre") or "").lower() or t in normalizar_telefono(c.get("telefono", ""))
    ]


def ultima_medida(medidas: list[dict], cliente_id: str) -> dict | None:
    suyas = [m for m in medidas if m.get("cliente_id") == cliente_id]
    if not suyas:
        return None
    return sorted(suyas, key=lambda m: m.get("fecha", ""))[-1]


def imprimir_ficha(cliente: dict, medidas: list[dict]) -> None:
    print(f"{cliente['id']}  {cliente['nombre']}  {cliente.get('telefono','')}  alta {cliente.get('alta','')}")
    if cliente.get("email"):
        print(f"  email: {cliente['email']}")
    if cliente.get("notas"):
        print(f"  notas: {cliente['notas']}")
    suyas = sorted([m for m in medidas if m.get("cliente_id") == cliente["id"]], key=lambda m: m.get("fecha", ""))
    if not suyas:
        print("  sin medidas registradas")
        return
    print(f"  {len(suyas)} toma(s) de medidas")
    for m in suyas:
        valores = " ".join(
            f"{k} {m[k]}" for k in ("pecho", "cintura", "cadera", "cuello", "hombro", "manga") if m.get(k)
        )
        print(f"    {m['fecha']}  {valores}  {m.get('notas','')}".rstrip())
    if len(suyas) >= 2:
        antes, ahora = suyas[-2], suyas[-1]
        cambios = [
            f"{k} {float(ahora[k]) - float(antes[k]):+.1f}"
            for k in ("pecho", "cintura", "cadera", "cuello", "hombro", "manga")
            if antes.get(k) and ahora.get(k) and abs(float(ahora[k]) - float(antes[k])) >= 0.5
        ]
        if cambios:
            print("  cambios respecto a la toma anterior: " + ", ".join(cambios))
        else:
            print("  sin cambios significativos respecto a la toma anterior")


def siguiente_id(clientes: list[dict], anio: int) -> str:
    prefijo = f"C-{anio}-"
    numeros = [
        int(c["id"].split("-")[-1]) for c in clientes
        if c.get("id", "").startswith(prefijo) and c["id"].split("-")[-1].isdigit()
    ]
    return f"{prefijo}{max(numeros, default=0) + 1:03d}"


def cmd_buscar(args: argparse.Namespace) -> int:
    clientes = leer(CLIENTES, CAMPOS_CLIENTE)
    medidas = leer(MEDIDAS, CAMPOS_MEDIDA)
    encontrados = buscar(clientes, args.texto)
    if not encontrados:
        print("Sin resultados. Prueba con parte del nombre o con el teléfono.")
        return 1
    for c in encontrados:
        imprimir_ficha(c, medidas)
    return 0


def cmd_ficha(args: argparse.Namespace) -> int:
    clientes = leer(CLIENTES, CAMPOS_CLIENTE)
    medidas = leer(MEDIDAS, CAMPOS_MEDIDA)
    cliente = next((c for c in clientes if c["id"] == args.id), None)
    if not cliente:
        print(f"No existe la ficha {args.id}")
        return 1
    imprimir_ficha(cliente, medidas)
    return 0


def cmd_alta(args: argparse.Namespace) -> int:
    clientes = leer(CLIENTES, CAMPOS_CLIENTE)
    telefono = normalizar_telefono(args.telefono)
    if not telefono:
        print("ERROR: el teléfono es obligatorio y debe tener dígitos.")
        return 2
    for c in clientes:
        if normalizar_telefono(c.get("telefono", "")) == telefono:
            print("Ya existe una ficha con ese teléfono. No se crea duplicado:")
            imprimir_ficha(c, leer(MEDIDAS, CAMPOS_MEDIDA))
            return 2
    nuevo = {
        "id": siguiente_id(clientes, date.today().year),
        "nombre": args.nombre.strip(),
        "telefono": telefono,
        "email": (args.email or "").strip(),
        "alta": args.alta or date.today().isoformat(),
        "notas": (args.notas or "").strip(),
    }
    clientes.append(nuevo)
    escribir(CLIENTES, CAMPOS_CLIENTE, clientes)
    print(f"Alta creada: {nuevo['id']}  {nuevo['nombre']}  {nuevo['telefono']}")
    return 0


def cmd_medidas(args: argparse.Namespace) -> int:
    clientes = leer(CLIENTES, CAMPOS_CLIENTE)
    if not any(c["id"] == args.cliente for c in clientes):
        print(f"No existe la ficha {args.cliente}. Créala antes con `alta`.")
        return 1
    medidas = leer(MEDIDAS, CAMPOS_MEDIDA)
    fila = {"cliente_id": args.cliente, "fecha": args.fecha or date.today().isoformat()}
    for campo in ("pecho", "cintura", "cadera", "cuello", "hombro", "manga"):
        valor = getattr(args, campo)
        if valor is not None and valor <= 0:
            print(f"ERROR: {campo} debe ser mayor que cero (se mide en centímetros).")
            return 2
        fila[campo] = "" if valor is None else f"{valor:g}"
    fila["notas"] = (args.notas or "").strip()
    if not any(fila.get(k) for k in ("pecho", "cintura", "cadera", "cuello", "hombro", "manga")):
        print("ERROR: no has dado ninguna medida.")
        return 2
    medidas.append(fila)
    escribir(MEDIDAS, CAMPOS_MEDIDA, medidas)
    print(f"Medidas añadidas a {args.cliente} con fecha {fila['fecha']}.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Clientes y medidas de la sastrería")
    sub = p.add_subparsers(dest="comando", required=True)

    b = sub.add_parser("buscar", help="Busca por nombre o teléfono")
    b.add_argument("texto")
    b.set_defaults(func=cmd_buscar)

    f = sub.add_parser("ficha", help="Ficha completa con historial de medidas")
    f.add_argument("id")
    f.set_defaults(func=cmd_ficha)

    a = sub.add_parser("alta", help="Crea una ficha nueva")
    a.add_argument("--nombre", required=True)
    a.add_argument("--telefono", required=True)
    a.add_argument("--email", default="")
    a.add_argument("--alta", default="")
    a.add_argument("--notas", default="")
    a.set_defaults(func=cmd_alta)

    m = sub.add_parser("medidas", help="Añade una toma de medidas (centímetros)")
    m.add_argument("cliente")
    for campo in ("pecho", "cintura", "cadera", "cuello", "hombro", "manga"):
        m.add_argument(f"--{campo}", type=float, default=None)
    m.add_argument("--fecha", default="")
    m.add_argument("--notas", default="")
    m.set_defaults(func=cmd_medidas)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
