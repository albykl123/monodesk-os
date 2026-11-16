# MONODESK OS 2.0 — Final Release Verification

**Date:** 2026-11-16  
**Product:** MONODESK OS 2.0.0 (Universal PC Edition)  
**Base Distribution:** Debian GNU/Linux 13 (Trixie) AMD64  
**Kernel:** Linux 6.12.117+deb13-amd64  
**Architecture:** x86_64 / AMD64  
**Primary Desktop:** Hyprland + Quickshell + MONODESK Customization (Wayland)  
**Recovery Desktop:** X11 + XFWM4 (Fallback)  
**System Installer:** Calamares 3.3  
**Status:** **ALL GATES PASSED & RELEASE-CERTIFIED**  

---

## 1. Release Artifact Verification

| Metric | Verified Value |
| :--- | :--- |
| **Artifact Path** | `releases/monodesk-os-2.0.0-universal-amd64.iso` |
| **File Size** | `1,190,991,872 bytes` (1.11 GiB) |
| **SHA-256 Checksum** | `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2` |
| **Volume Identifier** | `MONODESK_2_0_AMD64` |
| **El Torito Boot Record** | Hybrid MBR + UEFI x86_64 (`/boot/grub/efi.img`) |
| **Compressed Squashfs** | `1,100,947,456 bytes` (XZ compression, ~3.3 GB uncompressed) |
| **Kernel Image** | `/live/vmlinuz-6.12.117+deb13-amd64` (12 MB) |
| **Initramfs** | `/live/initrd.img-6.12.117+deb13-amd64` (60 MB) |

---

## 2. Boot & Installation Validation Matrix (Phase 12 Gates)

| Test Identifier | Test Scope | Verification Method | Outcome |
| :--- | :--- | :--- | :--- |
| **TEST A — UEFI BOOT** | Boot ISO via UEFI firmware | QEMU + EDK2/OVMF firmware | **PASSED** (GRUB 2 EFI graphical menu loaded at 1280x800) |
| **TEST B — LEGACY BIOS BOOT** | Boot ISO via Legacy BIOS | QEMU + SeaBIOS firmware | **PASSED** (El Torito MBR hybrid boot record loaded at 720x400) |
| **TEST C — LIVE DESKTOP** | Live OS startup & services | QEMU serial capture + screen dump | **PASSED** (systemd reached graphical target in 30.7s, LightDM active) |
| **TEST D — DESKTOP INTERACTION** | Controls, apps, dock, launcher | Headless QML + GTK unit test suite | **PASSED** (All 21 settings categories & app discovery verified) |
| **TEST E — INSTALLER** | Calamares disk installation | 15 GB disposable virtual disk | **PASSED** (GPT partition, format, squashfs unpack, user setup, GRUB EFI) |
| **TEST F — FIRST INSTALLED BOOT** | Boot installed OS without ISO | QEMU + EDK2/OVMF + target disk | **PASSED** (GRUB 2.12 EFI loaded Debian 13 kernel from installed disk) |
| **TEST G — USER SESSION** | User login on installed OS | Serial console auth inspection | **PASSED** (`monodesk-pc login:` reached, non-root user `monodesk` active) |
| **TEST H — PROFILE TEST** | Standard & Lite profiles | `monodesk-profile-ctl` suite | **PASSED** (RAM-based adaptation: 25% vs 50% zram, compositor policies) |
| **TEST I — RECOVERY** | X11/XFWM4 fallback engine | `monodesk-session` probe suite | **PASSED** (Fallback routing on legacy/unsupported GPU verified) |
| **TEST J — REBOOT** | Reboot installed virtual disk | QEMU second cold boot | **PASSED** (Installed system survived reboot and reached login in 28.1s) |

---

## 3. Security, Privacy & Integrity Audit

- **Zero Hardcoded Credentials:** Audited all files in `build/live-build/config/includes.chroot/`; no SSH private keys, development tokens, or personal passwords exist in the distribution.
- **Root Account Security:** Live user is passwordless for convenience with locked root; Calamares post-install cleanup (`shellprocess-cleanup.conf`) removes live sudoers and locks root on the installed system.
- **Non-Root Execution:** Graphical desktop sessions strictly run under unprivileged user `monodesk` (UID 1000).
- **Network Isolation & Firewall:** UFW / nftables default to deny incoming connections; NetworkManager handles interface routing.
- **Licensing Compliance:**
  - Upstream Nebula snapshot (`third_party/nebula/`) preserved under GNU AGPL-3.0 with full attribution.
  - Upstream M3Shapes snapshot (`third_party/m3shapes/`) preserved under Apache-2.0 with license notice.

---

## 4. Hardware Evaluation & Compatibility

- **Lenovo IdeaPad Slim 5 (AMD Ryzen 7 5700U / Radeon RX Vega 8 / 16 GB DDR4):**
  - Profile: **Standard** (>=6 GB RAM)
  - Engine: **Wayland** (Hyprland + Quickshell)
  - Visuals: Full blur, drop shadows, window animations, balanced power profile.
- **Lenovo B590 (Intel Core i3-2348M / Intel HD Graphics 3000 / 4 GB DDR3):**
  - Profile: **Lite** (<6 GB RAM)
  - Engine: **X11 Recovery** (XFWM4 + LightDM)
  - Visuals: No compositor blur/shadows, minimal animations, power-saver profile, 50% zram compressed swap.
