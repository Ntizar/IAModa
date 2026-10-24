#!/usr/bin/env python3
"""Pedidos y encargos: lista, alta, entregas próximas, parados y cambio de estado.

Ejemplos:
    python3 negocio/scripts/pedidos.py lista
    python3 negocio/scripts/pedidos.py entregas --dias 7
    python3 negocio/scripts/pedidos.py parados --dias 10
    python3 negocio/scripts/pedidos.py estado P-2026-014 en_confeccion
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NEGOCIO = RAIZ / "negocio"
PEDIDOS = NEGOCIO / "pedidos.csv"
CLIENTES = NEGOCIO / "clientes.csv"
TEJIDOS = NEGOCIO / "tejidos.csv"

CAMPOS = [
    "id", "cliente_id", "prenda", "tejido_ref", "fecha_encargo", "fecha_prueba",
    "fecha_entrega", "estado", "importe", "senal", "notas",
]
CAMPOS_CLIENTE = ["id", "nombre", "telefono", "email", "alta", "notas"]
CAMPOS_TEJIDO = [
    "ref", "nombre", "composicion", "color", "metros", "metros_minimos",
    "precio_m", "proveedor", "plazo_dias",
]

ESTADOS = ["presupuesto", "aceptado", "en_confeccion", "prueba", "ajustes", "entregado", "cancelado"]
TRANSICIONES = {
    "presupuesto": {"aceptado", "cancelado"},
    "aceptado": {"en_confeccion", "cancelado"},
    "en_confeccion": {"prueba", "cancelado"},
    "prueba": {"ajustes", "entregado", "cancelado"},
    "ajustes": {"prueba", "entregado", "cancelado"},
    "entregado": set(),
    "cancelado": set(),
}


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


def fecha(valor: str) -> date | None:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def num(valor: str) -> float:
    return float(str(valor).replace(",", ".") or 0)


def siguiente_id(pedidos: list[dict], anio: int) -> str:
    prefijo = f"P-{anio}-"
    numeros = [
        int(p["id"].split("-")[-1]) for p in pedidos
        if p.get("id", "").startswith(prefijo) and p["id"].split("-")[-1].isdigit()
    ]
    return f"{prefijo}{max(numeros, default=0) + 1:03d}"


def linea(p: dict, clientes: dict, hoy: date) -> str:
    cliente = clientes.get(p["cliente_id"], {})
    entrega = fecha(p.get("fecha_entrega", ""))
    dias = (entrega - hoy).days if entrega else None
    cuando = f"{dias:+d} d" if dias is not None else "sin fecha"
    aviso = ""
    if p["estado"] == "presupuesto" and num(p.get("senal", "0")) == 0:
        aviso = "  ← sin señal"
    return (
        f"{p['id']}  {p['prenda'][:24]:<25}{cliente.get('nombre','?')[:20]:<21}"
        f"{p.get('fecha_entrega',''):<12}{p['estado']:<14}{cuando:>7}{aviso}"
    )


def cmd_lista(args: argparse.Namespace) -> int:
    pedidos = leer(PEDIDOS, CAMPOS)
    clientes = {c["id"]: c for c in leer(CLIENTES, CAMPOS_CLIENTE)}
    if args.estado:
        pedidos = [p for p in pedidos if p["estado"] == args.estado]
    if not pedidos:
        print("No hay pedidos que mostrar.")
        return 0
    hoy = date.today()
    print(f"{'ID':<12}{'PRENDA':<25}{'CLIENTE':<21}{'ENTREGA':<12}{'ESTADO':<14}{'FALTAN':>7}")
    for p in sorted(pedidos, key=lambda x: x.get("fecha_entrega", "")):
        print(linea(p, clientes, hoy))
    return 0


def cmd_entregas(args: argparse.Namespace) -> int:
    pedidos = leer(PEDIDOS, CAMPOS)
    clientes = {c["id"]: c for c in leer(CLIENTES, CAMPOS_CLIENTE)}
    hoy = date.today()
    limite = hoy + timedelta(days=args.dias)
    proximos = [
        p for p in pedidos
        if p["estado"] not in {"entregado", "cancelado"}
        and (f := fecha(p.get("fecha_entrega", ""))) and hoy <= f <= limite
    ]
    if not proximos:
        print(f"Sin entregas en los próximos {args.dias} días.")
        return 0
    print(f"ENTREGAS PRÓXIMAS ({args.dias} días)")
    for p in sorted(proximos, key=lambda x: x["fecha_entrega"]):
        print(linea(p, clientes, hoy))
    return 0


def cmd_parados(args: argparse.Namespace) -> int:
    pedidos = leer(PEDIDOS, CAMPOS)
    clientes = {c["id"]: c for c in leer(CLIENTES, CAMPOS_CLIENTE)}
    hoy = date.today()
    limite = hoy - timedelta(days=args.dias)
    parados = []
    for p in pedidos:
        if p["estado"] in {"entregado", "cancelado"}:
            continue
        referencia = fecha(p.get("fecha_prueba", "")) or fecha(p.get("fecha_encargo", ""))
        if referencia and referencia <= limite:
            parados.append(p)
    if not parados:
        print(f"Sin pedidos parados más de {args.dias} días.")
        return 0
    print(f"PEDIDOS CON FASE VENCIDA (más de {args.dias} días)")
    for p in parados:
        print(linea(p, clientes, hoy))
    return 0


def cmd_alta(args: argparse.Namespace) -> int:
    clientes = {c["id"]: c for c in leer(CLIENTES, CAMPOS_CLIENTE)}
    tejidos = {t["ref"]: t for t in leer(TEJIDOS, CAMPOS_TEJIDO)}
    if args.cliente not in clientes:
        print(f"No existe el cliente {args.cliente}. Créalo antes con clientes.py alta.")
        return 1
    if args.tejido and args.tejido not in tejidos:
        print(f"No existe el tejido {args.tejido}. Revisa tejidos.csv.")
        return 1
    prueba, entrega = fecha(args.prueba), fecha(args.entrega)
    if not prueba or not entrega:
        print("ERROR: las fechas van en formato AAAA-MM-DD.")
        return 2
    if entrega <= prueba:
        print("ERROR: la entrega debe ser posterior a la prueba.")
        return 2
    pedidos = leer(PEDIDOS, CAMPOS)
    senal = args.senal if args.senal is not None else round(args.importe * 0.30, 2)
    nuevo = {
        "id": siguiente_id(pedidos, date.today().year),
        "cliente_id": args.cliente,
        "prenda": args.prenda,
        "tejido_ref": args.tejido or "",
        "fecha_encargo": date.today().isoformat(),
        "fecha_prueba": args.prueba,
        "fecha_entrega": args.entrega,
        "estado": "presupuesto",
        "importe": f"{args.importe:.2f}",
        "senal": f"{senal:.2f}",
        "notas": args.notas or "",
    }
    pedidos.append(nuevo)
    escribir(PEDIDOS, CAMPOS, pedidos)
    print(f"Pedido {nuevo['id']} creado en estado presupuesto · importe {nuevo['importe']} € · señal {nuevo['senal']} €")
    if args.tejido:
        disponibles = num(tejidos[args.tejido]["metros"])
        if disponibles < 3.5:
            print(f"AVISO: quedan {disponibles:.2f} m de {args.tejido}. Comprueba antes de prometer fecha.")
    return 0


def cmd_estado(args: argparse.Namespace) -> int:
    if args.nuevo not in ESTADOS:
        print(f"ERROR: estado desconocido. Válidos: {', '.join(ESTADOS)}")
        return 2
    pedidos = leer(PEDIDOS, CAMPOS)
    pedido = next((p for p in pedidos if p["id"] == args.id), None)
    if not pedido:
        print(f"No existe el pedido {args.id}")
        return 1
    actual = pedido["estado"]
    if args.nuevo == actual:
        print(f"{args.id} ya está en {actual}.")
        return 0
    if args.nuevo not in TRANSICIONES.get(actual, set()):
        permitidos = ", ".join(sorted(TRANSICIONES.get(actual, set()))) or "ninguno"
        print(f"ERROR: no se puede pasar de {actual} a {args.nuevo}. Permitidos: {permitidos}.")
        return 2
    if args.nuevo == "aceptado" and num(pedido.get("senal", "0")) <= 0:
        print("ERROR: sin señal cobrada no se acepta el pedido. Registra la señal primero.")
        return 2
    pedido["estado"] = args.nuevo
    escribir(PEDIDOS, CAMPOS, pedidos)
    print(f"{args.id}: {actual} → {args.nuevo}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Pedidos de la sastrería")
    sub = p.add_subparsers(dest="comando", required=True)

    l = sub.add_parser("lista")
    l.add_argument("--estado", choices=ESTADOS)
    l.set_defaults(func=cmd_lista)

    e = sub.add_parser("entregas")
    e.add_argument("--dias", type=int, default=7)
    e.set_defaults(func=cmd_entregas)

    pa = sub.add_parser("parados")
    pa.add_argument("--dias", type=int, default=10)
    pa.set_defaults(func=cmd_parados)

    a = sub.add_parser("alta")
    a.add_argument("--cliente", required=True)
    a.add_argument("--prenda", required=True)
    a.add_argument("--tejido", default="")
    a.add_argument("--prueba", required=True)
    a.add_argument("--entrega", required=True)
    a.add_argument("--importe", type=float, required=True)
    a.add_argument("--senal", type=float, default=None)
    a.add_argument("--notas", default="")
    a.set_defaults(func=cmd_alta)

    s = sub.add_parser("estado")
    s.add_argument("id")
    s.add_argument("nuevo")
    s.set_defaults(func=cmd_estado)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
