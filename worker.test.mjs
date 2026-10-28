// node --test worker.test.mjs — the worker against a fake upstream serving this repo's plugins.json.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

// worker.js is an ES module for Cloudflare; this repo has no package.json, so load it as one explicitly.
const source = readFileSync(new URL('./worker.js', import.meta.url), 'utf8');
const worker = await import('data:text/javascript,' + encodeURIComponent(source));
const plugins = JSON.parse(readFileSync(new URL('./plugins.json', import.meta.url), 'utf8'));

globalThis.fetch = async () => new Response(JSON.stringify(plugins), { status: 200 });
const get = (path, method = 'GET') => worker.default.fetch(new Request('https://decky.example' + path, { method }));

test('/versions is the name -> [newest version, sha256] map Decky 3.3.1 expects', async () => {
  for (const path of ['/versions', '/versions/']) {
    const body = await (await get(path)).json();
    assert.ok(!Array.isArray(body));
    for (const p of plugins) assert.deepEqual(body[p.name], [p.versions[0].name, p.versions[0].hash]);
  }
});

test('the plugin list, with or without a query, is passed through unchanged', async () => {
  for (const path of ['', '/', '/?sort_by=name&sort_direction=asc']) {
    assert.deepEqual(await (await get(path)).json(), plugins);
  }
});

test('preflight is answered with the header Decky sends', async () => {
  const res = await get('/versions', 'OPTIONS');
  assert.equal(res.status, 204);
  assert.match(res.headers.get('Access-Control-Allow-Headers'), /X-Decky-Version/);
});

test('a plugin without versions is left out instead of breaking the map', () => {
  assert.deepEqual(worker.versionMap([{ name: 'A', versions: [] }, { name: 'B', versions: [{ name: '1.0.0', hash: 'h' }] }]),
    { B: ['1.0.0', 'h'] });
});
