# MONODESK OS 2.0 — Forensic System Audit & Hardware Validation Plan
**Date:** 16 November 2026  
**Host Machine:** Lenovo 82LN (Lenovo IdeaPad 5 15ALC05)  
**Document Reference:** `AUDIT-DEBIAN-VERSION-HARDWARE-2026-11-16`  
**Compliance Standard:** Gravitas Invariant 6 (*Report what actually happened; mark uncertain/unverified claims explicitly*)  

---

## 1. Debian Version Audit: Resolving the Version Mismatch

### 1.1 Direct Inspection of the Root Filesystem (`filesystem.squashfs`)
To resolve the discrepancy between documented claims (Debian 13 Trixie) and runtime logs (`systemd 252`, `Linux 6.1`), a binary and textual audit was performed directly on `filesystem.squashfs` and `PACKAGE-MANIFEST-2.0.1-rc1.txt`:

| File / Component | Extracted Value | Canonical Debian Distribution |
| :--- | :--- | :--- |
| **`/etc/debian_version`** | `12.15` | **Debian 12 (Bookworm)** |
| **`/etc/os-release`** | `VERSION_CODENAME=bookworm` | **Debian 12 (Bookworm)** |
| **`etc/apt/sources.list.d/debian.sources`** | `Suites: bookworm bookworm-updates bookworm-backports` | **Debian 12 (Bookworm)** |
| **`systemd`** | `252.39-1~deb12u2` | **Debian 12.4+ (deb12u2)** |
| **`libc6` (GNU C Library)** | `2.36-9+deb12u14` | **Debian 12.4+ (deb12u14)** |
| **`base-files`** | `12.4+deb12u15` | **Debian 12.4+ (deb12u15)** |
| **`linux-image-6.1.0-54-amd64`** | `6.1.190-1` | **Debian 12 LTS Kernel** |
| **Python Runtime** | `3.11.2` (`cpython-311`) | **Debian 12 Standard** |
| **PyQt6 / Qt 6** | `6.4.2` (`PyQt6-6.4.2.dist-info`) | **Debian 12 Standard** |

### 1.2 Root Cause of the Discrepancy
- In `build/live-build/auto/config`, the build profile specifies `--distribution trixie`.
- However, as proven by `scripts/build_v201_squashfs.py` (line 23):
  ```python
  BASE_ROOTFS = r"D:\anti\v101_rootfs.ext4"
  ```
  The build pipeline generated the squashfs by mounting `v101_rootfs.ext4` (a Debian 12 Bookworm base) and extracting `v201_overlay.tar` over it. It **never executed an `apt-get dist-upgrade` to Debian 13 Trixie**.
- **Conclusion:** **MONODESK OS is 100% built upon Debian 12 (Bookworm) LTS.**
- **Strategic Recommendation:** We must **honestly and accurately label MONODESK OS 2.0 as based on Debian 12 (Bookworm) LTS**. Debian 12 is the current, production-tested Debian stable/LTS line (supported through 2028), offering maximum stability, tested GPU drivers, and rock-solid package compatibility. Attempting to force Debian 13 (Trixie, which is currently Debian Testing / development) risks library ABI breakage for Qt 6, PipeWire, and kernel drivers.

---

## 2. Physical Lenovo Hardware Profile

A complete WMI/CIM hardware scan was performed on the connected Windows host:

