---
titulo: NaN: cuenta, plan y clave de API
numero: "03"
resumen: Compras el acceso a NaN, generas la clave y la dejas donde Hermes la lee. Paso a paso, con el plano de qué se instala, dónde queda y qué no se toca nunca.
duracion: 30 min
nivel: Con Hermes instalado
objetivo: Tener una clave de NaN funcionando en Hermes, con el modelo elegido y la clave fuera del repositorio.
criterios:
  - Tengo cuenta en NaN y un plan con inferencia (no el plan de solo comunidad)
  - La clave sk- existe, está en .env y NO está en git
  - El agente responde con un modelo de NaN
  - Sé leer el gasto y los límites de mi plan
---

## El plano: qué se instala y dónde queda

Antes de comprar nada, ten claro el mapa. Son tres piezas y cada una vive en un sitio:

| Pieza | Qué es | Dónde vive |
|---|---|---|
| **Hermes** | El programa que ejecuta el agente | `~/.hermes/hermes-agent/` (instalado en el módulo 02) |
| **Tu configuración** | Modelo, proveedor, preferencias | `~/.hermes/config.yaml` |
| **Tu clave** | El secreto que paga el uso del modelo | `~/.hermes/.env` |
| **NaN** | Quien sirve el modelo | `https://api.nan.builders/v1` |

Regla que no se rompe: **el secreto va en `.env`, nunca en `config.yaml`, nunca en el repositorio**.
`config.yaml` dice *dónde* buscar la clave; `.env` la contiene.

## Por qué NaN y no pagar por token

Los proveedores clásicos te cobran cada token: la factura sube cuando el agente trabaja más. NaN es
una comunidad de GPUs compartidas: pagas una cuota fija y tienes modelos abiertos servidos en la UE,
sin factura por token. La API es **compatible con OpenAI**, así que cualquier herramienta que acepte
`base_url` + `api_key` funciona cambiando dos valores.

Para un agente que va a leer tus CSV, escribir informes y atender crons todos los días, una cuota
fija es mucho más fácil de presupuestar que un contador que no ves.

## Paso 1: crear la cuenta

1. Entra en <https://cloud.nan.builders/signup>.
2. Regístrate con tu correo y verifica.
3. Elige plan. Los que importan para este curso:

| Plan | Precio | Qué incluye | ¿Sirve para el curso? |
|---|---|---|---|
| **nan_community** | 14,99 €/mes | Discord, eventos, canales privados | **No**: no incluye API key ni llamadas a modelos |
| **nan_member** | 70 €/mes | Inferencia + API key + 1 workspace Micro gratis | **Sí**: es el plan normal para empezar |
| **GLM 5.3 premium** | 200 €/mes | Lo de nan_member + GLM 5.3 (753B, razonamiento) y 3.000M tokens por periodo | Sí, si vas a trabajar con el modelo grande a diario |

IVA incluido, sin permanencia, se cancela cuando quieras. El acceso se activa unos minutos después
del pago.

> **No compres el plan de 14,99 € pensando que incluye API.** Es solo comunidad. Sin plan de
> inferencia no hay clave y el agente no puede responder.

## Paso 2: generar la clave

1. Entra en <https://cloud.nan.builders/> con tu cuenta.
2. **Settings → API Keys**.
3. Crea una clave nueva. Se llama `sk-...`.
4. Cópiala **en ese momento**: no se vuelve a mostrar entera.

Si se te pierde, no pasa nada: se revoca y se crea otra. Lo que no se hace es compartirla.

## Paso 3: guardarla donde toca

En la carpeta de tu instalación:

```bash
# Linux / macOS
nano ~/.hermes/.env
```

Añade esta línea (sustituye por tu clave real):

```bash
OPENAI_API_KEY=sk-tu-clave-de-nan
```

En Windows, el fichero es `%USERPROFILE%\.hermes\.env` y se abre con el Bloc de notas.

Comprueba que el fichero está protegido y **no** dentro de ningún repositorio:

```bash
ls -l ~/.hermes/.env
grep -c "sk-" ~/.hermes/config.yaml   # debe dar 0: la clave no va en config.yaml
```

## Paso 4: decirle a Hermes que use NaN

La vía guiada:

```bash
hermes model
```

Elige **endpoint personalizado / OpenAI-compatible** y rellena:

- **Base URL**: `https://api.nan.builders/v1`
- **API key**: la variable `OPENAI_API_KEY` (no pegues la clave otra vez)
- **Modelo**: `deepseek-v4-flash`

Si prefieres editar el fichero, `~/.hermes/config.yaml` queda así:

```yaml
model:
  default: deepseek-v4-flash
  provider: nan
providers:
  nan:
    api: https://api.nan.builders/v1
    key_env: OPENAI_API_KEY
    default_model: deepseek-v4-flash
    api_mode: chat_completions
```

