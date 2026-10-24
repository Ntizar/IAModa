---
titulo: Pedidos y encargos
numero: "09"
resumen: Del «me lo apunto» al estado verificable: fechas de prueba y entrega, señal, cambios de estado y una lista semanal que evita retrasos.
duracion: 40 min
nivel: Con clientes y almacén funcionando
objetivo: Gestionar encargos con estados, fechas y señal, y tener una vista semanal que el agente puede preparar y vigilar.
criterios:
  - pedidos.csv tiene estados definidos y fechas de prueba y entrega
  - Un pedido no avanza a confección sin señal registrada
  - El script lista entregas próximas y pedidos parados
  - El agente puede responder «qué tengo esta semana» con datos reales
---

## Un pedido es una promesa con fecha

Todo lo demás (tejido, botones, hilo) se puede arreglar. Una fecha incumplida, no. Por eso el pedido
se guarda con lo mínimo que permite cumplir:

**`negocio/pedidos.csv`**

```csv
id,cliente_id,prenda,tejido_ref,fecha_encargo,fecha_prueba,fecha_entrega,estado,importe,senal,notas
P-2026-014,C-2026-002,Traje dos piezas,LANA-AZUL-01,2026-10-02,2026-10-20,2026-10-30,en_confeccion,890.00,267.00,Entallado en cintura
P-2026-015,C-2026-001,Vestido largo,SEDA-BUR-01,2026-10-05,2026-10-22,2026-11-05,prueba,650.00,195.00,
P-2026-016,C-2026-001,Camisa a medida,ALG-BLA-01,2026-10-06,2026-10-24,2026-11-02,presupuesto,120.00,0.00,Pendiente de confirmar
```

## Los estados, cerrados

| Estado | Significado | Quién puede pasar al siguiente |
|---|---|---|
| `presupuesto` | Enviado, sin confirmar | El cliente, pagando señal |
| `aceptado` | Confirmado con señal | Tú, al planificar la confección |
| `en_confeccion` | En el taller | Tú, al terminar |
| `prueba` | Cita de prueba hecha | Tú, tras ajustes |
| `ajustes` | Vuelve al taller | Tú, al terminar |
| `entregado` | En manos del cliente | — |
| `cancelado` | No sigue | Tú, con motivo en notas |

Sin estados cerrados pasa lo de siempre: cada uno llama «en proceso» a una cosa distinta y el
informe miente. La regla del curso: **si no está en la lista, no existe**.

## Los comandos

```bash
python3 negocio/scripts/pedidos.py lista
python3 negocio/scripts/pedidos.py lista --estado prueba
python3 negocio/scripts/pedidos.py entregas --dias 7
python3 negocio/scripts/pedidos.py parados --dias 10
python3 negocio/scripts/pedidos.py estado P-2026-014 en_confeccion
```

- `lista`: todos, ordenados por fecha de entrega.
- `entregas --dias 7`: lo que vence esta semana. Es la vista que salva el negocio.
- `parados --dias 10`: pedidos cuya fase actual lleva más de 10 días vencida (prueba pasada y aún
  sin terminar, encargo aceptado sin entrar en confección). Detecta lo que se quedó dormido.
- `estado`: cambia el estado y **valida** que la transición tenga sentido.

El validador no te deja pasar de `presupuesto` a `en_confeccion` sin señal. Es incómodo una vez y
te evita trabajar gratis diez veces.

## Paso 1: crear un pedido

```bash
python3 negocio/scripts/pedidos.py alta \
  --cliente C-2026-002 --prenda "Traje dos piezas" --tejido LANA-AZUL-01 \
  --prueba 2026-10-20 --entrega 2026-10-30 --importe 890
```

El script comprueba:

- que el cliente existe;
- que el tejido existe y hay metros suficientes (avisa, no bloquea: puede estar pedido);
- que la fecha de entrega es posterior a la de prueba;
- que la señal por defecto es el 30 % del importe.

## Paso 2: planificar la semana

```bash
python3 negocio/scripts/pedidos.py entregas --dias 7
```

Salida típica:

```text
ENTREGAS PRÓXIMAS (7 días)
P-2026-014  Traje dos piezas   C-2026-002   2026-10-30   en_confeccion   señal 267.00
P-2026-016  Camisa a medida   C-2026-001   2026-11-02   presupuesto     señal 0.00  ← sin señal
```

Ese «sin señal» es exactamente lo que quieres ver antes de cortar tela.

## Paso 3: que el agente lleve la agenda

```text
Prepara mi lunes: usa pedidos.py para listar las entregas de los próximos 7 días y los pedidos
parados más de 10 días. Para cada uno dime cliente, prenda, fecha y qué acción toca. No inventes
teléfonos: están en clientes.csv.
```

El agente debe ejecutar los scripts y montar una tabla. Si se salta el script y «recuerda» pedidos,
tienes un problema de skill: añade al `SKILL.md` la regla «los pedidos se consultan con
`pedidos.py`, nunca de memoria».

## Paso 4: retrasos sin dramas

Un retraso se gestiona antes de que ocurra:

1. `entregas --dias 7` el lunes y el jueves.
2. Si un pedido no va a llegar, se avisa **ese día**, no el día de la entrega.
3. Se propone fecha nueva y, si procede, una compensación (un ajuste gratis, prioridad en el
   siguiente).
4. Se apunta en `notas/` el motivo: así el informe trimestral dice la verdad.

Pídele al agente que redacte el mensaje, pero **no que lo envíe**. En el módulo 13 verás por qué
esto es una regla y no una manía.

## Ejercicio

1. Crea tres pedidos con estados distintos.
2. Intenta saltarte la señal: el script debe impedirlo.
3. Ejecuta `entregas --dias 7` y `parados --dias 10` y compara con tu agenda real.
4. Pide al agente el plan del lunes y corrígelo si se inventa algo.
5. Escribe en `notas/` una regla tuya de negocio que no esté en el skill (por ejemplo, «los viernes
   no se entregan trajes»).

## Checklist: ¿lo tengo?

- [ ] `pedidos.csv` con los siete estados y fechas completas
- [ ] La señal se registra y bloquea el paso a confección
- [ ] `entregas --dias 7` me dice la verdad de esta semana
- [ ] `parados` detecta lo dormido
- [ ] El agente prepara el plan usando los scripts, no de memoria

## Errores típicos

- **Estados libres** («en curso», «casi», «pendiente de…»): el informe deja de ser fiable.
- **Fechas en formato distinto** (`30/10/26`, `30-10-2026`): usa siempre `AAAA-MM-DD`.
- **Importe sin IVA y con IVA mezclados**: decide una convención y escríbela en el skill.
- **Contar la señal como ingreso disponible**: está cobrada, pero es un compromiso. Anótalo aparte.
- **Pedirle al agente que «avise a todos los clientes»**: eso es una acción externa masiva. Se
  prepara, se revisa y se envía por lotes aprobados.

## Siguiente

Módulo 10: redes sociales. El mismo rigor, pero con contenido: calendario, borradores y aprobación
antes de publicar.
