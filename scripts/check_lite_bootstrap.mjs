/** Run the shipped Lite configuration bootstrap against the assembled site.
 * A small DOM harness exercises configuration loading and bundle selection;
 * this is not a browser-rendering or kernel test. No npm dependencies needed.
 * Usage: node scripts/check_lite_bootstrap.mjs
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

process.on('uncaughtException', error => { console.error(`${error.name}: ${error.message}`); process.exit(1); });

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
const site = new URL('https://example.test/JupyterLite-World-Monitor-Prototype/');
const configUtils = fs.readFileSync(path.join(dist, 'config-utils.js'), 'utf8');
const rootPage = fs.readFileSync(path.join(dist, 'index.html'), 'utf8');
let runId = 0;

function attributes(text) {
  return Object.fromEntries([...text.matchAll(/([\w-]+)\s*=\s*["']([^"']*)["']/g)]
    .map(match => [match[1], match[2]]));
}

function elementWithId(html, id) {
  for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    const attrs = attributes(match[1]);
    if (attrs.id === id) {
      return {textContent: match[2], dataset: {jupyterLiteRoot: attrs['data-jupyter-lite-root']}};
    }
  }
  return null;
}

async function bootstrap(entry, parentHtml = rootPage) {
  const location = new URL(entry, site);
  const file = path.join(dist, location.pathname.slice(site.pathname.length));
  const html = fs.readFileSync(file, 'utf8');
  const script = elementWithId(html, 'jupyter-config-data');
  const link = [...html.matchAll(/<link\b([^>]*)>/gi)]
    .map(match => attributes(match[1])).find(attrs => attrs.id === 'jupyter-lite-main');
  assert.ok(script, `${entry} must supply a configuration element`);
  assert.ok(link, `${entry} must select an application bundle`);
  const appended = [];
  const original = {window: globalThis.window, document: globalThis.document,
                    DOMParser: globalThis.DOMParser, warn: console.warn};
  globalThis.window = {location, fetch: async url => {
    const request = new URL(url, location);
    assert.equal(request.origin, site.origin);
    assert.ok(request.pathname.startsWith(site.pathname), `Escaped repository path: ${request}`);
    const relative = request.pathname.slice(site.pathname.length);
    if (relative === 'index.html') return {text: async () => parentHtml};
    const asset = path.join(dist, relative);
    return {text: async () => fs.existsSync(asset) ? fs.readFileSync(asset, 'utf8') : 'Not found'};
  }};
  globalThis.document = {
    getElementById: id => id === 'jupyter-config-data' ? script :
      id === 'jupyter-lite-main' ? {href: new URL(link.href, location).href, attributes: {main: link.main}} : null,
    createElement: tagName => ({tagName}),
    head: {appendChild: element => appended.push(element)},
  };
  globalThis.DOMParser = class {
    parseFromString(text) { return {getElementById: id => elementWithId(text, id)}; }
  };
  // Missing optional .ipynb config files intentionally emit upstream warnings.
  console.warn = () => {};
  try {
    await import(`data:text/javascript;base64,${Buffer.from(configUtils).toString('base64')}#${runId++}`);
    const merged = JSON.parse(script.textContent);
    assert.equal(merged.baseUrl, site.pathname);
    assert.equal(merged.defaultKernelName, 'python');
    assert.ok(merged.federated_extensions.some(ext => ext.name === '@jupyterlite/pyodide-kernel-extension'));
    const bundle = appended.find(element => element.tagName === 'script');
    assert.ok(bundle, `${entry} never reached application bundle loading`);
    const bundleUrl = new URL(bundle.src);
    assert.ok(bundleUrl.pathname.startsWith(site.pathname));
    assert.ok(fs.existsSync(path.join(dist, bundleUrl.pathname.slice(site.pathname.length))));
  } finally {
    globalThis.window = original.window;
    globalThis.document = original.document;
    globalThis.DOMParser = original.DOMParser;
    console.warn = original.warn;
  }
}

for (const entry of ['lab/index.html', 'lab/index.html?path=00_Start_Here.ipynb', 'tree/index.html']) {
  await bootstrap(entry);
  console.log(`PASS configuration cascade and bundle selection: ${entry}`);
}
// Negative control: removing the root config reproduces the original crash.
const brokenRoot = rootPage.replace(/<script\b[^>]*id=["']jupyter-config-data["'][^>]*>[\s\S]*?<\/script>/i, '');
await assert.rejects(bootstrap('lab/index.html', brokenRoot), /textContent/);
console.log('PASS regression guard: a root landing page without Lite config is rejected.');
