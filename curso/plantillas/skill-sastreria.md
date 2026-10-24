---
name: sastreria
description: "Usa al trabajar con clientes, medidas, tejidos o encargos de sastrería."
---

# Sastrería

## Datos y dónde están

- Clientes: `negocio/clientes.csv` (id, nombre, telefono, email, alta, notas)
- Medidas: `negocio/medidas.csv` (cliente_id, fecha, pecho, cintura, cadera, cuello, hombro, manga)
- Tejidos: `negocio/tejidos.csv` (ref, nombre, composicion, color, metros, metros_minimos, precio_m, proveedor, plazo_dias)
- Pedidos: `negocio/pedidos.csv` (id, cliente_id, prenda, tejido_ref, fecha_encargo, fecha_prueba, fecha_entrega, estado, importe, senal, notas)
- Movimientos: `negocio/movimientos.csv` (fecha, ref, metros, tipo, pedido, motivo)

Los datos reales están en `negocio/produccion/`, fuera de git. No los pegues en notas ni en chats.

## Herramientas

Se usan los scripts, nunca la memoria del modelo:

```bash
python3 negocio/scripts/clientes.py buscar TEXTO
python3 negocio/scripts/clientes.py ficha ID
python3 negocio/scripts/clientes.py alta --nombre "..." --telefono ...
python3 negocio/scripts/clientes.py medidas ID --pecho 96 --cintura 78 ...
python3 negocio/scripts/almacen.py lista
python3 negocio/scripts/almacen.py bajo-minimo
python3 negocio/scripts/almacen.py consumir REF METROS --pedido ID
python3 negocio/scripts/pedidos.py entregas --dias 7
python3 negocio/scripts/pedidos.py estado ID NUEVO_ESTADO
python3 negocio/scripts/informe.py
```

## Reglas que no se rompen

1. Las medidas van en centímetros y con fecha. No reutilices una toma de más de un año sin avisar.
2. Un pedido no pasa a `en_confeccion` sin señal cobrada.
3. No se promete fecha de entrega sin comprobar la carga de la semana (`entregas --dias 7`).
4. Estados válidos: presupuesto, aceptado, en_confeccion, prueba, ajustes, entregado, cancelado.
5. Los importes llevan IVA incluido salvo que se diga lo contrario.
6. Para calcular tejido: metros del patrón × (1 + merma). Merma habitual: 8 % traje, 10 % vestido.

## Procedimiento: ficha de cliente

1. Busca por teléfono y por nombre antes de crear. El 30 % de las fichas duplicadas viene de aquí.
2. Crea la ficha si no existe (el script asigna `C-AÑO-NNN`).
3. Registra la toma de medidas con la fecha de hoy.
4. Resume al cliente en tres líneas: qué se le ha hecho y qué queda pendiente.

## Errores típicos

- Mezclar metros y centímetros (un traje se va a 3,2 m de tejido, no a 320).
- Dar por buena la última medida sin mirar la fecha.
- Redondear el importe antes de aplicar el IVA.
- Descontar stock «a ojo» sin usar `consumir`.
- Confirmar una entrega sin mirar los pedidos ya comprometidos de esa semana.

## Criterio de «hecho»

- La fila existe en el CSV y se puede volver a leer.
- El resumen cita el id del cliente y la fecha de las medidas.
- Si hubo cálculo, se enseña el cálculo.
