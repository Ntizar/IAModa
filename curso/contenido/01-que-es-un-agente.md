---
titulo: Qué es un agente (y qué no)
numero: "01"
resumen: La diferencia entre un chat que responde y un agente que ejecuta, recuerda y aprende. Con el ciclo completo de una tarea real de taller.
duracion: 25 min
nivel: Desde cero
objetivo: Entender el ciclo percibir → decidir → actuar → recordar y saber distinguirlo de un chatbot, para no construir el juguete equivocado.
criterios:
  - Distingues chat, copiloto y agente con un ejemplo propio
  - Sabes qué tres cosas necesita un agente para trabajar de verdad
  - Has escrito el ciclo de una tarea de tu negocio en cinco líneas
---

## La diferencia que importa

Un **chat** responde. Un **agente** hace. La diferencia no es el modelo: es que el agente tiene
herramientas (leer tus ficheros, ejecutar un script, buscar en la web, mandar un mensaje), memoria
(lo que aprendió ayer) y permiso para actuar sin que se lo pidas paso a paso.

Ejemplo con la sastrería:

- Chat: «¿Cuántos metros de lana azul me quedan?». Te responde con una generalidad inútil, porque
  no ve tu almacén.
- Agente: abre `negocio/tejidos.csv`, filtra la referencia, calcula los metros, detecta que estás
  por debajo del mínimo y te manda un aviso a Telegram con el proveedor y el plazo.

## El ciclo de una tarea

Todo agente, por complicado que sea, hace lo mismo:

1. **Percibe**: recibe tu mensaje, un fichero, un cron o un evento.
2. **Decide**: elige qué herramienta usar y en qué orden (leer, calcular, escribir, avisar).
3. **Actúa**: ejecuta y mira el resultado. Si falla, corrige y reintenta.
4. **Recuerda**: guarda lo aprendido (una preferencia tuya, un dato del entorno, un procedimiento).

Si te falta cualquiera de las cuatro, tienes un juguete:

| Falta | Qué pasa |
|---|---|
| Herramientas | Opina, pero no toca tus datos: alucina cifras |
| Memoria | Cada día empieza de cero y te pregunta lo mismo |
| Permiso de actuar | Te da instrucciones para que las ejecutes tú: sigue siendo tú el que trabaja |
| Criterio (saber cuándo parar) | Hace cosas irreversibles sin avisar |

## Las tres piezas que vas a montar

En este curso montas las tres, en este orden:

- **Identidad** (`SOUL.md`, `USER.md`): quién es, cómo habla, qué hace y qué no hace nunca.
- **Conocimiento** (`skills/`): tu oficio por escrito, cargado solo cuando la tarea lo pide.
- **Datos y herramientas** (`negocio/`, scripts): donde el agente mira antes de opinar.

> El error número uno de quien empieza es escribir un `SOUL.md` de 400 líneas y no darle ni un dato.
> El agente se vuelve teatral: habla como un sastre y no sabe cuántos metros de lana tienes.

## Qué significa «aprender» aquí

El agente no reentrena el modelo. Aprende de tres formas, todas verificables:

1. **Memoria**: frases cortas y densas que se cargan en cada sesión («David trabaja en Madrid,
   factura con IVA 21 %, prefiere respuestas cortas»).
2. **Skills**: procedimientos con pasos, comandos y avisos, que se cargan cuando la tarea encaja.
3. **Notas**: el registro de lo que pasó, buscable, para no volver a preguntar.

Nada de eso es magia: son ficheros de texto en tu repositorio. Puedes leerlos, corregirlos y
versionarlos. Esa es la diferencia entre un agente propio y un servicio cerrado que cambia solo.

## Dónde está el peligro

Un agente con herramientas puede **hacer daño real**: borrar un CSV, mandar un correo equivocado,
publicar en tu cuenta, gastar saldo de API. Por eso el curso insiste en tres cosas desde el minuto
uno:

- **Permisos mínimos**: el agente solo toca las carpetas del negocio, no todo el disco.
- **Aprobación humana** para lo que publica, gasta o borra.
- **Recibos**: si dice «hecho», tiene que poder enseñar el fichero, el commit o el mensaje enviado.

## Ejercicio: el ciclo de tu tarea

Elige una tarea que repitas cada semana y escríbela como ciclo. Ejemplo hecho:

```text
Tarea: avisar de tejidos bajo mínimo
1. Percibe: cada lunes a las 8:00, sin que nadie escriba.
2. Decide: leer tejidos.csv, comparar metros con metros_minimos, ordenar por urgencia.
3. Actúa: escribe informe en notas/ y manda resumen a Telegram.
4. Recuerda: si el proveedor tarda más de 15 días, anotarlo para la próxima.
```

Hazlo con la tuya. Si no puedes rellenar los cuatro pasos, la tarea aún no está bien definida (y
ningún agente la va a arreglar).

## Checklist: ¿lo tengo?

- [ ] Puedo explicar la diferencia entre chat y agente con un caso de mi negocio
- [ ] He escrito mi ciclo de cuatro pasos
- [ ] Sé qué pasa si falta memoria (y por qué me obligaría a repetirme)
- [ ] Tengo identificado algo que el agente NO debe hacer sin preguntarme

## Errores típicos

- **Confundir «agente» con «GPT con nombre».** Si no tiene herramientas ni memoria, es un chat con
  sombrero.
- **Darle acceso a todo el ordenador** porque «así es más útil». Es la forma más rápida de perder
  un archivo importante.
- **Pedirle creatividad antes que precisión.** Para llevar un negocio, primero que acierte con los
  números; el estilo se añade después.

## Siguiente

Módulo 02: instalas Hermes en tu ordenador y tienes tu primera conversación real. Sin tocar nada
del negocio todavía.
