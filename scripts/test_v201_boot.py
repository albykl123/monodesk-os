#!/usr/bin/env python3
"""
Test UEFI & BIOS Boot for MONODESK OS 2.0.1-rc1 ISO
"""
import os
import sys
import time
import json
import socket
import pathlib
import subprocess

QEMU_EXE = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
OVMF = r"C:\Program Files\qemu\share\edk2-x86_64-code.fd"
ISO = r"D:\anti\monodesk-os\releases\monodesk-os-2.0.1-rc1-universal-amd64.iso"
OUT_DIR = r"D:\anti\monodesk-os\docs\diagnostics"

def read_json_line(sock, match_keys):
    buf = ""
    sock.settimeout(15.0)
    while True:
        try:
            chunk = sock.recv(1024).decode("utf-8", errors="ignore")
        except socket.timeout:
            return None
        if not chunk:
            return None
        buf += chunk
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                if any(k in msg for k in match_keys):
                    return msg
            except json.JSONDecodeError:
                pass

def test_uefi_boot():
    print("[*] Testing UEFI Boot (x86_64 EDK2/OVMF)...")
    pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    dump_ppm = os.path.join(OUT_DIR, "v201_uefi_grub.ppm")
    if os.path.exists(dump_ppm):
        os.remove(dump_ppm)

    cmd = [
        QEMU_EXE,
        "-m", "2048",
        "-smp", "2",
        "-drive", f"if=pflash,format=raw,readonly=on,file={OVMF}",
        "-cdrom", ISO,
        "-boot", "d",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5560,server,nowait"
    ]
    proc = subprocess.Popen(cmd)
    try:
        time.sleep(3)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 5560))
        read_json_line(sock, ["QMP"])
        sock.sendall(b'{"execute": "qmp_capabilities"}\n')
        read_json_line(sock, ["return"])

        # Wait for GRUB menu to draw
        time.sleep(6)
        ppm_esc = dump_ppm.replace("\\", "/")
        sock.sendall(f'{{"execute": "screendump", "arguments": {{"filename": "{ppm_esc}"}}}}\n'.encode("utf-8"))
        read_json_line(sock, ["return"])
        sock.close()

        if os.path.exists(dump_ppm) and os.path.getsize(dump_ppm) > 10000:
            print(f"[✓] UEFI Boot SUCCESS: Screendump saved to {dump_ppm} ({os.path.getsize(dump_ppm)} bytes)")
            return True
        else:
            print("[-] UEFI Screendump was empty or missing.")
            return False
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

def test_bios_boot():
    print("[*] Testing Legacy BIOS Boot (El Torito)...")
    dump_ppm = os.path.join(OUT_DIR, "v201_bios_grub.ppm")
    if os.path.exists(dump_ppm):
        os.remove(dump_ppm)

    cmd = [
        QEMU_EXE,
        "-m", "2048",
        "-smp", "2",
        "-cdrom", ISO,
        "-boot", "d",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5561,server,nowait"
    ]
    proc = subprocess.Popen(cmd)
    try:
        time.sleep(2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 5561))
        read_json_line(sock, ["QMP"])
        sock.sendall(b'{"execute": "qmp_capabilities"}\n')
        read_json_line(sock, ["return"])

        time.sleep(5)
        ppm_esc = dump_ppm.replace("\\", "/")
        sock.sendall(f'{{"execute": "screendump", "arguments": {{"filename": "{ppm_esc}"}}}}\n'.encode("utf-8"))
        read_json_line(sock, ["return"])
        sock.close()

        if os.path.exists(dump_ppm) and os.path.getsize(dump_ppm) > 10000:
            print(f"[✓] Legacy BIOS Boot SUCCESS: Screendump saved to {dump_ppm} ({os.path.getsize(dump_ppm)} bytes)")
            return True
        else:
            print("[-] BIOS Screendump was empty or missing.")
            return False
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    u_ok = test_uefi_boot()
    b_ok = test_bios_boot()
    if u_ok and b_ok:
        print("[✓] ALL BOOT TESTS PASSED (UEFI + BIOS)")
        sys.exit(0)
    else:
        print("[-] One or more boot tests failed.")
        sys.exit(1)
