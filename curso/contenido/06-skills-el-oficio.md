---
titulo: Skills: el oficio por escrito
numero: "06"
resumen: Conviertes cómo trabajas en procedimientos que el agente carga cuando los necesita. Incluye el skill de sastrería completo y cómo instalarlo.
duracion: 40 min
nivel: Desde cero
objetivo: Crear, instalar y probar un skill propio de sastrería, entendiendo la diferencia entre skill, memoria y nota.
criterios:
  - El skill está en ~/.hermes/skills/ y Hermes lo lista
  - Al pedir una tarea de sastrería, el agente lo carga sin que se lo recuerdes
  - El skill tiene criterios y errores típicos, no solo teoría
  - Sabes cuándo crear uno nuevo y cuándo ampliar el que ya existe
---

## Qué es un skill

Un fichero `SKILL.md`: un procedimiento con nombre y descripción que el agente consulta **solo
cuando la tarea encaja**. No se carga todo el catálogo en cada turno: eso es lo que permite tener
50 skills sin arruinarte en tokens.

Un skill no es un prompt bonito. Es conocimiento operativo:

- qué datos mirar y en qué orden;
- qué reglas no se saltan (medidas en centímetros, señal del 30 %…);
- qué comandos ejecutar;
- qué errores se cometen siempre;
- cómo saber que salió bien.

## Paso 1: estructura

```text
skills/sastreria/
└── SKILL.md
```

El `SKILL.md` empieza con dos campos obligatorios:

```markdown
---
name: sastreria
description: "Usa al trabajar con clientes, medidas, tejidos o encargos de sastrería."
---
```

La descripción es el disparador. Si escribes «cosas del taller», no se activará nunca. Tiene que
decir **cuándo** usarlo, en tercera persona y en menos de 60 caracteres si puedes.

## Paso 2: el contenido que de verdad sirve

Estructura que funciona:

```markdown
# Sastrería

## Datos y dónde están
- Clientes: negocio/clientes.csv (id, nombre, telefono, email, alta, notas)
- Medidas: negocio/medidas.csv (cliente_id, fecha, pecho, cintura, cadera, cuello, hombro, manga)
- Tejidos: negocio/tejidos.csv (ref, nombre, composicion, color, metros, metros_minimos, precio_m)
- Pedidos: negocio/pedidos.csv (id, cliente_id, prenda, tejido_ref, prueba, entrega, estado, importe)

## Reglas que no se rompen
1. Las medidas van en centímetros y con fecha: nunca reutilices una toma de hace más de un año sin avisar.
2. Un pedido no pasa a «en confección» sin señal cobrada.
3. No se promete fecha de entrega sin comprobar la carga de trabajo de esa semana.
4. Los datos reales están en negocio/produccion/, fuera de git: no los pegues en notas.

## Procedimiento: ficha de cliente
1. Busca por teléfono o nombre antes de crear: el 30 % de las fichas duplicadas vienen de aquí.
2. Crea la fila con id `C-<año>-<número>`.
3. Registra la toma de medidas en medidas.csv con la fecha de hoy.
4. Resume al cliente en tres líneas: qué se le ha hecho y qué le queda pendiente.

## Errores típicos
- Mezclar metros y centímetros (un traje se va a 3,2 m de tejido, no a 320).
- Dar por buena la última medida sin mirar la fecha.
- Redondear el importe antes de aplicar el IVA.

## Criterio de «hecho»
- La fila existe en el CSV y se puede volver a leer.
- El resumen cita el id y la fecha de medidas.
```

> Copia el skill completo del curso: `plantillas/skill-sastreria.md`.

## Paso 3: instalarlo

Los skills viven en `~/.hermes/skills/`. Para no mantener dos copias, enlaza el del repositorio:

```bash
ln -sfn ~/mi-agente/skills/sastreria ~/.hermes/skills/sastreria
```

En Windows (sin enlaces simbólicos cómodos), copia:

```powershell
Copy-Item -Recurse -Force "$HOME\mi-agente\skills\sastreria" "$HOME\.hermes\skills\sastreria"
```

Comprueba que Hermes lo ve:

```bash
hermes skills list
```

Y en una conversación:

```text
/sastreria
```

Si aparece el contenido, está instalado.

## Paso 4: probarlo de verdad

Dentro del repositorio, pide algo que solo se resuelva con el skill:

```text
Necesito la ficha de la clienta que llamó ayer, Marta Ruiz. Teléfono 600 000 000.
Toma las medidas que te doy: pecho 96, cintura 78, cadera 100, cuello 36, hombro 12, manga 60.
```

El agente debe: buscar duplicados, crear la ficha con el formato de id, añadir medidas con fecha y
resumir. Si improvisa otro formato, el skill no se cargó o está mal escrito.

## Paso 5: crear skills sin escribirlos a mano

Hermes tiene `/learn`, que convierte material real en un skill:

```text
/learn cómo tomo medidas en el taller: primero cintura, luego pecho, siempre sobre ropa fina,
y anoto la fecha porque la gente cambia de talla
```

También desde documentación o desde una conversación que acabas de tener. Después revisa el
resultado: el agente escribe deprisa y a veces inventa comandos.

## Cuándo crear uno nuevo

- La tarea se repite y tiene pasos estables.
- Cometes el mismo error dos veces.
- Hay una regla del negocio que el agente no puede deducir (precios, plazos, quién autoriza).

Cuando dudes: **amplía** el skill existente antes de crear otro. Cinco skills buenos valen más que
treinta de una línea.

## Ejercicio

1. Copia el skill de sastrería y adáptalo a tu negocio.
2. Añádele un procedimiento que hoy solo está en tu cabeza (por ejemplo, cómo calculas la tela con
   caída y merma).
3. Instálalo y pruébalo con tres peticiones distintas.
4. Anota en `notas/` qué falló y corrige el skill. Un skill que no se corrige es documentación
   muerta.

## Checklist: ¿lo tengo?

- [ ] `hermes skills list` muestra mi skill
- [ ] `/sastreria` carga el contenido
- [ ] El agente ha usado el formato de mis datos sin que se lo dictara
- [ ] El skill tiene reglas, errores típicos y criterio de «hecho»
- [ ] He corregido al menos una cosa después de probarlo

## Errores típicos

- **Descripción vaga** («ayuda con el taller»): el skill nunca se activa.
- **Skill que es un manual de 2.000 líneas**: se come el contexto. Un skill = una responsabilidad.
- **Duplicar el CSV dentro del skill**: el dato se queda viejo. El skill dice **dónde** mirar, no
  copia los datos.
- **Instalar y no probar**. Un skill sin prueba es una hipótesis.

## Siguiente

Módulo 07: el primero de negocio puro. Clientes y medidas, con datos de verdad y consultas que el
agente puede ejecutar sin inventar.
