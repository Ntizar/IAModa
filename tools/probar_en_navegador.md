# Cómo regenerar las muestras de exportación del patrón

Las muestras de `tools/exportaciones-muestra/` salen del probador real
(`index.html`, sección «Patrón de taller»), no de un cálculo aparte.

1. Servir el repo en local (el módulo 3D necesita http, no file://):
   `python -m http.server 8123 --bind 127.0.0.1`
2. Abrir `http://127.0.0.1:8123/index.html` y esperar a que el probador
   dibuje el patrón (bajo «Rig & pasarela»).
3. En la consola del navegador, ejecutar el gancho y copiar la salida:

   ```js
   copy(window.__patronTest())   // deja el JSON en el portapapeles
   ```

4. Decodificar el JSON (campos `svg`, `pdf`, `dxf` en base64) y guardar:

   | campo | fichero |
   |---|---|
   | `svg` | `tools/exportaciones-muestra/patron-1a1.svg` |
   | `pdf` | `tools/exportaciones-muestra/patron-a4.pdf` |
   | `dxf` | `tools/exportaciones-muestra/patron-r12.dxf` |
   | `dom` | `tools/exportaciones-muestra/dom.json` (tal cual) |

5. Verificar: `python tools/verificar_exportaciones.py`

Con una sesión de Hermes, todo el ciclo (servir, probar, guardar,
verificar) corre en dos pasos — ver nota de sesión del 2026-10-29.
