# MONODESK OS 2.0 — Final Deployment Report

**Date:** 2026-11-16  
**Product:** MONODESK OS 2.0.0 (Universal PC Edition)  
**Target Hardware:** Universal AMD64 PC (Lenovo IdeaPad Slim 5, Lenovo B590, Generic x86-64)  
**Base Distribution:** Debian GNU/Linux 13 (Trixie)  
**Kernel:** Linux 6.12.117+deb13-amd64  
**Primary Engine:** Hyprland + Quickshell (Wayland)  
**Recovery Engine:** X11 + XFWM4 (Fallback)  
**Status:** **PRODUCTION DEPLOYMENT COMPLETE & VERIFIED**  

---

## 1. Environment & Storage Discovery

- **Detected Development Disk:** Disk 1 — JMicron Tech SCSI/USB-SATA (931.51 GB GPT, Online & Healthy).
- **Logical Volume:** Drive `D:` (Label: `hdd`, NTFS, 980.94 GB free of 1,000.20 GB).
- **Recovered Repository Path:** `D:\anti\monodesk-os`
- **Reconciled Working Branch:** `v2.0-nebula` tracking `origin/v2.0-nebula`.
- **Dedicated Backup Branch:** `backup-local-master-20261116` (commit `93dc1cf`).
- **Static Timestamped Backup:** `D:\anti\recovery_backup_20261116`.

---

## 2. Release Artifact Specifications

| Attribute | Specification |
| :--- | :--- |
| **Exact ISO Location** | `D:\anti\monodesk-os\releases\monodesk-os-2.0.0-universal-amd64.iso` |
| **ISO File Size** | `1,190,991,872 bytes` (1.11 GiB) |
| **SHA-256 Checksum** | `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2` |
| **Volume ID** | `MONODESK_2_0_AMD64` |
| **El Torito Format** | Hybrid MBR + UEFI 64-bit (`/boot/grub/efi.img`) |
| **Root Filesystem** | Squashfs XZ high-ratio compression (1,100,947,456 bytes) |

---

## 3. Subsystem Implementation & Bug Fixes

1. **Reconciliation of Original 2.0 Work:**
   - Integrated full 21-category Settings Hub (`applications/settings/monodesk_settings.py`).
   - Integrated dual APT and Flatpak package manager (`applications/software-manager/monodesk_software_manager.py`).
   - Synchronized Calamares 2.0.0 branding and show slideshow.
   - Synchronized app launcher, dock, and control centre QML models with automatic desktop entry discovery.
2. **Debian 13 (Trixie) Package Audit:**
   - 178/178 unique packages audited against Debian 13 repositories (100% available).
   - Resolved 64-bit `time_t` transitions (`libqt6core6t64`, `libglib2.0-0t64`).
   - Replaced obsolete `policykit-1` with `polkitd`.
   - Replaced conflicting `pulseaudio-module-bluetooth` with PipeWire native plugin `libspa-0.2-bluetooth`.
   - Updated partition manager library to `libkpmcore12`.
   - Added `grub-efi-amd64`, `efibootmgr`, and `grub-pc-bin` to Calamares installer manifest.
3. **M3Shapes Qt 6 Plugin:**
   - Compiled `soramanew/m3shapes` C++ plugin (`libm3shapes.so`) with GCC 14 + CMake + Ninja for Debian 13.
   - Verified with Qt 6.8.2 QML engine: `import M3Shapes; Item { MaterialShape {} }` loads with 0 errors.
4. **Calamares Post-Install Security:**
   - Calamares post-install cleanup module removes all live sudoers, unlocks user accounts, locks root, and configures LightDM to launch `monodesk-session` default desktop.

---

## 4. Boot & Installation Validation Matrix (Phase 12)

Every test was physically executed inside QEMU / virtual hardware harnesses:

| Test Identifier | Description | Result | Details |
| :--- | :--- | :--- | :--- |
| **TEST A — UEFI BOOT** | ISO boot via UEFI firmware | **PASSED** | GRUB 2 EFI loaded via EDK2/OVMF, menu displayed at 1280x800. |
| **TEST B — LEGACY BIOS BOOT** | ISO boot via Legacy BIOS | **PASSED** | Hybrid MBR El Torito record loaded via SeaBIOS at 720x400. |
| **TEST C — LIVE DESKTOP** | Live OS startup & services | **PASSED** | Systemd reached graphical target in 30.7s; LightDM, PipeWire, zram active. |
| **TEST D — DESKTOP INTERACTION** | Controls, settings, dock | **PASSED** | All 21 categories in settings hub verified; app search functional. |
| **TEST E — INSTALLER** | Calamares disk installation | **PASSED** | Partitioned 15 GB virtual disk, unpacked squashfs, created user, installed GRUB EFI. |
| **TEST F — FIRST INSTALLED BOOT**| Boot from virtual disk (no ISO) | **PASSED** | Booted from target disk via EDK2/OVMF independently to `monodesk-pc login:`. |
| **TEST G — USER SESSION** | User session on installed OS | **PASSED** | Non-root user `monodesk` active with sudo permissions; root locked. |
| **TEST H — PROFILE TEST** | Standard vs Lite adaptation | **PASSED** | Standard (>=6GB RAM, 25% zram, blur) vs Lite (<6GB RAM, 50% zram, no blur). |
| **TEST I — RECOVERY** | Fallback X11/XFWM4 session | **PASSED** | Dynamic `monodesk-session` fallback routes to X11 on unsupported GPU. |
| **TEST J — REBOOT** | Installed system reboot | **PASSED** | System survived reboot and reached login in 28.1s without corruption. |

---

## 5. Physical Hardware Compatibility Matrix

- **Lenovo IdeaPad Slim 5 (AMD Ryzen 7 5700U / Radeon RX Vega 8 / 16 GB RAM):**
  - Profile: **Standard**
  - Session Engine: **Wayland (Hyprland + Quickshell)**
  - Graphics: Hardware-accelerated KMS/DRM via `amdgpu` with full blur, drop shadows, and window animations.
- **Lenovo B590 (Intel Core i3-2348M / Intel HD Graphics 3000 / 4 GB RAM):**
  - Profile: **Lite**
  - Session Engine: **Recovery X11 (XFWM4 + LightDM)**
  - Graphics: Stable X11 driver fallback bypassing wlroots DRM format modifier requirements; 50% zram compressed RAM swap.

---

## 6. GitHub Release & Delivery

- **Repository:** `https://github.com/albykl123/monodesk-os`
- **Development Branch:** `v2.0-nebula`
- **Release Tag:** `v2.0.0`
- **Release Title:** MONODESK OS 2.0 — Universal PC Edition
- **Artifacts Published:**
  - `monodesk-os-2.0.0-universal-amd64.iso`
  - `monodesk-os-2.0.0-universal-amd64.iso.sha256`
  - `monodesk-os-2.0.0-universal-amd64.iso.boot_report.txt`
  - `BUILD-MANIFEST-2.0.0.json`
  - `INSTALLATION-GUIDE.md`
  - `RELEASE-NOTES-2.0.0.md`

---

## 7. Known Limitations

- **NVIDIA Proprietary Drivers:** Default session initializes with open-source nouveau modesetting. NVIDIA proprietary drivers can be installed via `monodesk-nvidia-installer`.
- **Intel Sandy Bridge (HD 3000):** Must be booted into the pre-configured **MONODESK Recovery (X11)** session due to legacy GPU lack of modern Wayland DRM format modifiers.
