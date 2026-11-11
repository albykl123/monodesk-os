# MONODESK OS 1.0 — Troubleshooting & Recovery Guide

---

### 1. Common Boot & Hardware Scenarios

#### 1.1 Black Screen on Boot (Graphics Issues)
If booting stalls on a black screen or blinking cursor:
1. At the GRUB menu, press `e` to edit the kernel boot entry.
2. Locate the line beginning with `linux /vmlinuz...`.
3. Add `nomodeset` to the end of the line.
4. Press `Ctrl + X` or `F10` to boot using basic VESA/EFI fallback graphics.
5. Once inside the desktop, open the terminal and inspect your GPU drivers:
   ```bash
   monodesk-hardware-report
   ```
6. If an NVIDIA dedicated GPU is present, run:
   ```bash
   sudo monodesk-nvidia-installer
   ```

#### 1.2 Wi-Fi Adapter Not Detected
1. Open the terminal and verify if firmware is missing:
   ```bash
   sudo dmesg | grep -i firmware
   ```
2. If using a Broadcom BCM43xx wireless chip:
   - Connect via an Ethernet cable or USB smartphone tethering.
   - Run:
     ```bash
     sudo apt-get update
     sudo apt-get install -y broadcom-sta-dkms
     sudo modprobe wl
     ```

#### 1.3 PipeWire Audio Output Issues
If no sound is produced from speakers or headphones:
1. Verify WirePlumber session status:
   ```bash
   systemctl --user status pipewire wireplumber
   ```
2. Restart user audio daemons:
   ```bash
   systemctl --user restart pipewire pipewire-pulse wireplumber
   ```
3. Open the graphical volume mixer (`pavucontrol`) and confirm the default output sink is unmuted.

#### 1.4 High Memory Consumption on 4 GB RAM PCs
1. Check if the Lite profile is active:
   ```bash
   monodesk-profile-ctl get
   ```
2. If Standard is active, switch to Lite immediately:
   ```bash
   sudo monodesk-profile-ctl set lite
   ```
3. Confirm that compressed zRAM is active:
   ```bash
   zramctl
   ```

---

### 2. Emergency Recovery Environment

If an installation fails to boot due to an unexpected GRUB or filesystem issue, boot from the MONODESK Live USB:
1. Boot into the live environment.
2. Open the terminal and identify the target root partition:
   ```bash
   lsblk -f
   ```
3. Mount the target filesystem and chroot for repair:
   ```bash
   sudo mount /dev/sdX2 /mnt
   sudo mount /dev/sdX1 /mnt/boot/efi   # For UEFI systems
   for i in /dev /dev/pts /proc /sys /run; do sudo mount -B $i /mnt$i; done
   sudo chroot /mnt
   ```
4. Reinstall GRUB and update kernel initramfs:
   ```bash
   grub-install /dev/sdX
   update-grub
   update-initramfs -u
   exit
   ```
5. Reboot the computer.
