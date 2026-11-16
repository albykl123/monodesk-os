# MONODESK OS 2.0 — Universal PC Edition
**Complete Debian 13 Trixie Universal AMD64 Operating System**

---

### Overview
MONODESK OS 2.0 is a genuine, installable Debian 13 (Trixie) Linux distribution featuring a custom Material 3 Wayland desktop environment (Hyprland + Quickshell), dynamic performance profiles (Standard & Lite), dual-engine session routing, and an X11 recovery environment.

### Specifications
- **Base Distribution:** Debian GNU/Linux 13 (Trixie) AMD64
- **Kernel:** Linux 6.12.117+deb13-amd64
- **Primary Desktop:** Hyprland + Quickshell (Wayland) with Material 3 Shapes & Nebula UI
- **Recovery Desktop:** X11 + XFWM4 (LightDM)
- **Installer:** Calamares 3.3 Graphical System Installer
- **Profiles:** Standard (>=6 GB RAM) and Lite (<6 GB RAM) with automatic zram and compositor scaling
- **Audio Stack:** PipeWire 1.2 + WirePlumber Multimedia Session Manager
- **Networking:** NetworkManager with Wi-Fi & Ethernet management

### Release Artifacts & Verification
- **ISO Image:** `monodesk-os-2.0.0-universal-amd64.iso` (1,190,991,872 bytes / 1.11 GiB)
- **SHA-256 Checksum:** `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2`
- **Volume ID:** `MONODESK_2_0_AMD64`
- **Bootloader:** Hybrid El Torito (UEFI 64-bit + SeaBIOS MBR)

### Validated Hardware Benchmarks
- **Lenovo IdeaPad Slim 5 (AMD Ryzen 7 5700U / 16 GB RAM):** Standard Profile, Wayland session with full animations & blur.
- **Lenovo B590 (Intel Core i3-2348M / Intel HD 3000 / 4 GB RAM):** Lite Profile, X11 Recovery session, 50% zram.

### Installation Instructions
Flash the ISO to a USB flash drive using **Rufus** (in DD Image Mode) on Windows or `dd if=monodesk-os-2.0.0-universal-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync` on Linux. Boot via UEFI or Legacy BIOS and double-click "Install MONODESK OS" on the live desktop.
