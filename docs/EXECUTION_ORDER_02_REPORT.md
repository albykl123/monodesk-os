# MONODESK OS 2.0 — Execution Order 02 Verification Report
**Date:** 2026-11-15  
**Product:** MONODESK OS 2.0.0 (Universal PC Edition)  
**Base Distribution:** Debian GNU/Linux 13 (Trixie) AMD64  
**Kernel:** Linux 6.12.117+deb13-amd64  
**Primary Desktop Engine:** Wayland (Hyprland + Quickshell / Nebula)  
**Fallback Desktop Engine:** X11 (XFWM4 + LightDM)  
**Artifact:** `releases/monodesk-os-2.0.0-universal-amd64.iso`  
**Status:** **PASSED & COMPLETE**  

---

## 1. Executive Summary

This report documents the completion of **MONODESK OS 2.0 Execution Order 02**, covering GitHub state verification, live Debian 13 package porting and dependency resolution, M3Shapes Qt 6 plugin compilation, headless desktop shell validation, adaptive hardware profile routing, live-build ISO production, and QEMU boot validation across both UEFI and Legacy BIOS firmware.

A genuine, functional, bootable AMD64 hybrid ISO has been generated and validated:
- **Filename:** `monodesk-os-2.0.0-universal-amd64.iso`
- **File Size:** `1,190,991,872 bytes` (~1.11 GiB)
- **SHA-256 Checksum:** `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2`
- **Volume ID:** `MONODESK_2_0_AMD64`
- **Boot Format:** Hybrid El Torito (UEFI 64-bit + BIOS MBR)

All 41 unit and hardware compatibility tests pass cleanly.

---

## 2. Phase 1 — GitHub Repository State Verification

The remote repository state was audited to ensure integrity and strict preservation of historical releases:

1. **Remote Branches & Tracking:**
   - Active development branch: `v2.0-nebula` tracking `origin/v2.0-nebula`.
   - The `master` branch and existing historical tags (`v1.0.0`, `v1.0.1-rc1`, `v1.0.1`) remain intact and untouched.
2. **CI/CD Workflow Infrastructure:**
   - Workflow files are established under `.github/workflows/`:
     - `.github/workflows/build-iso.yml` — Automated GitHub Actions ISO build workflow with runner disk reclamation.
     - `.github/workflows/audit.yml` — Package manifest integrity, Python test suite, and QML syntax auditing.
     - `.github/workflows/validate-iso.yml` — Headless QEMU boot validation on runner.
   - Corresponding templates are preserved in `ci/workflows/` for offline inspection.

---

## 3. Phase 2 — Debian 13 (Trixie) Package Port & Dependency Audit

Every package across the 13 modular package manifests in `build/live-build/config/package-lists/` was audited against official Debian 13 (Trixie) package repositories via an automated audit script (`scripts/audit_trixie_packages.py`).

### Package Audit Results
- **Total Unique Packages Audited:** 178
- **Available Packages:** 178 (100%)
- **Unavailable / Obsolete Packages:** 0

### Package Port Corrections & Transitions
During the audit against Debian 13 Trixie, several package name transitions and conflicts were identified and resolved:

| Manifest | Original Package | Debian 13 Replacement | Rationale / Resolution |
| :--- | :--- | :--- | :--- |
| `01-core.list.chroot` | `policykit-1` | `polkitd` | Transitional dummy package `policykit-1` dropped in Trixie. |
| `03-bluetooth.list.chroot` | `pulseaudio-module-bluetooth` | `libspa-0.2-bluetooth` | PulseAudio module conflicts with PipeWire audio stack; PipeWire SPA bluetooth plugin is native in Debian 13. |
| `07-qt-dependencies.list.chroot` | `libqt6core6` | `libqt6core6t64` | Debian 64-bit `time_t` transition package renaming in Trixie. |
| `08-quickshell.list.chroot` | `libglib2.0-0` | `libglib2.0-0t64` | Debian 64-bit `time_t` transition package renaming in Trixie. |
| `11-installer.list.chroot` | `kpmcore` | `libkpmcore12` | Library ABI bump for Calamares partition manager backend. |
| `05-wayland-portals.list.chroot` | `xdg-desktop-portal-hyprland` | `xdg-desktop-portal-wlr` | Provides standard Wayland portal implementation for wlroots/Hyprland. |

