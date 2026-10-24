---
titulo: Identidad y memoria
numero: "05"
resumen: SOUL.md, USER.md y MEMORY.md. Le dices quién es, cómo habla, qué sabe de ti y qué tiene que recordar entre sesiones.
duracion: 35 min
nivel: Desde cero
objetivo: Escribir una identidad breve y útil, y una memoria que sobreviva al cierre de sesión, sin llenarla de ruido.
criterios:
  - SOUL.md está copiado en ~/.hermes/ y se nota en la primera respuesta
  - MEMORY.md tiene 5-10 entradas densas, no un diario
  - El agente recuerda un dato en una sesión nueva
  - Sabes qué va en memoria y qué va en skill
---

## Tres ficheros, tres trabajos

| Fichero | Dónde | Para qué | Límite |
|---|---|---|---|
| `SOUL.md` | `~/.hermes/SOUL.md` | Identidad: quién es, cómo trabaja, qué no hace | Sin límite duro: sé breve |
| `USER.md` | `~/.hermes/memories/USER.md` | Quién eres tú: gustos, contexto, manías | 1.375 caracteres |
| `MEMORY.md` | `~/.hermes/memories/MEMORY.md` | Lo que el agente aprende del entorno y del negocio | 2.200 caracteres |

Los dos últimos se cargan **al empezar cada sesión** y no cambian a mitad (snapshot congelado).
Por eso, cuando guardas algo importante, se ve en la siguiente sesión, no en la actual.

Y un cuarto, específico del proyecto: `identidad/AGENTS.md` dentro del repositorio. Es el mapa que
el agente lee cuando trabaja ahí: dónde está cada cosa y qué está prohibido.

## Paso 1: escribe tu SOUL.md

Copia la plantilla del curso y adáptala:

```bash
cp plantillas/SOUL-ejemplo.md identidad/SOUL.md
```

La plantilla tiene esta forma (recórtala, no la infles):

```markdown
# Identidad

Eres el asistente de taller de [NOMBRE DEL NEGOCIO], una sastrería en [CIUDAD].
Trabajas para [TU NOMBRE]. Español de España, tuteo, directo, sin florituras.

## Qué haces
- Llevas clientes, medidas, tejidos y pedidos con los datos de `negocio/`.
- Preparas informes y borradores; no publicas ni envías nada sin aprobación.
- Cuando falta un dato, lo dices. No lo inventas nunca.

## Cómo trabajas
- Antes de opinar sobre stock o plazos, lee el CSV. Nunca de memoria.
- Si un cálculo afecta a dinero o a una fecha de entrega, enseña el cálculo.
- Un «hecho» va con prueba: ruta del fichero, commit o mensaje enviado.

## Lo que no haces nunca
- Inventar medidas, precios o disponibilidad.
- Publicar en redes o mandar mensajes a clientes sin que yo lo apruebe.
- Tocar ficheros fuera de este repositorio.
```

Guárdalo y cópialo a la instalación:

```bash
cp identidad/SOUL.md ~/.hermes/SOUL.md
```

En Windows, la ruta es `%USERPROFILE%\.hermes\SOUL.md`.

> Si usas perfiles de Hermes, el fichero va en `~/.hermes/profiles/TU-PERFIL/SOUL.md`. No mezcles
> el agente del curso con el que ya tengas en producción.

## Paso 2: escribe tu USER.md

Es tu ficha, no la del negocio. Ejemplo real y compacto:

```markdown
[yo] David, sastre en Madrid. 12 años de taller. Odio el relleno.
[prefs] Respuestas cortas, con la cifra delante. Nada de emojis en informes.
[horario] Taller de 9 a 19; reviso el móvil a las 8:30 y a las 18:00.
[decisiones] Precios con IVA incluido. Señal del 30 % para encargos a medida.
[datos] Los clientes reales están en negocio/produccion/, fuera de git.
```

