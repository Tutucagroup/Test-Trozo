// Comprueba que los desplegables del menú se abren al pasar el ratón: el CSS los
// mantiene ocultos con `visibility`, así que un fallo no se ve en una captura normal.
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
p.on('pageerror', (e) => console.log('[JS]', e.message.split('\n')[0]));
await p.goto('file://' + resolve(process.argv[2]), { waitUntil: 'domcontentloaded' });
for (const label of ['DRESSES', 'NEW', 'COLOUR']) {
  const link = p.locator('.pph__nav-link', { hasText: new RegExp(`^\\s*${label}\\s*$`) }).first();
  await link.hover();
  await p.waitForTimeout(350);
  const info = await p.evaluate((t) => {
    const item = [...document.querySelectorAll('.pph__nav-item')]
      .find((el) => el.querySelector('.pph__nav-link')?.textContent.trim().startsWith(t));
    const drop = item?.querySelector('.pph__drop');
    if (!drop) return { visible: false, reason: 'sin desplegable' };
    const cs = getComputedStyle(drop);
    const r = drop.getBoundingClientRect();
    return { visible: cs.visibility === 'visible' && cs.opacity === '1',
             mega: drop.classList.contains('pph__drop--mega'),
             enlaces: drop.querySelectorAll('a').length,
             ancho: Math.round(r.width), alto: Math.round(r.height), x: Math.round(r.x) };
  }, label);
  console.log(label, JSON.stringify(info));
  if (label === 'DRESSES') await p.screenshot({ path: process.argv[3], clip: { x: 0, y: 0, width: 1440, height: 460 } });
}
await b.close();