`key_env` significa «la clave está en la variable de entorno `OPENAI_API_KEY`», que es la que
acabas de escribir en `.env`. Así el YAML se puede compartir y la clave no.

## Paso 5: comprobar que responde

Primero la API sola, sin Hermes de por medio:

```bash
curl -s https://api.nan.builders/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Di solo: ok"}],"max_tokens":10}'
```

Si devuelve un JSON con `"ok"`, la clave y el modelo funcionan. Si devuelve `401`, la clave está mal
o es de otro plan. Si devuelve `404`, el nombre del modelo está mal escrito.

Ahora el agente:

```bash
hermes doctor
hermes chat -q "Responde solo con el modelo que estás usando y di ok"
```

## Los modelos que puedes pedir

| Modelo | Para qué | Cuota mensual por miembro |
|---|---|---|
| `deepseek-v4-flash` | **Empieza aquí**: razona, ve imágenes, tool calling, 1M de contexto | 3.000M tokens |
| `glm5.3-flash` | Multimodal, bueno en código y tareas largas | 2.000M tokens |
| `qwen3.8-flash` | Rápido y con visión | 500M tokens |
| `mimo-v2.6-flash` | Texto, imagen y audio | 1.000M tokens |
| `gemma4` | Ligero, contexto de 262K | — |
| `glm5.3` | El grande (753B), solo con plan premium | 3.000M por periodo |

Límites de la clave: **60 peticiones por minuto** y **7 peticiones simultáneas** en el plan base (10
en premium). Para un taller con un agente y unos cuantos crons, sobra.

## Paso 6: elegir modelo con criterio (y sin sustos)

- **Día a día y crons**: `deepseek-v4-flash`. Barato de cuota y suficiente para leer CSV y redactar.
- **Tareas de razonamiento largo** (un informe con cálculos, un plan): el mismo, subiendo
  `reasoning_effort` a `medium` o `high`.
- **Código y contexto enorme**: `glm5.3-flash`.
- **Cuando algo falla por «falta de cabeza»**: prueba `glm5.3` si tienes premium, pero no lo dejes
  fijo para todo.

Y una manía que ahorra disgustos: **fija un modelo distinto para los crons** (lo verás en el módulo
12). Así una rutina no te consume la cuota del modelo bueno.

## Paso 7: si no quieres NaN

El curso funciona igual con cualquier proveedor compatible con OpenAI:

- **OpenRouter**: una clave para muchos modelos; pagas por token.
- **OpenAI / Anthropic / Google**: claves propias, factura por uso.
- **Un modelo local** (Ollama, LM Studio): `http://localhost:11434/v1`, sin clave, pero necesitas
  hardware y el agente razona menos.

Cambia `api`, `key_env` y `default_model` y sigues en el módulo 04 sin tocar nada más.

## Ejercicio

1. Crea la cuenta y elige plan (si ya tienes clave, salta al paso 3).
2. Genera la clave y guárdala en `.env`.
3. Configura el proveedor y verifica con `curl`.
4. Pregúntale al agente: «¿Qué modelo eres y cuánto contexto tienes?». Contrasta con la tabla.
5. Anota en `notas/` la fecha de alta y el plan contratado (sin la clave, obviamente).

## Checklist: ¿lo tengo?

- [ ] Cuenta de NaN con plan de inferencia (no el de comunidad)
- [ ] Clave `sk-` generada y guardada en `~/.hermes/.env`
- [ ] `config.yaml` apunta a `https://api.nan.builders/v1` y usa `key_env`
- [ ] `curl` devuelve una respuesta del modelo
- [ ] El agente responde en una conversación normal
- [ ] Sé qué modelo uso, qué cuota tengo y cuántas peticiones por minuto

## Errores típicos

- **Comprar el plan de 14,99 €** y esperar clave: no la hay. Es comunidad, no inferencia.
- **Pegar la clave en `config.yaml`** o en un `SOUL.md`: se comparte sin querer. Va en `.env`.
- **Pegar la clave en el chat** para que «el agente la configure»: queda en el historial. Se escribe
  en el fichero, no se dicta.
- **Confundir `OPENAI_API_KEY` con una clave de OpenAI**: es solo el nombre de la variable; el valor
  es de NaN.
- **Modelo mal escrito** (`deepseek-v4` a secas): devuelve 404. Copia el id exacto de la tabla.
- **Compartir el `.env` por WhatsApp** «para que lo pruebe un compañero». Se genera otra clave.

## Siguiente

Módulo 04: creas el repositorio que será la memoria de tu negocio y aprendes a trabajar con el
agente dentro de él. Ahí empieza lo bueno.
