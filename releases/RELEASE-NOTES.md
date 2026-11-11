# MONODESK OS 1.0 — Official Release Notes
## Edition: Universal PC Edition (Release 1.0.0)

**Release Date:** 2026-11-11  
**Architecture:** x86-64 / AMD64  
**Base Distribution:** Debian 12 "Bookworm" LTS  
**Desktop Environment:** XFCE 4.18 with MONODESK Shell  
**Default Kernel:** Linux 6.1 LTS with Universal Microcode

---

### Highlights of MONODESK OS 1.0

The MONODESK Project is proud to announce the initial production release of **MONODESK OS 1.0 — Universal PC Edition**. Engineered from the ground up as an independent, lightweight, desktop-first Linux operating system, MONODESK OS delivers a cohesive monochrome dot-matrix aesthetic combined with rock-solid Debian enterprise stability.

#### 1. Universal PC Hardware Support
- Dual-family CPU support across Intel (Nehalem, Sandy Bridge through modern Raptor Lake/Meteor Lake) and AMD (Ryzen 1000 through 7000, Athlon 64, EPYC).
- Microcode updates embedded directly into the initramfs for Intel and AMD CPUs.
- Out-of-the-box hardware acceleration for Intel HD/UHD/Iris graphics and AMD Radeon/Vega/RDNA GPUs via Mesa and Linux DRM.
- Dedicated `monodesk-nvidia-installer` utility for one-click setup of proprietary NVIDIA drivers with DKMS.

#### 2. Dual Performance Profiles
- **MONODESK Lite:** Engineered for 4 GB RAM systems (such as the Lenovo B590 benchmark target), older dual-core processors, and SATA HDD/SSD hardware. Disables heavy desktop compositing, stops indexing daemons, and engages high-efficiency zram memory compression, targeting an idle footprint of ~700–900 MB RAM.
- **MONODESK Standard:** Full desktop compositing, window shadows, and desktop telemetry widget for modern PCs with 8 GB RAM or more (such as the Lenovo IdeaPad Slim 5).
- Dynamically toggleable via `monodesk-profile-ctl` without reinstalling.

#### 3. Custom Native Desktop Suite (Python 3 / GTK 3)
- **MONODESK Shell & Taskbar:** Polished bottom dock featuring an integrated dot-matrix clock, Whisker menu, PipeWire volume control, NetworkManager integration, and battery telemetry.
- **MONODESK Welcome:** First-boot onboarding assistant guiding users through performance profile selection, hardware diagnostics, and network configuration.
- **MONODESK Control Centre:** Unified quick-settings panel for Wi-Fi, Bluetooth, audio outputs, display brightness, power profiles, and theme toggling.
- **MONODESK Hardware Report:** Comprehensive diagnostic inspection tool with automatic privacy scrubbing of MAC addresses, device serials, and disk UUIDs.
- **MONODESK System Monitor:** Real-time resource inspector for CPU cores, RAM, zRAM, and process tree.
- **MONODESK Update Manager & Software Manager:** Safe package management preventing accidental removal of critical core packages.

#### 4. Calamares Graphical Installation Pipeline
- Bootable live desktop with one-click installation to internal NVMe/SATA drives.
- Automated disk partitioning, dual-boot alongside existing Windows installations, and manual partitioning.
- Optional full-disk LUKS2 encryption.
- Seamless dual-mode bootloader installation for modern UEFI (x86_64-efi) and legacy BIOS (i386-pc) systems.

#### 5. Zero-Telemetry & Hardened Security
- 100% Zero telemetry, zero analytics tracking, and no external phoning home.
- Default inbound DROP firewall policy powered by UFW.
- Verified cryptographic signatures for all Debian repository packages.

---

### Verification & Checksums

- **Target ISO:** `monodesk-os-1.0.0-universal-amd64.iso`
- **Checksum File:** `releases/monodesk-os-1.0.0-universal-amd64.iso.sha256`
- **Build Manifest:** `releases/BUILD-MANIFEST.txt`
- **Package Manifest:** `releases/PACKAGE-MANIFEST.txt`
