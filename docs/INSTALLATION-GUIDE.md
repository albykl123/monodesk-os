# MONODESK OS 2.0 — Installation Guide
**Universal PC Edition (Debian 13 Trixie AMD64)**

This guide walks you through preparing installation media, booting the live environment, running the Calamares graphical installer, and setting up MONODESK OS 2.0.

---

## 1. System Requirements

| Metric | Minimum (Lite Profile) | Recommended (Standard Profile) |
| :--- | :--- | :--- |
| **Processor** | 64-bit x86-64 CPU (Dual-Core 1.8 GHz+) | Modern Quad-Core / Octa-Core (e.g. AMD Ryzen 5/7, Intel Core i5/i7) |
| **RAM** | 2 GB (4 GB recommended) | 8 GB or 16 GB+ |
| **Storage** | 15 GB available space | 32 GB+ SSD / NVMe |
| **Graphics** | Legacy Intel HD 3000 / AMD / NVIDIA (X11) | Vulkan/DRM/KMS supported GPU (AMD Radeon, Intel Iris Xe, NVIDIA) |
| **Boot Firmware** | Legacy BIOS or UEFI 64-bit | UEFI 64-bit with Secure Boot disabled |

---

## 2. Preparing Installation Media

The ISO file is located at `releases/monodesk-os-2.0.0-universal-amd64.iso` (~1.11 GB).

### Option A: Using Rufus (Windows)
1. Insert a USB flash drive (minimum 4 GB capacity).
2. Download and launch **Rufus** (v4.0 or newer).
3. Select your USB drive under **Device**.
4. Click **Select** and browse to `monodesk-os-2.0.0-universal-amd64.iso`.
5. Partition scheme: **GPT** (for modern UEFI) or **MBR** (for legacy BIOS).
6. Target system: **UEFI (non-CSM)** or **BIOS/UEFI**.
7. When prompted, select **Write in DD Image mode** to preserve the hybrid El Torito boot structure.
8. Click **Start** to flash.

### Option B: Using Ventoy (Windows / Linux)
1. Format a USB drive with Ventoy.
2. Copy `monodesk-os-2.0.0-universal-amd64.iso` directly into the USB root partition.

### Option C: Using dd (Linux / macOS)
```bash
# Identify your USB drive device node (e.g., /dev/sdb)
lsblk

# Flash the ISO (CAUTION: ensure of=/dev/sdX points to your USB drive, not internal disk)
sudo dd if=monodesk-os-2.0.0-universal-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

---

## 3. Booting the Live Environment

1. Connect the USB drive to the target computer.
2. Power on the machine and repeatedly press the **Boot Menu key**:
   - **Lenovo (IdeaPad, ThinkPad):** `F12` or `Fn + F12`
   - **Dell:** `F12`
   - **HP:** `F9` or `Esc` then `F9`
   - **ASUS / Acer:** `F8` or `F12`
3. In the boot menu, select your USB flash drive:
   - For modern hardware (e.g. **Lenovo IdeaPad Slim 5**), choose the **UEFI** entry.
   - For legacy hardware (e.g. **Lenovo B590**), choose the **USB HDD / Legacy** entry.
4. When the **GRUB 2** boot screen appears, select:
   - **Live system (amd64)** for standard hardware-accelerated boot.
   - **Live system (amd64 fail-safe mode)** if experiencing display or ACPI issues.
5. The live desktop will automatically initialize.
   - On modern GPUs with KMS/DRM, the **Wayland (Hyprland + Quickshell)** session loads.
   - On legacy GPUs (e.g. Intel HD 3000), the **Recovery (X11 + XFWM4)** session loads automatically.

---

## 4. Running the Calamares Installer

1. On the live desktop, double-click the **Install MONODESK OS** icon.
2. **Welcome Screen:** Select your installation language.
3. **Location / Timezone:** Select your region and city on the world map.
4. **Keyboard Layout:** Choose your keyboard layout (e.g. English US).
5. **Partitioning:**
   - **Erase disk:** Automatically creates an EFI System Partition (512 MB) and an ext4 root partition spanning the remainder of the disk.
   - **Manual partitioning:** Recommended for dual-boot setups alongside Windows. Ensure an ESP partition (`/boot/efi`, vfat, 512 MB) and a root partition (`/`, ext4 or btrfs) are configured.
6. **User Account:**
   - Enter your name, username, computer hostname, and password.
   - Choose whether to require a password to log in.
7. **Summary:** Review your partitioning and installation choices.
8. **Install:** Click **Install Now**. Calamares will unpack the system squashfs, configure fstab, generate machine ID, set up user permissions, and install the GRUB 2 EFI/MBR bootloader.
9. **Finished:** Once installation completes, check **Restart now** and click **Done**.
10. Remove the USB flash drive when prompted and press Enter.

---

## 5. Post-Installation First Boot

1. The computer will boot into your newly installed MONODESK OS 2.0 system.
2. Log in using the username and password created during installation.
3. The **MONODESK Welcome** app will guide you through:
   - Automated performance profile verification (**Standard** vs **Lite**).
   - Display scaling and Material You theme preference.
   - Wi-Fi and Bluetooth configuration.
   - Package updates via **MONODESK Software Centre**.
