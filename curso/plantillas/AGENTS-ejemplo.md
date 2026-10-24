# Mapa del repositorio — plantilla del curso
# Cópiala a la raíz de tu repositorio como AGENTS.md (o a identidad/AGENTS.md).

- `identidad/` — `SOUL.md`, `USER.md` y este mapa. La identidad se copia a `~/.hermes/`.
- `skills/` — procedimientos. Cada carpeta es un skill con su `SKILL.md`.
- `negocio/` — datos del taller: clientes, medidas, tejidos, pedidos y movimientos.
- `negocio/produccion/` — datos reales. **Fuera de git. No se toca sin permiso.**
- `negocio/scripts/` — herramientas de consulta y cálculo (biblioteca estándar).
- `redes/` — calendario editorial y borradores. Nada se publica sin aprobación.
- `web/` — web pública. El catálogo se genera desde `negocio/tejidos.csv`.
- `notas/` — decisiones y aprendizajes, una nota por tema y fecha.

## Prohibido

- Editar ficheros de `negocio/produccion/` sin decírmelo.
- Inventar cifras: si falta un dato, se pregunta.
- Commitear `.env` o claves de cualquier tipo.
- Ejecutar comandos destructivos (`rm -rf`, `git reset --hard`) sin copia reciente.

## Cómo se comprueba el trabajo

- Los CSV se leen después de escribir: si no se puede releer, no está hecho.
- Los scripts se ejecutan desde la raíz del repositorio.
- Un informe cita la fecha de los datos que usa.
