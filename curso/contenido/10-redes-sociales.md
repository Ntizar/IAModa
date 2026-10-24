---
titulo: Redes sociales con criterio
numero: "10"
resumen: Calendario, pilares de contenido y borradores que tú apruebas. Publicar sin parecer un robot y sin regalar tu trabajo a un algoritmo.
duracion: 40 min
nivel: Con el negocio en datos
objetivo: Tener un calendario editorial que el agente rellena con borradores basados en encargos reales, con aprobación humana antes de publicar.
criterios:
  - calendario.csv tiene fecha, red, pilar, formato, estado y texto
  - El agente propone contenido usando datos reales del taller, no genéricos
  - Nada se publica sin estado aprobado
  - Tengo tres pilares de contenido y un ritmo sostenible
---

## La regla que evita el ridículo

Un sastre no necesita «virality». Necesita que la gente de su ciudad sepa que hace trajes a medida,
que entrega a tiempo y que tiene criterio. Eso se consigue con **pocas publicaciones buenas** y
constancia, no con cien posts genéricos generados por IA.

Y hay una línea roja: **la IA redacta, tú apruebas**. Publicar sin revisar es la forma más rápida de
que tu cuenta diga una barbaridad sobre un cliente o un precio.

## Tres pilares (elige los tuyos)

| Pilar | Qué cuenta | Ejemplo |
|---|---|---|
| **Oficio** | Cómo se hace algo, sin desvelar lo que te diferencia | «Por qué la entretela importa más que la tela» |
| **Prueba** | Trabajo terminado, con permiso del cliente | Detalle de un ojal, forro, ajuste |
| **Casa** | Quién eres, horarios, cómo se pide cita | «Los viernes cierro a las 14:00» |

Reparto sano: 40 % oficio, 40 % prueba, 20 % casa. Si todo es «mira qué bonito», no te diferencias.
Si todo es educativo, no vendes.

## El calendario

**`redes/calendario.csv`**

```csv
fecha,red,pilar,formato,estado,texto,notas
2026-10-26,instagram,oficio,reel,"Por qué planchamos antes de coser el bajo",borrador,
2026-10-28,instagram,prueba,post,"Detalle del forro de un traje de novio",aprobado,Cliente autorizó por escrito
2026-10-30,telegram,casa,texto,"Cerrado viernes 30 por inventario",borrador,
```

Estados: `idea` → `borrador` → `aprobado` → `publicado` → `descartado`. Nada salta de `borrador` a
`publicado`.

## Paso 1: el script de la semana

```bash
python3 redes/scripts/calendario.py semana
python3 redes/scripts/calendario.py pendientes
python3 redes/scripts/calendario.py estado 2026-10-28 aprobado
```

`semana` enseña lo que toca publicar en los próximos siete días, con huecos. `pendientes` lista lo
que está en borrador esperando tu aprobación.

## Paso 2: que proponga, no que invente

Dentro del repositorio:

```text
Con el skill de redes: mira los pedidos entregados de las últimas dos semanas y los tejidos nuevos
en almacén. Propón cinco ideas de contenido para los próximos diez días: tres de oficio y dos de
prueba. Para cada una: pilar, formato, gancho en una línea y qué foto haría falta.
No escribas el texto final todavía.
```

Lo que buscas: ideas **ancladas a tu realidad** (un tejido que acaba de llegar, un encargo que salió
bien), no «5 razones para amar la sastrería».

Después pides el texto de las que te gusten:

```text
Desarrolla las ideas 1 y 4 en texto para Instagram: máximo 700 caracteres, sin emojis, sin
signos de exclamación, con una llamada a la acción a pedir cita por teléfono. Añádelas al
calendario como borrador, no como aprobado.
```

## Paso 3: aprobar y publicar

Tú revisas y cambias el estado:

```bash
python3 redes/scripts/calendario.py estado 2026-10-28 aprobado
```

Publicar puede ser:

- **Manual** (lo más sensato al principio): abres la app, copias, publicas. Dos minutos.
- **Programado con la herramienta oficial** de la red (Meta Business Suite, etc.).
- **Con API**, solo si tienes cuenta profesional y claves. Requiere código y permisos; el agente
  puede hacerlo, pero entonces el estado `aprobado` es obligatorio y la clave vive en `.env`.

> El curso no te empuja a automatizar la publicación. Te empuja a no publicar sin leer. La
> diferencia entre un community manager y un generador de spam es exactamente esa.

## Paso 4: medir sin engañarte

Cada semana, anota tres números por red: alcance, guardados y mensajes recibidos. No likes: no
pagan el alquiler.

```text
Con los datos que te pego de la semana, dime qué dos publicaciones trajeron más mensajes y qué
tienen en común. No me des una lista de diez consejos genéricos: tres conclusiones con la cifra.
```

Y una regla de negocio: **si un contenido funciona, se repite con otro ángulo**. Si no funciona,
se descarta sin drama.

## Ejercicio

1. Define tus tres pilares y escríbelos en `skills/redes/SKILL.md`.
2. Rellena dos semanas de calendario, con huecos incluidos.
3. Pide al agente cinco ideas ancladas a tus datos y elige dos.
4. Redacta, corrige y aprueba una. Publícala a mano.
5. Anota el resultado en la columna `notas` al día siguiente.

## Checklist: ¿lo tengo?

- [ ] Calendario con estados y fechas ISO (`AAAA-MM-DD`)
- [ ] Tres pilares definidos y un ritmo que puedo sostener
- [ ] El agente propone desde datos reales del taller
- [ ] Nada pasa a publicado sin mi aprobación
- [ ] Tengo permiso escrito para las fotos de clientes

## Errores típicos

- **Pedirle «30 posts para un mes»**. Saldrán 30 variaciones del mismo post malo.
- **Publicar fotos de clientes sin permiso**. Un traje de novia reconocible es un dato personal.
- **Prometer plazos en redes que luego no cumples**. El calendario no conoce tu carga de trabajo;
  tú sí.
- **Automatizar publicación sin revisar**. Un error de precio publicado cuesta dinero real.
- **Medir likes**. Mide mensajes y citas.

## Siguiente

Módulo 11: tu web propia. Catálogo de tejidos que se actualiza solo desde tu CSV y una página que
puedes enseñar sin vergüenza.
