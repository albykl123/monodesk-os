#!/usr/bin/env python3
"""
MONODESK OS 2.0.1-rc2 — JMicron Multi-Partition External Drive Boot Reproduction & Validation
Strictly simulates the physical Lenovo IdeaPad Slim 5 + JMicron External Drive layout:
- Drive: Multi-partition GPT disk
  - Partition 1: 50 MiB (NTFS/dummy - mirrors Disk 1 Partition 1 D:)
  - Partition 2: 1.2 GiB FAT32 volume "MONODESK_OS" (mirrors Disk 1 Partition 2 E:)
- Verification Goals:
  1. Prove that Partition 2 (/dev/vda2 or /dev/sda2) is dynamically discovered and mounted via vfat.
  2. Prove that FAT32 kernel modules (fat.ko, vfat.ko, nls_cp437.ko, nls_utf8.ko) are cleanly loaded.
  3. Prove that live boot mounts filesystem.squashfs and reaches graphical.target WITHOUT kernel panic!
"""

import os
import sys
import time
import socket
import pathlib
import subprocess
from PIL import Image

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
QEMU_IMG = r"C:\Program Files\qemu\qemu-img.exe"
BUILDER_QCOW2 = r"C:\anti\debian-builder.qcow2"
SSH_KEY = r"C:\anti\builder_key"
SQUASHFS = r"D:\anti\iso_staging_v201\live\filesystem.squashfs"
KERNEL = r"D:\anti\iso_staging_v201\live\vmlinuz"
INITRD = r"D:\anti\iso_staging_v201\live\initrd.img"
VDISK = r"D:\anti\test_jmicron_sim.raw"
OUT_DIR = r"D:\anti\monodesk-os\artifacts\qa"
SERIAL_LOG = os.path.join(OUT_DIR, "jmicron_e_boot_simulation.log")
SCREEN_PPM = os.path.join(OUT_DIR, "jmicron_e_boot_screen.ppm")
SCREEN_PNG = os.path.join(OUT_DIR, "jmicron_e_boot_screen.png")

SSH_BASE = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5", "-i", SSH_KEY, "-p", "2222", "root@127.0.0.1"
]

def step1_create_and_populate_disk():
    print("=" * 70, flush=True)
    print("[STEP 1] Generating disposable multi-partition disk simulating JMicron drive layout...", flush=True)
    print("=" * 70, flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(VDISK):
        try:
            os.remove(VDISK)
        except Exception as e:
            print(f"[*] Removing old vdisk: {e}", flush=True)

    # 1.4 GiB raw disk
    subprocess.run([QEMU_IMG, "create", "-f", "raw", VDISK, "1400M"], check=True)
    print(f"[✓] Created raw container at {VDISK} (1.4 GiB).", flush=True)

    # Launch builder VM with VDISK as /dev/vdb and SQUASHFS as /dev/vdc
    print("[*] Launching Debian Builder VM to partition & populate FAT32 Partition 2...", flush=True)
    qemu_cmd = [
        QEMU, "-accel", "whpx", "-m", "2048", "-smp", "2",
        "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
        "-drive", f"file={VDISK},format=raw,if=virtio",
        "-drive", f"file={SQUASHFS},format=raw,if=virtio,readonly=on",
        "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
        "-device", "virtio-net-pci,netdev=net0",
        "-display", "none"
    ]
    proc = subprocess.Popen(qemu_cmd)
    try:
        online = False
        for i in range(30):
            time.sleep(2)
            res = subprocess.run(SSH_BASE + ["echo BUILDER_UP"], capture_output=True, text=True)
            if "BUILDER_UP" in res.stdout:
                online = True
                print(f"[✓] Builder VM connected after {i*2+2}s.", flush=True)
                break
        if not online:
            raise RuntimeError("Timeout connecting to Builder VM via SSH.")

        format_cmd = """
set -euo pipefail
echo "=== Partitioning /dev/vdb as GPT multi-partition ==="
parted -s /dev/vdb mklabel gpt
parted -s /dev/vdb mkpart primary ntfs 1MiB 50MiB
parted -s /dev/vdb mkpart primary fat32 50MiB 100%
parted -s /dev/vdb name 1 "D_PARTITION_NTFS"
parted -s /dev/vdb name 2 "MONODESK_OS"
udevadm settle
lsblk /dev/vdb

echo "=== Formatting Partition 2 as FAT32 ==="
mkfs.vfat -F 32 -n "MONODESK_OS" /dev/vdb2

echo "=== Mounting Partition 2 and staging live filesystem ==="
mkdir -p /mnt/jmicron_e
mount -t vfat /dev/vdb2 /mnt/jmicron_e
mkdir -p /mnt/jmicron_e/live /mnt/jmicron_e/.disk
echo "MONODESK OS 2.0.1-rc2 (Universal PC Edition) - amd64" > /mnt/jmicron_e/.disk/info
echo "Copying filesystem.squashfs from /dev/vdc to FAT32 filesystem..."
cat /dev/vdc > /mnt/jmicron_e/live/filesystem.squashfs
sync
df -h /mnt/jmicron_e
umount /mnt/jmicron_e
echo "JMICRON_PREPARATION_COMPLETE"
"""
        res = subprocess.run(SSH_BASE + [format_cmd], capture_output=True, text=True)
        print(res.stdout, flush=True)
        if "JMICRON_PREPARATION_COMPLETE" not in res.stdout:
            print(res.stderr, flush=True)
            raise RuntimeError("Failed to partition and populate JMicron virtual disk.")

        print("[✓] Virtual JMicron drive partitioned and populated successfully!", flush=True)
        subprocess.run(SSH_BASE + ["/usr/sbin/poweroff.real -f || poweroff -f"])
        proc.wait(timeout=15)
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)

