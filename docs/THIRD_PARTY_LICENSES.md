# MONODESK OS 2.0 — Third-Party Software Licenses & Attributions

**Project:** MONODESK OS 2.0.0 (Universal PC Edition)  
**Document:** Complete Third-Party Licenses, Copyright Notices and Upstream Attribution  
**Status:** Canonical Reference Document  

---

## 1. Statement of Independence and Non-Affiliation

MONODESK OS is an independent open-source Linux operating system. MONODESK OS is not affiliated with, sponsored by, or endorsed by Nothing Technology Limited.

MONODESK OS does not utilize, reproduce, or redistribute any proprietary Nothing OS software, source code, logos, trademarks, copyrighted font binaries, or protected interface assets. All artwork, glyphs, dot-matrix icons, and themes in MONODESK OS are original creations released under open-source and Creative Commons licenses.

---

## 2. Upstream Desktop Components

### 2.1 Nebula Desktop Shell Foundation

- **Upstream Repository:** [https://github.com/LilaccFlowerr/Nebula](https://github.com/LilaccFlowerr/Nebula)
- **Author:** LilaccFlowerr
- **Commit:** `9749c30402b4e6712d0222c48b645fa357d0217e` (Imported: 2026-11-15)
- **License:** GNU Affero General Public License v3.0 (AGPL-3.0)
- **Full License Text:** Preserved in `third_party/nebula/LICENSE`
- **Notice:** This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

### 2.2 Material 3 Shapes (M3Shapes)

- **Upstream Repository:** [https://github.com/soramanew/m3shapes](https://github.com/soramanew/m3shapes)
- **Author:** soramanew
- **Commit:** `8a6fe8961749887d677700b6508e0c9249968b7e`
- **License:** Apache License, Version 2.0
- **Full License Text:** Preserved in `third_party/m3shapes/LICENSE`
- **Notice:** Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

---

## 3. Core Operating System & Platform Dependencies

| Software Component | Upstream Maintainer | License | Function in MONODESK OS |
| :--- | :--- | :--- | :--- |
| **Linux Kernel** | Linus Torvalds / Kernel.org | GNU GPL v2 | Core operating system kernel and hardware drivers |
| **Debian GNU/Linux** | Software in the Public Interest, Inc. | DFSG / Open Source | Base package ecosystem and repository infrastructure |
| **Hyprland** | Vaxry / Hyprland Team | BSD 3-Clause | Dynamic tiling Wayland compositor |
| **Quickshell** | Quickshell Team | LGPL v3 / GPL v3 | Reactive Wayland desktop shell framework |
| **Qt 6 Framework** | The Qt Company / KDE Free Qt | LGPL v3 / GPL v3 | UI rendering, QML runtime, and core application logic |
| **Calamares** | Calamares Project | GNU GPL v3 | Live system graphical installer |
| **PipeWire & WirePlumber** | PipeWire Project / Red Hat | MIT / LGPL v2.1 | Unified low-latency audio server |
| **NetworkManager** | GNOME Project / Red Hat | GNU GPL v2 | Network connectivity management daemon |
| **BlueZ** | BlueZ Project | GNU GPL v2 | Bluetooth stack daemon and utilities |
| **Mesa 3D** | Mesa3D Project | MIT License | OpenGL, Vulkan, and Gallium graphics drivers |
| **UFW / nftables** | Canonical Ltd. / Netfilter | GNU GPL v2 / v3 | Inbound network firewall defense |
| **zram-tools** | Jonathan McDowell | GNU GPL v2 | In-memory compressed swap manager |
| **Inter Font Family** | Rasmus Andersson | SIL OFL 1.1 | Primary system UI typography |
| **JetBrains Mono** | JetBrains s.r.o. | SIL OFL 1.1 | Dot-matrix display and terminal typography |
| **Material Symbols** | Google LLC | Apache-2.0 | Action and system icons |

All corresponding source packages, license texts, and upstream copyrights are accessible within the Debian package repository and under `/usr/share/common-licenses/` in the live filesystem.
