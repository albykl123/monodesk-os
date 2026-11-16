# MONODESK OS 2.0.1-rc1 — Desktop Integration Fix Report

**Date:** 2026-11-16  
**Target Hardware:** Lenovo IdeaPad Slim 5 (82LN), AMD Ryzen 7 5700U with Radeon Graphics (`amdgpu`), 14 GB RAM  
**Target Release:** MONODESK OS 2.0.1-rc1 (Universal PC Edition)  
**Branch:** `v2.0-desktop-fix`  

---

## 1. Executive Summary

Following a forensic audit of the booted external JMicron 1TB storage medium (which executed the Live ISO image loaded onto partition `E:`), four critical defects were identified that prevented MONODESK OS 2.0 from displaying its signature Wayland/Nebula desktop environment and desktop applications:

1. **Incorrect Desktop Session Routing:** The pre-session hardware detection routine (`monodesk-hw-detect`) invoked `glxinfo -B` prior to X11/Wayland display initialization. Because no X display was active, `glxinfo` returned an exit code of 1, causing the detector to report acceleration as `unknown`. The session router interpreted this as unaccelerated hardware and dropped the user into the legacy X11 fallback shell (`monodesk_shell.py`).
2. **Broken Compositing and Mouse Interaction:** In the legacy X11 fallback session, the window manager was launched with `xfwm4 --compositor=off`. With compositing disabled on an X11 server, translucent windows, non-rectangular shapes, and rounded corners lose their window shaping hierarchy. Hover enter/leave (`EnterNotify` / `LeaveNotify`) events failed to register properly on interactive UI elements, resulting in unresponsive mouse interactions.
3. **Omission of Nebula Desktop from Live-Build RootFS:** The upstream Nebula desktop configurations (Hyprland dotfiles, Quickshell components, M3Shapes styling, dot-matrix shaders, and wallpapers) had been imported into the source repository (`third_party/nebula/` and `shell/quickshell/`) but were omitted from the live-build staging tree (`build/live-build/config/includes.chroot/`).
4. **Missing Application Executable Wrappers and Desktop Entries:** The MONODESK Settings Hub (`monodesk_settings.py`), Software Centre (`monodesk_software_manager.py`), and 22 other system tools were present in the source repository under `applications/`, but no executable wrappers were installed to `/usr/bin/` and no `.desktop` launcher files were registered in `/usr/share/applications/`.

---

## 2. Root Cause Analysis & Technical Resolutions

### 2.1 Hardware Detection Overhaul (`monodesk-hw-detect`)
- **Previous Failure Mode:** Relied on `glxinfo -B` to assess OpenGL hardware acceleration and split `lspci -nnk` output on `\n\n`, which failed because `lspci` entries are separated by single newlines.
- **Resolution:**
  - Implemented direct Linux kernel DRM subsystem inspection via `/sys/class/drm/card*/device/driver` and `/dev/dri/renderD*`.
  - Added deterministic kernel driver matching: `amdgpu`, `radeon`, `i915`, `xe`, `nouveau`, and `nvidia` are identified as hardware-accelerated DRM drivers.
  - Line-by-line regex parsing was implemented for `lspci -nnk`, accurately parsing PCI slot numbers, vendor/device IDs, subsystem IDs, and kernel drivers.
  - Specifically targeted the AMD Ryzen 7 5700U APU (`1002:164c` Lucienne / Renoir Radeon Graphics), ensuring it immediately reports `wayland` as the optimal compositor mode.
  - Isolated legacy hardware (Intel SandyBridge Gen 6 HD 2000/3000 `8086:0102`/`0106`/`0112`/`0116`/`0122`/`0126`) to return `x11` recovery mode.

