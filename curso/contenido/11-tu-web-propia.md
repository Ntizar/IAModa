---
titulo: Tu web propia
numero: "11"
resumen: Catálogo real generado desde tus datos, formulario de encargo sin backend y publicación gratis en GitHub Pages. Con Aurora, sin plantillas de pago.
duracion: 45 min
nivel: Con datos de almacén
objetivo: Publicar una web propia con el catálogo de tejidos leído de tu CSV y una vía clara para que un cliente pida cita.
criterios:
  - La web está publicada y responde 200 en su URL
  - El catálogo sale de tejidos.csv, no de HTML escrito a mano
  - Se ve bien a 320 px y a 1440 px, sin scroll horizontal
  - Hay una forma de contacto que funciona (y la he probado yo)
---

## Qué web necesita un sastre

No un escaparate de 12 secciones. Cuatro cosas, en una página:

1. **Quién eres** y dónde estás (con horario y teléfono visibles).
2. **Qué haces**: tres ejemplos con foto y una línea de contexto.
3. **Qué telas tienes** ahora mismo (tu ventaja real frente a una franquicia).
4. **Cómo se pide cita**: teléfono, WhatsApp o formulario. Sin fricción.

Todo lo demás es decoración. Y la decoración se hace después.

## Paso 1: el diseño, sin inventar CSS

Usamos **Aurora**, el design system de David Antizar: CSS puro, sin build y sin dependencias. Se
enlaza por CDN con un tag fijado (nunca `@master`):

```html
<html lang="es" data-nz-theme="light">
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/tokens.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/packs/p1-layout.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/packs/p3-typography.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/packs/p4-actions.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/packs/p6-feedback.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/packs/p10-commerce.css">
</head>
<body class="nz">
```

La regla del sistema: las clases propias van con prefijo (`mio-`), no se inventan clases `nz-*`, y
los colores salen de tokens (`var(--nz-brand)`), no de `#1a4488`. Si necesitas algo que no existe,
se añade a Aurora, no se parchea en tu web.

> Esta misma web del curso está hecha así: mira el código fuente y verás los packs y el pie de
> atribución.

## Paso 2: el catálogo sale de tus datos

Escribe `web/scripts/generar.py` (o copia el del curso). Hace una cosa: lee
`negocio/tejidos.csv` y escribe `web/datos-tejidos.json`.

```python
import csv, json
from pathlib import Path

raiz = Path(__file__).resolve().parents[2]
filas = []
with (raiz / "negocio" / "tejidos.csv").open(encoding="utf-8") as f:
    for fila in csv.DictReader(f):
        filas.append({
            "ref": fila["ref"],
            "nombre": fila["nombre"],
            "composicion": fila["composicion"],
            "color": fila["color"],
            "metros": float(fila["metros"]),
            "precio_m": float(fila["precio_m"]),
            "disponible": float(fila["metros"]) >= 3,
        })

(raiz / "web" / "datos-tejidos.json").write_text(
    json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"{len(filas)} tejidos publicados")
```

Y en la web, `fetch("datos-tejidos.json")` pinta las tarjetas. Ventajas:

- actualizas el CSV y vuelves a ejecutar el script: la web cambia sin tocar HTML;
- no publicas coste ni mínimo (solo lo que quieres enseñar);
- si el JSON falla, la página sigue teniendo el texto base (nunca dejes la web en blanco por un
  `fetch`).

```javascript
fetch("datos-tejidos.json")
  .then(r => r.ok ? r.json() : [])
  .then(tejidos => {
    const rejilla = document.querySelector("[data-tejidos]");
    if (!rejilla) return;
    rejilla.innerHTML = tejidos.map(t => `
      <article class="nz-article">
        <p class="nz-eyebrow">${t.composicion}</p>
        <h3 class="nz-h3">${t.nombre}</h3>
        <p>${t.color} · ${t.metros.toFixed(1)} m disponibles</p>
        <p class="nz-badge ${t.disponible ? "nz-badge--success" : "nz-badge--warning"}">
          ${t.disponible ? "Disponible" : "Bajo pedido"}
        </p>
      </article>`).join("");
  })
  .catch(() => { /* la sección se queda con el texto estático */ });
```

