# MONODESK OS 1.0 — Architecture Decision Log (ADL)

---

### Decision 1: Custom Desktop Shell in Qt 6 / QML vs. Desktop Reskinning
- **Date:** 2026-11-11
- **Status:** **APPROVED & IMPLEMENTED**
- **Context:** The project requires a distinctive, recognizable monochrome computing experience with dot-matrix typography, fluid animations, modular widgets, and functional dock/control panels. Default XFCE panel theming is limited by GTK3 CSS constraints and cannot deliver the responsive, unified feel required by the specification.
- **Decision:** Engineer a dedicated **MONODESK Shell** using **Qt 6 / QML** and Python. Qt Quick provides declarative, GPU-accelerated scenegraph rendering, seamless animation control, and modular component reusability.
- **Consequences:** Provides a completely custom, premium visual identity while leaving underlying X11 window management to XFWM4. Requires Qt 6 runtime libraries (`qml6-module-qtquick`, `python3-pyqt6`) in the live image package list.

---

### Decision 2: Retaining XFWM4 as Initial Window Manager Foundation
- **Date:** 2026-11-11
- **Status:** **APPROVED & IMPLEMENTED**
- **Context:** Writing a custom Wayland compositor from scratch for an initial 1.0 release introduces extreme hardware compatibility risks, driver regressions on older GPUs (such as Sandy Bridge Intel HD 3000 on Lenovo B590), and multi-monitor instability.
- **Decision:** Retain **XFWM4** as the underlying X11 window manager. The MONODESK Shell owns the desktop surface, dock, launcher, widgets, and control centre, while XFWM4 manages window borders, snapping, and Alt+Tab cycling.
- **Consequences:** Maximizes hardware compatibility across both legacy and modern PCs. Ensures a rock-solid, crash-resilient desktop.

---

### Decision 3: Pinned Debian 12 (Bookworm) Stable Base
- **Date:** 2026-11-11
- **Status:** **APPROVED & IMPLEMENTED**
- **Context:** An independent distribution intended for global distribution requires long-term package stability, rigorous security updates, and predictable ABI compatibility.
- **Decision:** Pin the distribution to **Debian 12 (Bookworm)** AMD64, utilizing official Debian security channels and non-free firmware repositories.
- **Consequences:** Guaranteed 5-year security maintenance, predictable dependency resolution, and deterministic live-build reproducibility.

---

### Decision 4: PipeWire & WirePlumber as Primary Audio Stack
- **Date:** 2026-11-11
- **Status:** **APPROVED & IMPLEMENTED**
- **Context:** Linux audio has historically suffered from latency and device contention between ALSA, PulseAudio, and JACK.
- **Decision:** Standardize on **PipeWire** with **WirePlumber**.
- **Consequences:** Low-latency audio routing, seamless Bluetooth codec switching (LDAC, AAC), and reliable multi-channel device management.

---

### Decision 5: Calamares Graphical Installer with LUKS2
- **Date:** 2026-11-11
- **Status:** **APPROVED & IMPLEMENTED**
- **Context:** The installation process must be accessible to students and general users while supporting advanced partitioning and encryption for technical professionals.
- **Decision:** Adopt **Calamares 3.2+** with custom MONODESK branding modules. Support automatic partitioning (erase disk with swap/zram), install alongside existing OS, manual partitioning, and LUKS2 encryption.
- **Consequences:** Modern, intuitive installer workflow that functions reliably in live desktop sessions.

---

### Decision 6: Local AI Assistant Strictly Opt-In & Disabled by Default
- **Date:** 2026-11-11
- **Status:** **APPROVED & IMPLEMENTED**
- **Context:** Artificial intelligence assistants often introduce heavy background resource drain, mandatory cloud tracking, and privacy concerns.
- **Decision:** Make the **MONODESK Local AI Assistant** completely optional, disabled by default, and 100% on-device (interfacing with local llama.cpp / Ollama endpoints). Zero cloud API keys, zero network telemetry.
- **Consequences:** MONODESK OS functions flawlessly without internet access or AI dependencies. Users with capable hardware can optionally enable local inference.
