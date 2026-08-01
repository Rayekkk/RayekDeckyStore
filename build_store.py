"""Rebuild plugins.json from the four plugin repos.

Decky's frontend fetches whatever URL is configured and parses the body as
StorePlugin[] (frontend/src/store.tsx). Everything it needs is in that array,
so this store is a static file and there is no API to implement.

The field that matters most is versions[].artifact. When it is set, Decky
downloads from it directly; when it is missing it falls back to the official
CDN keyed by hash, which will not have these plugins. Pointing it at GitHub
Releases also sidesteps a TLS problem: the backend verifies certificates
against certifi's bundle alone, so a self-signed certificate would be refused
and adding one to the system trust store does not help.

Run it after any release, then commit the result. The URL never changes.
"""
import hashlib
import json
import os
import subprocess
import urllib.request

OWNER = "Rayekkk"

# Order is deliberate and is the order Decky shows them in.
REPOS = [
    ("LeGoTDP",            r"c:\Users\Rayek\Documents\GitHub\LeGoTDP"),
    ("LeGo-Vibe-Control",  r"c:\Users\Rayek\Documents\GitHub\LeGo-Vibe-Control"),
    ("LeGo2BrightnessFix", r"c:\Users\Rayek\Desktop\Legion Go 2 SteamOS HDR\LeGo2BrightnessFix"),
    ("DeckyVibranceHDR",   r"c:\Users\Rayek\Desktop\Legion Go 2 SteamOS HDR\DeckyVibranceHDR"),
]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins.json")


def latest_release(repo):
    raw = subprocess.run(["gh", "api", "repos/%s/%s/releases/latest" % (OWNER, repo)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(raw)


store = []
for i, (repo, path) in enumerate(REPOS, start=1):
    rel = latest_release(repo)
    url = rel["assets"][0]["browser_download_url"]

    # Decky checks this after downloading and refuses to install on a mismatch,
    # so hash what will actually be served rather than a local build.
    with urllib.request.urlopen(url) as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()

    pj = json.load(open(os.path.join(path, "plugin.json"), encoding="utf-8"))
    pub = pj.get("publish", {})

    if pj["version"] != rel["tag_name"].lstrip("v"):
        print("UWAGA %s: plugin.json ma %s, ostatnie wydanie %s"
              % (repo, pj["version"], rel["tag_name"]))

    store.append({
        "id": i,
        # Must match plugin.json's name exactly: this is the key Decky matches
        # an installed plugin against when it looks for an update.
        "name": pj["name"],
        "author": pj.get("author", ""),
        "description": pub.get("description", ""),
        "tags": pub.get("tags", []),
        "image_url": pub.get("image", ""),
        # Newest first: checkForPluginUpdates() only ever reads versions[0].
        "versions": [{"name": pj["version"], "hash": digest, "artifact": url}],
    })

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(store, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

for p in store:
    print("%d. %-22s %-7s %s...  obrazek: %s" % (
        p["id"], p["name"], p["versions"][0]["name"], p["versions"][0]["hash"][:12],
        "jest" if p["image_url"] else "BRAK"))
print("\nzapisano: %s (%d B)" % (OUT, os.path.getsize(OUT)))
