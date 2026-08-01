<div align="center">

# Rayek's Decky Store

A custom plugin store for [Decky Loader](https://decky.xyz), holding my plugins for the
Lenovo Legion Go family. Add the address once and they install and update through Decky's
own **Store** tab, like anything else.

</div>

---

## Adding it to Decky

Copy this address:

```
https://decky.rayek.workers.dev
```

On the device, open **Decky → Settings → General → Store channel**, switch it to **Custom**,
and paste the address into the field that appears. The **Store** tab then lists everything
below.

Switching back to **Default** at any time restores the official store. Plugins already
installed from here stay installed.

---

## Power

<div align="center">

<a href="https://github.com/Rayekkk/LeGoTDP"><img src="https://raw.githubusercontent.com/Rayekkk/LeGoTDP/main/docs/logo.png" alt="LeGoTDP" width="640"></a>

[![Release](https://img.shields.io/github/v/release/Rayekkk/LeGoTDP?style=for-the-badge&label=release&color=C2410C&labelColor=141417)](https://github.com/Rayekkk/LeGoTDP/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Rayekkk/LeGoTDP/total?style=for-the-badge&label=downloads&color=15803D&labelColor=141417)](https://github.com/Rayekkk/LeGoTDP/releases)
[![License](https://img.shields.io/github/license/Rayekkk/LeGoTDP?style=for-the-badge&label=license&color=424A53&labelColor=141417)](https://github.com/Rayekkk/LeGoTDP/blob/main/LICENSE)

</div>

**[LeGoTDP](https://github.com/Rayekkk/LeGoTDP)** sets AMD CPU TDP limits from the Steam
overlay on the Legion Go 2 and Legion Go S. Preset ladders spaced against each machine's own
firmware ceilings, per-game profiles with separate battery and charging limits, and live
power draw read from RAPL.

---

## Haptics

<div align="center">

<a href="https://github.com/Rayekkk/LeGo-Vibe-Control"><img src="https://raw.githubusercontent.com/Rayekkk/LeGo-Vibe-Control/main/docs/logo.png" alt="LeGoVibeControl" width="640"></a>

[![Release](https://img.shields.io/github/v/release/Rayekkk/LeGo-Vibe-Control?style=for-the-badge&label=release&color=C2410C&labelColor=141417)](https://github.com/Rayekkk/LeGo-Vibe-Control/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Rayekkk/LeGo-Vibe-Control/total?style=for-the-badge&label=downloads&color=15803D&labelColor=141417)](https://github.com/Rayekkk/LeGo-Vibe-Control/releases)
[![License](https://img.shields.io/github/license/Rayekkk/LeGo-Vibe-Control?style=for-the-badge&label=license&color=424A53&labelColor=141417)](https://github.com/Rayekkk/LeGo-Vibe-Control/blob/main/LICENSE)

</div>

**[LeGoVibeControl](https://github.com/Rayekkk/LeGo-Vibe-Control)** controls vibration
intensity, pattern and touchpad haptics on the Legion Go and Legion Go 2. Five rumble
patterns, a touchpad motor set apart from the handles, and per-game profiles.

---

## SteamOS Brightness Fix

<div align="center">

<a href="https://github.com/Rayekkk/LeGo2BrightnessFix"><img src="https://raw.githubusercontent.com/Rayekkk/LeGo2BrightnessFix/main/docs/logo.png" alt="LeGo2BrightnessFix" width="640"></a>

[![Release](https://img.shields.io/github/v/release/Rayekkk/LeGo2BrightnessFix?style=for-the-badge&label=release&color=C2410C&labelColor=141417)](https://github.com/Rayekkk/LeGo2BrightnessFix/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Rayekkk/LeGo2BrightnessFix/total?style=for-the-badge&label=downloads&color=15803D&labelColor=141417)](https://github.com/Rayekkk/LeGo2BrightnessFix/releases)
[![License](https://img.shields.io/github/license/Rayekkk/LeGo2BrightnessFix?style=for-the-badge&label=license&color=424A53&labelColor=141417)](https://github.com/Rayekkk/LeGo2BrightnessFix/blob/main/LICENSE)

</div>

**[LeGo2BrightnessFix](https://github.com/Rayekkk/LeGo2BrightnessFix)** makes the Steam
brightness slider work on the Legion Go 2 OLED while the panel is in HDR, and gives games the
panel's real HDR metadata instead of DXVK's 1499 nit placeholder. Both halves are automatic
and stand down whenever they are not needed.

---

## Display Vibrancy

<div align="center">

<a href="https://github.com/Rayekkk/DeckyVibranceHDR"><img src="https://raw.githubusercontent.com/Rayekkk/DeckyVibranceHDR/main/docs/logo.png" alt="DeckyVibranceHDR" width="640"></a>

[![Release](https://img.shields.io/github/v/release/Rayekkk/DeckyVibranceHDR?style=for-the-badge&label=release&color=C2410C&labelColor=141417)](https://github.com/Rayekkk/DeckyVibranceHDR/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Rayekkk/DeckyVibranceHDR/total?style=for-the-badge&label=downloads&color=15803D&labelColor=141417)](https://github.com/Rayekkk/DeckyVibranceHDR/releases)
[![License](https://img.shields.io/github/license/Rayekkk/DeckyVibranceHDR?style=for-the-badge&label=license&color=424A53&labelColor=141417)](https://github.com/Rayekkk/DeckyVibranceHDR/blob/main/LICENSE)

</div>

**[DeckyVibranceHDR](https://github.com/Rayekkk/DeckyVibranceHDR)** is saturation control
under gamescope, in SDR and HDR alike. Which mapping applies is read from the panel's EDID
rather than the model name, so it is not tied to one handheld.

---

## How this store works

There is no server. `plugins.json` is the entire store: Decky fetches it, parses it as a list
of plugins, and downloads each zip straight from its own GitHub release.

`build_store.py` regenerates the file. It reads `plugin.json` from each plugin repo for the
name, author, description and tags, asks GitHub for the latest release, and hashes the
published zip so Decky can verify what it downloaded. Run it after a release and commit the
result. **The address never changes.**

```bash
python build_store.py
git commit -am "Refresh the store" && git push
```

The file is served by GitHub Pages from `main`, and `worker.js` fronts it at the address
above. A push takes a minute or so to appear.

The worker exists for one reason. Decky adds an `X-Decky-Version` header, which makes the
request non-simple, so the browser sends a `OPTIONS` preflight first and only issues the real
`GET` if the answer names that header. **No static host answers it:** GitHub Pages replies
405, `raw.githubusercontent` 403, and jsDelivr replies 200 but without
`Access-Control-Allow-Headers`, which the browser rejects just the same. A blocked request
leaves the store spinning forever rather than showing an error, because `Store.tsx` has no
`catch` around the fetch.

The worker never needs redeploying. It reads whatever `plugins.json` currently says.

Three details the file has to get right, all handled by the generator:

- **`artifact`** must be present on every version. Without it Decky falls back to the official
  CDN, which does not have these plugins.
- **`hash`** is the SHA-256 of the zip and is verified after download; a mismatch refuses the
  install.
- **`name`** must match `plugin.json` exactly, because that is how Decky matches an installed
  plugin against a store entry when it checks for updates.

---

<div align="center">

*Plugins are BSD 3-Clause. See each repository for its own licence and notices.*

</div>
