#!/usr/bin/env python3
"""
Test UEFI & BIOS Boot for MONODESK OS 2.0.1-rc2 ISO
"""
import os
import sys
import time
import socket
import pathlib
import subprocess
from PIL import Image

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
OVMF = r"C:\Program Files\qemu\share\edk2-x86_64-code.fd"
ISO = r"D:\anti\monodesk-os\releases\monodesk-os-2.0.1-rc2-universal-amd64.iso"
OUT_DIR = r"D:\anti\monodesk-os\artifacts\qa"
UEFI_LOG = os.path.join(OUT_DIR, "v201_rc2_uefi_boot.log")
UEFI_PPM = os.path.join(OUT_DIR, "v201_rc2_uefi_screen.ppm")
UEFI_PNG = os.path.join(OUT_DIR, "v201_rc2_uefi_screen.png")

def test_uefi_boot():
    print("=" * 70)
    print("[*] Testing UEFI Boot with MONODESK OS 2.0.1-rc2 ISO...")
    print("=" * 70)
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(UEFI_LOG):
        os.remove(UEFI_LOG)
    if os.path.exists(UEFI_PPM):
        os.remove(UEFI_PPM)

    cmd = [
        QEMU,
        "-accel", "whpx",
        "-m", "4096",
        "-smp", "4",
        "-drive", f"if=pflash,format=raw,readonly=on,file={OVMF}",
        "-cdrom", ISO,
        "-boot", "d",
        "-vga", "virtio",
        "-serial", f"file:{UEFI_LOG}",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5571,server,nowait"
    ]

    start_t = time.time()
    proc = subprocess.Popen(cmd)
    try:
        time.sleep(3)
        qmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        qmp.connect(("127.0.0.1", 5571))
        qmp.recv(1024)
        qmp.sendall(b'{"execute": "qmp_capabilities"}\n')
        qmp.recv(1024)
        print("[✓] QMP connected.", flush=True)

        reached_steady = False
        for i in range(75):
            time.sleep(1)
            elapsed = time.time() - start_t
            if os.path.exists(UEFI_LOG):
                try:
                    with open(UEFI_LOG, "r", encoding="utf-8", errors="ignore") as f:
                        log_txt = f.read()
                    if ("Kernel panic" in log_txt):
                        print(f"[-] FATAL: Kernel panic detected in log at {elapsed:.1f}s!", flush=True)
                        break
                    if ("login:" in log_txt or "monodesk" in log_txt or "graphical.target" in log_txt) and elapsed > 40:
                        print(f"[✓] Reached graphical/login target after {elapsed:.1f}s!", flush=True)
                        reached_steady = True
                        break
                except Exception:
                    pass
            if i % 10 == 0:
                print(f"    Elapsed: {elapsed:.1f}s...", flush=True)

        time.sleep(5)
        safe_ppm = UEFI_PPM.replace("\\", "/")
        req = f'{{"execute": "screendump", "arguments": {{"filename": "{safe_ppm}"}}}}\n'
        qmp.sendall(req.encode("utf-8"))
        time.sleep(2)
        qmp.close()

        if os.path.exists(UEFI_PPM):
            img = Image.open(UEFI_PPM)
            img.save(UEFI_PNG)
            print(f"[✓] Saved UEFI screendump: {UEFI_PNG} ({img.size})", flush=True)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    if os.path.exists(UEFI_LOG):
        print(f"[✓] UEFI serial log size: {os.path.getsize(UEFI_LOG)} bytes", flush=True)
        with open(UEFI_LOG, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"[*] Last 20 lines of UEFI serial log:")
        for line in lines[-20:]:
            print("  |", line.strip())

if __name__ == "__main__":
    test_uefi_boot()
