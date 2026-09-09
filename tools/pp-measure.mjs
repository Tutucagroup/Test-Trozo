import { chromium } from 'playwright';
import { resolve } from 'node:path';
const [file, w] = process.argv.slice(2);
const b = await chromium.launch();
const p = await (await b.newContext({ viewport: { width: parseInt(w,10), height: 1000 } })).newPage();
await p.goto('file://' + resolve(file), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(700);
console.log(JSON.stringify(await p.evaluate(() => {
  const box = (s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height) }; };
  const t = document.querySelector('[data-ppp-thumb="0"]');
  return {
    media: box('.ppp__media'), rail: box('.ppp__rail'), stage: box('.ppp__stage'),
    slides: box('[data-ppp-slides]'), slide0: box('[data-ppp-slide="0"]'),
    thumb0: box('[data-ppp-thumb="0"]'), thumbImg: box('[data-ppp-thumb="0"] img'),
    thumbCS: t ? { alignSelf: getComputedStyle(t).alignSelf, flex: getComputedStyle(t).flex, height: getComputedStyle(t).height } : null,
    railCS: (() => { const e = document.querySelector('.ppp__rail'); return e ? { alignItems: getComputedStyle(e).alignItems, maxHeight: getComputedStyle(e).maxHeight, overflowY: getComputedStyle(e).overflowY } : null; })(),
  };
}, null), null, 1));
await b.close();
