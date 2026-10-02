/** Real-browser launch regression test, run in an isolated CI browser profile.
 * npm install --prefix _build/browser --no-audit --no-fund playwright@1.63.0
 * node _build/browser/node_modules/playwright/cli.js install --with-deps chromium
 * node scripts/check_browser_launch.mjs
 * BROWSER_TEST_BASE_URL may point at a served build instead of GitHub Pages.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = await import(pathToFileURL(path.join(root, '_build/browser/node_modules/playwright/index.mjs')));
const base = process.env.BROWSER_TEST_BASE_URL || 'https://jltobias.github.io/JupyterLite-World-Monitor-Prototype/';
const out = path.join(root, '_build/browser-report');
fs.mkdirSync(out, {recursive: true});
const browser = await chromium.launch();
const results = [];

async function check(name, entry, warmWorkspace = false) {
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}});
  const page = await context.newPage();
  const errors = [], failures = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('requestfailed', request => failures.push({url: request.url(), error: request.failure()?.errorText}));
  page.on('response', response => { if (response.status() >= 400) failures.push({url: response.url(), status: response.status()}); });
  let status = 'passed', reason;
  try {
    if (warmWorkspace) {
      await page.goto(new URL('lab/index.html', base).href);
      await page.getByRole('menuitem', {name: 'File', exact: true}).waitFor({state: 'visible', timeout: 60000});
    }
    await page.goto(new URL(entry, base).href);
    await page.getByRole('heading', {name: /shared picture, an inspectable analysis/i})
      .waitFor({state: 'visible', timeout: 60000});
  } catch (error) {
    status = 'failed'; reason = String(error);
  }
  const body = await page.locator('body').innerText();
  await page.screenshot({path: path.join(out, name+'.png')});
  const result = {name, entry, status, reason, finalUrl: page.url(), errors, failures, body: body.slice(0,12000)};
  fs.writeFileSync(path.join(out,name+'.json'), JSON.stringify(result,null,2));
  results.push(result);
  console.log(JSON.stringify(result));
  await context.close();
}

try {
  await check('lab-notebook-fresh', 'lab/index.html?path=00_Start_Here.ipynb');
  await check('lab-notebook-returning', 'lab/index.html?path=00_Start_Here.ipynb', true);
  await check('single-notebook', 'notebooks/index.html?path=00_Start_Here.ipynb');
} finally {
  await browser.close();
}
fs.writeFileSync(path.join(out,'summary.json'), JSON.stringify(results.map(({name,status})=>({name,status})),null,2));
if (results.some(result => result.status === 'failed')) process.exitCode = 1;
