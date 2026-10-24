---
titulo: Autonomía: rutinas y copias
numero: "12"
resumen: Conviertes el agente en un empleado que trabaja aunque no estés: informes, avisos, digest y copias de seguridad, con coste controlado.
duracion: 40 min
nivel: Con el negocio funcionando
objetivo: Tener dos rutinas fiables (informe semanal y aviso de stock), saber comprobarlas y tener una copia recuperable del sistema.
criterios:
  - Hay al menos una tarea programada que se ha ejecutado de verdad
  - El resultado llega al canal correcto y no genera ruido cuando no hay nada
  - Sé lanzar la tarea a mano para probarla
  - Tengo copia del repositorio y de la instalación de Hermes
---

## Qué merece la pena automatizar

Solo tres cosas, al principio:

1. **Lo que haces siempre a la misma hora** (informe del lunes, cierre de caja).
2. **Lo que si se olvida cuesta dinero** (stock bajo, entrega próxima sin señal).
3. **Lo que quieres leer con el café** (resumen del día anterior).

Todo lo demás puede esperar a que se lo pidas. Automatizar de más es la forma más rápida de tener
un agente que manda 14 mensajes al día y que dejes de leer.

## Paso 1: el informe del lunes

Primero, que funcione a mano:

```bash
python3 negocio/scripts/informe.py
```

Debe imprimir: pedidos de la semana, entregas próximas, tejidos bajo mínimo y total a cobrar. Si
esto no funciona, el cron tampoco: **un cron no arregla un script roto, lo esconde**.

Ahora pídeselo al agente:

```text
Crea una tarea programada para todos los lunes a las 8:00 (hora de Madrid) que ejecute
`python3 negocio/scripts/informe.py` desde este repositorio y me envíe el resultado por Telegram.
Si el script falla, avísame con el error completo.
```

Lo que hace Hermes por dentro:

- guarda la tarea en `~/.hermes/cron/`;
- la ejecuta en una sesión limpia (sin tu contexto del momento);
- te entrega el resultado donde le digas: el chat de origen, Telegram, o un fichero local.

## Paso 2: el aviso que no molesta

```text
Crea otra tarea, martes y jueves a las 8:30, que ejecute `almacen.py bajo-minimo`.
Si no hay tejidos bajo mínimo, no me escribas nada. Si hay, mándame la lista con el proveedor.
```

La parte importante es **«si no hay nada, no me escribas»**. Un aviso que llega siempre se convierte
en ruido y a la tercera semana lo ignoras. Ese silencio hay que programarlo a propósito.

Si tu script ya devuelve código 1 cuando hay aviso, puedes usar el **modo sin agente**: ejecuta el
script y entrega su salida tal cual, sin gastar modelo. Ideal para comprobaciones baratas.

## Paso 3: comprobar que existe y que corre

Lista las tareas:

```bash
hermes cron list
```

Fuerza una ejecución ahora, sin esperar al lunes:

```text
Ejecuta ahora la tarea del informe semanal y enséñame la salida.
```

O pídeselo al propio agente en lenguaje natural: «lanza la tarea de stock ahora». Si la salida
llega, la tubería funciona. Si no llega, revisa en este orden:

1. ¿El script funciona a mano, desde la carpeta correcta?
2. ¿La tarea apunta al directorio del repositorio?
3. ¿El destino de entrega es el chat correcto?
4. ¿El modelo de la tarea tiene saldo y proveedor?
5. `~/.hermes/logs/` para el error real.

## Paso 4: coste bajo control

Las tareas programadas gastan tokens aunque tú no estés mirando. Tres palancas:

| Palanca | Cómo |
|---|---|
| Modelo barato para rutinas | Fija un modelo distinto para cron (`cron.model`) o por tarea |
| Modo sin agente | Si solo hay que ejecutar un script y enviar su salida, no hace falta modelo |
| Menos frecuencia | Diario no siempre es mejor que semanal. Empieza semanal |

Revisa el gasto una vez al mes. Si una rutina cuesta más que el valor que aporta, se simplifica o
se borra. No hay nada más caro que una automatización que nadie lee.

## Paso 5: copias que se pueden restaurar

Dos capas:

**1. El repositorio** (ya lo tienes): código, datos de ejemplo, skills, identidad.

```bash
git add -A && git commit -m "estado del negocio" && git push
```

**2. La instalación de Hermes** (memoria, sesiones, configuración):

```bash
hermes backup
```

Guarda el fichero resultante **fuera del ordenador** (un disco externo o una nube privada). Una
copia en el mismo disco que se rompe no es una copia.

Y una vez al trimestre, la prueba que casi nadie hace: **restaura en una carpeta temporal** y
comprueba que el agente arranca y recuerda. Una copia que nunca se ha restaurado es una hipótesis.

## Paso 6: que no se muera en silencio

El fallo clásico: el cron lleva tres semanas sin ejecutarse y te enteras cuando falta el informe.
Antídoto: una rutina de salud semanal.

```text
Crea una tarea los viernes a las 18:00 que compruebe:
1) que el último informe se generó en los últimos 7 días,
2) que el repositorio no tiene cambios sin commit,
y me mande una línea con OK o con el problema.
```

Si esa rutina deja de llegar, ya sabes que algo se ha roto: es tu canario.

## Ejercicio

1. Ejecuta `informe.py` a mano y corrige lo que falle.
2. Crea la tarea del lunes y lánzala ahora para probarla.
3. Crea la del stock con la regla «si no hay nada, silencio».
4. Haz `hermes backup` y guarda el fichero fuera del ordenador.
5. Apunta en `notas/` la fecha y el resultado de la primera ejecución real.

## Checklist: ¿lo tengo?

- [ ] Una tarea programada se ha ejecutado y he visto su salida
- [ ] La tarea de stock calla cuando no hay nada que decir
- [ ] Sé lanzar una tarea a mano para probarla
- [ ] `hermes cron list` muestra lo que creo que tengo
- [ ] Copia del repo en GitHub y copia de Hermes fuera del ordenador
- [ ] He restaurado una copia al menos una vez (o sé exactamente cómo hacerlo)

## Errores típicos

- **Programar un script que solo funciona en tu carpeta**: el cron corre en otra ruta. Usa rutas
  absolutas o `cd` explícito.
- **Zona horaria**: un cron a las 8:00 UTC te despierta a las 10:00 en Madrid. Configura
  `HERMES_TIMEZONE`.
- **Tareas duplicadas** porque pediste la misma dos veces: `hermes cron list` antes de crear.
- **Ruido diario**: si no aporta, semanal.
- **No probar la restauración**: el día que la necesites no quieres aprender.

## Siguiente

Módulo 13: límites, seguridad, coste y proyecto final. Lo que separa un juguete divertido de un
sistema que puedes dejar funcionando con clientes reales.
