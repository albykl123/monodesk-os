# MONODESK OS — EXECUTION ORDER 05A
## Windows Host + External JMicron Disk Read-Only Forensic Audit Report

**Audit Timestamp:** Mon Nov 16 10:48:00 IST 2026 (05:18:00 UTC)  
**Host Machine:** Lenovo IdeaPad Slim 5 (82LN)  
**External Disk:** JMicron Tech SCSI Disk Device (1 TB USB-SATA GPT)  
**Mode:** Strictly Read-Only / Forensic Diagnostic  

---

## 1. Windows Host Hardware & Environment Specifications

| Parameter | Detected Value |
| :--- | :--- |
| **Operating System** | Microsoft Windows 11 Pro (Version 10.0.26300, Build 26300, 64-bit) |
| **Device Model** | LENOVO 82LN (Lenovo IdeaPad Slim 5 15ALC05) |
| **Processor (CPU)** | AMD Ryzen 7 5700U with Radeon Graphics (8 Cores, 16 Threads, 1.80 GHz base) |
| **Physical Memory (RAM)** | 13.85 GB Physical Available Memory |
| **Integrated GPU** | AMD Radeon(TM) Graphics (Device ID: `0x164C`, Lucienne / Vega 8, 2048 MB VRAM) |
| **GPU Driver Version** | `31.0.21925.1001` (Driver Date: 05/20/2026) |
| **Display Resolution** | 1920 x 1080 @ 60 Hz |
| **BIOS Version / Date** | LENOVO `H2CN36WW` (09/02/2024), SMBIOS 3.3 |
| **Secure Boot** | Supported (Hardware UEFI) |
| **Storage Usage** | C: 425.46 GB Used / 50.39 GB Free; D: 19.05 GB Used / 881.21 GB Free; E: 1.11 GB Used / 30.12 GB Free |

