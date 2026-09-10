import { chromium } from 'playwright';
import { resolve } from 'node:path';
const [file, out] = process.argv.slice(2);
const b = await chromium.launch();
const p = await (await b.newContext({ viewport: { width: 600, height: 200 }, deviceScaleFactor: 2 })).newPage();
await p.setContent(`<body style="margin:0;display:grid;place-items:center;height:200px;background:#fff">
  <img src="file://${resolve(file)}" style="width:420px">
</body>`);
await p.waitForTimeout(500);
await p.screenshot({ path: out });
await b.close();
