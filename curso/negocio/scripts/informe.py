#!/usr/bin/env python3
"""Informe semanal del taller: pedidos, entregas, stock y cobros pendientes.

Uso:
    python3 negocio/scripts/informe.py
    python3 negocio/scripts/informe.py --json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NEGOCIO = RAIZ / "negocio"


def leer(nombre: str) -> list[dict]:
    ruta = NEGOCIO / nombre
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8", newline="") as f:
        return [dict(fila) for fila in csv.DictReader(f)]


def num(valor) -> float:
    return float(str(valor).replace(",", ".") or 0)


def fecha(valor: str):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def construir(hoy: date | None = None) -> dict:
    hoy = hoy or date.today()
    limite = hoy + timedelta(days=7)
    pedidos = leer("pedidos.csv")
    clientes = {c["id"]: c for c in leer("clientes.csv")}
    tejidos = leer("tejidos.csv")

    activos = [p for p in pedidos if p.get("estado") not in {"entregado", "cancelado"}]
    entregas = [
        p for p in activos
        if (f := fecha(p.get("fecha_entrega", ""))) and hoy <= f <= limite
    ]
    pruebas = [
        p for p in activos
        if (f := fecha(p.get("fecha_prueba", ""))) and hoy <= f <= limite
    ]
    stock = [
        t for t in tejidos if num(t.get("metros", 0)) < num(t.get("metros_minimos", 0))
    ]
    pendiente_cobro = sum(
        max(num(p.get("importe", 0)) - num(p.get("senal", 0)), 0)
        for p in activos
        if p.get("estado") != "presupuesto"
    )
    sin_senal = [p for p in activos if p.get("estado") == "presupuesto" and num(p.get("senal", 0)) == 0]

    def fila(p: dict, campo_fecha: str = "fecha_entrega") -> dict:
        return {
            "id": p["id"],
            "cliente": clientes.get(p.get("cliente_id", ""), {}).get("nombre", "?"),
            "prenda": p.get("prenda", ""),
            "fecha": p.get(campo_fecha, ""),
            "estado": p.get("estado", ""),
            "importe": num(p.get("importe", 0)),
            "senal": num(p.get("senal", 0)),
        }

    return {
        "fecha": hoy.isoformat(),
        "entregas_7_dias": [fila(p) for p in sorted(entregas, key=lambda x: x["fecha_entrega"])],
        "pruebas_7_dias": [fila(p, "fecha_prueba") for p in sorted(pruebas, key=lambda x: x["fecha_prueba"])],
        "stock_bajo": [
            {
                "ref": t["ref"],
                "nombre": t["nombre"],
                "metros": num(t["metros"]),
                "minimo": num(t["metros_minimos"]),
                "faltan": round(num(t["metros_minimos"]) - num(t["metros"]), 2),
                "coste": round((num(t["metros_minimos"]) - num(t["metros"])) * num(t["precio_m"]), 2),
                "proveedor": t.get("proveedor", ""),
                "plazo_dias": t.get("plazo_dias", ""),
            }
            for t in stock
        ],
        "pendiente_cobro": round(pendiente_cobro, 2),
        "presupuestos_sin_senal": [fila(p) for p in sin_senal],
        "pedidos_activos": len(activos),
    }


def texto(datos: dict) -> str:
    lineas = [f"INFORME DEL TALLER · {datos['fecha']}", ""]
    lineas.append(f"Pedidos activos: {datos['pedidos_activos']} · Pendiente de cobro: {datos['pendiente_cobro']:.2f} €")

    lineas += ["", "ENTREGAS (7 días)"]
    if datos["entregas_7_dias"]:
        for p in datos["entregas_7_dias"]:
            lineas.append(f"  {p['fecha']}  {p['id']}  {p['cliente']}  {p['prenda']}  [{p['estado']}]")
    else:
        lineas.append("  ninguna")

    lineas += ["", "PRUEBAS (7 días)"]
    if datos["pruebas_7_dias"]:
        for p in datos["pruebas_7_dias"]:
            lineas.append(f"  {p['fecha']}  {p['id']}  {p['cliente']}  {p['prenda']}")
    else:
        lineas.append("  ninguna")

    lineas += ["", "STOCK BAJO MÍNIMO"]
    if datos["stock_bajo"]:
        for t in datos["stock_bajo"]:
            lineas.append(
                f"  {t['ref']}  quedan {t['metros']:.2f} m (mínimo {t['minimo']:.1f}) · "
                f"faltan {t['faltan']:.2f} m · {t['coste']:.2f} € · {t['proveedor']} ({t['plazo_dias']} días)"
            )
    else:
        lineas.append("  todo por encima del mínimo")

    if datos["presupuestos_sin_senal"]:
        lineas += ["", "PRESUPUESTOS SIN SEÑAL"]
        for p in datos["presupuestos_sin_senal"]:
            lineas.append(f"  {p['id']}  {p['cliente']}  {p['prenda']}  {p['importe']:.2f} €")

    return "\n".join(lineas)


def main() -> int:
    p = argparse.ArgumentParser(description="Informe del taller")
    p.add_argument("--json", action="store_true", help="Salida JSON para automatizar")
    args = p.parse_args()
    datos = construir()
    print(json.dumps(datos, ensure_ascii=False, indent=2) if args.json else texto(datos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
