---
titulo: Instala Hermes y habla con él
numero: "02"
resumen: Instalación en Windows, macOS y Linux, elección de modelo, primer chat y diagnóstico. La base de todo lo que viene después.
duracion: 40 min
nivel: Desde cero
objetivo: Tener Hermes instalado, con un modelo funcionando y una conversación de prueba que lea un fichero de tu ordenador.
criterios:
  - hermes doctor no muestra errores graves
  - El agente responde en una conversación normal, no solo en modo prueba
  - El agente ha leído un fichero tuyo y ha citado su contenido
  - Sabes dónde viven la configuración, las claves y las sesiones
---

## Qué vas a instalar

**Hermes Agent** es el motor: el programa que habla con el modelo, ejecuta herramientas en tu
ordenador, guarda memoria, carga skills y atiende Telegram, cron y consola. Es software libre de
Nous Research y se instala con un comando.

El modelo (la «inteligencia») se elige aparte. Puede ser Nous Portal, OpenRouter, Anthropic, OpenAI
o un endpoint propio. El curso no asume ninguno en concreto: donde diga «tu proveedor», pones el
tuyo.

## Paso 1: instalar

**Linux, macOS o WSL2** — abre una terminal y pega:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

**Windows nativo** — abre PowerShell y pega:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

**Windows o macOS con interfaz** — descarga el instalador de escritorio desde
<https://hermes-agent.nousresearch.com/> y ejecútalo. Instala la app y deja el comando `hermes`
disponible.

El instalador se encarga de Python, Node, ripgrep, ffmpeg y del entorno virtual. No tienes que
instalar nada de eso a mano.

Después, recarga la shell:

```bash
source ~/.bashrc    # en macOS con zsh: source ~/.zshrc
```

En PowerShell, cierra y vuelve a abrir la ventana.

## Paso 2: comprobar que está

```bash
hermes doctor
```

Deberías ver un resumen del entorno y, como mucho, avisos de herramientas que no usas. Un error
rojo de proveedor o de configuración sí hay que resolverlo antes de seguir.

```bash
hermes --version
```

Si el comando no existe, el instalador no añadió `~/.local/bin` al PATH. Añádelo:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Paso 3: elegir modelo

En este curso el modelo se sirve desde **NaN** (cuota fija, API compatible con OpenAI). La cuenta,
el plan y la clave se explican paso a paso en el **módulo 03**; aquí solo dejamos Hermes listo para
recibirla.

La vía más rápida, si ya tienes una suscripción de Nous Portal:

```bash
hermes setup --portal
```

Te abre el navegador para el login OAuth, configura Nous como proveedor y activa las herramientas
del gateway (búsqueda web, imágenes, voz, navegador).

Si prefieres tu propia clave o un endpoint compatible con OpenAI:

```bash
hermes model
```

Te guía por proveedor, modelo y clave. La clave se guarda en `~/.hermes/.env`, nunca en el
repositorio.

> **Consejo de coste:** empieza con un modelo bueno para razonar y barato para el día a día. En el
> módulo 12 verás cómo fijar un modelo distinto solo para las tareas programadas.

## Paso 4: primera conversación

```bash
hermes
```

Escribe estas tres cosas, en este orden:

1. `Hola. ¿Qué herramientas tienes disponibles?`
2. `Crea un fichero llamado prueba.md en mi carpeta actual con tres líneas sobre mí.`
3. `Lee prueba.md y dime qué pone.`

Si la tercera respuesta cita el contenido real, el agente está ejecutando de verdad: no está
inventando. Ese es el primer criterio del módulo.

Sal con `/exit` (o `Ctrl+C` dos veces).

## Paso 5: saber dónde vive todo

```bash
hermes config get model
ls ~/.hermes
```

| Ruta | Qué es |
|---|---|
| `~/.hermes/config.yaml` | Configuración: modelo, terminal, compresión, herramientas |
| `~/.hermes/.env` | Claves y secretos. **Fuera de git, siempre** |
| `~/.hermes/SOUL.md` | Identidad del agente |
| `~/.hermes/memories/` | `MEMORY.md` y `USER.md`: la memoria persistente |
| `~/.hermes/skills/` | Los skills (procedimientos) |
| `~/.hermes/cron/` | Tareas programadas |
| `~/.hermes/sessions/` | Historial de sesiones |
| `~/.hermes/logs/` | Errores y actividad (secretos redactados) |

Dos comandos que usarás mucho:

```bash
hermes config get model          # ¿qué modelo estoy usando?
hermes config set model tu-proveedor/tu-modelo
```

## Paso 6: Telegram (opcional, pero muy recomendable)

Con el gateway, tu agente te atiende desde el móvil. Es la diferencia entre «una cosa del
ordenador» y «un empleado al que le escribes».

1. En Telegram, habla con **@BotFather** y manda `/newbot`.
2. Elige nombre y usuario (debe terminar en `bot`).
3. Copia el token que te da.
4. Configura:

```bash
hermes gateway setup
```

El asistente te pide el token y tu ID de usuario. Guarda `TELEGRAM_BOT_TOKEN` y
`TELEGRAM_ALLOWED_USERS` en el `.env` del perfil. Arranca el gateway:

```bash
hermes gateway start
hermes gateway status
```

Escríbele al bot. Si no responde, revisa que el gateway esté en marcha y que tu ID esté en la lista
de permitidos.

> **Seguridad:** sin `TELEGRAM_ALLOWED_USERS`, cualquiera que encuentre tu bot puede hablar con tu
> agente. Es lo primero que se configura, no lo último.

## Ejercicio

Crea `prueba.md` con tres datos reales de tu negocio (sin nombres de clientes) y pídele al agente
que lo lea, lo resuma en una línea y lo guarde en memoria como contexto de tu negocio. Cierra la
sesión y abre otra: debe seguir sabiéndolo.

## Checklist: ¿lo tengo?

- [ ] `hermes --version` responde y `hermes doctor` no tiene errores graves
- [ ] He elegido modelo y sé cuál está activo (`hermes config get model`)
- [ ] El agente ha leído `prueba.md` y ha citado su contenido
- [ ] Sé dónde están `config.yaml`, `.env` y las sesiones
- [ ] (Opcional) El bot de Telegram me responde solo a mí

## Errores típicos

- **`hermes: command not found`**: PATH sin `~/.local/bin`. Recarga la shell o añade la línea del
  paso 2.
- **`API key not set`**: no hay proveedor configurado. `hermes model` otra vez.
- **Instalar como root y luego usar otro usuario**: el instalador deja los datos en
  `/root/.hermes`. Instala como tu usuario normal.
- **El bot contesta a cualquiera**: falta `TELEGRAM_ALLOWED_USERS`.
- **Mezclar el Hermes del curso con el de producción**: usa perfiles (`hermes profile`). Si eres
  principiante, no toques el que ya funciona: este curso crea el suyo.

## Siguiente

Módulo 03: compras el acceso a NaN, generas tu clave y la dejas donde Hermes la encuentra. Es el
paso que separa «tener el programa» de «tener un agente que responde».
