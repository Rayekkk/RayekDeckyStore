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

test('the plugin list without a sort is passed through unchanged', async () => {
  for (const path of ['', '/', '/?sort_by=unknown']) {
    assert.deepEqual(await (await get(path)).json(), plugins);
  }
});

test("every option of Decky's Store sort menu orders the list", async () => {
  const names = async (q) => (await (await get('/?' + q)).json()).map((p) => p.name);
  const sample = [
    { name: 'beta', created: '2026-01-02T00:00:00Z', downloads: 5 },
    { name: 'Alpha', created: '2026-03-01T00:00:00Z', downloads: 50 },
    { name: 'gamma', created: '2025-12-01T00:00:00Z', downloads: 1 },
  ];
  globalThis.fetch = async () => new Response(JSON.stringify(sample), { status: 200 });
  try {
    assert.deepEqual(await names('sort_by=name&sort_direction=asc'), ['Alpha', 'beta', 'gamma']);
    assert.deepEqual(await names('sort_by=name&sort_direction=desc'), ['gamma', 'beta', 'Alpha']);
    assert.deepEqual(await names('sort_by=date&sort_direction=asc'), ['gamma', 'beta', 'Alpha']);
    assert.deepEqual(await names('sort_by=date&sort_direction=desc'), ['Alpha', 'beta', 'gamma']);
    assert.deepEqual(await names('sort_by=downloads&sort_direction=desc'), ['Alpha', 'beta', 'gamma']);
    assert.deepEqual(await names('sort_by=downloads&sort_direction=asc'), ['gamma', 'beta', 'Alpha']);
  } finally {
    globalThis.fetch = async () => new Response(JSON.stringify(plugins), { status: 200 });
  }
});

test('the real catalog carries the fields the sort needs', () => {
  for (const p of plugins) {
    assert.match(p.created, /^\d{4}-\d\d-\d\dT/, p.name);
    assert.ok(Number.isInteger(p.downloads), p.name);
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
