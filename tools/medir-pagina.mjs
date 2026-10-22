// Mide una página a varios anchos con Chrome headless + CDP (sin dependencias).
// Uso: node --experimental-websocket tools/medir-pagina.mjs <archivo.html> [320,360,390,1440]
// Sale con código 1 si alguna anchura desborda el documento.
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

const CHROME = process.env.CHROME_BIN ||
  'C:/Program Files/Google/Chrome/Application/chrome.exe';
const file = process.argv[2];
const anchos = (process.argv[3] || '320,360,390,414,768,1440').split(',').map(Number);
if (!file || !existsSync(file)) {
  console.error('Falta el HTML o no existe:', file);
  process.exit(2);
}

const url = 'file:///' + resolve(file).replace(/\\/g, '/').replace(/^\//, '');
const port = 9333 + Math.floor(Math.random() * 200);
const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--hide-scrollbars', '--mute-audio',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${process.env.TEMP || '/tmp'}/cdp-medir-${port}`,
  'about:blank'
], { stdio: ['ignore', 'ignore', 'pipe'] });

let wsUrl = null;
chrome.stderr.on('data', (b) => {
  const m = String(b).match(/DevTools listening on (ws:\/\/\S+)/);
  if (m) wsUrl = m[1];
});

for (let i = 0; i < 100 && !wsUrl; i++) await sleep(100);
if (!wsUrl) { console.error('Chrome no arrancó'); chrome.kill(); process.exit(2); }

const ws = new WebSocket(wsUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let id = 0;
const esperas = new Map();
const sucesos = [];
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && esperas.has(msg.id)) {
    const { res, rej } = esperas.get(msg.id);
    esperas.delete(msg.id);
    msg.error ? rej(new Error(JSON.stringify(msg.error))) : res(msg.result);
  } else if (msg.method) {
    sucesos.push(msg);
  }
};
function enviar(method, params = {}, sessionId) {
  const mid = ++id;
  const payload = { id: mid, method, params };
  if (sessionId) payload.sessionId = sessionId;
  return new Promise((res, rej) => {
    esperas.set(mid, { res, rej });
    ws.send(JSON.stringify(payload));
  });
}
async function evaluar(sessionId, expression) {
  const r = await enviar('Runtime.evaluate', {
    expression, returnByValue: true, awaitPromise: true
  }, sessionId);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text || 'error JS');
  return r.result.value;
}

const MEDIDA = `(() => {
  const d = document.documentElement;
  const cw = d.clientWidth;
  const culpables = [];
  document.querySelectorAll('body *').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.width > 0 && r.right > cw + 1.5) {
      const cn = (e.className && e.className.baseVal !== undefined) ? e.className.baseVal : (e.className || '');
      culpables.push(e.tagName + '.' + String(cn).slice(0, 36) + ' (right ' + Math.round(r.right) + ')');
    }
  });
  return {
    url: location.href.slice(-40), titulo: document.title.slice(0, 30), secciones: document.querySelectorAll('main section').length,
    cw, sw: d.scrollWidth, alto: Math.round(d.scrollHeight),
    hojas: document.styleSheets.length,
    navDisplay: getComputedStyle(document.querySelector('.nz-navbar') || document.body).display,
    culpables: culpables.slice(0, 6)
  };
})()`;

let fallos = 0;
for (const ancho of anchos) {
  const { targetId } = await enviar('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await enviar('Target.attachToTarget', { targetId, flatten: true });
  await enviar('Page.enable', {}, sessionId);
  await enviar('Runtime.enable', {}, sessionId);
  await enviar('Emulation.setDeviceMetricsOverride', {
    width: ancho, height: 1000, deviceScaleFactor: 1, mobile: false
  }, sessionId);
  const antes = sucesos.length;
  await enviar('Page.navigate', { url }, sessionId);
  for (let i = 0; i < 80; i++) {
    if (sucesos.slice(antes).some(s => s.method === 'Page.loadEventFired')) break;
    await sleep(100);
  }
  // espera activa: que el CSS del CDN este realmente aplicado (navbar flex) o 12 s
  let listo = false;
  for (let i = 0; i < 40; i++) {
    const ok = await evaluar(sessionId,
      "(() => { const n = document.querySelector('.nz-navbar'); return !!n && getComputedStyle(n).display === 'flex'; })()");
    if (ok) { listo = true; break; }
    await sleep(300);
  }
  if (!listo) console.log('  AVISO: el CSS no llego a aplicarse en esta pasada (CDN lento)');
  await sleep(600);
  const m = await evaluar(sessionId, MEDIDA);
  const desborda = m.sw > m.cw + 1;
  if (desborda) fallos++;
  console.log(
    `${desborda ? 'DESBORDA' : 'ok      '} ${String(ancho).padStart(4)} px · ` +
    `scroll ${m.sw}/${m.cw} · alto ${m.alto}px · hojas ${m.hojas} · nav ${m.navDisplay} · secs ${m.secciones} · ${m.url}` +
    (m.culpables.length ? '\n            culpables: ' + m.culpables.join(' | ') : '')
  );
  await enviar('Target.closeTarget', { targetId });
}

ws.close();
chrome.kill();
process.exit(fallos ? 1 : 0);
