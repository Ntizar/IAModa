# Curso Mastermind — tu agente de IA para llevar el negocio

Curso práctico, en castellano y desde cero, para que cualquier persona con un ordenador pueda
tener su propio agente de IA trabajando: instalar Hermes, **comprar acceso a NaN y colocar la clave**,
montar su repositorio en GitHub, darle identidad y memoria, enseñarle el oficio con skills y ponerlo
a llevar **clientes, almacén, pedidos, redes sociales y su propia web**.

El caso que se usa de principio a fin es una **sastrería**: clientes con medidas, tejidos en
almacén, encargos con fechas de prueba y entrega, contenido para redes y catálogo web. Sirve igual
para una carpintería, una ferretería o una consultoría: cambia el oficio, no el método.

## URL

- Curso publicado: <https://ntizar.github.io/IAModa/curso/>
- IAModa (documento padre): <https://ntizar.github.io/IAModa/>

## Qué hay aquí

| Ruta | Qué es |
|---|---|
| `contenido/NN-*.md` | **La fuente de verdad**: una guía por módulo (14 módulos, 00 a 13). Se escribe aquí, no en el HTML. |
| `scripts/build.py` | Genera el sitio (portada + módulos) desde el Markdown. Sin dependencias raras: `markdown`. |
| `assets/curso.css` · `assets/curso.js` | Capa propia sobre Aurora: modo presentación, copiar código, navegación. |
| `plantillas/` | Ficheros que el alumno copia y renombra: `SOUL-ejemplo.md` → `SOUL.md`, `AGENTS-ejemplo.md` → `AGENTS.md`, `USER.md`, `config.yaml` y los skills de sastrería y redes. |
| `negocio/` | Datos y scripts de ejemplo del negocio: `clientes.csv`, `tejidos.csv`, `pedidos.csv` y sus herramientas. |
| `web/` | Web de ejemplo del taller, con catálogo generado desde `tejidos.csv`. |
| `modulos/` · `index.html` | **Generado**. No se edita a mano. |

## Cómo se construye

```bash
python3 -m pip install --user markdown==3.10.2
python3 curso/scripts/build.py    # desde la raíz de IAModa → curso/index.html y curso/modulos/
```

El generador:

- parte cada módulo en **tramos** (cada `##` es un tramo, para el modo presentación);
- convierte las tablas Markdown en `.nz-table-wrap--apilable` + `.nz-table--apilable` con
  `data-etiqueta`, que es lo que hace que en móvil no desborden;
- convierte los bloques de código en `.nz-code--block` con botón de copiar;
- convierte las listas `- [ ]` en checklist visual;
- añade el índice del módulo, la navegación anterior/siguiente y la atribución exacta.

## Diseño

Todo el CSS viene de **Aurora** (`Ntizar/Aurora`), pineado al tag `v10.1.0` resuelto con el PASO 0
del skill `aurora-design-system`. Aquí no hay colores a mano, ni gradientes, ni clases `nz-*`
inventadas: la capa propia usa solo prefijo `curso-`. Si algo falta, se sube a Aurora, no se
resuelve en este repo.

## Reglas del curso

1. **Castellano**, tuteo y sin humo: cada paso se puede ejecutar.
2. **Un «listo» sin prueba no es un listo**: cada módulo termina en checklist verificable.
3. **Nada de secretos en el repo**: claves en `.env`, `.env` fuera de git.
4. **Human loop**: lo que gasta dinero, publica o borra se aprueba antes.
5. **Se aprende haciendo**: cada módulo tiene un ejercicio con datos reales del taller.

---

Hecho con ❤️ por David Antizar
