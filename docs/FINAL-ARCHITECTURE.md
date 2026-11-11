# MONODESK OS 1.0 — Final Product Architecture Specification
## The Monochrome Computing Experience

**Document Version:** 1.0.0  
**Classification:** Official Product Architecture Baseline  
**Release:** 1.0.0 (Universal PC Edition)  
**Target Architecture:** AMD64 / x86-64  
**Base Distribution:** Debian 12 (Bookworm) Stable

---

### 1. Architectural Philosophy

MONODESK OS is engineered as an integrated, desktop-first personal computer operating system. It achieves a unique, cohesive monochrome computing experience inspired by high-contrast industrial minimalism and dot-matrix visual language, without duplicating or infringing upon proprietary Nothing OS intellectual property.

The system is structured into four distinct, decoupled engineering layers:

```
+-------------------------------------------------------------------------------+
|                       LAYER 1: MONODESK EXPERIENCE                            |
|  MONODESK Shell (Qt 6 / QML) • Dock • Launcher • Quick Search (Alt+Space)     |
|  Control Centre • Notification Centre • Dot-Matrix Telemetry Widgets         |
+-------------------------------------------------------------------------------+
|                       LAYER 2: MONODESK APPLICATIONS                          |
|  Welcome Onboarding • Central Settings • Software Store • Safe Updater        |
|  Hardware Centre • System Monitor • Privacy Dashboard • Backup Manager        |
|  Recovery Centre • Smart Workspace • Performance Profiles • Optional Local AI |
+-------------------------------------------------------------------------------+
|                       LAYER 3: MONODESK SYSTEM PLATFORM                       |
|  D-Bus Session Services (org.monodesk.Shell) • PolicyKit Helpers              |
|  monodesk-profile-ctl (Lite vs Standard) • Hardware Event Integration        |
|  System Diagnostics & Redaction Engine • Power Management Daemons             |
+-------------------------------------------------------------------------------+
|                       LAYER 4: LINUX FOUNDATION                               |
|  Debian 12 Bookworm Pinned Stable • Linux 6.1 LTS Kernel with Universal Microcode |
|  XFWM4 Window Manager (Compositing/Snapping) • PipeWire Audio • NetworkManager|
|  Mesa 3D (OpenGL/Vulkan) • systemd Init • APT/dpkg • UFW & AppArmor Security  |
+-------------------------------------------------------------------------------+
```

---

### 2. Component Ownership & Boundary Model

A critical engineering principle of MONODESK OS is **strict component ownership**:
1. **Desktop Surface, Dock, Launcher, Quick Search, Control Centre, and Widgets:**
   - Exclusively owned by `MONODESK Shell` (built with Qt 6 / QML).
   - Redundant default panels and notification applets from the base desktop are disabled during session configuration to prevent duplicate UI elements.
2. **Window Management, Snapping, and Compositing:**
   - Handled by `XFWM4` via X11. XFWM4 provides lightweight, reliable, hardware-accelerated window snapping, Alt+Tab previews, and border rendering.
3. **Session Coordination & User Daemons:**
   - Coordinated via `systemd --user` (`services/monodesk-shell.service`) with automatic recovery on failure. If the shell crashes, `systemd` restarts it within 2 seconds without terminating running user applications.
4. **Privilege Boundaries:**
   - No graphical application runs as `root`. Privileged actions (package installation, firewall reload, driver installation) are strictly mediated through PolicyKit (`pkexec`) and narrowly scoped helper scripts.

---

### 3. Subsystem Architecture

#### 3.1 Display & Shell Subsystem
- **Engine:** Qt 6 / QML with Python backend bridge (`desktop/shell/monodesk_shell.py`).
- **Rendering:** Qt Quick scenegraph with OpenGL hardware acceleration via Mesa.
- **Design Tokens:** Defined centrally in `themes/design-tokens.json` and consumed through `themes/MonodeskTheme.qml`.
- **Adaptive Modes:** Dark mode (`#0A0A0C` void black surface), Light mode (`#F6F6F8` soft white surface), and automated scheduled solar switching.

#### 3.2 Audio & Multimedia Subsystem
- **Core Server:** PipeWire 0.3+ with WirePlumber session manager.
- **Routing:** Replaces legacy PulseAudio and ALSA while maintaining backwards-compatible emulation libraries (`pipewire-pulse`, `pipewire-alsa`).
- **Control:** The Control Centre and taskbar interact with PipeWire via standard D-Bus and `pactl` interfaces.

#### 3.3 Hardware & Power Profiles Subsystem
- **Dynamic Profiles:**
  - **MONODESK Lite:** Configured for 4 GB RAM systems (e.g. Lenovo B590). Disables window compositing shadows, engages aggressive zRAM compression (zstd, 50% RAM), and sets power-saver governor.
  - **MONODESK Standard:** Configured for 8 GB+ RAM systems (e.g. Lenovo IdeaPad Slim 5). Enables full compositing, window snapping, desktop widgets, and balanced power governor.
- **Driver Model:**
  - Intel: Kernel `i915` / `xe` + Mesa Iris/Crocus.
  - AMD: Kernel `amdgpu` + Mesa RADV/RadeonSI.
  - NVIDIA: Nouveau open-source driver out-of-the-box; proprietary DKMS driver installed via `monodesk-nvidia-installer`.

#### 3.4 Software Management & Updater Subsystem
- **Engine:** Debian APT and PackageKit (`applications/store/` and `applications/updater/`).
- **Safeguards:** Cryptographic GPG signature verification is enforced. Essential packages (`systemd`, `linux-image`, `grub`, `libc6`, `xfwm4`) cannot be removed by user actions.
- **Update Verification:** Categorizes security patches vs regular updates, provides download progress, and detects kernel reboot requirements.

#### 3.5 Privacy & Security Subsystem
- **Telemetry:** 100% Zero Telemetry. No analytics, tracking beacons, or background remote pings.
- **Firewall:** UFW active by default with `INPUT DROP` policy.
- **Diagnostic Redaction:** `monodesk-hardware-centre` automatically scrubs MAC addresses, serial numbers, and storage UUIDs before displaying or exporting reports.

---
*Authored by Antigravity Operating System Engineering Team.*
