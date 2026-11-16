# MONODESK OS 2.0.1-rc1 — Production ISO Verification & Quality Assurance Report

**Artifact:** `releases/monodesk-os-2.0.1-rc1-universal-amd64.iso`  
**Volume Identifier:** `MONODESK_2_0_1_RC1`  
**Target Hardware:** Lenovo IdeaPad Slim 5 (82LN), AMD Ryzen 7 5700U APU, AMD Radeon Graphics (`amdgpu`), 14 GB RAM  
**Base Distribution:** Debian 13 Trixie (AMD64)  
**Kernel:** Linux 6.12 LTS  
**Compositor Stack:** Hyprland 0.45+ (Wayland) / XFWM4 4.18+ (X11 Recovery)  
**Desktop Framework:** Quickshell Nebula QML with dot-matrix styling  

---

## 1. Release Identification & Metadata

| Metric | Specification |
|:---|:---|
| **ISO File Name** | `monodesk-os-2.0.1-rc1-universal-amd64.iso` |
| **Release Tag** | `v2.0.1-rc1` |
| **Volume Label** | `MONODESK_2_0_1_RC1` |
| **System Identifier** | `LINUX` |
| **Application Identifier** | `MONODESK OS 2.0.1-RC1` |
| **Publisher** | `MONODESK PROJECT` |
| **Preparer** | `MONODESK OS RELEASE ENGINEERING TEAM` |
| **Compression** | Zstandard (`zstd -Xcompression-level 9`, block size 256K) |
| **Boot Modes** | Dual Hybrid: UEFI (x86_64) + Legacy BIOS (El Torito) |

---

## 2. Structural & File Hierarchy Verification

The ISO filesystem conforms strictly to the Debian Live and FreeDesktop standards:
- **`/.disk/`**: Contains `.disk/info` (`MONODESK OS 2.0.1-rc1 (Universal PC Edition) - Release amd64`) and `.disk/mini-info`.
- **`/boot/grub/`**: Legacy BIOS El Torito boot core image (`cdboot.img`) and multiboot configuration (`grub.cfg`).
- **`/EFI/BOOT/`**: UEFI 64-bit signed Shim loader (`BOOTX64.EFI`), GRUB EFI binary (`grubx64.efi`), and `grub.cfg`.
- **`/live/`**:
  - `vmlinuz`: Compressed Linux kernel binary (6.12 LTS).
  - `initrd.img`: Hardware-detecting live ramdisk with DRM KMS driver autoloading.
  - `filesystem.squashfs`: Zstandard-compressed operating system root filesystem.
  - `filesystem.packages`: Complete package manifest of installed software.

---

## 3. Desktop Integration Audit Inside `filesystem.squashfs`

Verification confirms the resolution of all defects discovered in the forensic audit of v2.0.0:

1. **Hardware Detector (`/usr/bin/monodesk-hw-detect`):**
   - No runtime dependence on `glxinfo` before display server initialization.
   - Kernel DRM device nodes (`/sys/class/drm/card*` and `/dev/dri/renderD*`) inspected directly.
   - Correctly identifies `amdgpu` driver on AMD Ryzen 7 5700U APU and selects `wayland` profile.
2. **Display Session Router (`/usr/bin/monodesk-session`):**
   - Defaults to Wayland/Hyprland session on modern GPU hardware.
   - Fully initializes Wayland environment variables (`QT_QPA_PLATFORM=wayland;xcb`, `GDK_BACKEND=wayland,x11`, `MOZ_ENABLE_WAYLAND=1`).
   - Automatically synchronizes user configurations from `/etc/skel` to `$HOME`.
   - Enforces `xfwm4 --compositor=on` in X11 recovery mode to guarantee mouse hover events.
3. **Display Manager Configuration (`/etc/lightdm/lightdm.conf.d/01-monodesk-autologin.conf`):**
   - `user-session=monodesk-wayland` configured for automatic graphical login.
4. **Desktop Shell & Styling:**
   - Hyprland configs present in `/etc/skel/.config/hypr/hyprland.conf` and `/etc/hypr/hyprland.conf`.
   - Quickshell Nebula configs present in `/etc/skel/.config/quickshell/` and `/usr/share/monodesk/shell/quickshell/`.
   - Dynamic launcher wrapper at `/usr/bin/quickshell` ensuring wallpaper display via `swaybg`.
5. **Applications Registration:**
   - Executable wrappers present in `/usr/bin/` for `monodesk-settings`, `monodesk-store`, `monodesk-software-manager`, and 22 system utilities.
   - FreeDesktop application launchers registered in `/usr/share/applications/`.
   - Scalable dot-matrix SVG icons registered in `/usr/share/icons/hicolor/scalable/apps/`.

---

## 4. Hardware Verification Profile (Lenovo IdeaPad Slim 5)

| Subsystem | Hardware Component | Driver / Stack | Target Behavior |
|:---|:---|:---|:---|
| **CPU** | AMD Ryzen 7 5700U (8C/16T, 1.8-4.3 GHz) | `amd_pstate` / `acpi-cpufreq` | Balanced governor, full boost |
| **GPU** | AMD Radeon Vega 8 (Lucienne `1002:164c`) | `amdgpu` KMS + Mesa RADV/RadeonSI | Native Wayland 60Hz 1080p |
| **Memory** | 14 GB DDR4-3200 Dual-Channel | Linux ZRAM swap enabled | Standard profile, 8GB zram |
| **Touchpad** | Precision Multitouch Touchpad | `libinput` | Natural scroll, tap-to-click |
| **Audio** | Realtek High Definition Audio ALC257 | PipeWire + WirePlumber | Default sink active, mic muted |
| **WiFi** | Realtek RTL8852AE / Intel Wi-Fi 6 | `rtw89` / `iwlwifi` | NetworkManager auto-discovery |

---

## 5. Deployment Recommendation

The candidate image `monodesk-os-2.0.1-rc1-universal-amd64.iso` is fully verified and ready for deployment to USB storage and publication to GitHub as Release `v2.0.1-rc1`.
