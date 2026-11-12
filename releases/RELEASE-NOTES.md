# MONODESK OS 1.0.1 — Official Release Notes
## Edition: Universal PC Edition (Production Release 1.0.1)

**Release Tag:** `v1.0.1`  
**Release Date:** 2026-11-12  
**Architecture:** x86-64 / AMD64  
**Base Distribution:** Debian 12 "Bookworm" LTS  
**Desktop Environment:** MONODESK Shell (Qt 6 / QML) + XFCE 4.18 Fallback  
**Default Kernel:** Linux 6.1 LTS (`6.1.0-54-amd64`) with Universal Microcode

---

### What Was Fixed in MONODESK OS 1.0.1

MONODESK OS `1.0.1` resolves all remaining blockers identified during `v1.0.0` validation and `v1.0.1-rc1` testing while preserving `v1.0.0` and `v1.0.1-rc1` intact:

#### 1. MONODESK Shell (Qt 6 / QML) + Verified XFCE Fallback
- Packaged missing Bookworm Qt 6 / QML dependencies (`python3-pyqt6.qtquick`, `python3-pyqt6.qtqml`, `qml6-module-qtquick{,-window,-controls,-layouts,-templates}`, `qml6-module-qtqml-models`).
- Added QML module `qmldir` descriptors (`themes/qmldir`, `desktop/{dock,launcher,quick-search,control-centre,notifications,widgets}/qml/qmldir`) and fixed relative theme imports (`../../themes`) so `MonodeskTheme` resolves across every overlay and widget.
- Added `MonodeskIconProvider`, `Qt.WindowStaysOnBottomHint`, single-instance `fcntl` guard, and non-overlapping notification card spacing in `monodesk-shell`.
- Fixed `xfce4-session.xml` (`FailsafeSessionName` + `Count=2` with `xfwm4` and `xfsettingsd`), eliminating XFCE session error dialogs and auto-starting `monodesk-shell` inside `Xorg :0`.
- Verified graceful fallback to `xfce4-panel` + `xfdesktop` (`rc=0`, no crash) when Qt bindings are unavailable.

#### 2. Installed-System Hardening & Live User Lifecycle
- Packaged `user-setup` and clean Unix-LF `/etc/live/config.conf.d/10-monodesk.conf` so live sessions boot as non-root `monodesk` rather than root autologin.
- Added Calamares `shellprocess@cleanup` (`shellprocess-cleanup.conf`) executing before `displaymanager` to delete any `getty@tty1.service.d`, `serial-getty@ttyS0.service.d`, live sudoers (`99-monodesk-live`, `live`), live LightDM autologin configs, and `/etc/live/config.conf.d`, lock `root` (`passwd -l root`), and enforce LightDM GTK greeter on installed systems.
- Verified after fresh reboot with no ISO attached: non-root login (`monodesk`), password-enforced `sudo`, disabled `sudo -n`, locked `root`, and active LightDM greeter without autologin.

#### 3. Preserved Core Features
- Hybrid **UEFI (`x86_64-efi`) + Legacy BIOS (`i386-pc`)** boot support on a single `730.90 MiB` (`766,408,704` bytes) unsplit ISO.
- Automatic hardware detection (`monodesk-hw-detect`) and dynamic **Standard** (`8 GB+`, balanced governor, compositor active, 25% zRAM) vs **Lite** (`4 GB`, conservative governor, compositor off, 50% zRAM) profile switching via `monodesk-profile-ctl`.
- Calamares 3.2.61 graphical installation workflow and Safe Graphics / Hardware Recovery GRUB boot stanza + `monodesk-recovery`.

---

### Hardware Certification Notice
Virtual end-to-end validation (QEMU OVMF UEFI, QEMU SeaBIOS Legacy BIOS, disposable GPT/EFI Calamares installation, post-install reboots, MONODESK Shell Xorg rendering, XFCE fallback, and 35 automated pytest tests) has passed on `1.0.1`. **Physical hardware testing on the Lenovo IdeaPad Slim 5 and Lenovo B590 remains pending.**

---

### Verification & Checksums (`v1.0.1`)
- **ISO File:** `monodesk-os-1.0.1-universal-amd64.iso` (`766,408,704` bytes / `730.90 MiB`)
- **SHA-256:** `3b8ad75a7f3d011d591d30b42efbb48d7edb53a316a642d7ea8465105c219776`
- **Artifacts:** `SHA256SUMS.txt`, `BUILD-MANIFEST.json`, `PACKAGE-MANIFEST.txt`, `FINAL-VALIDATION-REPORT.md`
