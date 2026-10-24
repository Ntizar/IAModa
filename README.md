# IAModa — De la idea a la prenda

Propuesta de asignatura de IA aplicada al ciclo del producto de moda, en un único HTML.

**Web:** https://ntizar.github.io/IAModa/

Documento único (`index.html`, ~137 KB) con un plan de estudios de IA aplicada a la moda y
**seis artefactos interactivos que calculan de verdad**: patrón paramétrico, simulación de tela,
estampado tileable, ficha técnica con coste, pasaporte digital (ESPR) y probador 3D con prendas
que se autoajustan.

## Abrir

```bash
# doble clic o:
start index.html
```

Necesita red la primera vez: el CSS viene del CDN de Aurora pineado a `v10.0.0`
(`tokens.css` + `packs/all.css`) y la fuente Inter viaja en ese CSS.

## Verificar antes de entregar

```bash
node --experimental-websocket tools/medir-pagina.mjs index.html 320,360,390,414,768,1440
# -> 0 desbordes; sale con código 1 si algo desborda

node --experimental-websocket tools/capturar.mjs index.html 1440 ./cap tesis,plan,demos,herramientas
# -> PNG por sección (captureBeyondViewport, sin depender del scroll)

python <ruta-al-repo-Aurora>/scripts/auditar-uso.py index.html
# -> 0 fallos
```

## Estructura del documento

| Sección | Qué contiene |
|---|---|
| Hero | tesis en una frase, 4 KPIs, accesos |
| 01 Tesis | capa commodity vs cadena que distingue, regla anti-slop |
| 02 Cadena | 9 eslabones, con «IA hace» y «IA falla» en cada uno |
| 03 Plan | 12 sesiones en tabla apilable + bloques A/B/C |
| 04 Demos | 5 demos interactivas (SVG + 2 canvas + tablas + checklist) |
| 05 Probador 3D | maniquí paramétrico + 5 prendas que se autoajustan + patrón y descarga SVG |
| 06 Herramientas | 5 pestañas × 27 fichas, cada una con nivel de alcance (1-4), «te lleva a» y «techo» |
| 07 Ejercicios | 2 ejercicios completos: enunciado, entregables, rúbrica y trampa |
| 08 Evaluación | rúbrica de 5 ejes, riesgos, kit de arranque |

## Probador 3D

`three.js` desde jsDelivr (`three@0.169.0`), escena en centímetros. El cuerpo y las prendas
se generan anillo a anillo (`anillos(perfil, …)`): cada perfil es una lista de
`{y, rx, rz, cx}` derivada de pecho, cintura, cadera y largo. Al mover un slider se
destruye la geometría anterior (`dispose()`) y se reconstruye; el patrón 2D se calcula con
las mismas medidas.

- Enlace directo: `index.html?prenda=vestido&pecho=110&cintura=90`.
- Sin red el módulo cae al modo patrón 2D y lo dice en el estado del visor.
- Aviso honesto: **no es un motor de tela**; es geometría paramétrica. Los pliegues son
  una modulación senoidal del radio, no física.

## Notas de implementación

- Todo el cálculo de las demos es local (sin IA, sin red): son las reglas del oficio en código.
- La tela es un integrador de Verlet con restricciones de distancia y pinzas fijas.
- El estampado usa un PRNG determinista por celda y dibuja el motivo repetido en los bordes
  cuando «sin costura» está activo; al apagarlo se ve la costura a propósito.
- Las pestañas son mejora progresiva: sin JavaScript se ven los cinco paneles apilados.

Hecho con ❤️ por David Antizar

## Curso de agentes

Dentro de este repositorio vive el **Curso Mastermind**: 14 módulos para montar un agente de IA
(Hermes + NaN + GitHub) y ponerlo a llevar clientes, almacén, pedidos, redes y web, con una
sastrería como caso real.

- Curso: https://ntizar.github.io/IAModa/curso/
- Fuente: `curso/contenido/*.md` · se regenera con `python3 curso/scripts/build.py`
