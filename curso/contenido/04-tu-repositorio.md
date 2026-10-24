---
titulo: Tu repositorio en GitHub
numero: "04"
resumen: Creas el repositorio que guarda la identidad, los skills, los datos y la web. GitHub deja de ser «una nube» y pasa a ser la memoria del negocio.
duracion: 40 min
nivel: Desde cero
objetivo: Tener un repositorio propio, con la estructura del curso y sin secretos, clonado en el ordenador donde trabaja el agente.
criterios:
  - El repositorio existe en GitHub y está clonado en local
  - .env y los datos reales están fuera de git
  - Hay al menos un commit propio, no solo el inicial
  - El agente puede leer y escribir dentro del repositorio
---

## Por qué un repositorio y no una carpeta cualquiera

Porque un negocio no se lleva con «archivos sueltos en el escritorio». El repositorio te da cuatro
cosas que necesitas el primer mes:

- **Historial**: qué cambió, cuándo y por qué. Si el agente estropea un CSV, vuelves atrás.
- **Copia fuera del ordenador**: si se rompe el portátil, clonas y sigues.
- **Trabajo entre máquinas**: tu PC y el de la tienda ven lo mismo.
- **Revisión**: un cambio se lee antes de aceptarlo (o se ve en el diff después).

Y para el agente es aún más importante: **es su directorio de trabajo**. Ahí lee, escribe, ejecuta
scripts y guarda notas. Fuera de ahí, no toca nada.

## Paso 1: crear el repositorio

En GitHub: **New repository** → nombre `mi-agente` → **Private** (recomendado al principio) →
*Add a README* → **Create**.

Si prefieres terminal, con GitHub CLI:

```bash
gh repo create mi-agente --private --clone
```

Sin `gh`, clona el que acabas de crear:

```bash
cd ~
git clone https://github.com/TU-USUARIO/mi-agente.git
cd mi-agente
```

## Paso 2: la estructura

Crea estas carpetas y ficheros vacíos. No hace falta que sepas qué va dentro todavía: cada módulo
los rellena.

```bash
mkdir -p identidad skills negocio/scripts negocio/produccion redes web notas plantillas
touch identidad/SOUL.md identidad/USER.md identidad/AGENTS.md
touch negocio/clientes.csv negocio/medidas.csv negocio/tejidos.csv negocio/pedidos.csv
touch redes/calendario.csv
```

Queda así:

```text
mi-agente/
├── identidad/        # quién es el agente y cómo trabajas tú
├── skills/           # el oficio, un SKILL.md por especialidad
├── negocio/          # datos del taller (ejemplos) y scripts
│   └── produccion/   # datos reales: FUERA de git
├── redes/            # calendario de contenido y borradores
├── web/              # tu web publicada
└── notas/            # lo que aprendes y lo que decides
```

## Paso 3: proteger lo que no se publica

Copia el `.gitignore` del repositorio del curso o escribe este:

```gitignore
# Datos reales de clientes y producción
negocio/produccion/
*.sqlite
*.db

# Secretos
.env
.env.*

# Basura del sistema
__pycache__/
.DS_Store
```

Y crea un `.env.example` **sin valores**, para documentar qué claves necesita el proyecto:

```bash
cat > .env.example <<'EOF'
# Copia este fichero a .env y rellena los valores. .env NUNCA se commitea.
TELEGRAM_BOT_TOKEN=
GITHUB_TOKEN=
EOF
```

> **La regla que no se rompe:** si una clave aparece en un commit, se considera filtrada. Aunque la
> borres después, queda en el historial. Se revoca y se genera otra.

## Paso 4: primer commit

```bash
git add -A
git commit -m "estructura inicial del negocio"
git push
```

Comprueba en GitHub que **no** aparece `.env` ni `negocio/produccion/`. Si aparece, para y
corrige: `git rm --cached .env` antes de seguir.

## Paso 5: el agente trabaja aquí

Abre Hermes **dentro de la carpeta del repositorio**:

```bash
cd ~/mi-agente
hermes
```

Y pídele algo pequeño y verificable:

```text
Mira la estructura de este repositorio y explícame en cinco líneas para qué sirve cada carpeta.
Después crea notas/2026-01-15-inicio.md con la fecha de hoy y una línea sobre mi negocio.
```

Comprueba tú el fichero:

```bash
ls notas/
cat notas/2026-01-15-inicio.md
```

Si existe y tiene lo que pediste, el agente está trabajando dentro de tu repositorio. Ese es el
criterio del módulo.

## Paso 6: higiene mínima

Tres costumbres que te van a salvar:

1. **Un cambio, un commit.** No mezcles «arreglo el CSV» con «cambio el SOUL».
2. **Mensajes que expliquen el porqué**: `feat(negocio): añade columna proveedor a tejidos`.
3. **Nada de `git push --force`** hasta que sepas muy bien lo que hace. Ni siquiera entonces.

Si trabajas con otra persona (o con otro agente), usa ramas:

```bash
git checkout -b negocio/stock-minimo
# cambios
git add -A && git commit -m "feat(negocio): stock mínimo por tejido"
git push -u origin negocio/stock-minimo
```

## Ejercicio

1. Crea el repositorio y la estructura.
2. Añade un `README.md` de tres líneas: qué negocio es, quién lo lleva y qué va a hacer el agente.
3. Haz un commit y súbelo.
4. Pide al agente que lea el README y proponga **una** mejora. Acéptala o recházala tú, y haz el
   commit con el motivo.

## Checklist: ¿lo tengo?

- [ ] Repo creado y clonado; `git status` limpio
- [ ] `.gitignore` con `.env`, `negocio/produccion/`, `*.db`
- [ ] `.env.example` documenta las claves sin valores
- [ ] Un commit propio subido a GitHub
- [ ] El agente ha creado un fichero dentro del repo y lo he comprobado yo

## Errores típicos

- **Commitear `.env`.** Pasa hasta a los que llevan años. Si ocurre: revoca la clave, bórrala del
  historial con cuidado y cambia el `.gitignore`.
- **Trabajar en `~/Downloads` o en el escritorio.** El agente no sabrá qué es «el proyecto» y
  mezclará ficheros.
- **Repositorio público con datos de clientes.** Empieza privado; si luego publicas la web, publica
  solo la carpeta `web/` con datos de ejemplo.
- **Subir CSVs de 200 MB.** Git no es para eso. Los datos grandes van fuera (o a una base de
  datos); en el repo solo lo que se versiona bien.

## Siguiente

Módulo 05: le das identidad (`SOUL.md`, `USER.md`) y memoria (`MEMORY.md`). El agente deja de ser
genérico y empieza a trabajar como tú necesitas.