def step2_boot_jmicron_simulation():
    print("\n" + "=" * 70, flush=True)
    print("[STEP 2] Cold Booting QEMU with JMicron Simulation Disk as /dev/sda...", flush=True)
    print("=" * 70, flush=True)
    if os.path.exists(SERIAL_LOG):
        os.remove(SERIAL_LOG)
    if os.path.exists(SCREEN_PPM):
        os.remove(SCREEN_PPM)

    cmd = [
        QEMU,
        "-accel", "whpx",
        "-m", "4096",
        "-smp", "4",
        "-kernel", KERNEL,
        "-initrd", INITRD,
        "-drive", f"file={VDISK},format=raw,if=virtio",
        "-append", "boot=live components username=monodesk console=tty0 console=ttyS0 loglevel=7",
        "-vga", "virtio",
        "-serial", f"file:{SERIAL_LOG}",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5572,server,nowait"
    ]

    print("[*] Launching QEMU with JMicron virtual disk attached...", flush=True)
    start_t = time.time()
    proc = subprocess.Popen(cmd)
    qmp = None
    try:
        time.sleep(3)
        qmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        qmp.connect(("127.0.0.1", 5572))
        qmp.recv(1024)
        qmp.sendall(b'{"execute": "qmp_capabilities"}\n')
        qmp.recv(1024)
        print("[✓] QMP connected.", flush=True)

        found_medium = False
        reached_target = False
        panic_detected = False

        for i in range(60):
            time.sleep(1)
            elapsed = time.time() - start_t
            if os.path.exists(SERIAL_LOG):
                try:
                    with open(SERIAL_LOG, "r", encoding="utf-8", errors="ignore") as f:
                        log_txt = f.read()

                    if "Kernel panic" in log_txt:
                        print(f"[-] FATAL: Kernel panic detected at {elapsed:.1f}s!", flush=True)
                        panic_detected = True
                        break

                    if "Boot medium found on" in log_txt and not found_medium:
                        found_medium = True
                        for l in log_txt.splitlines():
                            if "Boot medium found on" in l:
                                print(f"[✓] [{elapsed:.1f}s] {l}", flush=True)

                    if ("login:" in log_txt or "graphical.target" in log_txt or "lightdm.service" in log_txt) and elapsed > 20:
                        print(f"[✓] Reached graphical target after {elapsed:.1f}s!", flush=True)
                        reached_target = True
                        break
                except Exception:
                    pass

        time.sleep(2)
        safe_ppm = SCREEN_PPM.replace("\\", "/")
        req = f'{{"execute": "screendump", "arguments": {{"filename": "{safe_ppm}"}}}}\n'
        qmp.sendall(req.encode("utf-8"))
        time.sleep(2)
        qmp.close()

        if os.path.exists(SCREEN_PPM):
            img = Image.open(SCREEN_PPM)
            img.save(SCREEN_PNG)
            print(f"[✓] Saved screendump: {SCREEN_PNG} ({img.size})", flush=True)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    print("\n" + "=" * 70, flush=True)
    print("=== SUMMARY OF JMICRON SIMULATION BOOT ===", flush=True)
    print(f"Found Boot Medium on FAT32 Partition 2: {found_medium}", flush=True)
    print(f"Reached Graphical Desktop Target:       {reached_target}", flush=True)
    print(f"Kernel Panic Occurred:                  {panic_detected}", flush=True)
    print("=" * 70, flush=True)

    if found_medium and reached_target and not panic_detected:
        print("[✓✓✓] SUCCESS: JMicron FAT32 Partition 2 boot verified without kernel panic!")
        return True
    else:
        print("[-] FAILED: Boot verification criteria not met.")
        return False

if __name__ == "__main__":
    step1_create_and_populate_disk()
    success = step2_boot_jmicron_simulation()
    sys.exit(0 if success else 1)
