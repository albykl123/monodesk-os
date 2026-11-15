# Upstream Nebula Audit Report

**Project:** MONODESK OS 2.0.0 (Universal PC Edition)  
**Document:** Upstream Nebula Security, Architecture & Dependency Audit  
**Status:** Approved & Validated  
**Date of Import:** 2026-11-15  

---

## 1. Upstream Metadata & Attribution

| Attribute | Specification |
| :--- | :--- |
| **Upstream Repository** | [https://github.com/LilaccFlowerr/Nebula](https://github.com/LilaccFlowerr/Nebula) |
| **Upstream Author** | LilaccFlowerr |
| **Pinned Commit Hash** | `9749c30402b4e6712d0222c48b645fa357d0217e` |
| **Pinned Commit Date** | Sat Nov 14 21:13:01 2026 +0100 |
| **Commit Subject** | `Merge pull request #7 from LilaccFlowerr/feat/widget-system` |
| **License** | GNU Affero General Public License v3.0 (AGPL-3.0) |
| **Local Import Directory** | `third_party/nebula/` |
| **Related Submodule** | `third_party/m3shapes/` (Apache-2.0, commit `8a6fe8961749887d677700b6508e0c9249968b7e`) |

All upstream copyright notices, author credits, and license files have been strictly preserved in `third_party/nebula/LICENSE` and `third_party/m3shapes/LICENSE`.

---

## 2. Upstream Architecture & Directory Layout

Upstream Nebula is a complete Wayland desktop environment built on **Hyprland** (compositor) and **Quickshell** (flexible Qt 6 / QML desktop shell engine).

```
third_party/nebula/
├── assets/                  # Wallpapers, sound effects, audio profiles
├── components/              # Reusable QtQuick / QML UI controls
├── services/                # Backend service bridges (D-Bus, CLI wrappers, IPC)
├── shaders/                 # Hardware-accelerated GLSL fragment shaders (glass, blur)
├── theme/                   # Dynamic design tokens, color bridges, typography
├── widgets/                 # Composite desktop UI panels
│   ├── bar/                 # Top status bar / dock (island-style)
│   ├── launcher/            # Application launcher & fuzzy search
│   ├── notification/        # Desktop notification daemon & popups
│   ├── popups/              # Tray, audio, network, bluetooth flyouts
│   ├── recorder/            # Screen recording UI overlay
│   ├── screenshot/          # Interactive area/window screenshot utility
│   ├── settings/            # Modular desktop settings interface
│   └── wallpaper/           # Dynamic wallpaper engine & background manager
├── hypr/                    # Hyprland compositor & idle/lock configuration
├── matugen/                 # Material 3 dynamic color scheme generator config
├── fastfetch/               # Dot-matrix terminal system information profile
├── fish/                    # Shell configuration
└── ghostty/                 # Terminal emulator configuration
```

---

## 3. Dependency Inventory & Upstream vs Debian 13 Trixie Mapping

Upstream assumes an Arch Linux base running `pacman` and AUR helpers. For MONODESK OS 2.0.0 on Debian 13 Trixie, every component is mapped to native Debian packages or reproducible source builds:

| Component | Upstream (Arch) | Debian 13 Trixie Equivalent | Port Strategy |
| :--- | :--- | :--- | :--- |
| **Compositor** | `hyprland` | `hyprland` (0.42+) | Available in Debian Trixie / bookworm-backports; source fallback |
| **Idle Daemon** | `hypridle` | `hypridle` | Debian 13 native package |
| **Screen Locker** | `hyprlock` | `hyprlock` | Debian 13 native package |
| **Shell Framework** | `quickshell` | Source build (CMake + Qt 6) | Packaged in Debian build overlay (`/usr/bin/quickshell`) |
| **QML Shapes** | `m3shapes` (AUR) | CMake + Qt 6 build | Built from `third_party/m3shapes` into Qt 6 QML module path |
| **Material Colors** | `matugen` (AUR) | Cargo / binary package | Rust package or static binary in `/usr/local/bin/matugen` |
| **Portal** | `xdg-desktop-portal-hyprland` | `xdg-desktop-portal-hyprland` | Debian 13 native package |
| **Terminal** | `ghostty` | `ghostty` / `foot` fallback | Installed via deb package / apt |
| **File Manager** | `nautilus` | `nautilus` | Debian 13 native package |
| **Audio Server** | `pipewire`, `wireplumber` | `pipewire`, `wireplumber` | Debian 13 native packages |
| **Volume Control** | `playerctl`, `cava` | `playerctl`, `cava` | Debian 13 native packages |
| **Brightness** | `brightnessctl` | `brightnessctl` | Debian 13 native package |
| **Clipboard** | `wl-clipboard`, `cliphist` | `wl-clipboard`, `cliphist` | Debian 13 native packages |
| **Screen Capture** | `grim`, `slurp` | `grim`, `slurp` | Debian 13 native packages |
| **Polkit Agent** | `mate-polkit` | `mate-polkit` | Debian 13 native package |
| **Notification** | `libnotify` | `libnotify-bin` | Debian 13 native package |
| **Fonts** | `inter-font`, `ttf-material-symbols` | `fonts-inter`, `fonts-material-design-icons-iconfont` | Debian 13 native packages + custom dotmatrix font overlay |

---

## 4. Key Upstream Modifications Required for MONODESK OS 2.0

1. **Do Not Run Upstream `install.sh`**:
   The upstream installation script assumes `pacman` and writes to `~/.config/`. MONODESK OS manages all configurations system-wide via `/etc/skel/` and `/usr/share/monodesk/` overlays during Debian `live-build`.
2. **Dual-Engine Compositor Architecture**:
   While Nebula operates under Hyprland (Wayland), MONODESK OS 2.0.0 provides an automatic dual-engine architecture:
   - Modern GPUs (Intel Iris/Xe, AMD Radeon, NVIDIA with KMS/DRM): Boots into **MONODESK Wayland** (`Hyprland` + `Quickshell`).
   - Legacy / Non-DRM GPUs (Intel HD 3000 Sandy Bridge, legacy BIOS, safe graphics): Automatically falls back to **MONODESK Recovery** (`X11` + `XFWM4` + Qt 6 Shell).
3. **Nothing-Inspired Monochrome Design Language**:
   Upstream Nebula uses vibrant Material 3 palettes. In MONODESK OS, `matugen` templates and QML theme tokens are tailored to MONODESK's signature monochrome dot-matrix aesthetic (`#000000`, `#FFFFFF`, `#121212`, `#242424`, `#E0E0E0`, `#D70A53` Nothing red accent).
4. **Integration with MONODESK System Services**:
   - `monodesk-profile-ctl`: Standard vs. Lite resource profile switching.
   - `monodesk-hw-detect`: Automatic hardware detection, GPU driver selection, and audio/network diagnostics.
   - Calamares Live Installer: Integrated launcher icon and live desktop installer launcher.
   - `monodesk-settings`: Full 21-page system configuration tool.
   - `monodesk-software-manager`: Native APT and Flatpak package manager.
