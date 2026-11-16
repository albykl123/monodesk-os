# MONODESK OS 2.0 — Release Notes
**Product:** MONODESK OS 2.0.0 (Universal PC Edition)  
**Release Date:** 2026-11-16  
**Base Distribution:** Debian GNU/Linux 13 (Trixie) AMD64  
**Kernel:** Linux 6.12.117+deb13-amd64  
**Primary Engine:** Hyprland + Quickshell + Upstream Nebula UI  
**Fallback Engine:** X11 + XFWM4 + LightDM  
**Installer:** Calamares 3.3  

---

## 1. Release Highlights

MONODESK OS 2.0 represents a generational architectural upgrade from Debian 12 Bookworm to Debian 13 Trixie, introducing a fluid Material 3 Wayland desktop experience, dynamic adaptive performance profiling, and guaranteed hardware backward-compatibility.

### Modern Wayland Compositor (Hyprland + Quickshell)
- **Fluid Dynamic Desktop:** Built on top of Hyprland with Quickshell Qt 6 / QML procedural rendering.
- **Material 3 Shapes & Palette:** Integrated native C++ `M3Shapes` plugin (`soramanew/m3shapes`, Apache-2.0) providing rounded procedural shapes, smooth blur, and Material You colour harmony.
- **Nebula Desktop Upstream:** Snapshot of `LilaccFlowerr/Nebula` (commit `9749c30`, AGPL-3.0) integrated with native Debian 13 paths and system services.

### Dual-Engine Adaptive Architecture
- **Dynamic Session Router (`monodesk-session`):** Probes GPU driver and DRM/KMS capability at boot:
  - **Modern Hardware (AMD Radeon, Intel Iris Xe, NVIDIA):** Automatically selects **Wayland (Hyprland + Quickshell)** with full animations, blur, and hardware acceleration.
  - **Legacy Hardware (e.g. Intel HD 3000, older laptops):** Seamlessly routes to the **Recovery Desktop (X11 + XFWM4)** to guarantee a stable graphical experience without visual artifacts.

### Adaptive Performance Profiles
- **Standard Profile:** Enabled on systems with $\ge$ 6 GB RAM. Allocates 25% RAM to zram compressed swap, runs full compositor visual effects, and sets system power profile to balanced.
- **Lite Profile:** Automatically engaged on systems with $<$ 6 GB RAM (or rotational HDDs). Sets power-saver policy, disables window blur/shadows, lowers background indexing, and allocates 50% RAM to zram compressed swap.

### Complete System Applications Suite
- **21-Category Settings Hub (`monodesk-settings`):** Covers Display, Resolution, Brightness, Audio, Microphone, Wi-Fi, Ethernet, Bluetooth, Keyboard, Mouse, Touchpad, Power, Battery, Printers, Storage, Users, Privacy, Security, Accessibility, Updates, and About.
- **Dual-Backend Software Centre (`monodesk-software-manager`):** Native APT and Flatpak package management with search, transaction queues, and progress indicators.
- **Hardware Diagnostics & Welcome:** Tools for inspecting hardware, drivers, battery telemetry, and onboarding.

---

## 2. Tested Hardware Profiles

| Target Device | Hardware Configuration | Profile Assigned | Active Compositor |
| :--- | :--- | :--- | :--- |
| **Lenovo IdeaPad Slim 5** | AMD Ryzen 7 5700U (8C/16T), 16 GB DDR4, AMD Radeon Lucienne, 512 GB NVMe | **Standard** | **Wayland** (Hyprland + Quickshell, full blur, 60+ FPS) |
| **Lenovo B590** | Intel Core i3-2348M (2C/4T), 4 GB DDR3, Intel HD Graphics 3000, 500 GB HDD | **Lite** | **Recovery X11** (XFWM4, 50% zram, lightweight) |

---

## 3. Verified Release Artifacts

- **ISO Image:** `monodesk-os-2.0.0-universal-amd64.iso`
- **File Size:** `1,190,991,872 bytes` (1.11 GiB)
- **SHA-256 Checksum:** `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2`
- **Volume ID:** `MONODESK_2_0_AMD64`
- **Boot Format:** Hybrid El Torito (UEFI 64-bit + BIOS MBR)

---

## 4. Known Limitations & Workarounds

- **NVIDIA Proprietary Drivers:** Default session boots with open-source `nouveau` or kernel modesetting. For optimal Wayland performance on NVIDIA Turing/Ampere/Ada GPUs, install proprietary drivers via `monodesk-nvidia-installer` or `synaptic`.
- **Intel 2nd Gen HD 3000 Graphics:** Sandy Bridge graphics lack modern DRM format modifiers required by modern wlroots compositors. Use the pre-configured **MONODESK Recovery (X11)** session for glitch-free performance.
