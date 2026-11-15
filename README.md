# MONODESK OS 2.0 — Universal PC Edition
> **A complete, independent, publicly distributable PC operating system and modern Windows alternative featuring a fluid Wayland desktop shell, Nothing-inspired monochrome design language, and enterprise Debian 13 base.**

[![Base](https://img.shields.io/badge/Base-Debian%2013%20(Trixie)-D70A53.svg)](https://www.debian.org)
[![Architecture](https://img.shields.io/badge/Architecture-x86--64%20%2F%20AMD64-blue.svg)](https://en.wikipedia.org/wiki/X86-64)
[![Desktop](https://img.shields.io/badge/Desktop%20Shell-Hyprland%20%2B%20Quickshell%20(Wayland)-black.svg)](shell/)
[![License](https://img.shields.io/badge/License-GPLv3%20%2F%20AGPLv3-green.svg)](LICENSE)
[![Zero Telemetry](https://img.shields.io/badge/Privacy-100%25%20Zero%20Telemetry-blueviolet.svg)](docs/PRIVACY.md)

---

## 1. Vision & Architecture Overview

MONODESK OS 2.0.0 is an independent, production-grade Linux operating system designed for daily personal computing. It provides a full, seamless alternative to Windows 10/11 with zero proprietary tracking, zero forced cloud telemetry, and complete user privacy.

### The Dual-Engine Desktop Architecture

MONODESK OS 2.0 introduces an intelligent dual-engine architecture to guarantee universal PC compatibility across both cutting-edge hardware and decade-old systems:

1. **Primary Session — MONODESK Wayland:**
   - **Compositor:** Hyprland 0.42+ dynamic tiling Wayland compositor with hardware-accelerated animations and GLSL shaders.
   - **Shell Framework:** Quickshell (Qt 6 / QML) powered by the **Nebula** foundation.
   - **Shapes & Effects:** Dynamic Material 3 shapes via `m3shapes`, fluid blur, and dark dot-matrix aesthetics.
   - **Target Hardware:** Intel Iris/Xe/UHD, AMD Radeon (amdgpu/radeonsi), NVIDIA (proprietary/nouveau with KMS/DRM), and modern virtual machines.

2. **Recovery / Legacy Session — MONODESK Recovery (X11):**
   - **Compositor / Window Manager:** X11 + XFWM4.
   - **Shell Engine:** MONODESK Qt 6 Shell.
   - **Target Hardware:** Legacy Intel HD 3000 (Sandy Bridge), non-DRM graphics chips, safe-graphics mode, and low-RAM legacy systems.

The `/usr/bin/monodesk-session` router automatically benchmarks GPU capabilities via `monodesk-hw-detect --check-compositor` at login to deploy the optimal desktop engine.

---

## 2. Desktop Feature Matrix

| Area | Feature | Implementation |
| :--- | :--- | :--- |
| **Shell** | Floating Island Bar & Dock | Quickshell reactive QML desktop shell with pinned/running app state |
| **Launcher** | Dynamic Application Search | Fuzzy-filtered search indexing all standard `.desktop` applications |
| **Quick Settings** | System Control Center | Real-time toggles for Wi-Fi (`nmcli`), Bluetooth (`bluetoothctl`), Audio (`PipeWire`), and Power |
| **Hardware** | Adaptive Profile Engine | Dual profile tiers: **Standard** (8GB+ RAM, full effects) and **Lite** (2-4GB RAM, zram, reduced animations) |
| **Settings** | 21-Page System Settings | Dedicated control panel for display, resolution, brightness, sound, users, privacy, and updates |
| **Software** | Software Centre | Native APT package management and sandboxed Flatpak application catalog |
| **Installer** | Calamares Live Installer | Graphical installer with automated partitioning, LUKS encryption, Btrfs, and UEFI/BIOS support |

---

## 3. Third-Party Attribution & Non-Affiliation

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

## 4. Building the ISO

### Automated Build via GitHub Actions (Recommended)
1. Fork or push to your GitHub repository.
2. Navigate to **Actions** → **MONODESK OS 2.0 — Build Universal ISO**.
3. Select **Run workflow**. The workflow automatically:
   - Reclaims runner storage to guarantee > 25 GB free space.
   - Compiles `m3shapes` for Qt 6.
   - Executes Debian 13 `live-build`.
   - Generates and uploads `monodesk-os-2.0.0-universal-amd64.iso` and SHA-256 checksums.

### Local Build in Linux Builder VM
```bash
# 1. Install prerequisites
sudo apt-get update && sudo apt-get install -y live-build debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin cmake ninja-build qt6-base-dev qt6-declarative-dev

# 2. Compile M3Shapes
cmake -S third_party/m3shapes -B build/m3shapes -G Ninja -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build/m3shapes
sudo cmake --install build/m3shapes

# 3. Configure and build ISO
cd build/live-build
sudo lb clean --all
sudo lb config
sudo lb build
```

---

## 5. Verification & Testing

Run unit tests locally:
```bash
pytest tests/ -v
```

Validate ISO boot in QEMU:
```bash
qemu-system-x86_64 -m 4096 -cdrom releases/monodesk-os-2.0.0-universal-amd64.iso -boot d
```
