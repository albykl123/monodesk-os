# MONODESK OS 1.0 — Universal PC Edition
> **A complete, independently branded, lightweight, desktop-first Linux operating system for universal Intel & AMD x86-64 personal computers.**

[![Base](https://img.shields.io/badge/Base-Debian%2012%20(Bookworm)-D70A53.svg)](https://www.debian.org)
[![Architecture](https://img.shields.io/badge/Architecture-x86--64%20%2F%20AMD64-blue.svg)](https://en.wikipedia.org/wiki/X86-64)
[![Desktop](https://img.shields.io/badge/Desktop-XFCE%204.18%20%2B%20MONODESK%20Shell-white.svg)](https://xfce.org)
[![License](https://img.shields.io/badge/License-GPLv3%20%2F%20MIT-green.svg)](LICENSE)
[![Zero Telemetry](https://img.shields.io/badge/Privacy-100%25%20Zero%20Telemetry-blueviolet.svg)](docs/SECURITY-PRIVACY.md)

---

## 1. Overview

MONODESK OS is an independent Linux operating system engineered for personal computers (laptops, desktops, workstations, and virtual machines). Inspired by minimalist monochrome industrial design, high-contrast aesthetics, and dot-matrix typography, MONODESK OS delivers a distraction-free, high-efficiency desktop experience paired with the enterprise stability of Debian 12 (Bookworm).

MONODESK OS is not an imitation mobile OS or an Android launcher; it is designed from the ground up for mouse, keyboard, touchpad, multi-monitor setups, and high-performance computing.

---

## 2. Universal Hardware Architecture

MONODESK OS operates on a **Universal x86-64 baseline**:
- **Processors:** Intel Core (Nehalem through modern Raptor Lake/Meteor Lake), Intel Celeron/Pentium (64-bit), AMD Ryzen 1000 through 7000, Athlon 64-bit, and AMD EPYC.
- **Microcode:** Upstream `intel-microcode` and `amd64-microcode` embedded in initramfs.
- **Graphics Acceleration:** Out-of-the-box DRM/KMS drivers for Intel HD/Iris and AMD Radeon/Vega/RDNA via Mesa OpenGL/Vulkan; open-source Nouveau for NVIDIA cards, with an automated one-click proprietary driver installer (`monodesk-nvidia-installer`).
- **Audio:** Modern low-latency PipeWire sound server with WirePlumber session management.
- **Network & Peripherals:** Upstream Linux firmware packages for Intel Wi-Fi, Realtek, Qualcomm Atheros, Broadcom, Bluetooth, USB, and ACPI power management.

---

## 3. Dual Performance Profiles

| Profile | Hardware Target | Characteristics |
| :--- | :--- | :--- |
| **MONODESK Lite** | 4 GB RAM, older dual-core CPUs (e.g., Lenovo B590), SATA HDD/SSD | Minimal startup apps, compositor shadows disabled, aggressive zram compression, conservative power governor. Target idle RAM: ~700–900 MB. |
| **MONODESK Standard** | 8 GB+ RAM, modern quad/octa-core CPUs (e.g., Lenovo IdeaPad Slim 5), NVMe | Full XFWM4 compositor effects, window snapping, desktop telemetry widget, balanced power profile. |

*Switch profiles on the fly via `monodesk-profile-ctl set [lite|standard]`.*

---

## 4. Native Desktop Application Suite

All system utilities are native Python 3 / GTK 3 applications adhering to the monochrome dot-matrix design system:
- **`monodesk-welcome`**: First-boot onboarding assistant (profile selection, hardware check, network tour).
- **`monodesk-control-centre`**: Unified quick-settings panel (Wi-Fi, Bluetooth, Audio, Brightness, Power profiles, Theme toggle).
- **`monodesk-hardware-report`**: Diagnostic hardware inspector with automatic privacy redaction of MAC addresses, serial numbers, and UUIDs.
- **`monodesk-system-monitor`**: Real-time per-core CPU, memory, swap/zram, and process manager.
- **`monodesk-settings`**: Centralized configuration hub.
- **`monodesk-update-manager`**: Safe APT package updater with security notifications and essential package removal prevention.
- **`monodesk-software-manager`**: Curated graphical package manager for official Debian repositories.
- **`monodesk-nvidia-installer`**: Automated DKMS proprietary driver installer for NVIDIA GPUs.

---

## 5. Repository Structure

```
├── applications/               # Native Python 3 / GTK 3 desktop applications
│   ├── control-centre/         # Quick settings & hardware switches
│   ├── hardware-report/        # Diagnostic hardware scanner with privacy redaction
│   ├── nvidia-installer/       # Proprietary NVIDIA driver assistant
│   ├── settings/               # System configuration hub
│   ├── software-manager/       # Debian package manager GUI
│   ├── system-monitor/         # Task manager & resource monitor
│   ├── update-manager/         # Safe APT updater
│   └── welcome/                # First-boot onboarding wizard
├── branding/                   # Original assets, vector logos, dot-matrix wallpapers
├── build/                      # Debian live-build definitions & chroot overlays
│   └── live-build/             # auto/config, package lists, chroot hooks, Calamares
├── desktop/                    # Desktop shell, panel configuration, widgets, GTK themes
├── docs/                       # Project documentation, audit, compatibility matrix
├── scripts/                    # Build pipeline, linter, ISO test harness, manifest tools
├── system/                     # Security policies (UFW), power profiles, terminal configs
├── tests/                      # Automated unit, hardware, and performance test suites
├── LICENSE                     # GNU General Public License v3
└── README.md                   # Project overview & quick start
```

---

## 6. Building the Hybrid ISO

### Prerequisites
Run on a Debian 12 (Bookworm) or compatible Linux build host with root privileges:
```bash
sudo bash scripts/install-build-deps.sh
```

### Source Validation & Build
```bash
# 1. Validate syntax and desktop entries
bash scripts/check-source.sh

# 2. Build the live filesystem and bootable hybrid ISO
sudo bash scripts/build-iso.sh

# 3. Verify the generated ISO checksum and El Torito boot headers
bash scripts/verify-iso.sh releases/monodesk-os-1.0.0-universal-amd64.iso

# 4. Test the ISO in a disposable QEMU virtual machine
bash scripts/test-iso.sh releases/monodesk-os-1.0.0-universal-amd64.iso 4096 uefi
```

---

## 7. Documentation Index

- [Project Audit & Workspace Status](docs/PROJECT-AUDIT.md)
- [Master Implementation Plan](docs/IMPLEMENTATION-PLAN.md)
- [Requirement Traceability Matrix](docs/REQUIREMENT-TRACEABILITY.md)
- [Build Status & Engineering Log](docs/BUILD-STATUS.md)
- [Hardware Compatibility Matrix](docs/HARDWARE-COMPATIBILITY.md)
- [Installation & Quick Start Guide](docs/INSTALLATION.md)
- [Security Hardening & Privacy Policy](docs/SECURITY-PRIVACY.md)
- [Troubleshooting & Recovery](docs/TROUBLESHOOTING.md)
- [Official Release Notes](docs/RELEASE-NOTES.md)
- [Software License Inventory](docs/LICENSES.md)

---
*Developed autonomously by Antigravity Operating System Engineering Agent.*
