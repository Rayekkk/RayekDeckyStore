// Cloudflare Worker that serves the store with the CORS headers Decky needs.
//
// Decky's frontend adds an X-Decky-Version header to its request. A custom
// header makes the request "non-simple", so the browser sends an OPTIONS
// preflight first and only issues the real GET if the answer allows that
// header by name. Static hosts do not answer OPTIONS at all: GitHub Pages
// replies 405, raw.githubusercontent 403, and jsDelivr replies 200 but without
// Access-Control-Allow-Headers, which the browser rejects just the same.
//
// Store.tsx has no catch around the fetch, so a blocked request leaves the
// plugin list at null and the store spins forever instead of showing an error.
//
// This worker answers the preflight and passes the file through. plugins.json
// stays where it is and build_store.py still owns it; nothing here needs
// redeploying when a plugin is released.
//
// Decky 3.3.1 checks installed plugins for updates at <store>/versions and
// expects {"Plugin name": ["version", "sha256"]}, not the plugin list; a list
// there makes it reject the answer, so no update is ever offered. That map is
// built from the same plugins.json (versions[0] is the newest, build_store.py
// keeps that order).

const STORE = 'https://rayekkk.github.io/RayekDeckyStore/plugins.json';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
  'Access-Control-Allow-Headers': 'X-Decky-Version',
  'Access-Control-Max-Age': '600',
};

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response('Method not allowed', { status: 405, headers: CORS });
    }

    // Kept short on purpose. A store this small is fetched a handful of times
    // a day, so there is nothing to protect GitHub from, and a long cache means
    // pushing a release and then wondering why the store still shows the old
    // one. Sixty seconds only stops a console that reopens the tab repeatedly.
    const upstream = await fetch(STORE, { cf: { cacheTtl: 60 } });

    if (!upstream.ok) {
      return new Response(`Upstream returned ${upstream.status}`, {
        status: 502,
        headers: CORS,
      });
    }

    const headers = { ...CORS, 'Content-Type': 'application/json; charset=utf-8' };
    if (new URL(request.url).pathname.replace(/\/+$/, '').endsWith('/versions')) {
      return new Response(JSON.stringify(versionMap(await upstream.json())), { status: 200, headers });
    }
    return new Response(upstream.body, { status: 200, headers });
  },
};

export function versionMap(plugins) {
  const map = {};
  for (const plugin of plugins) {
    const newest = plugin.versions?.[0];
    if (newest) map[plugin.name] = [newest.name, newest.hash];
  }
  return map;
}
