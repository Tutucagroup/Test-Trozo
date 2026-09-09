import { chromium } from 'playwright';
import { resolve } from 'node:path';
const [file, out, w, sel, h] = process.argv.slice(2);
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: parseInt(w,10), height: parseInt(h||'1200',10) }, deviceScaleFactor: 1 });
const p = await c.newPage();
await p.goto('file://' + resolve(file), { waitUntil: 'domcontentloaded', timeout: 60000 });
await p.evaluate(() => document.querySelectorAll('img').forEach(i => { i.loading='eager'; }));
await p.evaluate(async () => { await Promise.all([...document.images].filter(i=>!i.complete).map(i=>new Promise(r=>{i.onload=i.onerror=r;setTimeout(r,6000);}))); });
await p.waitForTimeout(900);
const el = await p.$(sel);
if (el) { await el.screenshot({ path: out }); } else { await p.screenshot({ path: out }); }
console.log(out, sel, !!el);
await b.close();
