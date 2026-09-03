import { chromium } from 'playwright';
import { resolve } from 'node:path';
const b = await chromium.launch();
for (const vp of [{n:'desktop',w:1440,h:950},{n:'mobile',w:390,h:844}]) {
  const c = await b.newContext({viewport:{width:vp.w,height:vp.h}});
  const p = await c.newPage();
  await p.goto('file://'+resolve('out/preview.local.html'),{waitUntil:'domcontentloaded',timeout:60000});
  await p.evaluate(()=>document.querySelectorAll('video').forEach(v=>{v.preload='none';v.removeAttribute('autoplay')}));
  // fuerza carga de TODAS las imágenes, incluidas las lazy fuera de pantalla
  await p.evaluate(()=>document.querySelectorAll('img').forEach(i=>{i.loading='eager'; if(i.dataset.src&&!i.src)i.src=i.dataset.src;}));
  await p.evaluate(async()=>{const s=innerHeight;for(let y=0;y<document.body.scrollHeight;y+=s){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}scrollTo(0,0);});
  await p.evaluate(async()=>{await Promise.all([...document.images].filter(i=>!i.complete).map(i=>new Promise(r=>{i.onload=i.onerror=r;setTimeout(r,6000)})))});
  await p.waitForTimeout(1500);
  const bad = await p.evaluate(()=>[...document.images].filter(i=>!i.naturalWidth).map(i=>{
    const s=i.closest('section')||i.closest('div[class]');
    return {src:(i.currentSrc||i.src).split('/').pop(), cls:i.className||'(sin clase)', sec:s?s.className.split(' ')[0]:'?', alt:(i.alt||'').slice(0,40)};
  }));
  const tot = await p.evaluate(()=>document.images.length);
  console.log(`${vp.n}: ${tot} imgs, ${bad.length} sin cargar`);
  bad.forEach(x=>console.log('   ',JSON.stringify(x)));
  await c.close();
}
await b.close();
