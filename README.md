# MONODESK OS 1.0 — Universal PC Edition
> **A complete, independent, publicly distributable PC operating system and modern Windows alternative with an original Nothing-inspired monochrome design language.**

[![Base](https://img.shields.io/badge/Base-Debian%2012%20(Bookworm)-D70A53.svg)](https://www.debian.org)
[![Architecture](https://img.shields.io/badge/Architecture-x86--64%20%2F%20AMD64-blue.svg)](https://en.wikipedia.org/wiki/X86-64)
[![Desktop](https://img.shields.io/badge/Desktop%20Shell-MONODESK%20Shell%20(Qt%206%20%2F%20QML)-black.svg)](desktop/shell/)
[![License](https://img.shields.io/badge/License-GPLv3%20%2F%20MIT-green.svg)](LICENSE)
[![Zero Telemetry](https://img.shields.io/badge/Privacy-100%25%20Zero%20Telemetry-blueviolet.svg)](docs/PRIVACY.md)

---

## 1. Vision: A Genuine Windows Alternative

MONODESK OS is engineered as an everyday personal computer operating system that people can install on their laptop or desktop, switch on every morning, and use for work, education, programming, gaming, multimedia entertainment, file management, and system administration.

It bridges three core pillars:
1. **The Monochrome Computing Experience:** Minimalist high-contrast monochrome design, distinctive dot-matrix visual language, functional widgets, and subtle red accents (`#E63946`).
2. **Windows-Class Completeness:** A complete first-party ecosystem matching every major Windows capability without proprietary bloat or forced cloud accounts.
3. **Enterprise Linux Stability:** Built upon a pinned Debian 12 (Bookworm) stable foundation, the Linux LTS kernel, PipeWire audio, NetworkManager, and universal x86-64 hardware enablement.

---

## 2. Windows Capabilities vs. MONODESK OS

| Windows 10/11 Capability | MONODESK OS Equivalent | Technical Implementation |
| :--- | :--- | :--- |
| **Windows Desktop & DWM** | **MONODESK Desktop Shell** | Custom Qt 6 / QML modular desktop surface + XFWM4 window management |
| **Start Menu** | **MONODESK Launcher** | Fullscreen / popup categorized launcher with instant keyboard search (`Super`) |
| **Taskbar** | **MONODESK Dock** | Bottom centered dock with pinned & running indicators, context menus |
| **File Explorer** | **MONODESK Files** | First-party integrated file manager with archive, network & drive support |
| **Windows Settings** | **MONODESK Settings** | Centralized configuration hub for displays, sound, network, themes, power |
| **Microsoft Store** | **MONODESK Software Store** | Curated software store for verified Debian packages & Flatpak apps |
| **Windows Update** | **MONODESK Updater** | Signed APT updater with essential package protection and reboot detection |
| **Task Manager** | **MONODESK System Monitor** | Real-time per-core CPU, RAM, zRAM, and per-process kill/priority control |
| **Device Manager** | **MONODESK Device Manager** | Tree-based PCI/USB controller discovery and kernel module inspection |
| **Disk Management** | **MONODESK Disk Manager** | Storage discovery, partition inspection, mounting, and SMART health checks |
| **Control Panel** | **MONODESK Control Centre** | Quick settings for Wi-Fi, Bluetooth, Audio, Brightness, Power profiles |
| **User Accounts** | **MONODESK Account Manager** | Local users, password management, administrator privileges (`sudo`), sessions |
| **Windows Search (Spotlight)** | **MONODESK Quick Search** | Instant universal spotlight search (`Alt + Space`) across apps and settings |
| **Windows Defender** | **MONODESK Security Centre** | UFW network firewall, AppArmor sandboxing, signed GPG package verification |
| **Windows Recovery** | **MONODESK Recovery Centre** | Package database repair (`dpkg --configure -a`), EFI boot diagnostics, chroot |
| **Backup and Restore** | **MONODESK Backup Manager** | Scheduled rsync snapshots, integrity hashing, restore preview with confirmation |
| **Virtual Desktops** | **MONODESK Smart Workspace** | Multi-desktop management, window snapping and tiling (`Super + Arrows`) |
| **Power & Battery** | **MONODESK Performance Manager** | Dual profiles (**Lite** for 4GB RAM vs. **Standard** for 8GB+ RAM) via `monodesk-profile-ctl` |
| **Windows Compatibility** | **MONODESK Compatibility Centre**| Wine & Proton runtime manager, prefix manager, compatibility database |
| **Gaming Platform** | **MONODESK Gaming Centre** | Steam, Proton, Lutris, Heroic, controller detection, Vulkan 3D diagnostics |
| **Developer Tools** | **MONODESK Developer Centre** | One-click toolchains for Git, Python, C/C++, Rust, Node.js, and containers |
| **Local AI (Copilot Alt.)** | **MONODESK Local AI** | 100% on-device private assistant (disabled by default, 0 cloud dependency) |

---

## 3. Four-Layer Operating System Architecture

```
Layer 1 — MONODESK Experience
  MONODESK Shell (Qt 6 / QML) • Dock • Launcher • Quick Search • Widgets • Notifications • Adaptive Themes

Layer 2 — MONODESK Applications
  Welcome • Settings • Files • Store • Updater • Hardware Centre • Device Manager • Disk Manager •
  Network Centre • Bluetooth Centre • Print Centre • System Monitor • Privacy • Backup • Recovery •
  Accessibility • Clipboard • Workspace • Compatibility Centre • Gaming Centre • Developer Centre • Local AI

Layer 3 — MONODESK System Platform
  D-Bus Session Services (org.monodesk.Shell) • PolicyKit Privileged Helpers • monodesk-profile-ctl •
  Diagnostics & Privacy Redaction Engine • Power Management Daemons

Layer 4 — Linux Foundation
  Debian 12 (Bookworm) Pinned Stable • Linux 6.1 LTS Kernel with Universal Microcode (Intel & AMD) •
  XFWM4 Window Manager • PipeWire Audio • NetworkManager • Mesa 3D • UFW & AppArmor Security • Calamares
```

---

## 4. Hardware Support & Benchmarks

MONODESK OS maintains a **Universal x86-64 baseline**:
- **Processors:** Intel Core (Nehalem through modern Raptor Lake/Meteor Lake), Celeron, Pentium (64-bit); AMD Ryzen 1000 through 7000 series, Athlon 64-bit, EPYC.
- **Reference Targets:**
  - **Lenovo B590 (Low-End Benchmark):** Intel Core i3-2348M, 4 GB RAM, Intel HD 3000. Operates on **MONODESK Lite** (~700–900 MB idle RAM with zRAM).
  - **Lenovo IdeaPad Slim 5 (Modern Reference):** AMD Ryzen 7 5700U, 16 GB RAM, NVMe SSD. Operates on **MONODESK Standard** (full compositing & widgets).
- **Graphics Acceleration:** Out-of-the-box Mesa DRM/KMS drivers for Intel and AMD GPUs; open-source Nouveau for NVIDIA cards, with an automated proprietary driver assistant (`monodesk-nvidia-installer`).

---

## 5. Building and Testing the Hybrid ISO

Run inside a Debian 12 (Bookworm) build environment with root privileges:
```bash
# 1. Install build prerequisites
sudo bash scripts/install-build-deps.sh

# 2. Execute automated live-build pipeline
sudo bash scripts/build-iso.sh

# 3. Verify SHA-256 and El Torito boot sectors
bash scripts/verify-iso.sh releases/monodesk-os-1.0.0-universal-amd64.iso

# 4. Test boot and live installation in disposable QEMU virtual machine
bash scripts/test-iso.sh releases/monodesk-os-1.0.0-universal-amd64.iso 4096 uefi
```

---

## 6. Comprehensive Documentation Index

- [Final Architecture Specification](docs/FINAL-ARCHITECTURE.md)
- [Architecture Decision Log](docs/DECISION-LOG.md)
- [Project Audit & Baseline](docs/PROJECT-AUDIT.md)
- [Master Implementation Plan](docs/IMPLEMENTATION-PLAN.md)
- [Requirement Traceability Matrix](docs/REQUIREMENT-TRACEABILITY.md)
- [Build Status & Engineering Log](docs/BUILD-STATUS.md)
- [Test Status & Evidence](docs/TEST-STATUS.md)
- [Known Limitations & Scope Boundaries](docs/KNOWN-LIMITATIONS.md)
- [Hardware Compatibility Matrix](docs/HARDWARE-COMPATIBILITY.md)
- [Windows Application Compatibility Database](docs/WINDOWS-APP-COMPATIBILITY.md)
- [Gaming & Multimedia Compatibility Matrix](docs/GAMING-COMPATIBILITY.md)
- [Official User & Administrator Guide](docs/USER-GUIDE.md)
- [Comprehensive Installation Guide](docs/INSTALLATION-GUIDE.md)
- [Security Specification & Policy](docs/SECURITY.md)
- [Privacy Policy & Zero-Telemetry Commitment](docs/PRIVACY.md)
- [Public Release & Maintenance Process](docs/RELEASE-PROCESS.md)
- [Official Release Notes](docs/RELEASE-NOTES.md)
- [Third-Party Software Licenses & Attributions](docs/THIRD-PARTY-LICENSES.md)

---
*Authored autonomously by Antigravity Operating System Engineering Team.*