*Raw audit data preserved at [windows-host-audit.txt](file:///D:/anti/monodesk-os/docs/diagnostics/windows-host-audit.txt).*

---

## 2. JMicron External Disk Identification & Partition Topology

### Physical Disk Attributes
* **Friendly Name:** `JMicron Tech` (`JMicron Tech SCSI Disk Device`)
* **Physical Disk Number:** **`Disk 1`** (`\\.\PHYSICALDRIVE1`)
* **Serial Number:** `K94PT9325BHV`
* **Bus Type:** `USB` (External USB-to-SATA Bridge)
* **Total Physical Capacity:** `1,000,204,886,016 bytes` (931.51 GiB / ~1 TB)
* **Partition Style:** `GPT` (GUID Partition Table)
* **Health / Operational Status:** `Healthy` / `Online`

### Partition Map
```text
Physical Disk 1 (1,000,204,886,016 bytes / GPT)
├── Partition 1: D: "hdd"         Offset: 1,048,576       Size: 966,647,611,392 bytes (900.26 GB) [NTFS, Basic Data]
└── Partition 2: E: "MONODESK_OS" Offset: 966,648,659,968 Size:  33,554,432,000 bytes ( 31.25 GB) [FAT32, Basic Data]
```

### Partition Readable Status & Findings
1. **Readable by Windows:** Both Partition 1 (`D:`) and Partition 2 (`E:`) are fully formatted and accessible by Windows.
2. **Linux Partitions:** **There are ZERO Linux `ext4`, `btrfs`, `xfs`, or Linux swap partitions on the JMicron disk.**
3. **Crucial Finding:** The operating system running from this disk was **NOT an installed Linux system**. It was the **Live ISO environment booting from Partition 2 (`E:`)**! The full OS installation to disk was never executed; the system booted directly into live mode.

---

## 3. MONODESK Repository State & Commit History

* **Repository Location:** `D:\anti\monodesk-os`
* **Current Working Branch:** `v2.0-nebula` (Tracking `origin/v2.0-nebula`)
* **Working Tree State:** Clean (no uncommitted file modifications)
* **Current Remote & Local HEAD:** Commit `b415b62` (`docs: record bootable media deployment verification for Partition E:`)
* **Recent Commits:**
  * `b415b62` — `docs: record bootable media deployment verification for Partition E:`
  * `83b29b9` — `docs: verify final ISO release asset upload to GitHub v2.0.0`
  * `d5a3f7f` — `docs: record final GitHub release URL in deployment report`
  * `96d15c9` — `feat(release): reconcile original 2.0 applications, complete Calamares installer, validate installed OS boot, and prepare v2.0.0 release`
  * `288284c` — `feat(iso): complete Execution Order 02 - Debian 13 package audit, M3Shapes Qt6 plugin, and validated universal ISO build`
* **Branch `v2.0-desktop-fix`:** Not present on local or remote repository.

---

## 4. ISO Artifact Verification

* **Live ISO File:** [monodesk-os-2.0.0-universal-amd64.iso](file:///D:/anti/monodesk-os/releases/monodesk-os-2.0.0-universal-amd64.iso)
* **File Size:** `1,190,991,872 bytes` (1.11 GiB)
* **Calculated SHA-256:** `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2`
* **Official Release SHA-256:** `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2`
* **Status:** Verified 100% exact match against GitHub release `v2.0.0`.

---

## 5. Forensic Root Cause Analysis

### Why the Desktop Showed the Legacy Dark/Light UI and Mouse Hover Failed

Our forensic inspection of the live-build staging tree (`build/live-build/config/includes.chroot/`) revealed the exact chain of execution:

1. **Session Routing Fallback to X11 (`monodesk_shell.py`):**
   * LightDM launched `/usr/bin/monodesk-session auto` as defined in `/usr/share/xsessions/monodesk-session.desktop`.
   * `/usr/bin/monodesk-session` called `/usr/bin/monodesk-hw-detect --check-compositor`.
   * In `monodesk-hw-detect`, GPU acceleration is detected via `glxinfo -B`. When invoked during early session initialization prior to an active X/Wayland client display, `glxinfo` fails, causing `accel` to fall back to `"unknown"`.
   * Because `accel != "hardware"`, `check_compositor` returned `"x11"`.
   * In `monodesk-session`, the `"x11"` fallback block was executed:
     ```bash
     xfwm4 --compositor=off &
     exec python3 /usr/share/monodesk/desktop/shell/monodesk_shell.py
     ```
   * **`monodesk_shell.py` IS THE OLD LEGACY PYTHON/QT6/QML DESKTOP SHELL** (the dark/light desktop).
   * Because `xfwm4 --compositor=off` disabled compositing, QtQuick frameless windows failed to receive mouse enter/leave hover events properly under X11, causing mouse hover interactions to become non-responsive.

2. **Why Hyprland + Quickshell (Nebula) Did Not Launch:**
   * In `build/live-build/config/includes.chroot/etc/skel/.config/hypr/`: Missing (the directory was never created or staged into `includes.chroot`).
   * In `build/live-build/config/includes.chroot/usr/share/monodesk/shell/quickshell/`: Missing (Nebula quickshell source was kept in `shell/quickshell` and `third_party/nebula`, but not copied into `includes.chroot`).

3. **Why Settings Hub and Software Centre Were Not Accessible:**
   * Both applications exist in source code (`applications/settings/monodesk_settings.py` and `applications/software-manager/monodesk_software_manager.py`) and were copied to `/usr/share/monodesk/applications/`.
   * **Missing Executable Wrappers in `/usr/bin/`:** `monodesk_shell.py` attempts to launch `monodesk-settings` and `monodesk-store`. However, neither binary exists in `/usr/bin/`.
   * **Missing System Desktop Entries:** None of the `.desktop` files were installed to `/usr/share/applications/` (they were only in `/usr/share/monodesk/applications/*`). Standard Linux desktop search and launchers only scan `/usr/share/applications/`.

---

## 6. What Needs to be Inspected in Stage 2 (Running Linux Session)

When booting into the live USB environment on Partition 2:
1. Verify if running `/usr/bin/monodesk-session wayland` manually launches Hyprland on the AMD Ryzen 7 5700U Radeon GPU.
2. Inspect `journalctl -b -p err` to verify kernel DRM/KMS module loading for `amdgpu`.
3. Check `lspci -nnk | grep -A4 -Ei 'VGA|Display'` to confirm `amdgpu` kernel driver in use.
4. Verify whether `glxinfo -B` succeeds once an Xwayland or X11 display is active.
5. Confirm that the Calamares installer icon on the live desktop can partition and install the OS to target disks when desired.
