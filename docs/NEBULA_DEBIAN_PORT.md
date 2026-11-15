# MONODESK OS 2.0 — Nebula Debian 13 Port Specification

**Document:** Debian 13 (Trixie) Porting Architecture & Integration Specification  
**Version:** 2.0.0  
**Target Architecture:** AMD64 / x86-64  
**Base Distribution:** Debian 13 Trixie  

---

## 1. Executive Summary

MONODESK OS 2.0.0 integrates the **Nebula** desktop environment (Hyprland + Quickshell) into an enterprise-grade, zero-telemetry Debian 13 Trixie distribution. Upstream Nebula originally targeted Arch Linux with user-space compilation and rolling AUR packages. This document specifies the complete, reproducible Debian 13 porting strategy, including system-level packaging, library compilation, session management, and hardware fallback.

---

## 2. Directory Layout & Source Tree Integration

The repository integrates Nebula and custom MONODESK components cleanly:

```
monodesk-os/
├── compositor/
│   ├── hyprland/                  # Hyprland 0.42+ configs & monitors
│   │   ├── hyprland.conf          # Main compositor rules & keybindings
│   │   ├── hypridle.conf          # Power-saving & idle screen timeout
│   │   └── hyprlock.conf          # Lockscreen with dot-matrix clock
│   └── sessions/                  # Display manager session descriptors
│       ├── monodesk-wayland.desktop
│       └── monodesk-recovery.desktop
├── shell/
│   ├── quickshell/                # Quickshell shell configurations
│   ├── monodesk-branding/         # Monochrome SVG assets & dot-matrix glyphs
│   └── monodesk-components/       # MONODESK-specific QML bridges & widgets
├── third_party/
│   ├── nebula/                    # Upstream Nebula source snapshot (AGPL-3.0)
│   └── m3shapes/                  # Material 3 Shapes Qt 6 plugin (Apache-2.0)
├── applications/                  # Native MONODESK desktop applications
│   ├── settings/                  # 21-page system configuration utility
│   ├── software-manager/          # APT / Flatpak package manager
│   ├── system-monitor/            # Process and hardware monitor
│   └── recovery/                  # Emergency diagnostics & restore tool
└── build/
    └── live-build/                # Debian 13 live-build manifests & hooks
```

---

## 3. Debian 13 Packaging & Build Pipeline

### 3.1 M3Shapes Qt 6 QML Plugin Build

Nebula requires `m3shapes` for rendering Material 3 rounded surfaces and dynamic shapes. In Debian 13:
1. Build dependencies: `cmake`, `ninja-build`, `qt6-base-dev`, `qt6-declarative-dev`, `g++`.
2. Build command:
   ```bash
   cmake -S third_party/m3shapes -B build/m3shapes -G Ninja \
         -DCMAKE_BUILD_TYPE=Release \
         -DCMAKE_INSTALL_PREFIX=/usr \
         -DCMAKE_INSTALL_LIBDIR=lib/x86_64-linux-gnu
   cmake --build build/m3shapes
   cmake --install build/m3shapes --destdir target/chroot
   ```
3. Installed Artifacts:
   - `/usr/lib/x86_64-linux-gnu/qt6/qml/m3shapes/libm3shapesplugin.so`
   - `/usr/lib/x86_64-linux-gnu/qt6/qml/m3shapes/qmldir`

### 3.2 Quickshell Desktop Framework

Quickshell provides the reactive QML desktop runtime interfacing directly with Wayland protocols and IPC:
- Build dependencies: `cmake`, `ninja-build`, `qt6-base-dev`, `qt6-declarative-dev`, `qt6-wayland-dev`, `wayland-protocols`, `libwayland-dev`, `pkg-config`.
- Binary deployment: Installed to `/usr/bin/quickshell`.

### 3.3 Dynamic Material Colors with Matugen

- Upstream relies on `matugen` to extract color palettes from wallpaper images.
- MONODESK pre-compiles and deploys `matugen` to `/usr/bin/matugen`.
- Default color generation is triggered at user initialization and profile creation:
  ```bash
  matugen image /usr/share/backgrounds/monodesk/monodesk-dark-dotmatrix.svg
  ```

---

## 4. Dual-Engine Session Architecture

To guarantee 100% universal PC hardware compatibility (ranging from modern high-end laptops to legacy Intel HD 3000 / Sandy Bridge systems):

### 4.1 Intelligent Hardware Router (`/usr/bin/monodesk-session`)

At login, `monodesk-session` executes:
1. Query `monodesk-hw-detect --check-compositor`.
2. Evaluates:
   - DRM / KMS kernel modesetting availability (`/dev/dri/card0`).
   - Vulkan / OpenGL ES 3.1+ support.
   - User profile selection (`Standard` vs `Lite`).
3. If hardware meets Wayland requirements:
   - Launches `Hyprland` with Quickshell desktop.
4. If running in safe graphics mode, legacy VM without acceleration, or GPU lacks DRM:
   - Launches `MONODESK Recovery Session` (`X11` + `xfwm4` + Qt 6 Shell).

### 4.2 Display Manager Configuration

- GDM / LightDM session definitions:
  - `/usr/share/wayland-sessions/monodesk-wayland.desktop`:
    `Exec=monodesk-session wayland`
  - `/usr/share/xsessions/monodesk-recovery.desktop`:
    `Exec=monodesk-session x11`

---

## 5. System Services & Polkit Integration

All user interactions in the Nebula / MONODESK UI trigger real system commands:
- **Networking:** NetworkManager D-Bus API (`nmcli connection up`, `nmcli device wifi connect`).
- **Bluetooth:** BlueZ D-Bus API (`bluetoothctl power on`, `bluetoothctl connect`).
- **Audio:** PipeWire & WirePlumber (`wpctl set-volume @DEFAULT_AUDIO_SINK@`).
- **Brightness:** `brightnessctl set 5%+`.
- **System Power:** `systemctl poweroff`, `systemctl reboot`, `loginctl lock-session`.
- **Package Management:** Native `apt-get` and `flatpak` via `monodesk-software-manager` protected by Polkit.

---

## 6. Verification and Acceptance Gates

- [x] Upstream Nebula source cleanly imported into `third_party/nebula/` without `.git` nesting.
- [x] M3Shapes source cleanly imported into `third_party/m3shapes/`.
- [x] Zero Arch-specific package invocations in production scripts.
- [x] Modular package lists for Debian 13 (`01-core.list.chroot`, `02-hyprland.list.chroot`, etc.).
- [x] Dual-engine fallback verified for legacy BIOS and older hardware.
- [x] Full test suite passing across all core desktop components.
