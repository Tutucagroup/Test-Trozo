import { chromium } from 'playwright';
import { resolve } from 'node:path';

// La salida a internet de este entorno pasa por un proxy: sin pasárselo a
// Chromium las fotos del CDN y las tipografías se quedan colgadas y la
// navegación agota el tiempo. `curl` ya lo usa por estas mismas variables.
const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy;
const LAUNCH = PROXY ? { proxy: { server: PROXY } } : {};

const page_file = process.argv[2];
const out = process.argv[3];
const width = parseInt(process.argv[4] || '1440', 10);
const b = await chromium.launch(LAUNCH);
const c = await b.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
const p = await c.newPage();
await p.goto('file://' + resolve(page_file), { waitUntil: 'domcontentloaded', timeout: 60000 });
await p.evaluate(() => document.querySelectorAll('img').forEach(i => { i.loading = 'eager'; }));
await p.evaluate(() => document.querySelectorAll('.vsa').forEach(e => e.remove())); // barra fija: taparía el contenido
await p.evaluate(async () => { const s = innerHeight; for (let y = 0; y < document.body.scrollHeight; y += s) { scrollTo(0, y); await new Promise(r => setTimeout(r, 80)); } scrollTo(0, 0); });
await p.evaluate(async () => { await Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 6000); }))); });
await p.waitForTimeout(1500);
await p.screenshot({ path: out, fullPage: true, timeout: 120000 });
console.log(out, await p.evaluate(() => document.body.scrollHeight));
await b.close();
