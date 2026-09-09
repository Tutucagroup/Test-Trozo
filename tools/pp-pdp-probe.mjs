import { chromium } from 'playwright';
import { resolve } from 'node:path';

const file = process.argv[2];
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: 1440, height: 900 } });
const p = await c.newPage();
const errors = [];
p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
await p.goto('file://' + resolve(file), { waitUntil: 'domcontentloaded', timeout: 60000 });
await p.waitForTimeout(800);

const read = () => p.evaluate(() => ({
  precio: document.querySelector('[data-ppp-price]')?.textContent.trim(),
  talle: document.querySelector('[data-ppp-size-name]')?.textContent.trim(),
  atc: document.querySelector('[data-ppp-atc]')?.textContent.trim(),
  atcOff: document.querySelector('[data-ppp-atc]')?.disabled,
  stock: (() => { const e = document.querySelector('[data-ppp-stock]'); return e && !e.hidden ? e.textContent.trim() : null; })(),
  notify: !document.querySelector('[data-ppp-notify]')?.hidden,
  sticky: document.querySelector('[data-ppp-sticky-size]')?.value,
  eta: document.querySelector('[data-ppp-eta]')?.textContent.trim(),
  recientes: !document.querySelector('[data-pprv]')?.hidden,
}));

console.log('inicial   ', JSON.stringify(await read()));
await p.click('[data-ppp-size="US 4"]');
console.log('US 4      ', JSON.stringify(await read()));
await p.click('[data-ppp-size="US 0"]');
console.log('US 0 (sin)', JSON.stringify(await read()));
await p.click('[data-ppp-size="US 6"]');
console.log('US 6      ', JSON.stringify(await read()));

await p.click('[data-ppp-open-guide]');
console.log('guía abierta:', await p.evaluate(() => !document.querySelector('[data-ppp-guide]').hidden));
await p.click('.ppp__guide-close');
console.log('guía cerrada:', await p.evaluate(() => document.querySelector('[data-ppp-guide]').hidden));

await p.click('.ppp__acc-item:nth-child(2) .ppp__acc-head');
console.log('acordeón 2 abierto:', await p.evaluate(() => document.querySelectorAll('.ppp__acc-item')[1].classList.contains('is-open')));

await p.click('[data-ppp-thumb="3"]');
await p.waitForTimeout(1200);
console.log('miniatura 3 activa:', await p.evaluate(() => document.querySelector('[data-ppp-thumb="3"]').classList.contains('is-active')),
            '| foto en pantalla:', await p.evaluate(() => {
              const box = document.querySelector('[data-ppp-slides]');
              return Math.round(box.scrollLeft / box.clientWidth);
            }));
await p.click('[data-ppp-next]');
await p.waitForTimeout(1200);
console.log('tras siguiente:', await p.evaluate(() => {
  const box = document.querySelector('[data-ppp-slides]');
  return { foto: Math.round(box.scrollLeft / box.clientWidth), thumb: [...document.querySelectorAll('[data-ppp-thumb]')].findIndex(t => t.classList.contains('is-active')) };
}));
await p.click('[data-ppp-prev]');
await p.click('[data-ppp-prev]');
await p.click('[data-ppp-prev]');
await p.click('[data-ppp-prev]');
await p.click('[data-ppp-prev]');
await p.waitForTimeout(1400);
console.log('tras 5 anteriores (da la vuelta):', await p.evaluate(() => {
  const box = document.querySelector('[data-ppp-slides]');
  return { foto: Math.round(box.scrollLeft / box.clientWidth), total: document.querySelectorAll('[data-ppp-slide]').length };
}));

await p.click('[data-ppp-slide="1"]');
await p.waitForTimeout(300);
console.log('lupa:', await p.evaluate(() => document.querySelector('[data-ppp-zoombox]').classList.contains('is-on')));
await p.keyboard.press('Escape');

await p.evaluate(() => window.scrollTo(0, 1800));
await p.waitForTimeout(600);
console.log('barra fija visible:', await p.evaluate(() => document.querySelector('[data-ppp-sticky]').classList.contains('is-on')));

// Segunda visita: la fila de «vistos hace poco» tiene que aparecer.
await p.reload({ waitUntil: 'domcontentloaded' });
await p.waitForTimeout(600);
console.log('recientes tras recargar:', await p.evaluate(() => !document.querySelector('[data-pprv]').hidden),
            '| tarjetas:', await p.evaluate(() => document.querySelectorAll('[data-pprv-list] li').length));

console.log('errores:', errors.filter(e => !/net::ERR|Failed to load/.test(e)));
await b.close();
