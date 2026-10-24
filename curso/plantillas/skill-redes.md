---
name: redes-sastreria
description: "Usa al planificar, redactar o revisar contenido de redes sociales del taller."
---

# Redes de la sastrería

## Datos y dónde están

- Calendario: `redes/calendario.csv` (fecha, red, pilar, formato, estado, texto, notas)
- Estados: idea → borrador → aprobado → publicado → descartado

```bash
python3 redes/scripts/calendario.py semana
python3 redes/scripts/calendario.py pendientes
python3 redes/scripts/calendario.py estado AAAA-MM-DD aprobado
```

## Pilares y proporción

- **Oficio** (40 %): cómo se hace algo, sin desvelar el diferencial del taller.
- **Prueba** (40 %): trabajo terminado, con permiso escrito del cliente.
- **Casa** (20 %): horarios, vacaciones, cómo se pide cita.

## Reglas que no se rompen

1. Nada pasa a `publicado` sin que yo lo haya aprobado antes (estado `aprobado`).
2. No se publican datos de clientes, caras reconocibles ni precios sin confirmar.
3. Sin emojis, sin signos de exclamación, sin promesas de plazo que no estén comprobadas.
4. Cada propuesta parte de algo real: un pedido, un tejido nuevo, una pregunta frecuente.
5. Las ideas se piden primero; el texto se escribe solo de las que yo elija.

## Procedimiento: propuesta semanal

1. Mira los pedidos entregados de las dos últimas semanas y los tejidos nuevos.
2. Propón 5 ideas: pilar, formato, gancho en una línea y qué foto haría falta.
3. Espera mi selección.
4. Redacta las elegidas (máx. 700 caracteres) y guárdalas como `borrador`.
5. Resume qué necesita mi aprobación y no publiques nada.

## Errores típicos

- Generar 30 posts genéricos en vez de 5 anclados a la realidad del taller.
- Usar fotos de clientes sin permiso escrito.
- Mezclar el tono de la marca con el de un folleto comercial.
- Medir likes en vez de mensajes y citas.
