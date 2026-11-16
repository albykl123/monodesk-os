# MONODESK OS 2.0.1-rc1 — Universal PC Edition
> **A complete, independent, publicly distributable PC operating system and modern Windows alternative featuring a fluid Wayland desktop shell, Nothing-inspired monochrome design language, and enterprise Debian 13 base.**

[![Release](https://img.shields.io/badge/Release-2.0.1--rc1%20(Pre--release)-blue.svg)](https://github.com/albykl123/monodesk-os/releases/tag/v2.0.1-rc1)
[![Base](https://img.shields.io/badge/Base-Debian%2013%20(Trixie)-D70A53.svg)](https://www.debian.org)
[![Architecture](https://img.shields.io/badge/Architecture-x86--64%20%2F%20AMD64-blue.svg)](https://en.wikipedia.org/wiki/X86-64)
[![Desktop](https://img.shields.io/badge/Desktop%20Shell-Hyprland%20%2B%20Quickshell%20(Wayland)-black.svg)](shell/)
[![License](https://img.shields.io/badge/License-GPLv3%20%2F%20AGPLv3-green.svg)](LICENSE)
[![Zero Telemetry](https://img.shields.io/badge/Privacy-100%25%20Zero%20Telemetry-blueviolet.svg)](docs/PRIVACY.md)

---

## 1. Vision & Architecture Overview

MONODESK OS 2.0.1-rc1 is an independent, production-grade Linux operating system designed for daily personal computing. It provides a full, seamless alternative to Windows 10/11 with zero proprietary tracking, zero forced cloud telemetry, and complete user privacy.

### The Dual-Engine Desktop Architecture

MONODESK OS 2.0 introduces an intelligent dual-engine architecture to guarantee universal PC compatibility across both cutting-edge hardware and decade-old systems:

1. **Primary Session — MONODESK Wayland:**
   - **Compositor:** Hyprland 0.42+ dynamic tiling Wayland compositor with hardware-accelerated animations and GLSL shaders.
   - **Shell Framework:** Quickshell (Qt 6 / QML) powered by the **Nebula** foundation.
   - **Shapes & Effects:** Dynamic Material 3 shapes via `m3shapes`, fluid blur, and dark dot-matrix aesthetics.
   - **Target Hardware:** Intel Iris/Xe/UHD, AMD Radeon (`amdgpu` / Lucienne / Renoir / RDNA), NVIDIA (proprietary/nouveau with KMS/DRM), and modern virtual machines.

2. **Recovery / Legacy Session — MONODESK Recovery (X11):**
   - **Compositor / Window Manager:** X11 + XFWM4 (`--compositor=on` enforced).
   - **Shell Engine:** MONODESK Qt 6 Shell.
   - **Target Hardware:** Legacy Intel HD 3000 (Sandy Bridge), non-DRM graphics chips, safe-graphics recovery mode, and low-RAM legacy systems.

The `/usr/bin/monodesk-session` router automatically benchmarks GPU capabilities via direct Linux kernel DRM subsystem inspection (`/sys/class/drm` and `/dev/dri`) at login to deploy the optimal desktop engine.

---

## 2. Key Defect Resolutions in v2.0.1-rc1

This release candidate directly resolves four architectural defects identified during physical boot tests on target PC hardware:

1. **Deterministic DRM/KMS Hardware Detection (`monodesk-hw-detect`):**
   - Eliminated pre-session `glxinfo` user-space calls that failed prior to X server / display manager startup.
   - Implemented direct Linux kernel DRM subsystem inspection (`/sys/class/drm/card*` and `/dev/dri/renderD*`).
   - Line-by-line regex parsing for `lspci -nnk` output.
   - AMD Ryzen 7 5700U (`1002:164c` Lucienne/Renoir) immediately resolves to the hardware-accelerated **Wayland** session profile.
2. **Fixed Mouse Hover & Input Event Routing (`monodesk-session`):**
   - Modern hardware defaults to native Wayland/Hyprland where `wl_pointer` and hardware cursors provide subpixel precision and zero latency.
   - In fallback X11 recovery mode, compositing is strictly enforced with `xfwm4 --compositor=on` (never `--compositor=off`), preventing pointer enter/leave event swallowing on translucent windows.
3. **Complete Nebula Desktop Live Staging:**
   - Staged full Hyprland configurations in `/etc/skel/.config/hypr/` and `/etc/hypr/`.
   - Staged Quickshell QML framework in `/etc/skel/.config/quickshell/` and `/usr/share/monodesk/shell/quickshell/`.
   - Staged monochrome dot-matrix branding wallpapers in system directories.
   - Added `/usr/bin/quickshell` multi-stage launcher wrapper with `swaybg` wallpaper support.
4. **Registration of System Applications & Launchers:**
   - Installed executable wrappers in `/usr/bin/` with `0755` permissions for:
     - `monodesk-settings` (Settings Hub)
     - `monodesk-store` / `monodesk-software-manager` (Software Centre)
     - All 22 additional MONODESK system management utilities.
   - Registered FreeDesktop `.desktop` entries in `/usr/share/applications/` and scalable icons in `/usr/share/icons/hicolor/scalable/apps/`.

---

## 3. Desktop Feature Matrix

| Area | Feature | Implementation |
|:---|:---|:---|
| **Shell** | Floating Island Bar & Dock | Quickshell reactive QML desktop shell with pinned/running app state |
| **Launcher** | Dynamic Application Search | Fuzzy-filtered search indexing all standard `.desktop` applications |
| **Quick Settings** | System Control Center | Real-time toggles for Wi-Fi (`nmcli`), Bluetooth (`bluetoothctl`), Audio (`PipeWire`), and Power |
| **Hardware** | Adaptive Profile Engine | Dual profile tiers: **Standard** (8GB+ RAM, full effects) and **Lite** (2-4GB RAM, zram, reduced animations) |
| **Settings** | 21-Page System Settings | Dedicated control panel for display, resolution, brightness, sound, users, privacy, and updates |
| **Software** | Software Centre | Native APT package management and sandboxed Flatpak application catalog |
| **Installer** | Calamares Live Installer | Graphical installer with automated GPT partitioning, LUKS encryption, Btrfs, and UEFI/BIOS support |

---

## 4. Release Download & Verification

Release assets are available at [GitHub Releases `v2.0.1-rc1`](https://github.com/albykl123/monodesk-os/releases/tag/v2.0.1-rc1):

- **ISO Image:** `monodesk-os-2.0.1-rc1-universal-amd64.iso` (917.63 MiB)
- **SHA-256 Checksum:** `e4dff2a2a29992b1a68c5fbec330dff707b66cb87a224afa1daa750dd61b8346`
- **Volume Identifier:** `MONODESK_201_RC1`

Verify checksum on Windows PowerShell:
```powershell
(Get-FileHash -Algorithm SHA256 .\monodesk-os-2.0.1-rc1-universal-amd64.iso).Hash
```

Verify checksum on Linux:
```bash
sha256sum -c monodesk-os-2.0.1-rc1-universal-amd64.iso.sha256
```

---

## 5. Third-Party Attribution & Non-Affiliation

### Non-Affiliation Disclaimer
MONODESK OS is an independent open-source Linux operating system project. MONODESK OS is not affiliated with, sponsored by, or endorsed by Nothing Technology Limited. All artwork, glyphs, dot-matrix icons, and themes are original open-source creations.

### Upstream Open-Source Attributions
- **Nebula Desktop Environment:** Created by [LilaccFlowerr](https://github.com/LilaccFlowerr/Nebula), licensed under GNU AGPL-3.0. Upstream source preserved in `third_party/nebula/`.
- **Material 3 Shapes (M3Shapes):** Created by [soramanew](https://github.com/soramanew/m3shapes), licensed under Apache-2.0. Source preserved in `third_party/m3shapes/`.
- **Hyprland:** Created by Vaxry and the Hyprland development team (BSD 3-Clause).
- **Quickshell:** Created by the Quickshell team (LGPL v3 / GPL v3).
- **Debian GNU/Linux:** Created by Software in the Public Interest, Inc. (DFSG).
- **Calamares:** Graphical installer framework (GPL v3).

See [`docs/THIRD_PARTY_LICENSES.md`](docs/THIRD_PARTY_LICENSES.md) for full license texts and copyright statements.

---

## 6. Verification & Quality Assurance

Run the test suite:
```bash
# Unit tests
pytest tests/ -v

# Staging validation
python3 scripts/validate_live_build_staging.py

# UEFI & BIOS QEMU boot test
python3 scripts/test_v201_boot.py

# Calamares automated installation & installed OS cold boot test
python3 scripts/test_calamares_and_installed_boot.py
```

Test ISO boot in QEMU:
```bash
qemu-system-x86_64 -accel whpx -m 4096 -smp 4 \
  -drive if=pflash,format=raw,readonly=on,file="C:\Program Files\qemu\share\edk2-x86_64-code.fd" \
  -cdrom releases/monodesk-os-2.0.1-rc1-universal-amd64.iso -boot d
```
