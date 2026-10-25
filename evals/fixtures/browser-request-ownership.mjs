import http from 'node:http';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, i, all) => {
  if (i % 2 === 0) pairs.push([value, all[i + 1]]);
  return pairs;
}, []));
assert(args['--playwright'] && args['--out'], 'Explicit Playwright module and fresh output directory required');
const require = createRequire(import.meta.url);
const { chromium } = require(path.resolve(args['--playwright']));
const output = path.resolve(args['--out']);
await mkdir(output, { recursive: false });

// Synthetic loopback fixture only. No account, repository, remote host or secret.
const html = `<!doctype html><html><body>
<button id="read">Read status</button><output id="result"></output>
<script>
document.querySelector('#read').onclick=async()=>{
 const value=await (await fetch('/api/status',{cache:'no-store'})).json();
 document.querySelector('#result').textContent=value.value;
};
</script></body></html>`;
const worker = `
self.addEventListener('install',event=>{
 event.waitUntil(fetch('/assets/api/status.js').then(r=>r.text()));
 self.skipWaiting();
});
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
 if(new URL(event.request.url).pathname==='/api/status')event.respondWith(fetch(event.request));
});`;
const server = http.createServer((req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.url === '/') { res.setHeader('Content-Type', 'text/html'); res.end(html); }
  else if (req.url === '/sw.js') { res.setHeader('Content-Type', 'application/javascript'); res.end(worker); }
  else if (req.url === '/assets/api/status.js') {
    res.setHeader('Content-Type', 'application/javascript'); res.end('self.fixtureAssetLoaded=true;');
  } else if (req.url === '/api/status') {
    res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify({ value: 'server' }));
  } else { res.statusCode = 404; res.end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
let browser;
const observations = [];

async function read(page) {
  await page.locator('#result').evaluate(el => { el.textContent = ''; });
  await page.locator('#read').click();
  await page.waitForFunction(() => document.querySelector('#result').textContent !== '');
  return page.locator('#result').textContent();
}
async function activate(page) {
  await page.evaluate(async () => {
    const controlled = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('service worker control timeout')), 10000);
      if (navigator.serviceWorker.controller) { clearTimeout(timeout); resolve(); return; }
      navigator.serviceWorker.addEventListener('controllerchange', () => { clearTimeout(timeout); resolve(); }, { once: true });
    });
    await navigator.serviceWorker.register('/sw.js');
    await navigator.serviceWorker.ready;
    await controlled;
  });
}

try {
  browser = await chromium.launch({ headless: true, ...(args['--executable'] ? { executablePath: args['--executable'] } : {}) });
  // Negative control: a correct exact URL matcher at the wrong request owner.
  {
    const context = await browser.newContext(); const page = await context.newPage();
    const matched = []; const errors = [];
    page.on('pageerror', e => errors.push(e.name + ': ' + e.message));
    await page.goto(origin);
    await page.route(url => url.pathname === '/api/status', async route => {
      matched.push(new URL(route.request().url()).pathname);
      await route.fulfill({ json: { value: 'controlled' } });
    });
    const before = await read(page); await activate(page); const after = await read(page);
    assert.equal(before, 'controlled'); assert.equal(after, 'server'); assert.deepEqual(errors, []);
    observations.push({ case: 'page-exact-owner-counterexample', before, after, matched, pageErrors: errors });
    await context.close();
  }
  // Negative control: a broad matcher sees a JS asset fetched by the worker too.
  {
    const context = await browser.newContext(); const page = await context.newPage();
    const matched = []; const errors = [];
    page.on('pageerror', e => errors.push(e.name + ': ' + e.message));
    await context.route('**/api/status**', async route => {
      const response = await route.fetch(); const row = { path: new URL(route.request().url()).pathname };
      try { await response.json(); row.json = true; }
      catch { row.json = false; }
      matched.push(row); await route.fulfill({ response });
    });
    await page.goto(origin); await activate(page); await read(page);
    assert(matched.some(row => row.path === '/assets/api/status.js' && row.json === false));
    assert.deepEqual(errors, []);
    observations.push({ case: 'context-broad-path-counterexample', matched, pageErrors: errors });
    await context.close();
  }
  // Positive control: retain the actual worker and target the semantic endpoint.
  {
    const context = await browser.newContext(); const page = await context.newPage();
    const matched = []; const errors = [];
    page.on('pageerror', e => errors.push(e.name + ': ' + e.message));
    await context.route(url => url.pathname === '/api/status', async route => {
      const response = await route.fetch(); const data = await response.json();
      assert.equal(data.value, 'server');
      matched.push({ path: new URL(route.request().url()).pathname, workerOwned: !!route.request().serviceWorker() });
      await route.fulfill({ response, json: { value: 'controlled' } });
    });
    await page.goto(origin); const before = await read(page); await activate(page); const after = await read(page);
    assert.equal(before, 'controlled'); assert.equal(after, 'controlled');
    assert(matched.some(row => row.workerOwned)); assert(matched.every(row => row.path === '/api/status'));
    assert.deepEqual(errors, []);
    observations.push({ case: 'context-exact-endpoint-control', before, after, matched, pageErrors: errors });
    await context.close();
  }
  await writeFile(path.join(output, 'result.json'), JSON.stringify({
    passed: true, cases: observations, browserVersion: browser.version(),
    limits: ['Synthetic familiar-coordinator fixture, not a blind agent or product trial',
      'No claim of backend writes, PWA/offline acceptance, host hook operation or efficiency',
      'The broad-match case catches the parse rejection to preserve the negative observation without an unhandled harness exception'],
  }, null, 2), { flag: 'wx' });
  console.log(JSON.stringify({ passed: true, cases: observations.length, browserVersion: browser.version() }));
} catch (error) {
  await writeFile(path.join(output, 'failure.json'), JSON.stringify({ name: error.name, message: error.message, observations }, null, 2), { flag: 'wx' });
  throw error;
} finally {
  await browser?.close(); await new Promise(resolve => server.close(resolve));
}
