import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const page_file = process.argv[2] || 'out/preview.local.html';
const OUT = resolve(process.argv[3] || 'out/shots');
mkdirSync(OUT, { recursive: true });
const url = 'file://' + resolve(page_file);

const viewports = [
  { name: 'desktop', width: 1440, height: 950 },
  { name: 'mobile', width: 390, height: 844 },
];

const browser = await chromium.launch();

for (const vp of viewports) {
  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => console.log(`  [JS ${vp.name}] ${e.message.split('\n')[0]}`));

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

  // Los videos no aportan a la captura y su carga bloquea el evento load.
  await page.evaluate(() => {
    document.querySelectorAll('video').forEach((v) => {
      v.preload = 'none';
      v.removeAttribute('autoplay');
    });
  });

  await page.evaluate(() => document.fonts.ready);

  // Recorre la página para disparar las imágenes con loading="lazy".
  await page.evaluate(async () => {
    const step = window.innerHeight;
    for (let y = 0; y < document.body.scrollHeight; y += step) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 70));
    }
    window.scrollTo(0, 0);
  });

  await page.evaluate(async () => {
    await Promise.all(
      Array.from(document.images)
        .filter((i) => !i.complete)
        .map(
          (i) =>
            new Promise((res) => {
              i.onload = i.onerror = res;
              setTimeout(res, 4000);
            })
        )
    );
  });
  await page.waitForTimeout(1200);

  const broken = await page.evaluate(() =>
    Array.from(document.images)
      .filter((i) => !i.naturalWidth)
      .map((i) => i.currentSrc || i.src)
      .slice(0, 8)
  );
  const height = await page.evaluate(() => document.body.scrollHeight);
  console.log(`${vp.name}  ${vp.width}x${height}  imagenes rotas: ${broken.length}`);
  broken.forEach((b) => console.log(`   roto: ${b.slice(-70)}`));

  const sections = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('body > *').forEach((el, i) => {
      const r = el.getBoundingClientRect();
      if (r.height < 5) return;
      const cls = (typeof el.className === 'string' ? el.className : '').split(' ')[0] || el.tagName.toLowerCase();
      out.push({ i, cls, h: Math.round(r.height) });
    });
    return out;
  });

  for (const s of sections) {
    const name = `${vp.name}-${String(s.i).padStart(2, '0')}-${s.cls}.png`;
    try {
      await page.locator('body > *').nth(s.i).screenshot({ path: `${OUT}/${name}`, timeout: 25000 });
      console.log(`   ${name}  (h=${s.h})`);
    } catch (e) {
      console.log(`   FALLO ${name}: ${e.message.split('\n')[0]}`);
    }
  }
  await ctx.close();
}
await browser.close();
console.log('listo');
