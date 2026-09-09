import { chromium } from 'playwright';
import { resolve } from 'node:path';
const b = await chromium.launch();
for (const vp of [{n:'desktop',w:1440,h:950},{n:'mobile',w:390,h:844}]) {
  const c = await b.newContext({viewport:{width:vp.w,height:vp.h}});
  const p = await c.newPage();
  await p.goto('file://'+resolve('pp-out/preview.local.html'),{waitUntil:'domcontentloaded',timeout:60000});
  await p.evaluate(()=>document.querySelectorAll('img').forEach(i=>{i.loading='eager';}));
  await p.evaluate(async()=>{const s=innerHeight;for(let y=0;y<document.body.scrollHeight;y+=s){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}scrollTo(0,0);});
  await p.evaluate(async()=>{await Promise.all([...document.images].filter(i=>!i.complete).map(i=>new Promise(r=>{i.onload=i.onerror=r;setTimeout(r,6000)})))});
  await p.waitForTimeout(1500);
  const bad = await p.evaluate(()=>[...document.images].filter(i=>!i.naturalWidth).map(i=>({src:(i.currentSrc||i.src).split('/').pop(), cls:i.className||'-', parent:i.parentElement?.className||'-'})));
  console.log(`${vp.n}: ${await p.evaluate(()=>document.images.length)} imgs, ${bad.length} sin cargar`);
  bad.forEach(x=>console.log('   ',JSON.stringify(x)));
  await c.close();
}
await b.close();