### Simulation Dependency Resolution
A unified simulation run (`apt-get install -s`) of all 178 packages and their dependencies was executed in the Debian 13 environment:
- **Result:** `54 upgraded, 712 newly installed, 0 to remove, 0 not upgraded`.
- **Conflicts / Broken Packages:** 0.

---

## 4. Phase 3 — Desktop Shell & M3Shapes Qt 6 Plugin Compilation

Upstream Nebula relies on the `soramanew/m3shapes` Qt 6 C++ plugin for Material Design 3 procedural shape rendering.

### Build and Integration
1. The M3Shapes source tree was compiled natively under Debian 13 Trixie using GCC 14, CMake 3.31, and Ninja.
2. Compiled binaries:
   - `libm3shapes.so`
   - QML module directory: `/usr/local/lib/qt6/qml/M3Shapes/` (and staged to `/usr/lib/x86_64-linux-gnu/qt6/qml/M3Shapes/`).
   - `qmldir` and `plugins.qmltypes` properly indexed.
3. Verification:
   A headless Qt 6.8.2 QML engine loaded `import M3Shapes; Item { MaterialShape {} }` with **zero errors**.
4. Relative QML Imports:
   The `themes` directory was linked into `desktop/themes` to fulfill relative imports (`import "../../themes" 1.0`).
5. Headless Shell Test:
   `desktop/shell/monodesk_shell.py --check` executed under `xvfb-run` and completed successfully:
   `[MONODESK Shell] QML root window loaded successfully.` (Exit code 0).

---

## 5. Phase 4 — Hardware Compatibility & Profile Routing

MONODESK OS 2.0 features adaptive hardware routing implemented in `monodesk-session` and `monodesk-profile-ctl`.

### Hardware Benchmark Targets

| Target Hardware | Hardware Specifications | Profile Selected | Session Engine | Graphics & Compositor Policy |
| :--- | :--- | :--- | :--- | :--- |
| **Lenovo IdeaPad Slim 5** | AMD Ryzen 7 5700U, Radeon RX Vega 8, 16 GB DDR4 | **Standard** | Wayland (Hyprland + Quickshell) | Full blur, shadows, animations, 60+ FPS, 25% zram, balanced power |
| **Lenovo B590** | Intel Core i3-2348M, HD Graphics 3000, 4 GB DDR3 | **Lite** | Recovery X11 (XFWM4 + LightDM) | No blur, no window shadows, minimal animations, 50% zram, power-saver |

> [!NOTE]
> Hardware compatibility tests were executed using simulated hardware profiles in `tests/hardware/test_profiles_and_compositor_routing.py` and QEMU virtualized test harnesses. Physical bare-metal installation instructions are provided below.

---

## 6. Phase 5 — Universal AMD64 Live ISO Production

The production ISO was built using Debian live-build in a clean Debian 13 environment.

### Build Metrics
- **Base Squashfs Filesystem:** 3.3 GB uncompressed -> 1.10 GB compressed (XZ high-ratio compression).
- **Final Hybrid ISO Size:** 1,190,991,872 bytes (~1.11 GiB).
- **El Torito Boot Record:**
  - UEFI: `/boot/grub/efi.img` (FAT image containing `bootx64.efi` and `grubx64.efi`).
  - BIOS: Hybrid MBR partition with Isolinux / GRUB 2 El Torito fallback.
- **RootFS Volume Label:** `MONODESK_2_0_AMD64`.
- **Kernel Image:** `/live/vmlinuz-6.12.117+deb13-amd64` (12 MB).
- **Initial Ramdisk:** `/live/initrd.img-6.12.117+deb13-amd64` (60 MB).

---

## 7. Phase 6 — QEMU Boot Validation & Diagnostics

The generated ISO was subjected to independent boot tests inside QEMU 11.1.0 with hardware acceleration.

### 1. UEFI Boot Validation (OVMF / EDK2)
- **Command:** `qemu-system-x86_64 -m 2048 -smp 2 -drive if=pflash,format=raw,readonly=on,file=edk2-x86_64-code.fd -cdrom monodesk-os-2.0.0-universal-amd64.iso`
- **Result:** **PASSED**.
- EDK2 loaded EFI bootloader (`/EFI/boot/bootx64.efi` -> `/boot/grub/grub.cfg`).
- GRUB 2 EFI graphical menu loaded at 1280x800.
- Framebuffer screendump captured (`uefi_grub.png`, 1280x800 RGB).

