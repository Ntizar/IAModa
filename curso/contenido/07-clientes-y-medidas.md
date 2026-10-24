---
titulo: Clientes y medidas
numero: "07"
resumen: Pasas la libreta al CSV, creas la ficha de cliente con historial de medidas y le das al agente las consultas que evitan duplicados y errores.
duracion: 40 min
nivel: Con el agente ya instalado
objetivo: Tener clientes y medidas en datos limpios, con scripts que el agente pueda ejecutar y reglas para no duplicar fichas.
criterios:
  - clientes.csv y medidas.csv existen con cabeceras correctas
  - El script de clientes busca, crea y añade medidas sin romper el CSV
  - El agente resuelve «ficha de X» citando datos reales, no inventados
  - Los datos reales viven en negocio/produccion/ y no están en git
---

## Del papel al dato

Una sastrería vive de dos cosas: la confianza y las medidas. Las dos se pierden igual de fácil: en
una libreta que nadie encuentra y en una ficha duplicada con la talla vieja.

Empezamos con lo mínimo que se puede mantener:

**`negocio/clientes.csv`**

```csv
id,nombre,telefono,email,alta,notas
C-2026-001,Ana López,600111222,ana@example.com,2026-01-12,Prefiere cita por la tarde
C-2026-002,Marta Ruiz,600000000,marta@example.com,2026-02-03,Cliente de su madre
```

**`negocio/medidas.csv`**

```csv
cliente_id,fecha,pecho,cintura,cadera,cuello,hombro,manga,notas
C-2026-001,2026-01-12,96,78,100,36,12,60,Toma sobre camisa fina
C-2026-001,2026-03-04,97,79,101,36,12,60,Subida de invierno
C-2026-002,2026-02-03,88,70,94,33,11,58,
```

Reglas de oro:

- **Una fila por toma de medidas**, con fecha. La gente cambia de talla, y una prenda hecha con
  medidas de hace dos años es una devolución.
- **Centímetros, sin excepciones.** Nada de «38 de cintura» sin decir de qué.
- **ID estable** (`C-AÑO-NÚMERO`). El nombre se puede repetir; el ID no.

## Si vienes de Excel

1. Abre el Excel y revisa que la primera fila sean cabeceras limpias (sin acentos raros, sin celdas
   combinadas).
2. **Archivo → Guardar como → CSV UTF-8**.
3. Ábrelo con un editor de texto y comprueba que las columnas están separadas por comas.
4. Cambia el nombre a `clientes.csv` y muévelo a `negocio/`.
5. Copia el original a `negocio/produccion/` (fuera de git) como respaldo.

> El CSV no es «cutre»: es el formato que cualquier herramienta lee, que se ve en el diff de git y
> que no te encierra en una suscripción.

## Los scripts del curso

Copia la carpeta `negocio/scripts/` del repositorio del curso. Cuatro herramientas, solo biblioteca
estándar de Python (nada que instalar):

```bash
python3 negocio/scripts/clientes.py buscar ruiz
python3 negocio/scripts/clientes.py ficha C-2026-002
python3 negocio/scripts/clientes.py alta --nombre "Marta Ruiz" --telefono 600000000
python3 negocio/scripts/clientes.py medidas C-2026-002 --pecho 96 --cintura 78 --cadera 100 --cuello 36 --hombro 12 --manga 60
```

Salida esperada al buscar:

```text
C-2026-002  Marta Ruiz  600000000  alta 2026-02-03
  1 toma de medidas · última: 2026-02-03 (pecho 88, cintura 70)
```

Lo importante no es el script: es que **el agente lo ejecuta en vez de inventar**. En el skill de
sastrería ya le dijiste que los datos están en `negocio/`. Ahora le das la herramienta.

## Paso 1: crear el primero

```bash
python3 negocio/scripts/clientes.py alta --nombre "Marta Ruiz" --telefono 600000000 --email marta@example.com
```

El script:

- normaliza el teléfono (quita espacios y guiones);
- comprueba duplicados por teléfono;
- asigna el siguiente ID del año;
- escribe con `utf-8` y comillas correctas.

Si el teléfono ya existe, no crea nada y te enseña la ficha existente. Esa es la primera regla del
negocio metida en código: **no duplicar**.

## Paso 2: medir sin liarla

```bash
python3 negocio/scripts/clientes.py medidas C-2026-002 \
  --pecho 96 --cintura 78 --cadera 100 --cuello 36 --hombro 12 --manga 60 \
  --notas "Toma sobre camisa fina"
```

El script añade una fila nueva, no sobrescribe la anterior. La fecha la pone él.

Comprueba el historial:

```bash
python3 negocio/scripts/clientes.py ficha C-2026-002
```

## Paso 3: que el agente lo use

En una sesión dentro del repositorio:

```text
Usa el skill de sastrería. Busca a la clienta Marta Ruiz, dime su última toma de medidas y
calcula cuánto tejido necesita un traje de dos piezas si el patrón pide 3,2 m y añadimos un 8 %
de merma. Enséñame el cálculo.
```

Lo que tiene que pasar:

1. Ejecuta `buscar` y `ficha` (con datos reales).
2. Hace 3,2 × 1,08 = **3,46 m** y lo enseña.
3. No se inventa ninguna medida que falte: si falta el largo de pierna, lo dice.

Si en vez de eso recita medidas de ejemplo, no ha cargado el skill o no ha mirado los datos. Pídele
que enseñe el comando que ha ejecutado.

## Paso 4: privacidad, sin dramatismo pero sin excusas

- **Datos reales en `negocio/produccion/`**, fuera de git (ya está en el `.gitignore`).
- En el repositorio, ejemplos inventados. El curso no necesita datos personales para enseñarte.
- Si usas un modelo en la nube, los datos que le pegas viajan. Pega lo mínimo: «la clienta C-2026-002»
  en vez de nombre, teléfono y dirección.
- Si un cliente pide borrar sus datos, tienes que poder hacerlo: con CSV es `grep` y borrar la fila.
  Con una base de datos, un `DELETE`. Con una libreta, no.

## Ejercicio

1. Crea tres clientes de prueba y dos tomas de medidas para uno de ellos.
2. Pide al agente la ficha del que tiene dos tomas y que **diga qué cambió** entre la primera y la
   segunda.
3. Pídele que calcule el tejido para una prenda concreta con merma. Revisa la cuenta a mano.
4. Rompe algo a propósito (un teléfono con letras) y mira cómo responde el script. Un script que no
   valida te rompe el CSV en la tercera semana.

## Checklist: ¿lo tengo?

- [ ] Los dos CSV tienen cabeceras y datos coherentes
- [ ] El script busca, crea y añade medidas sin duplicar
- [ ] El agente usa el script y cita datos reales
- [ ] Sé qué columnas son obligatorias y cuáles opcionales
- [ ] Los datos reales están fuera de git

## Errores típicos

- **Guardar el CSV desde Excel con punto y coma** (depende del idioma): el script espera comas.
  Usa «CSV UTF-8» y comprueba la primera línea.
- **Sobrescribir la fila de medidas**: se pierde el historial. Siempre fila nueva con fecha.
- **IDs inventados a mano** (`C-1`, `C-2`, `C-2026-1`): el script y el agente se lían. Un formato.
- **Pedirle al agente que «recuerde» la lista de clientes**: no es memoria, son datos. Van al CSV.

## Siguiente

Módulo 08: el almacén. Tejidos, metros, mínimos y alertas que llegan solas antes de quedarte sin
lana en medio de un encargo.
