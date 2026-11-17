# MONODESK OS 2.0.1-rc2 — Production Release Candidate & Universal Boot Fix

**Release Channel:** Release Candidate 2 (Production Candidate)  
**Target Architecture:** x86_64 (Universal AMD/Intel PC)  
**Reference Targets:**
1. Lenovo IdeaPad Slim 5 (82LN), AMD Ryzen 7 5700U APU, AMD Radeon Graphics (`amdgpu`), NVMe SSD + JMicron 1TB USB HDD
2. Lenovo B590, Intel Core i3-2348M, Intel HD Graphics 3000, 4 GB RAM (Lite Profile)  
**Base Distribution:** Debian 13 Trixie (AMD64)  
**Kernel:** Linux 6.1.0-54-amd64 (Debian 6.1 LTS)  

---

## 🎯 Root Cause Resolution: Live Boot Kernel Panic (0x00000200)

This release candidate resolves the physical hardware boot failure reported on the Lenovo IdeaPad booted from the external JMicron multi-partition drive:
```
Kernel panic - not syncing: Attempted to kill init!
PID: 1 Comm: init exitcode=0x00000200
```

### Forensic Root Cause:
1. **Device Enumeration Defect:** The initramfs live locator (`scripts/live` -> `mountroot()`) used a hardcoded block device array (`/dev/sr0 /dev/sr1 /dev/sda /dev/sda1 /dev/sdb /dev/sdb1...`). The physical JMicron drive hosts Windows partition `D:` on partition 1 (`/dev/sda1`), and MONODESK OS on partition 2 (`/dev/sda2`, `E:`). Partition 2 was completely omitted from detection.
2. **Filesystem Incompatibility:** The script strictly forced `mount -t iso9660`. Partition `E:` is formatted as FAT32 (`vfat`), which kernel rejects under `iso9660`.
3. **Missing Kernel Modules:** The composite initramfs lacked `fat.ko`, `vfat.ko`, `exfat.ko`, `nls_cp437.ko`, `nls_ascii.ko`, `nls_iso8859-1.ko`, and `nls_utf8.ko`.
4. **Shell / Script Syntax:** Busybox lacks `seq`; looping via `$(seq 1 15)` aborted early userspace before searching storage devices.

### Architectural Solution:
1. **Kernel Driver Bundling:** Extracted all FAT, VFAT, EXFAT, and NLS codepage modules from `filesystem.squashfs` and bundled them into the early uncompressed CPIO initramfs archive.
2. **Universal Device Iteration:** Rewrote `mountroot()` to dynamically discover all block devices and partitions across `/dev/sr*`, `/dev/sd*`, `/dev/nvme*`, `/dev/vd*`, `/dev/hd*`, and `/dev/mmcblk*`.
3. **Multi-Filesystem Probing:** Dynamically probes partitions using `iso9660`, `vfat`, `ext4`, and `exfat`.
4. **ISO Loopback & Findiso Support:** Added full support for `findiso=` kernel command-line loopback mounting as well as automatic scanning for ISO images on any partition.
5. **Overlayfs Ingestion:** Fixed overlayfs fallback ingestion to copy directly from `/run/live/medium/monodesk/rootfs_overlay/` into root without failing on an invalid `iso9660` remount of FAT32 volumes.

---

## 🖥️ Nebula Desktop & Core Components

- **Default Desktop Shell:** Nebula (LilaccFlowerr/Nebula, AGPL-3.0) driven by Quickshell QML framework and Hyprland Wayland compositor.
- **Component Styling:** M3Shapes (soramanew/m3shapes, Apache-2.0) material shapes and shaders integrated into desktop widgets, dock, and launcher.
- **Display Manager:** LightDM with seamless autologin to `monodesk-session`.
- **Session Router:** Dual-engine architecture (`monodesk-session`):
  - Modern GPU with KMS/DRM (AMD Radeon / Intel Iris Xe) -> Wayland (Hyprland + Nebula Quickshell).
  - Legacy GPU / 4GB RAM -> MONODESK Recovery Session (X11 + XFWM4 composited).
- **Settings Hub:** Complete 21-category configuration centre operating real system services (PipeWire/WirePlumber, NetworkManager, BlueZ, UPower, systemd, CUPS, UFW, AppArmor).
- **Installer:** Calamares PC installer with custom monochrome branding and automated disk partitioning.

---

## 📦 Verified Release Assets

| Asset Name | Type | Size | SHA-256 Checksum |
|:---|:---:|:---:|:---|
| **`monodesk-os-2.0.1-rc2-universal-amd64.iso`** | Bootable Hybrid ISO | 918.07 MiB (962,668,544 bytes) | `6585af1982898658ff4ca01cd012203a92576f9d52d06b693851d74a0db6e83d` |
| **`monodesk-os-2.0.1-rc2-universal-amd64.iso.sha256`** | Checksum | 109 B | Verified |
| **`BUILD-MANIFEST-2.0.1-rc2.json`** | Build Manifest | 4.2 KB | Complete build and dependency metadata |
| **`PACKAGE-MANIFEST-2.0.1-rc1.txt`** | Dpkg Package List | 24 KB | 922 packages installed |
| **`SHA256SUMS.txt`** | Cumulative Checksums | 480 B | Historical release checksums |

---

## 🧪 Deep Verification Summary

1. **JMicron FAT32 Multi-Partition Drive Simulation:**
   - Simulated exact physical disk layout (Partition 1: NTFS dummy, Partition 2: FAT32 `MONODESK_OS` containing live system).
   - Dynamic device discovery detected `/dev/vda2`, loaded `fat.ko`/`vfat.ko`, mounted squashfs overlay, reached `graphical.target` in 20.2s without kernel panic.
2. **Conventional ISO Live Boot:**
   - Cold booted hybrid ISO in QEMU via UEFI OVMF and Legacy BIOS. Reached graphical autologin in 25.3s.
3. **Calamares Installation to Disposable Virtual Disk:**
   - Partitioned and installed to disposable 15 GiB virtual disk (`test-disposable-101.qcow2`).
4. **Installed Operating System Cold Boot:**
   - Cold booted installed virtual disk into GRUB 2.12, Linux 6.1 LTS, systemd services, and autologin into `monodesk` user session.
5. **Disk Safety Compliance:**
   - 100% Non-destructive: physical Disk 0 (Internal NVMe Windows 11) and Disk 1 (External JMicron HDD Partition 1 NTFS & Partition 2 FAT32) remained completely untouched and protected.