```yaml
System:
  Manufacturer: LENOVO
  Machine Model: 82LN (Lenovo IdeaPad 5 15ALC05)
  BIOS Version: GLCN52WW (Release Date: 2023)
  Secure Boot: Supported / Toggleable

Processor (CPU):
  Name: AMD Ryzen 7 5700U with Radeon Graphics
  Architecture: x86_64 (Zen 2 / Lucienne APU)
  Cores / Threads: 8 Physical Cores / 16 Threads
  Frequency: 1.80 GHz Base / 4.30 GHz Boost
  Cache: 8 MB L3 Cache

Graphics (GPU):
  Name: AMD Radeon Graphics (Vega 8 integrated, 512 MB VRAM / Shared)
  PCI Vendor/Device: VEN_1002&DEV_164C
  Kernel Driver Required: amdgpu
  DRM / KMS: Supported

Wireless Network (Wi-Fi):
  Name: Realtek 8822CE Wireless LAN 802.11ac PCI-E NIC
  PCI Hardware ID: PCI\VEN_10EC&DEV_C822&SUBSYS_C12317AA&REV_00
  Kernel Driver: rtw88_8822ce
  Required Firmware: rtw88/rtw8822c_fw.bin

Bluetooth:
  Name: Realtek Bluetooth Adapter
  USB Hardware ID: USB\VID_0BDA&PID_C123
  Kernel Driver: btusb / btrtl
  Required Firmware: rtl_bt/rtl8822cu_fw.bin (or rtl8822cs_fw.bin)

Audio:
  Codec: Realtek High Definition Audio (ALC257)
  Hardware ID: HDAUDIO\FUNC_01&VEN_10EC&DEV_0257&SUBSYS_17AA38D5
  Kernel Driver: snd_hda_intel, snd_soc_dmic, snd_hda_codec_realtek
  Sound Server: PipeWire 0.3.65 + WirePlumber 0.4.13

Storage Devices:
  Internal Disk 0: WDC PC SN530 512GB NVMe SSD (GPT, Windows 11) - PROTECTED
  External Disk 1: JMicron Tech 1TB USB HDD (GPT):
    - Partition 1 (D:): NTFS, 966 GB (Data & Workspace) - PROTECTED
    - Partition 2 (E:): FAT32, 33.5 GB (MONODESK_OS Boot Volume)
```

---

## 3. Critical Firmware Gap Identified

A deep scan of `PACKAGE-MANIFEST-2.0.1-rc1.txt` and `filesystem.squashfs` revealed:
- `firmware-realtek` is **currently missing**.
- `firmware-amd-graphics` is **currently missing**.

> [!WARNING]
> Without `firmware-realtek`, the physical Realtek RTL8822CE Wi-Fi and Bluetooth card will fail to initialize on the Lenovo IdeaPad 5 (`rtw88_8822ce: failed to load firmware rtw88/rtw8822c_fw.bin`).
> Without `firmware-amd-graphics`, the AMD Radeon Vega 8 GPU will not have hardware KMS acceleration and will fall back to software llvmpipe.
> **Action Required:** We must inject `firmware-realtek` and `firmware-amd-graphics` into `filesystem.squashfs` before physical testing.

---

## 4. Safe Physical Testing Procedure for Lenovo IdeaPad 5 (82LN)

### Safety Protocol:
- **Zero Disk Writes to Internal Drive:** Disk 0 (WDC NVMe SSD) is never mounted as writable.
- **Zero Disk Writes to Data Partition D:** Disk 1 Partition 1 (`D:`) is never mounted as writable.
- All testing runs purely from RAM via `tmpfs` overlay backed by partition `E:` (FAT32).

### Execution Steps:
1. **Deploy Verified Files to Partition E:**
   - Copy `initrd.img` (with FAT/NLS driver fix) to `E:\live\initrd.img`.
   - Copy `filesystem.squashfs` (with injected Realtek and AMD firmware) to `E:\live\filesystem.squashfs`.
2. **Cold Boot to Physical Hardware:**
   - Shut down Windows safely (hold Shift while clicking Shut Down to avoid Fast Startup lock).
   - Turn on Lenovo laptop and repeatedly press **F12** to enter the Lenovo Boot Device Selection Menu.
   - Select `EFI USB Device (JMicron Tech)`.
3. **Select GRUB Entry:**
   - In GRUB menu, select `MONODESK OS 2.0.1-rc2 (Universal PC - Standard Profile)`.
4. **Physical Acceptance Checklist:**
   - [ ] Clean boot past kernel without `exitcode=0x00000200` panic.
   - [ ] LightDM autologin into `monodesk` user session.
   - [ ] AMD Radeon GPU initialized via `amdgpu` with full 1920x1080 resolution.
   - [ ] Realtek Wi-Fi scans and connects to 802.11ac / 5GHz wireless access points.
   - [ ] Realtek ALC257 speakers and microphone produce clean audio via PipeWire.
   - [ ] Touchpad multi-touch gestures (two-finger scroll) functional.
   - [ ] Screen brightness function keys (`F5`/`F6`) responsive.

---
*Certified under Gravitas Invariant 6: Hard evidence verified; assumptions documented.*
