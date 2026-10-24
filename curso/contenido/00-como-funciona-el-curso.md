---
titulo: Cómo funciona este curso
numero: "00"
resumen: El mapa completo, qué vas a construir, cuánto cuesta en tiempo y cómo se comprueba que has aprendido.
duracion: 15 min
nivel: Desde cero
objetivo: Entender la ruta de los 14 módulos y tener el caso de negocio (la sastrería) en la cabeza antes de instalar nada.
criterios:
  - Sabes qué tendrás funcionando al terminar el último módulo
  - Tienes claro que el repositorio es la memoria y el agente es el que trabaja
  - Sabes dónde pedir ayuda cuando un comando falle
---

## La idea en una frase

Vas a montar un **agente de IA que vive en tu ordenador**, con su identidad, su memoria y el
conocimiento de tu oficio; y le vas a dar acceso ordenado a los datos de tu negocio, a tus redes y
a tu web. El agente no «sabe» de sastrería por arte de magia: se lo enseñas tú, por escrito, y él
lo aplica todas las veces que haga falta.

## El caso: una sastrería

Todos los ejemplos son del mismo negocio, para que no tengas que imaginar:

- **Clientes** con ficha y medidas tomadas en fechas distintas (la gente cambia de talla).
- **Tejidos** en almacén, con metros disponibles, mínimo de seguridad y proveedor.
- **Encargos**: prenda, tejido, fecha de prueba, fecha de entrega, señal pagada y estado.
- **Redes**: calendario de contenido, con borradores que tú apruebas antes de publicar.
- **Web**: catálogo de tejidos leído de tus datos reales y formulario para pedir cita.

Si tu negocio es una carpintería, cambia «tejidos» por «tableros» y «metros» por «unidades».
El método es idéntico: **datos claros, reglas escritas, tareas repetidas automatizadas**.

## La ruta

| Bloque | Módulos | Qué pasa |
|---|---|---|
| Fundamentos | 00 a 06 | Instalas el agente, montas el repositorio, le das identidad, memoria y skills |
| El negocio | 07 a 10 | Clientes y medidas, almacén, pedidos, redes sociales |
| Web y autonomía | 11 a 13 | Tu web publicada, rutinas con cron, límites y proyecto final |

> No te saltes los del primer bloque aunque tengas prisa. El 80 % de los problemas de la gente que
> empieza viene de ahí: agente sin identidad, memoria que se pierde y skills inventados.

## Cuánto se tarda

Calcula **30-40 minutos por módulo** y dos tardes para el proyecto final. Si un módulo te lleva el
doble, no pasa nada: lo normal es atascarse en el 02 (instalación) o en el 04 (GitHub), y ambos
traen una sección de errores típicos para eso.

## Cómo se comprueba que has aprendido

Cada módulo abre con **criterios de aceptación**: una lista corta de cosas que tienen que estar en
verde. No son deberes: son la definición de «terminado». Al final del módulo hay una checklist con
la misma idea, formulada como pasos que puedes ejecutar.

Si un criterio no se cumple, no sigas: vuelve al paso que lo resuelve. Un curso a medias se nota
siempre en el módulo 11, cuando la web no lee los datos porque el CSV estaba mal desde el 08.

## Qué necesitas tener a mano

- Ordenador con **Windows, macOS o Linux** y permisos para instalar programas.
- **GitHub** (cuenta gratuita) y **Telegram** en el móvil.
- Una cuenta de modelo: Nous Portal, OpenRouter o el proveedor que prefieras.
- **Tus datos**, aunque estén en una libreta. En el módulo 07 los pasamos a un CSV.

## Dónde pedir ayuda

1. El propio agente: si algo falla, pégale el error tal cual y pídele que lo diagnostique.
2. La sección **Errores típicos** de cada módulo.
3. La documentación oficial: <https://hermes-agent.nousresearch.com/docs>
4. El repositorio del curso: <https://github.com/Ntizar/curso-mastermind>

## Ejercicio: tu punto de partida

Antes de seguir, escribe en un papel (o en `notas/punto-de-partida.md` de tu futuro repo) estas
cuatro respuestas:

- Qué vendes y a quién.
- Qué dato repites más veces al día (medidas, stock, plazos, precios…).
- Qué tarea odias hacer y es igual todas las semanas.
- Qué NO quieres que el agente haga nunca sin preguntarte.

Ese último punto será tu lista de límites en el módulo 13. Guárdala.

## Checklist: ¿lo tengo?

- [ ] Sé qué es la sastrería de ejemplo y qué papel juega cada dato
- [ ] He reservado dos tardes y media en el calendario
- [ ] Tengo cuenta de GitHub y Telegram
- [ ] He escrito mis cuatro respuestas del ejercicio
- [ ] Entiendo que «terminado» significa criterios en verde, no haber leído el módulo

## Errores típicos

- **Empezar por el módulo de la web.** La web es la cara; los datos son el negocio. Sin el 07 y el
  08, la web del 10 no tiene nada que enseñar.
- **Instalar cinco cosas antes de hablar con el agente.** Primero un chat que funcione; después
  gateway, cron, skills. El orden importa.
- **Guardar datos de clientes reales en el repositorio público.** En el 04 montamos el `.gitignore`
  precisamente para eso.

## Siguiente

Módulo 01: qué es un agente y en qué se diferencia de un chat. Corto, pero es el que evita que
dentro de un mes tengas un chatbot caro en vez de un empleado.