## Paso 3: contacto que funcione

Sin backend, tres opciones honestas:

| Opción | Ventaja | Límite |
|---|---|---|
| `tel:` y `https://wa.me/34...` | Cero infraestructura, cero coste | Requiere que contestes |
| `mailto:` con asunto prerelleno | Sirve para encargos largos | Algunos móviles lo abren mal |
| Formulario con servicio externo (Formspree y similares) | Recoges estructura | Dependes de un tercero y de su plan gratis |

Para empezar: **teléfono y WhatsApp visibles en la cabecera y al final**. Un formulario que no
llega a ningún sitio es peor que no tenerlo.

Si pones formulario, pruébalo tú: envía uno real y comprueba que llega. No lo dejes «para luego».

## Paso 4: publicar gratis en GitHub Pages

1. Crea `.github/workflows/pages.yml` en tu repositorio:

```yaml
name: Publicar la web
on:
  push:
    branches: ["main", "master"]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  publicar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: "web"
      - uses: actions/deploy-pages@v4
```

2. En GitHub: **Settings → Pages → Source: GitHub Actions**.
3. Commit y push. Espera un minuto.
4. Comprueba:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://TU-USUARIO.github.io/mi-agente/
```

Tiene que devolver `200`. Si devuelve `404`, revisa que el workflow haya corrido y que `web/`
tenga un `index.html` en minúsculas.

## Paso 5: comprobar que no está rota

Tres pruebas que se hacen en dos minutos:

```bash
# 1. ¿Se sirve el HTML?
curl -s https://TU-USUARIO.github.io/mi-agente/ | grep -o "<title>.*</title>"

# 2. ¿Se sirve el CSS de Aurora?
curl -s -o /dev/null -w "%{http_code}\n" https://cdn.jsdelivr.net/gh/Ntizar/Aurora@v10.1.0/tokens.css

# 3. ¿Se sirven los datos?
curl -s https://TU-USUARIO.github.io/mi-agente/datos-tejidos.json | head -20
```

Y en el móvil: abre la web, gira el móvil, pide cita desde el enlace. Si algo de eso falla, no está
terminada.

## Ejercicio

1. Copia la plantilla de `web/` del curso y cambia textos, teléfono y colores de marca.
2. Ejecuta el generador con tus tejidos y comprueba el JSON.
3. Publica y verifica el 200.
4. Pide a alguien que abra la web en su móvil y te diga qué no entiende. Corrige eso, no el color
   del botón.

## Checklist: ¿lo tengo?

- [ ] URL viva y `curl` devuelve 200
- [ ] Catálogo generado desde `tejidos.csv`
- [ ] Teléfono/WhatsApp visibles y probados
- [ ] Sin scroll horizontal a 320 px
- [ ] El pie dice «Hecho con ❤️ por David Antizar» si usas Aurora
- [ ] Sé actualizar la web en dos comandos (`generar.py` + `git push`)

## Errores típicos

- **Enlazar `@master` en el CSS**: cualquier cambio del sistema te rompe la web. Tag fijado.
- **Escribir las tarjetas a mano** y llamarlo «catálogo»: en dos semanas está desactualizado.
- **Publicar precios de coste o mínimos de stock**: eso es información interna.
- **`index.html` en mayúsculas**: GitHub Pages devuelve 404 en la raíz y te volverás loco.
- **Formulario sin probar**: el cliente escribe, le das al botón y no pasa nada.
- **Copiar CSS de otro sitio**: rompe la coherencia y la accesibilidad. Usa el sistema.

## Siguiente

Módulo 12: autonomía. El agente deja de esperar a que le hables: informes, avisos y copias de
seguridad que ocurren solos.
