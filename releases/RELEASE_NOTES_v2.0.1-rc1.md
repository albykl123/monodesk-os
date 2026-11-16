# MONODESK OS 2.0.1-rc1 — Critical Desktop & Hardware Integration Release

**Release Channel:** Release Candidate 1 (Pre-release)  
**Target Architecture:** x86_64 (Universal AMD/Intel PC)  
**Reference Target:** Lenovo IdeaPad Slim 5 (82LN), AMD Ryzen 7 5700U APU, AMD Radeon Graphics (`amdgpu`), 14 GB RAM  
**Base Distribution:** Debian 13 Trixie (AMD64)  
**Kernel:** Linux 6.12 LTS  

---

## 🎯 Key Defect Resolutions

This release candidate directly resolves four critical architectural defects identified during hardware testing of the booted live media on target PC hardware:

1. **Deterministic Hardware Detection & Wayland Routing (`monodesk-hw-detect`):**
   - Eliminated pre-session `glxinfo` execution that caused GPU acceleration to report as `unknown` before display server initialization.
   - Implemented direct Linux kernel DRM subsystem inspection (`/sys/class/drm/card*` and `/dev/dri/renderD*`).
   - Line-by-line regex parsing implemented for `lspci -nnk`, avoiding broken newline splitting.
   - AMD Ryzen 7 5700U (`1002:164c` Lucienne/Renoir) immediately resolves to the hardware-accelerated **Wayland** session profile.
2. **Fixed Mouse Hover & Input Event Routing (`monodesk-session`):**
   - Defaulted modern GPU hardware to native Wayland/Hyprland session, where pointer coordination (`wl_pointer`) and hardware cursors provide subpixel precision and zero latency.
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
5. **Sanitization of Wrapper Binary Headers & Shebangs:**
   - Eliminated UTF-8 Byte Order Marks (`\xef\xbb\xbf`) and carriage returns (`\r\n`) across all `/usr/bin/monodesk-*` and `/usr/bin/quickshell` launchers.
   - Restored Linux kernel `execve()` direct invocation capability from GUI and CLI contexts.
   - Updated `monodesk-profile-ctl` with resilient exception handling, ensuring `monodesk-profile.service` starts with zero errors.
6. **Installed Operating System Identity Verification:**
   - Configured Calamares post-install hooks to write authoritative `2.0.1-rc1 (Universal PC Edition)` identity metadata to `/etc/os-release`, `/etc/issue`, and `/etc/issue.net`.

---

## 📦 Verified Release Assets

| Asset Name | Type | Size | SHA-256 Checksum |
|:---|:---:|:---:|:---|
| **`monodesk-os-2.0.1-rc1-universal-amd64.iso`** | Bootable Hybrid ISO | 917.63 MiB | `e4dff2a2a29992b1a68c5fbec330dff707b66cb87a224afa1daa750dd61b8346` |
| **`monodesk-os-2.0.1-rc1-universal-amd64.iso.sha256`** | Checksum | 108 B | Verified via `Get-FileHash` |
| **`BUILD-MANIFEST-2.0.1-rc1.json`** | Build Manifest | 2.5 KB | Complete subsystem metadata |
| **`PACKAGE-MANIFEST-2.0.1-rc1.txt`** | Dpkg Package List | 24 KB | 922 packages installed |
| **`DESKTOP_INTEGRATION_FIX_REPORT.md`** | QA Report | 6 KB | Full root-cause analysis |
| **`ISO_2.0.1_RC1_VERIFICATION.md`** | QA Report | 4 KB | Boot & filesystem audit |
| **`SETTINGS_HUB_VERIFICATION.md`** | QA Report | 3 KB | Settings Hub integration audit |
| **`SOFTWARE_CENTRE_VERIFICATION.md`** | QA Report | 3 KB | Software Centre integration audit |
| **`MOUSE_INTERACTION_TEST_REPORT.md`** | QA Report | 4 KB | Mouse & compositor event audit |
| **`MONODESK_2.0.1_FINAL_RELEASE_REPORT.md`** | Final Release Report | 8 KB | Master directive audit report |
| **`v201_installed_screen.png`** | Verification Capture | 4 KB | QMP framebuffer screendump of cold boot |

---

## 🚀 Quality Assurance Validation
- **Staging Audit:** `scripts/validate_live_build_staging.py` passed 100% (28 checks).
- **Rootfs Squashfs Audit:** Verified presence of all 24 application wrappers in `/usr/bin/` and desktop entries in `/usr/share/applications/`.
- **UEFI Boot:** Verified via QEMU (x86_64 EDK2/OVMF firmware).
- **BIOS Boot:** Verified via QEMU (Legacy BIOS El Torito boot core).
- **Calamares Installation:** Partitioned and installed to disposable virtual disk (`test-disposable-101.qcow2`).
- **Cold Boot of Installed OS:** Verified independent UEFI boot from installed disk without ISO attached (clean systemd multi-user target and automatic user session in 41.2s).
