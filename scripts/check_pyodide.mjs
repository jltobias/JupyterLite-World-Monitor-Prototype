/** Execute all notebook code in the same WebAssembly Python version as Lite.
 * Node-based compute test; does not claim to test browser UI, WebGL, or CORS.
 * Setup: npm install --prefix _build/wasm --no-audit --no-fund pyodide@314.0.0
 * Run from repo root: node scripts/check_pyodide.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
process.on('uncaughtException', error => { console.error(String(error)); process.exit(1); });
const { loadPyodide } = await import(pathToFileURL(path.join(root, '_build/wasm/node_modules/pyodide/pyodide.mjs')));
const py = await loadPyodide({stdout: () => {}, stderr: console.error,
  packageCacheDir: path.join(root, '_build/wasm/packages'),
  packageBaseUrl: 'https://cdn.jsdelivr.net/pyodide/v314.0.0/full/'});
await py.loadPackage(['micropip', 'ipython']);
py.FS.mkdir('/course');
py.FS.mount(py.FS.filesystems.NODEFS, {root: path.join(root, 'content')}, '/course');
// The packaged piplite wheel is tested directly; no substitute/shim installer.
py.FS.mkdir('/site');
py.FS.mount(py.FS.filesystems.NODEFS, {root: path.join(root, 'dist')}, '/site');
await py.runPythonAsync(`
import os, sys, micropip
import warnings
warnings.filterwarnings('ignore', message='FigureCanvasAgg is non-interactive')
os.environ['MPLBACKEND'] = 'Agg'
os.chdir('/course')
sys.path.insert(0, '/course')
await micropip.install('emfs:/site/extensions/@jupyterlite/pyodide-kernel-extension/static/pypi/piplite-0.8.0-py3-none-any.whl')
`);
let count = 0;
for (const name of fs.readdirSync(path.join(root, 'content')).filter(x => x.endsWith('.ipynb')).sort()) {
  const notebook = JSON.parse(fs.readFileSync(path.join(root, 'content', name), 'utf8'));
  const globals = py.runPython('dict(__name__="__main__")');
  for (const [index, cell] of notebook.cells.entries()) {
    if (cell.cell_type !== 'code') continue;
    try {
      await py.runPythonAsync(cell.source.join(''), {globals});
      count++;
    } catch (error) {
      console.error(`FAIL ${name}, cell ${index}: ${error}`);
      process.exit(1);
    }
  }
  globals.destroy();
  await py.runPythonAsync('import matplotlib.pyplot as plt; plt.close("all")');
  console.log(`PASS ${name}`);
}
console.log(`Executed ${count} code cells across 12 notebooks in Pyodide ${py.version}.`);
