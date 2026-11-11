# MONODESK OS 1.0 — Installation & Quick Start Guide

**Edition:** Universal PC Edition 1.0.0  
**Target Architecture:** AMD64 / x86-64

---

### 1. System Requirements

| Specification | MONODESK Lite (Minimum) | MONODESK Standard (Recommended) |
| :--- | :--- | :--- |
| **Processor (CPU)** | 64-bit Dual-Core x86-64 (e.g., Intel Core i3-2348M) | 64-bit Quad-Core / Octa-Core (e.g., AMD Ryzen 7 5700U) |
| **System Memory (RAM)** | 4 GB RAM | 8 GB RAM or greater |
| **Storage (Disk)** | 20 GB available storage (SATA HDD / SSD) | 64 GB+ NVMe SSD |
| **Graphics (GPU)** | Intel HD 3000 / AMD Radeon / Nouveau (OpenGL 3.3) | Intel Iris / AMD Radeon Vega / NVIDIA GeForce (Vulkan capable) |
| **Display** | 1024 x 768 resolution | 1920 x 1080 (Full HD) or higher |
| **Boot Mode** | Legacy BIOS or UEFI | UEFI with GPT partitioning |

---

### 2. Creating Installation Media (Live USB)

You will need a USB flash drive with at least **4 GB capacity**.

#### Option A: Using Rufus (Windows)
1. Download the official ISO (`monodesk-os-1.0.0-universal-amd64.iso`) and [Rufus](https://rufus.ie/).
2. Insert your USB drive and launch Rufus.
3. Select your USB drive under **Device**.
4. Click **SELECT** and choose the `monodesk-os-1.0.0-universal-amd64.iso` file.
5. Partition scheme: Choose **GPT** for UEFI systems or **MBR** for legacy BIOS systems.
6. When prompted, select **Write in DD Image mode** (recommended for hybrid Linux images).
7. Click **START** and wait for the process to complete.

#### Option B: Using Ventoy (Multi-boot USB)
1. Install [Ventoy](https://www.ventoy.net/) onto your USB drive.
2. Drag and drop `monodesk-os-1.0.0-universal-amd64.iso` directly onto the Ventoy partition.

#### Option C: Using `dd` (Linux / macOS)
```bash
sudo dd if=monodesk-os-1.0.0-universal-amd64.iso of=/dev/sdX bs=4M status=progress conv=fdatasync
```
*(Replace `/dev/sdX` with your actual USB block device path).*

---

### 3. Booting the Live USB Environment

1. Insert the USB drive into your computer.
2. Power on the computer and immediately press the Boot Menu key:
   - **Lenovo:** `F12` or `Fn + F12` (or press the Novo button)
   - **Dell:** `F12`
   - **HP:** `F9` or `Esc`
   - **ASUS / Acer:** `F8` or `F12`
3. Select the USB device from the boot list.
4. From the MONODESK bootloader menu, select **MONODESK OS 1.0 (Live Desktop)**.
5. The live desktop will automatically load with the monochrome dot-matrix shell.

---

### 4. Running the Graphical Installer (Calamares)

1. Double-click the **Install MONODESK OS** shortcut on the desktop.
2. **Language & Location:** Select your preferred display language, timezone, and regional format.
3. **Keyboard Layout:** Choose your keyboard layout and test keys in the verification field.
4. **Partitioning:**
   - **Erase disk:** Automatically sets up an ext4 root partition, EFI boot partition, and swap.
   - **Install alongside:** Resizes existing Windows or Linux partitions safely.
   - **Manual partitioning:** For advanced users requiring custom mount points (`/home`, `/var`, etc.).
   - *(Optional)* Check **Encrypt system** to enable LUKS2 full-disk encryption.
5. **User Setup:** Enter your name, desired username, computer hostname, and password.
6. **Summary & Install:** Review your selections and click **Install**.
7. Once finished, click **Restart Now** and remove your USB flash drive.

---

### 5. First Boot Onboarding

On your first login, the **MONODESK Welcome Assistant** will launch automatically to guide you through:
- Confirming your performance profile (**Lite** vs. **Standard**).
- Verifying hardware detection and graphics acceleration via the **Hardware Diagnostic Report**.
- Setting up Wi-Fi or Bluetooth devices.
- Checking for the latest system security updates.
