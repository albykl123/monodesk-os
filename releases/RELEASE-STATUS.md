# MONODESK OS — Release Status & Validation Summary

**Production Release:** `v1.0.1` (`monodesk-os-1.0.1-universal-amd64.iso`)  
**Previous Preserved Releases:** `v1.0.0` (GitHub Release), `v1.0.1-rc1` (local candidate)  
**Base Distribution:** Debian GNU/Linux 12 (Bookworm) AMD64 (`6.1.0-54-amd64`)  
**Source Commit:** `e0efd886af79b8f8c7db62f8adf1e14b177efb05`  
**Validation Date:** 2026-11-12

---

## Release Gate Comparison (`v1.0.0` -> `v1.0.1-rc1` -> `v1.0.1`)

| Check / Gate | `v1.0.0` (Preserved) | `v1.0.1-rc1` (Preserved) | `v1.0.1` (Final) | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Single Unsplit ISO < 2 GiB** | **PASSED** (`400.14 MiB`) | **PASSED** (`655.23 MiB`) | **PASSED** (`730.90 MiB` / `766,408,704` B) | Single hybrid ISO (`3b8ad75a...`) |
| **QEMU UEFI Live Boot (OVMF)** | **PASSED** | **PASSED** | **PASSED** (`BOOT_MODE=UEFI`) | SquashFS + OverlayFS, user `monodesk` |
| **Legacy BIOS Live Boot (SeaBIOS)** | **FAILED** | **PASSED** | **PASSED** (`BOOT_MODE=LEGACY_BIOS`) | 5/5 core services active, QtQml/QtQuick OK |
| **MONODESK Shell Xorg Rendering** | **FAILED** | **FAILED** (QtQml missing) | **PASSED** (`PyQt6.QtQml` `6.4.2`) | Single QML root window rendered (`shell_xorg.png`) |
| **XFCE Fallback (Missing Qt)** | **FAILED** | **PARTIAL** | **PASSED** (`FALLBACK_RC=0`) | Launches `xfce4-panel` & `xfdesktop` safely |
| **Calamares Disposable Install** | **FAILED** | **PASSED** | **PASSED** (`25 GiB` qcow2) | GPT + FAT32 EFI + ext4 + `shellprocess@cleanup` |
| **Installed System Boot (No ISO)** | **FAILED** | **PASSED** | **PASSED** (8 GiB & 4 GiB boots) | Direct UEFI boot via `MONODESK_OS` |
| **No Root Autologin / Non-Root Security** | **FAILED** | **FAILED** (getty drop-in persisted) | **PASSED** (`root` locked, `sudo -n` blocked) | LightDM greeter active, live creds removed |
| **Standard / Lite & ZRAM Switching** | **PARTIAL** | **PASSED** | **PASSED** (`zram0` `2031308` <-> `4062616` KiB) | 4 GiB auto->Lite verified across reboot |
| **Applications & Recovery** | **FAILED** | **PARTIAL** | **PASSED** | Welcome, Recovery, HW Report, GRUB Recovery |
| **Automated Host Test Suite (`pytest`)** | **PASSED** (32) | **PASSED** (32) | **PASSED** (35 passed in `2.90s`) | Added QML/fallback/cleanup unit tests |
| **Physical Lenovo Slim 5 & B590** | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | Pending physical hardware execution |

See [FINAL-VALIDATION-REPORT.md](FINAL-VALIDATION-REPORT.md) for exact command outputs, Verified Results vs Unverified Claims, and Remaining Limitations.
