"""Rebuild plugins.json from the plugin repositories.

Decky's frontend fetches whatever URL is configured and parses the body as
StorePlugin[] (frontend/src/store.tsx). Everything it needs is in that array,
so this store is a static file and there is no API to implement.

Every published release is listed, not just the newest, because PluginCard.tsx
builds its version dropdown straight from the versions array and marks the one
already installed. Order matters: checkForPluginUpdates() only ever compares
versions[0], so the newest has to come first.

Two other fields have to be right. artifact must be set, or Decky falls back to
the official CDN which does not carry these plugins. hash is the SHA-256 of the
zip and is verified after downloading, so it has to be the published file
rather than a local build.

Released assets never change, so hashes already in plugins.json are reused and
only new releases are downloaded.
"""
import base64
import hashlib
import json
import os
import subprocess
import urllib.request

OWNER = "Rayekkk"

# Order is deliberate. IDs are permanent and must not change when reordered.
REPOS = [
    ("LegionGo2Companion", 7),
    ("Ayaneo3Companion", 4),
    ("DeckyVibranceHDR", 5),
    ("SpotiDeck", 6),
    ("LeGoTDP", 1),
    ("LeGo-Vibe-Control", 2),
    ("LeGo2BrightnessFix", 3),
]
DESCRIPTION_OVERRIDES = {
    "LegionGo2Companion": "TDP and CPU profiles, battery protection, gyro, haptics, lighting, button remapping, OLED brightness/HDR fixes and Wi-Fi controls for Legion Go 2.",
    "SpotiDeck": "Spotify playback, playlists, search and your library inside Decky, with separate music and game audio controls. Requires Spotify Premium and your own Spotify Web API Client ID; local playback also requires a Spotify Soloist API key.",
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins.json")


def gh_json(path):
    raw = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout
    return json.loads(raw)


def semver(tag):
    """Sort key. Anything unparseable sorts last rather than crashing the run."""
    try:
        return tuple(int(p) for p in tag.lstrip("vV").split(".")[:3])
    except ValueError:
        return (-1, -1, -1)


def known_hashes():
    """(plugin name, version, artifact URL) -> hash from the previous catalog."""
    try:
        with open(OUT, encoding="utf-8") as fh:
            return {(p["name"], v["name"], v["artifact"]): v["hash"]
                    for p in json.load(fh) for v in p["versions"]}
    except (OSError, ValueError, KeyError):
        return {}


cache = known_hashes()
store = []
fetched = 0

for repo, plugin_id in REPOS:
    content = gh_json("repos/%s/%s/contents/plugin.json?ref=main" % (OWNER, repo))
    pj = json.loads(base64.b64decode(content["content"]))
    pub = pj.get("publish", {})
    name = pj["name"]

    releases = [r for r in gh_json("repos/%s/%s/releases?per_page=100" % (OWNER, repo))
                if not r["draft"] and not r["prerelease"] and r["assets"]]
    releases.sort(key=lambda r: semver(r["tag_name"]), reverse=True)

    versions = []
    for rel in releases:
        tag = rel["tag_name"].lstrip("vV")
        # Checksums and source archives must never become install targets.
        filename = "%s-%s.zip" % (repo, tag)
        assets = [a for a in rel["assets"]
                  if a["name"] == filename or (
                      a["name"].lower().endswith(".zip")
                      and (name, tag, a["browser_download_url"]) in cache)]
        if len(assets) != 1:
            print("POMINIETE %s %s: brak jednoznacznej paczki %s" % (repo, tag, filename))
            continue
        asset = assets[0]
        url = asset["browser_download_url"]
        digest = cache.get((name, tag, url))
        if digest is None:
            with urllib.request.urlopen(url) as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
            expected = asset.get("digest")
            if expected and expected != "sha256:" + digest:
                raise ValueError("SHA-256 mismatch: " + url)
            fetched += 1
        versions.append({"name": tag, "hash": digest, "artifact": url})

    if not versions:
        print("POMINIETE %s: zadne wydanie nie ma pliku" % repo)
        continue
    if versions[0]["name"] != pj["version"]:
        print("UWAGA %s: plugin.json ma %s, najnowsze wydanie %s"
              % (repo, pj["version"], versions[0]["name"]))

    store.append({
        "id": plugin_id,
        # Must match plugin.json exactly: this is the key Decky matches an
        # installed plugin against when it looks for a store entry.
        "name": name,
        "author": pj.get("author", ""),
        "description": DESCRIPTION_OVERRIDES.get(repo, pub.get("description", "")),
        "tags": pub.get("tags", ["utilities", "hardware"]),
        "image_url": "https://raw.githubusercontent.com/%s/RayekDeckyStore/main/assets/%s.png" % (OWNER, repo),
        "versions": versions,
    })

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(store, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

for p in store:
    print("%d. %-22s %2d wersji, najnowsza %-7s opis %3d znakow  obrazek: %s" % (
        p["id"], p["name"], len(p["versions"]), p["versions"][0]["name"],
        len(p["description"]), "jest" if p["image_url"] else "brak"))
print("\npobrano %d nowych archiwow, %d hashy wzietych z poprzedniego pliku" % (fetched, len(cache)))
print("zapisano: %s (%d B)" % (OUT, os.path.getsize(OUT)))
