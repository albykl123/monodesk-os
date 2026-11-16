# MONODESK OS 2.0.1-rc1 — Software Centre Integration & Verification Report

**Component:** MONODESK Software Centre (`monodesk-store` / `monodesk-software-manager`)  
**Package:** `monodesk-software-manager`  
**Source Path:** `applications/software-manager/monodesk_software_manager.py`  
**Installed Target:** `/usr/share/monodesk/applications/software-manager/monodesk_software_manager.py`  
**System Wrappers:** `/usr/bin/monodesk-store` and `/usr/bin/monodesk-software-manager`  
**Desktop Launcher:** `/usr/share/applications/monodesk-software-manager.desktop`  
**Icon Asset:** `/usr/share/icons/hicolor/scalable/apps/monodesk-store.svg`  

---

## 1. Overview & Architectural Role

The MONODESK Software Centre provides a streamlined graphical storefront and package manager for Debian 13 Trixie packages, Flatpak applications, and curated developer toolchains. Designed with an ultra-minimalist aesthetic, it features real-time search, category browsing, one-click installation, background dependency resolution, and update tracking.

In MONODESK OS 2.0.0, the application code existed only inside `applications/software-manager/` without corresponding executable commands in `/usr/bin/` or application registrations in `/usr/share/applications/`.

---

## 2. Technical Implementation in v2.0.1-rc1

### 2.1 Dual Executable Wrappers
To provide maximum ergonomic flexibility, both `monodesk-store` (common user command) and `monodesk-software-manager` (system name) are installed to `/usr/bin/` with permissions `0755`:

- `/usr/bin/monodesk-store`:
```bash
#!/usr/bin/env bash
set -e
export QT_QUICK_CONTROLS_STYLE=Basic
export QML_IMPORT_PATH="/usr/share/monodesk:/usr/lib/x86_64-linux-gnu/qt6/qml:/usr/local/lib/qt6/qml:${QML_IMPORT_PATH}"
export QML2_IMPORT_PATH="${QML_IMPORT_PATH}"

if [ -f /usr/share/monodesk/applications/software-manager/monodesk_software_manager.py ]; then
    exec python3 /usr/share/monodesk/applications/software-manager/monodesk_software_manager.py "$@"
elif [ -f /root/monodesk-os/applications/software-manager/monodesk_software_manager.py ]; then
    exec python3 /root/monodesk-os/applications/software-manager/monodesk_software_manager.py "$@"
else
    echo "[MONODESK Store] Application executable not found." >&2
    exit 1
fi
```

- `/usr/bin/monodesk-software-manager`: Symlinked or wrapping the identical launcher entrypoint.

### 2.2 Desktop Launcher (`/usr/share/applications/monodesk-software-manager.desktop`)
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=MONODESK Software
Comment=Application store and software manager
Exec=monodesk-store
Icon=monodesk-store
Categories=System;PackageManager;
Terminal=false
StartupNotify=true
StartupWMClass=monodesk-software-manager
```

### 2.3 Hyprland Compositor Integration
In `hyprland.conf`, the Software Centre is bound to `SUPER+A` (Application Store):
```ini
# Application Store Shortcut
bind = $mainMod, A, exec, monodesk-store

# Window Rule
windowrulev2 = float, class:^(monodesk-software-manager)$
```

---

## 3. Subsystem Functionality Matrix

| Subsystem Feature | Underlying Technology | Verification Status |
|:---|:---|:---:|
| **Debian 13 Repositories** | `apt`, `libapt-pkg`, `dpkg` | **VERIFIED** |
| **Flatpak Integration** | `flatpak` CLI & Flathub remote | **VERIFIED** |
| **Search & Filtering** | In-memory indexing & APT cache parsing | **VERIFIED** |
| **Installation Queue** | Background threaded worker, Polkit elevation | **VERIFIED** |
| **System Updates** | APT update / upgrade transaction manager | **VERIFIED** |

---

## 4. Verification Verdict
The MONODESK Software Centre is fully registered, accessible via `/usr/bin/monodesk-store`, discoverable in application menus, and callable via `SUPER+A` in the live environment.
