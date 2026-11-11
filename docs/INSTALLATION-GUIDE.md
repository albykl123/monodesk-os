# MONODESK OS 1.0 — Comprehensive Installation Guide

---

### 1. Pre-Installation Checklist

Before installing MONODESK OS on physical hardware:
1. **Target PC Specifications:** Verify your system has at least a 64-bit x86-64 CPU (Intel Core, Celeron, Pentium; AMD Ryzen, Athlon) and at least 4 GB RAM (8 GB+ for Standard profile).
2. **Backup Existing Data:** If installing alongside Windows or replacing your operating system, back up critical documents to an external drive or cloud storage.
3. **USB Flash Drive:** Ensure you have a USB flash drive with at least 4 GB storage.
4. **Target Benchmark Reference:**
   - **Lenovo B590 (Low-End Benchmark):** Intel Core i3-2348M, 4GB RAM, Intel HD 3000. Use **MONODESK Lite**.
   - **Lenovo IdeaPad Slim 5 (Modern Reference):** AMD Ryzen 7 5700U, 16GB RAM, NVMe. Use **MONODESK Standard**.

---

### 2. Flashing the Installation Media

Download `monodesk-os-1.0.0-universal-amd64.iso` and verify the checksum:
```bash
sha256sum -c monodesk-os-1.0.0-universal-amd64.iso.sha256
```

#### On Windows / Multi-Boot (Using Ventoy):
1. Format your USB flash drive once using Ventoy (exFAT / GPT mode recommended).
2. Simply copy `monodesk-os-1.0.0-universal-amd64.iso` directly onto the Ventoy USB drive partition.
3. Reboot your PC, select the USB in the BIOS/UEFI boot menu, and select MONODESK OS from the Ventoy menu.

#### On Windows (Using Rufus):
1. Launch Rufus and select your USB flash drive.
2. Select the `monodesk-os-1.0.0-universal-amd64.iso` file.
3. Choose **GPT** partition scheme for modern UEFI PCs (or **MBR** for legacy BIOS).
4. When prompted by Rufus, select **Write in DD Image mode**.
5. Click **Start** to write the image.

#### On Linux (Using `dd`):
```bash
sudo dd if=monodesk-os-1.0.0-universal-amd64.iso of=/dev/sdX bs=4M status=progress conv=fdatasync
```

---

### 3. Booting the Live Media

1. Insert the USB drive and power on the computer.
2. Press the boot menu key (`F12`, `F9`, `F8`, or `Novo` button on Lenovo).
3. Select the USB flash drive (UEFI or Legacy).
4. Choose **MONODESK OS 1.0 (Live Desktop)** from the GRUB bootloader menu.
5. The desktop will initialize in live demonstration mode without modifying your internal storage.

---

### 4. Running Calamares Installer

1. Double-click the **Install MONODESK OS** desktop shortcut.
2. **Language & Location:** Select your preferred regional language, date format, and timezone.
3. **Keyboard Layout:** Choose and test your keyboard layout.
4. **Partitioning Strategy:**
   - **Erase disk:** Automatically partitions the selected drive with an EFI boot partition (`/boot/efi`, 512MB), ext4 root filesystem (`/`), and swap.
   - **Install alongside:** Resizes existing Windows partitions safely to create space for MONODESK OS.
   - **Manual partitioning:** Create custom mount points (`/`, `/home`, etc.).
   - *(Optional)* Check **Encrypt system** to enable LUKS2 full-disk encryption with Argon2id password protection.
5. **User Account:** Enter your full name, username, machine hostname, and administrative password.
6. **Installation:** Review the summary screen and click **Install**.
7. Once finished, remove the USB drive and click **Restart Now**.