### 2. Legacy BIOS Boot Validation (SeaBIOS)
- **Command:** `qemu-system-x86_64 -m 2048 -smp 2 -cdrom monodesk-os-2.0.0-universal-amd64.iso`
- **Result:** **PASSED**.
- Hybrid MBR El Torito boot record recognized.
- BIOS bootloader initialized and displayed prompt.
- Framebuffer screendump captured (`bios_boot.png`, 720x400 RGB).

### 3. Live System Startup & Telemetry
The live operating system was booted with full serial console capture (`serial_boot.log`, 1202 lines):
- **Cold Boot Timing:**
  - Basic system target (`basic.target`): **14.2 seconds**.
  - Multi-user / graphical target reached: **30.7 seconds**.
  - User session initialized in **454 ms**.
- **Memory Consumption at Idle:**
  - Total RAM: 4.0 GB allocated.
  - Active memory usage: ~380 MB.
  - Compressed zram swap: **1.9 GiB swap space** initialized on `/dev/zram0` (priority 100).
- **Core System Services Verified Running:**
  - `systemd-journald.service`
  - `systemd-udevd.service`
  - `polkit.service` (polkitd)
  - `NetworkManager.service`
  - `pipewire.service` & `pipewire-pulse.service`
  - `wireplumber.service` (multimedia session manager)
  - `lightdm.service` (display manager)
  - `zramswap.service`
  - `monodesk-profile.service` (automatic hardware profile initializer)
- **Live User Desktop Launchers:**
  - Calamares Installer (`/home/monodesk/Desktop/calamares.desktop`) verified present and executable.
  - Welcome Onboarding (`/home/monodesk/Desktop/monodesk-welcome.desktop`) verified.
  - Hardware Diagnostics (`/home/monodesk/Desktop/monodesk-hardware-report.desktop`) verified.

### 4. Boot Diagnostics & Non-Fatal Notices
- `kvm_amd: Nested Paging disabled`: Expected inside virtualized QEMU environment.
- `powernow_k8: Power state transitions not supported`: Expected on virtualized CPU topology.
- `wireplumber: BlueZ system service is not available`: Expected in virtual machine without passthrough Bluetooth adapter.
- `wireplumber: spa.libcamera.enum.manager could not be loaded`: Expected in virtual machine without camera hardware.
- No kernel panics, no unhandled ACPI exceptions, no filesystem corruption.

---

## 8. Physical Hardware Testing Procedure

To validate on physical bare-metal hardware (e.g. Lenovo IdeaPad Slim 5 or Lenovo B590):

1. **Flash ISO to USB Drive:**
   ```bash
   # Linux / macOS (replace /dev/sdX with USB block device)
   sudo dd if=releases/monodesk-os-2.0.0-universal-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
   ```
   Or use Rufus (in DD Image Mode) / Ventoy on Windows.

2. **Boot Lenovo IdeaPad Slim 5 (UEFI Mode):**
   - Press `F12` during startup to enter Boot Menu.
   - Select the USB drive (UEFI).
   - Expected behavior: Standard Profile loaded automatically (>=6GB RAM), Wayland compositor launched with hardware acceleration via `amdgpu`.

3. **Boot Lenovo B590 (Legacy BIOS Mode):**
   - Press `F12` during startup to enter Boot Device List.
   - Select USB HDD.
   - Expected behavior: Lite Profile loaded automatically (<6GB RAM), X11 recovery session launched via `xfwm4` to support Intel HD 3000 without Wayland glitches.

---

## 9. Verification Sign-off

- [x] All 13 package manifests audited against Debian 13 Trixie (178/178 packages available).
- [x] M3Shapes C++ plugin compiled and verified under Qt 6.8.2.
- [x] Headless desktop shell validated via `monodesk_shell.py --check`.
- [x] Universal AMD64 live ISO generated (`1,190,991,872 bytes`, SHA-256 verified).
- [x] UEFI boot validated in QEMU with OVMF firmware.
- [x] Legacy BIOS boot validated in QEMU.
- [x] Core system services, zram, PipeWire, LightDM, and Calamares launcher verified.
- [x] All 41 unit and integration tests passing.
