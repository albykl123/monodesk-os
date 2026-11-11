# MONODESK OS 1.0 — Universal PC Edition
## Phase 1: Comprehensive Project Audit & Workspace Inspection

**Document Version:** 1.0.0  
**Date:** 2026-11-11  
**Lead Engineer:** Antigravity Autonomous OS Development Agent  
**Distribution Codename:** Monodesk Bookworm (Debian 12 Stable Base)  
**Target Architecture:** AMD64 / x86-64 (Universal PC)

---

### 1. Executive Summary

MONODESK OS is an independent, lightweight, desktop-first Linux operating system engineered for universal x86-64 personal computers (Intel and AMD laptops, desktops, and workstations). The operating system embodies a distinct monochrome minimalist aesthetic inspired by high-contrast industrial design, dot-matrix typography, and high-efficiency desktop productivity, while completely avoiding proprietary assets or trademarks from Nothing OS.

This audit establishes the baseline status of the workspace, evaluates hardware constraints, identifies required upstream components, and provides an end-to-end blueprint for engineering the distribution from source code to a bootable, installable hybrid ISO.

---

### 2. Workspace & Environment Audit

| Parameter | Observed State | Status / Assessment |
| :--- | :--- | :--- |
| **Active Workspace** | `f:\anti` (mapped by IDE) | **Blocker Identified:** Physical drive `F:` not mounted in Windows session; internal storage resides on `C:\`. Process launcher fails when cwd is set to missing `f:\`. |
| **Physical Storage** | `C:\anti` | **Operational:** Available on primary NVMe/SSD. All repository files, source code, configs, tests, and build definitions are staged here. |
| **Primary Dev Machine** | Lenovo IdeaPad Slim 5 | AMD Ryzen 7 5700U (8C/16T), 16 GB DDR4 RAM, 512 GB NVMe SSD. Excellent host for compilation, containerized chroot, and QEMU VM testing. |
| **Low-End Benchmark Target**| Lenovo B590 | Intel Core i3-2348M (Sandy Bridge, 2C/4T @ 2.3 GHz), 4 GB DDR3 RAM, Intel HD Graphics 3000. Serves as minimum viable hardware profile. |
| **Base Operating System** | Debian 12 "Bookworm" (Stable) | Kernel 6.1 LTS, XFCE 4.18, systemd 252, PipeWire 0.3.65, Mesa 22.3+, Calamares 3.2.61, live-build 20230131. |
| **Existing Codebase State** | Clean slate (`docs/`, `scripts/`) | No legacy technical debt or duplicated prototype cruft to remove; clean modular architecture built from ground up. |

---

### 3. Upstream Component & Dependency Architecture

To ensure stability, long-term support, and reproducible builds across global installations, MONODESK OS relies on battle-tested Debian infrastructure:

1. **Package Management & Base**:
   - Upstream Debian `bookworm`, `bookworm-updates`, and `bookworm-security` repositories.
   - Non-free firmware components (`firmware-linux`, `firmware-misc-nonfree`, `firmware-iwlwifi`, `firmware-realtek`, `firmware-atheros`, `intel-microcode`, `amd64-microcode`).
   - Strict GPG signature verification (`debian-archive-keyring`).

2. **Desktop Shell & Window Management**:
   - XFCE 4.18 desktop environment (`xfce4-session`, `xfwm4`, `xfce4-panel`, `xfdesktop4`, `thunar`).
   - GTK3 + PyGObject for custom MONODESK applications and applets.
   - Custom monochrome GTK theme (`Monodesk-Dark` and `Monodesk-Light`).
   - Custom dot-matrix icon suite and scalable SVG iconography.
   - Open-source, legally redistributable typography: *JetBrains Mono*, *Inter*, and *DSEG7/DotMatrix* fallbacks.

3. **Audio & Media**:
   - PipeWire audio server + WirePlumber session manager (`pipewire`, `wireplumber`, `pipewire-pulse`, `pipewire-alsa`). Full low-latency audio support.

4. **Networking**:
   - NetworkManager core daemon + `network-manager-gnome` applet + custom GTK quick-toggle integration.

5. **Display & Session Management**:
   - LightDM display manager with `lightdm-gtk-greeter` themed with monochrome dot-matrix lockscreen.

6. **Installer & Live System**:
   - Debian `live-build` utility to construct SquashFS chroot image and hybrid ISO.
   - `calamares` graphical installer with custom Monodesk branding module, automated partitioning, manual partitioning, LUKS full-disk encryption, and user setup.
   - Dual bootloader support: GRUB2 EFI (`x86_64-efi`) and GRUB2 BIOS (`i386-pc`) via `xorriso`.

---

### 4. Hardware Support Strategy

MONODESK OS maintains a strict "Universal PC" compatibility standard without promising impossible capabilities:
- **CPU Support:** Generic `x86-64-v1` baseline to ensure execution on older CPUs (such as Intel Sandy Bridge Core i3-2348M) while leveraging modern instruction sets (SSE4.2, AVX, AVX2) dynamically.
- **Intel Graphics:** Out-of-the-box DRM/KMS support via kernel drivers (`i915`, `xe`) and Mesa Intel driver (`iris`, `crocus`).
- **AMD Graphics:** Out-of-the-box AMDGPU and Radeon KMS drivers + Mesa RADV/RadeonSI for Vulkan/OpenGL.
- **NVIDIA Graphics:** Standard boot uses open-source Nouveau drivers for universal display output; inclusion of `monodesk-nvidia-installer` tool enables one-click installation of proprietary NVIDIA drivers from Debian non-free repositories.
- **Power & Laptops:** Upower, TLP, ACPI event daemons, and `monodesk-profile-ctl` for dynamic Lite vs. Standard performance profiles.

---

### 5. Identified Gap Analysis & Implementation Roadmap

| Subsystem | Requirement | Implementation Strategy |
| :--- | :--- | :--- |
| **Shell & Dock** | Bottom dock/taskbar with dot-matrix clock, quick toggles, launcher | Custom XFCE panel configuration + Python/GTK MONODESK Shell applets |
| **Control Centre** | Unified volume, brightness, Wi-Fi, Bluetooth, power profiles | `monodesk-control-centre` GTK3 application |
| **System Apps** | Welcome, Settings, Hardware Report, System Monitor, Update Manager | Modular Python 3 / GTK3 native desktop applications |
| **Performance Profiles** | 4GB RAM low-end profile vs 8GB+ standard profile | `monodesk-profile-ctl` + zram-tools configuration |
| **Branding & Assets** | Original logos, monochrome wallpapers, dot-matrix icons | Scalable SVG generator scripts & artwork packaging |
| **Installer** | Live bootable environment to bare-metal installation | Custom Calamares distribution package & configuration |
| **Build Pipeline** | Deterministic ISO generation scripts | Automated `live-build` pipeline with pre-flight checks |
| **Quality Assurance** | Automated testing across unit, integration, and ISO boot | Pytest test suite, shell linter, and QEMU test harness |

---
*Audit completed by Antigravity Autonomous Agent. Proceeding to Implementation Plan.*
