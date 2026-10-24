---
titulo: Almacén de tejidos
numero: "08"
resumen: Control de stock con mínimos, consumo por encargo y aviso automático antes de quedarte a cero. La primera rutina que trabaja sin que la pidas.
duracion: 40 min
nivel: Con clientes y medidas ya en CSV
objetivo: Tener el almacén en datos, con consumo trazable y una alerta que se dispara sola cuando un tejido baja del mínimo.
criterios:
  - tejidos.csv tiene referencia, metros, mínimo y proveedor
  - El consumo descuenta metros y deja rastro del pedido
  - El script devuelve código de error cuando hay stock bajo (para poder automatizarlo)
  - El agente explica el estado del almacén sin inventar cifras
---

## Qué se controla y qué no

No necesitas un ERP. Necesitas responder tres preguntas todos los días:

1. ¿Qué tejido está por debajo del mínimo?
2. ¿Cuánto cuesta reponerlo y a quién se lo pido?
3. ¿Qué encargos dependen de un tejido que no llega?

Con esas tres, un CSV y un script tienes el 90 % del control. El otro 10 % es contar físicamente de
vez en cuando, porque ningún sistema sabe que un rollo estaba cortado a la mitad.

**`negocio/tejidos.csv`**

```csv
ref,nombre,composicion,color,metros,metros_minimos,precio_m,proveedor,plazo_dias
LANA-AZUL-01,Lana fría 120s,100% lana,Azul marino,6.4,8,42.50,Textiles Norte,12
LANA-GRIS-02,Lana fría 120s,100% lana,Gris perla,15.0,8,42.50,Textiles Norte,12
LINO-NAT-01,Lino belga,100% lino,Natural,3.1,5,28.00,Linera Sur,20
SEDA-BUR-01,Seda salvaje,100% seda,Burdeos,9.8,4,76.00,Sedas del Ebro,25
ALG-BLA-01,Algodón popelín,100% algodón,Blanco,22.0,10,9.80,Textiles Norte,7
```

Reglas:

- **`metros` es lo que hay físicamente**, no lo que dice el proveedor. Se actualiza al consumir y en
  el inventario mensual.
- **`metros_minimos` es el punto de pedido**, no el cero. Se calcula con el consumo medio y el plazo
  del proveedor: si tardan 12 días y gastas 0,5 m/día, el mínimo son 6 m más colchón.
- **La referencia no cambia nunca.** Si cambia el proveedor, se añade columna, no se renombra.

## Los comandos

```bash
python3 negocio/scripts/almacen.py lista
python3 negocio/scripts/almacen.py bajo-minimo
python3 negocio/scripts/almacen.py consumir LANA-AZUL-01 3.2 --pedido P-2026-014
```

`lista` enseña el almacén ordenado por urgencia. `bajo-minimo` imprime solo lo que hay que pedir y
**sale con código 1** si hay algo bajo: eso es lo que permite usarlo en un cron y que el sistema
sepa que hay un aviso.

Ejemplo de salida:

```text
REF             TEJIDO                 METROS   MÍNIMO   ESTADO
LANA-AZUL-01    Lana fría 120s           6.4      8.0   PEDIR (faltan 1.6 m)
LINO-NAT-01     Lino belga               3.1      5.0   PEDIR (faltan 1.9 m)
SEDA-BUR-01     Seda salvaje             9.8      4.0   ok
```

## Paso 1: consumo con trazabilidad

Cuando se corta un traje, el tejido sale del almacén. Si no lo descuentas el mismo día, el stock es
ficción.

```bash
python3 negocio/scripts/almacen.py consumir LANA-AZUL-01 3.46 --pedido P-2026-014
```

El script:

- comprueba que hay metros suficientes (si no, **no descuenta** y avisa);
- resta y redondea a dos decimales;
- apunta en `negocio/movimientos.csv` la fecha, la referencia, los metros y el pedido.

Ese movimiento es tu auditoría: si un mes no cuadra, se mira ahí.

## Paso 2: el aviso automático

Aquí empieza la autonomía. Primero a mano:

```bash
python3 negocio/scripts/almacen.py bajo-minimo; echo "código: $?"
```

`código: 1` significa «hay tejidos bajo mínimo». Ese detalle es lo que hace que un cron pueda avisar
solo cuando toca, sin mandarte ruido todos los días.

En el módulo 12 lo programas. Si quieres verlo ya, pídeselo al agente dentro del repositorio:

```text
Crea una tarea programada para cada lunes a las 8:00 que ejecute
`python3 negocio/scripts/almacen.py bajo-minimo` y me mande el resultado a Telegram.
Si no hay nada bajo mínimo, que no me escriba.
```

El agente tiene una herramienta de cron; no hace falta que toques ficheros. En el 11 veremos cómo
revisar que quedó bien y cómo evitar que te despierte a las 3 de la mañana.

## Paso 3: preguntarle al almacén

```text
Con los datos de negocio/tejidos.csv: ¿qué tejidos están bajo mínimo, cuánto cuesta reponerlos
hasta el mínimo y cuál es el proveedor con más plazo? Enséñame la tabla y el cálculo.
```

El agente debe leer el CSV, calcular `(mínimo − metros) × precio_m` por referencia y sumar. Si
redondea a ojo o inventa un proveedor, corrígelo y refuerza el skill con la regla del cálculo.

## Paso 4: inventario mensual (la verdad incómoda)

Una vez al mes, cuenta lo que hay de verdad y ajusta:

```bash
python3 negocio/scripts/almacen.py ajustar LANA-AZUL-01 6.0 --motivo "inventario mensual"
```

La diferencia entre el sistema y la realidad se llama merma no registrada, y casi siempre es:
recortes que no se apuntaron, un rollo mal medido o un encargo sin pedido. Si el descuadre es
grande, el problema no es el script: es que se está cortando sin registrar.

## Ejercicio

1. Carga tus tejidos reales (o inventa diez) con mínimo y plazo de proveedor.
2. Consume un tejido para un pedido y comprueba el movimiento.
3. Intenta consumir más metros de los que hay: el script debe negarse y explicar por qué.
4. Pide al agente un informe de reposición con coste total y plazo máximo.
5. Programa el aviso (o déjalo preparado para el módulo 12).

## Checklist: ¿lo tengo?

- [ ] `tejidos.csv` con referencia, metros, mínimo, precio y proveedor
- [ ] El consumo descuenta y apunta el movimiento con el pedido
- [ ] `bajo-minimo` devuelve código 1 cuando hay aviso
- [ ] El agente calcula la reposición con la fórmula, no a ojo
- [ ] Sé cuándo fue el último inventario físico

## Errores típicos

- **Poner el mínimo en cero.** Te enteras cuando ya no hay tela y el cliente espera.
- **Descontar «cuando me acuerde».** El stock deja de ser real en dos semanas.
- **Mezclar unidades**: metros, rollos y kilos en la misma columna. Una unidad por columna.
- **Un cron que avisa siempre**, aunque no haya nada: el ruido hace que dejes de leerlo.
- **Editar el CSV a mano mientras el script escribe**: usa el script o edita con el agente parado.

## Siguiente

Módulo 09: los pedidos. El almacén dice qué tienes; los pedidos dicen qué has prometido y para
cuándo. Ahí se gana o se pierde la reputación.
