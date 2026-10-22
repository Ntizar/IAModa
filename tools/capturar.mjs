// Captura franjas de una página larga con Chrome headless + CDP, sin depender del scroll.
// Uso: node --experimental-websocket tools/capturar.mjs <archivo.html> <ancho> <prefijo> [id1,id2,...]
// Cada sección se recorta con Page.captureScreenshot + clip (captureBeyondViewport).
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { existsSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const CHROME = process.env.CHROME_BIN || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [file, anchoArg, prefijo, idsArg, queryArg] = process.argv.slice(2);
const ancho = Number(anchoArg || 1440);
const ids = (idsArg || 'tesis,cadena,plan,demos,herramientas,evaluacion').split(',');
if (!file || (!/^https?:\/\//.test(file) && !existsSync(file))) { console.error('Falta el HTML:', file); process.exit(2); }

const base = /^https?:\/\//.test(file) ? file :
  'file:///' + resolve(file).replace(/\\/g, '/').replace(/^\//, '');
const url = base + (queryArg ? '?' + queryArg : '');
const port = 9533 + Math.floor(Math.random() * 200);
const chrome = spawn(CHROME, [
  '--headless=new', '--no-first-run', '--hide-scrollbars',
  '--enable-unsafe-swiftshader', '--use-gl=angle',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${process.env.TEMP || '/tmp'}/cdp-cap-${port}`,
  `--window-size=${ancho},1000`, 'about:blank'
], { stdio: ['ignore', 'ignore', 'pipe'] });

let wsUrl = null;
chrome.stderr.on('data', b => {
  const m = String(b).match(/DevTools listening on (ws:\/\/\S+)/);
  if (m) wsUrl = m[1];
});
for (let i = 0; i < 100 && !wsUrl; i++) await sleep(100);
if (!wsUrl) { console.error('Chrome no arranco'); chrome.kill(); process.exit(2); }

const ws = new WebSocket(wsUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0; const esperas = new Map(); const sucesos = [];
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && esperas.has(m.id)) {
    const { res, rej } = esperas.get(m.id); esperas.delete(m.id);
    m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result);
  } else if (m.method) sucesos.push(m);
};
const enviar = (method, params = {}, sessionId) => {
  const mid = ++id; const p = { id: mid, method, params };
  if (sessionId) p.sessionId = sessionId;
  return new Promise((res, rej) => { esperas.set(mid, { res, rej }); ws.send(JSON.stringify(p)); });
};
const evaluar = async (sid, expression) => {
  const r = await enviar('Runtime.evaluate', { expression, returnByValue: true }, sid);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
  return r.result.value;
};

const { targetId } = await enviar('Target.createTarget', { url: 'about:blank' });
const { sessionId } = await enviar('Target.attachToTarget', { targetId, flatten: true });
await enviar('Page.enable', {}, sessionId);
await enviar('Runtime.enable', {}, sessionId);
await enviar('Emulation.setDeviceMetricsOverride',
  { width: ancho, height: 1000, deviceScaleFactor: 1, mobile: false }, sessionId);
const antes = sucesos.length;
await enviar('Page.navigate', { url }, sessionId);
for (let i = 0; i < 80; i++) {
  if (sucesos.slice(antes).some(s => s.method === 'Page.loadEventFired')) break;
  await sleep(100);
}
await sleep(2000);

const cajas = await evaluar(sessionId, `(() => {
  const out = {};
  ${JSON.stringify(ids)}.forEach(id => {
    const e = document.getElementById(id);
    if (e) { const r = e.getBoundingClientRect(); out[id] = { y: Math.round(r.top + scrollY), h: Math.round(r.height) }; }
  });
  return out;
})()`);

for (const [id, c] of Object.entries(cajas)) {
  const alto = Math.min(c.h, 2600);
  const shot = await enviar('Page.captureScreenshot', {
    format: 'png',
    clip: { x: 0, y: c.y, width: ancho, height: alto, scale: 1 },
    captureBeyondViewport: true
  }, sessionId);
  const f = `${prefijo}-${id}.png`;
  writeFileSync(f, Buffer.from(shot.data, 'base64'));
  console.log(`${id.padEnd(14)} y=${String(c.y).padStart(6)} alto=${String(c.h).padStart(5)} -> ${f}`);
}

ws.close(); chrome.kill(); process.exit(0);
