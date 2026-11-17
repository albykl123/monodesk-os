import os
import sys
import time
import socket
import json
import subprocess
from PIL import Image

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
OVMF = r"C:\Program Files\qemu\share\edk2-x86_64-code.fd"
ISO = r"D:\anti\monodesk-os\releases\monodesk-os-2.0.1-rc1-universal-amd64.iso"
OUT_DIR = r"D:\anti\monodesk-os\artifacts\qa"
SERIAL_LOG = os.path.join(OUT_DIR, "live_uefi_boot.log")
SCREEN_PPM = os.path.join(OUT_DIR, "live_uefi_screen.ppm")
SCREEN_PNG = os.path.join(OUT_DIR, "live_uefi_screen.png")

def test_live_uefi_boot():
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(SERIAL_LOG):
        os.remove(SERIAL_LOG)
    if os.path.exists(SCREEN_PPM):
        os.remove(SCREEN_PPM)

    cmd = [
        QEMU,
        "-accel", "whpx",
        "-m", "4096",
        "-smp", "4",
        "-drive", f"if=pflash,format=raw,readonly=on,file={OVMF}",
        "-cdrom", ISO,
        "-boot", "d",
        "-serial", f"file:{SERIAL_LOG}",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5565,server,nowait"
    ]

    print("[*] Launching QEMU UEFI Live Boot...", flush=True)
    proc = subprocess.Popen(cmd)
    qmp = None
    try:
        time.sleep(3)
        qmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        qmp.connect(("127.0.0.1", 5565))
        qmp.recv(1024)
        qmp.sendall(b'{"execute": "qmp_capabilities"}\n')
        qmp.recv(1024)
        print("[✓] QMP connected.", flush=True)

        # Wait for GRUB menu (timeout is 5 seconds) then kernel boot
        print("[*] Waiting 35 seconds for live boot to proceed...", flush=True)
        for i in range(35):
            time.sleep(1)
            if i % 5 == 0:
                print(f"    Elapsed: {i}s...", flush=True)

        # Capture screendump
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

    if os.path.exists(SERIAL_LOG):
        print(f"[✓] Serial log captured: {os.path.getsize(SERIAL_LOG)} bytes", flush=True)
        with open(SERIAL_LOG, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"[*] Total log lines: {len(lines)}", flush=True)
        for line in lines[-20:]:
            print("  |", line.strip())

if __name__ == "__main__":
    test_live_uefi_boot()