### 2.2 Session Router & Autologin Alignment (`monodesk-session`)
- **Previous Failure Mode:** Fallback routing to `monodesk-shell.py` under an uncomposited XFWM4 session; LightDM default session was ambiguous.
- **Resolution:**
  - `monodesk-session` now defaults to `wayland` on all modern GPU configurations with $\ge 2\text{ GB}$ system RAM.
  - Configured `includes.chroot/etc/lightdm/lightdm.conf.d/01-monodesk-autologin.conf` with `user-session=monodesk-wayland` and `autologin-user=monodesk`.
  - Staged `/usr/share/wayland-sessions/monodesk-wayland.desktop` executing `/usr/bin/monodesk-session`.
  - Initialized full Wayland environment variables prior to launching Hyprland:
    - `XDG_CURRENT_DESKTOP=Hyprland`
    - `XDG_SESSION_TYPE=wayland`
    - `XDG_SESSION_DESKTOP=Hyprland`
    - `QT_QPA_PLATFORM=wayland;xcb`
    - `GDK_BACKEND=wayland,x11`
    - `CLUTTER_BACKEND=wayland`
    - `MOZ_ENABLE_WAYLAND=1`
  - In recovery/fallback X11 mode, enforced `xfwm4 --compositor=on` to guarantee hardware-accelerated window compositing and active event handling.
  - Set `OnlyShowIn=MONODESK-Legacy;` in `02-configure-desktop-theme.hook.chroot` to prevent legacy shell autostart in Wayland.

### 2.3 Nebula Desktop Staging & Synchronization
- Staged complete Hyprland configurations:
  - `/etc/skel/.config/hypr/hyprland.conf`
  - `/etc/skel/.config/hypr/hyprlock.conf`
  - `/etc/skel/.config/hypr/hypridle.conf`
  - `/etc/hypr/hyprland.conf`
- Staged complete Quickshell QML desktop framework:
  - `/etc/skel/.config/quickshell/`
  - `/usr/share/monodesk/shell/quickshell/`
- Staged high-resolution monochrome dot-matrix branding wallpapers:
  - `/usr/share/backgrounds/monodesk/monodesk-dark-dotmatrix.svg`
  - `/usr/share/monodesk/branding/wallpapers/monodesk-dark-dotmatrix.svg`
- Created `/usr/bin/quickshell` multi-stage dispatcher supporting native Quickshell, `qml6`, and background wallpaper rendering via `swaybg`.

### 2.4 System Applications Integration
- Staged all 24 native MONODESK application suites into `/usr/share/monodesk/applications/`.
- Created executable Unix wrappers in `/usr/bin/` with permissions `0755`:
  - `monodesk-settings`
  - `monodesk-store`
  - `monodesk-software-manager`
  - `monodesk-system-monitor`
  - `monodesk-update-manager`
  - `monodesk-welcome`
  - `monodesk-control-centre`
  - `monodesk-device-manager`
  - `monodesk-disk-manager`
  - `monodesk-gaming`
  - `monodesk-network-centre`
  - `monodesk-bluetooth-centre`
  - `monodesk-print-centre`
  - `monodesk-privacy`
  - `monodesk-backup`
  - `monodesk-accounts`
  - `monodesk-ai`
  - `monodesk-accessibility`
  - `monodesk-clipboard`
  - `monodesk-workspace`
  - `monodesk-hardware-report`
  - `monodesk-profile-ctl`
  - `monodesk-compatibility`
  - `monodesk-recovery`
- Installed corresponding `.desktop` launchers in `/usr/share/applications/`.
- Installed scalable vector icons in `/usr/share/icons/hicolor/scalable/apps/`.

---

## 3. Verification Matrix

| Test Item | Expected Result | Verified Status |
|:---|:---|:---:|
| GPU Detection (`AMD Ryzen 7 5700U`) | Returns `wayland` compositor mode | **PASS** |
| Pre-session DRM Inspection | Direct `/sys/class/drm` and `/dev/dri` query without X11 | **PASS** |
| LightDM Autologin | Boots directly into `monodesk-wayland` | **PASS** |
| Hyprland Configuration | Staged in `/etc/skel/.config/hypr/` and `/etc/hypr/` | **PASS** |
| Quickshell Shell Staging | Staged in `/etc/skel/.config/quickshell/` and `/usr/share/monodesk/` | **PASS** |
| Settings Hub Wrapper | `/usr/bin/monodesk-settings` launches `monodesk_settings.py` | **PASS** |
| Software Centre Wrapper | `/usr/bin/monodesk-store` launches `monodesk_software_manager.py` | **PASS** |
| Application Launchers | 24 `.desktop` entries in `/usr/share/applications/` | **PASS** |
| Fallback Compositing | `xfwm4 --compositor=on` in X11 recovery mode | **PASS** |
| Packaging Validation | `scripts/validate_live_build_staging.py` passes 100% | **PASS** |

---
**Report Approved by:** Lead Linux Distribution Engineer & Systems Architect
