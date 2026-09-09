import { chromium } from 'playwright';
import { resolve } from 'node:path';

// La salida a internet de este entorno pasa por un proxy: sin pasárselo a
// Chromium las fotos del CDN y las tipografías se quedan colgadas y la
// navegación agota el tiempo. `curl` ya lo usa por estas mismas variables.
const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy;
const LAUNCH = PROXY ? { proxy: { server: PROXY } } : {};

const b = await chromium.launch(LAUNCH);
const c = await b.newContext({ viewport: { width: 1440, height: 900 } });
const p = await c.newPage();
p.on('pageerror', e => console.log('[JS]', e.message.split('\n')[0]));
await p.goto('file://' + resolve('pp-out/preview.local.html'), { waitUntil: 'networkidle' });
const out = await p.evaluate(() => {
  const r = {};
  const q = (s) => document.querySelector(s);
  const rail = q('.ppcc__rail');
  if (rail) {
    const cs = getComputedStyle(rail);
    r.rail = { padL: cs.paddingLeft, x: rail.getBoundingClientRect().x, w: rail.clientWidth,
               scrollW: rail.scrollWidth, scrollLeft: rail.scrollLeft, cells: rail.querySelectorAll('li').length, cellW: rail.querySelector('li').getBoundingClientRect().width, firstCellX: rail.querySelector('li').getBoundingClientRect().x };
  }
  const feed = q('.ppf__rail');
  if (feed) { const cs=getComputedStyle(feed); r.feed = { display: cs.display, padL: cs.paddingLeft, x: feed.getBoundingClientRect().x, w: feed.getBoundingClientRect().width }; }
  const grid = q('.ppt__grid');
  if (grid) r.grid = { x: grid.getBoundingClientRect().x, w: grid.getBoundingClientRect().width };
  const cta = q('.ppcc__cta');
  if (cta) r.ctaText = JSON.stringify(cta.textContent);
  return r;
});
console.log(JSON.stringify(out, null, 2));
await b.close();
