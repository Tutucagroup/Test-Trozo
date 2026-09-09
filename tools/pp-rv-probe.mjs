import { chromium } from 'playwright';
const b = await chromium.launch();
const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
const url = 'http://localhost:8731/preview-product.local.html';
await p.goto(url, { waitUntil: 'domcontentloaded' });
// Simula una visita previa a otra ficha, que es cuando la fila tiene sentido.
await p.evaluate(() => localStorage.setItem('pp-recently-viewed', JSON.stringify([{
  handle: 'otro-vestido', url: '/products/otro-vestido', title: 'Otro Vestido "Comillas" & Co',
  price: '$59.99', was: '$79.99', onSale: true,
  image: 'assets/' + (document.querySelector('.ppcard__img--main')?.getAttribute('src') || '').split('/').pop(),
  alt: ''
}])));
await p.goto(url, { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(700);
console.log('visible:', await p.evaluate(() => !document.querySelector('[data-pprv]').hidden),
            '| tarjetas:', await p.evaluate(() => document.querySelectorAll('[data-pprv-list] li').length),
            '| titulo:', await p.evaluate(() => document.querySelector('[data-pprv-list] .ppcard__title')?.textContent),
            '| orden guardado:', await p.evaluate(() => JSON.parse(localStorage.getItem('pp-recently-viewed')).map(i => i.handle)));
await b.close();