El agente lo gestiona con la herramienta `memory`, pero también puedes escribirlo a mano:

```bash
cp plantillas/USER.md ~/.hermes/memories/USER.md
```

## Paso 3: deja que la memoria se llene sola (pero con criterio)

Pídele esto en una conversación dentro del repositorio:

```text
Guarda en memoria, de forma compacta: (1) el negocio es una sastrería y los datos viven en negocio/;
(2) no publico nada en redes sin aprobarlo; (3) los informes se entregan los lunes a las 8:00.
```

Comprueba el fichero:

```bash
cat ~/.hermes/memories/MEMORY.md
```

Abre una sesión **nueva** (`/new` o salir y entrar) y pregúntale: «¿Qué sabes de mi negocio?».
Debe citar las tres cosas.

## Paso 4: qué NO va en memoria

La memoria es cara (se inyecta en cada turno) y pequeña. No es un diario:

| No va en memoria | Va en |
|---|---|
| El procedimiento de tomar medidas | Un skill `sastreria` |
| La lista de 80 clientes | `negocio/clientes.csv` |
| Lo que pasó el martes | `notas/2026-01-20-....md` |
| El horario de un proveedor concreto | El CSV de proveedores, o una nota |

Regla práctica: si la frase empieza por «cuando…» o «para hacer…», es un **skill**. Si empieza por
«mi negocio es…» o «prefiero…», es **memoria**.

## Paso 5: AGENTS.md, el mapa del repositorio

`identidad/AGENTS.md` (o `AGENTS.md` en la raíz) le dice al agente dónde está cada cosa cuando
trabaja en el proyecto:

```markdown
# Mapa del repositorio

- `negocio/` — datos del taller. `produccion/` es privado y no se toca sin permiso.
- `skills/` — procedimientos. Cada carpeta es un skill con su SKILL.md.
- `redes/` — calendario y borradores. Nada se publica sin aprobación.
- `web/` — web pública. Se genera desde `negocio/tejidos.csv`.
- `notas/` — decisiones y aprendizajes, una nota por tema y fecha.

## Prohibido
- Editar ficheros de `negocio/produccion/` sin decírmelo.
- Inventar cifras: si falta un dato, se pregunta.
```

Ponlo en la raíz del repo si trabajas siempre ahí:

```bash
cp identidad/AGENTS.md AGENTS.md
```

## Ejercicio

1. Adapta `SOUL.md` a tu negocio (máximo 40 líneas).
2. Escribe tu `USER.md` con cinco entradas.
3. Pide al agente que guarde tres hechos en memoria y compruébalos en `MEMORY.md`.
4. Abre sesión nueva y verifica que los recuerda.
5. Si algo no lo recuerda, mira el fichero antes de culpar al modelo: casi siempre no se guardó.

## Checklist: ¿lo tengo?

- [ ] `~/.hermes/SOUL.md` es mío y se nota en el tono de las respuestas
- [ ] `USER.md` tiene 5 entradas y no pasa del límite
- [ ] `MEMORY.md` tiene entre 5 y 10 entradas densas
- [ ] Una sesión nueva recuerda lo guardado
- [ ] Tengo un `AGENTS.md` que explica el repositorio y lo prohibido

## Errores típicos

- **SOUL.md de 300 líneas** con la historia de tu vida: come contexto y no mejora nada.
- **Meter datos de clientes en memoria**: se inyectan en cada turno y se filtran con facilidad.
- **Creer que «lo recuerda» sin comprobarlo**. La memoria solo existe si se llamó a la herramienta
  y el texto está en el fichero.
- **Editar `MEMORY.md` a mano mientras otra sesión escribe**: puede pisarse. Mejor pídeselo al
  agente o hazlo con la sesión cerrada.

## Siguiente

Módulo 06: skills. El oficio deja de estar en tu cabeza y pasa a estar en un fichero que el agente
carga solo cuando toca.
