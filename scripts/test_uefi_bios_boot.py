import os
import sys
import time
import json
import socket
import subprocess

QEMU_EXE = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
OVMF = r"C:\Program Files\qemu\share\edk2-x86_64-code.fd"
ISO = r"D:\anti\monodesk-os\releases\monodesk-os-2.0.0-universal-amd64.iso"
OUT_DIR = r"C:\anti\iso_boot_test"

def read_json_line(sock, match_keys):
    buf = ""
    sock.settimeout(15.0)
    while True:
        try:
            chunk = sock.recv(1024).decode("utf-8", errors="ignore")
        except socket.timeout:
            print("[QMP] Read timeout!")
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
    dump_ppm = os.path.join(OUT_DIR, "uefi_grub.ppm")
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
        "-qmp", "tcp:127.0.0.1:5558,server,nowait"
    ]

    print("[UEFI Test] Starting QEMU with OVMF...")
    proc = subprocess.Popen(cmd)
    try:
        time.sleep(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 5558))
        greeting = read_json_line(s, ["QMP"])
        print("[UEFI Test] QMP greeting received:", greeting)
        
        s.sendall(b'{"execute": "qmp_capabilities"}\n')
        resp = read_json_line(s, ["return", "error"])
        print("[UEFI Test] QMP capabilities negotiated:", resp)

        print("[UEFI Test] Waiting for OVMF and GRUB 2 to load (12s)...")
        time.sleep(12)

        safe_ppm = dump_ppm.replace("\\", "/")
        req = json.dumps({"execute": "screendump", "arguments": {"filename": safe_ppm}}) + "\n"
        s.sendall(req.encode("utf-8"))
        res = read_json_line(s, ["return", "error"])
        print("[UEFI Test] Screendump result:", res)
        time.sleep(1)
        s.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    if os.path.exists(dump_ppm) and os.path.getsize(dump_ppm) > 0:
        print(f"[UEFI Test] SUCCESS: UEFI GRUB screendump created ({os.path.getsize(dump_ppm)} bytes) at {dump_ppm}")
        return True
    else:
        print(f"[UEFI Test] FAILED: Screendump file not created or empty.")
        return False

def test_bios_boot():
    dump_ppm = os.path.join(OUT_DIR, "bios_boot.ppm")
    if os.path.exists(dump_ppm):
        os.remove(dump_ppm)

    cmd = [
        QEMU_EXE,
        "-m", "2048",
        "-smp", "2",
        "-cdrom", ISO,
        "-boot", "d",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5559,server,nowait"
    ]

    print("[BIOS Test] Starting QEMU with Legacy BIOS...")
    proc = subprocess.Popen(cmd)
    try:
        time.sleep(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 5559))
        greeting = read_json_line(s, ["QMP"])
        print("[BIOS Test] QMP greeting received:", greeting)
        
        s.sendall(b'{"execute": "qmp_capabilities"}\n')
        resp = read_json_line(s, ["return", "error"])
        print("[BIOS Test] QMP capabilities negotiated:", resp)

        print("[BIOS Test] Waiting for BIOS and bootloader to load (6s)...")
        time.sleep(6)

        safe_ppm = dump_ppm.replace("\\", "/")
        req = json.dumps({"execute": "screendump", "arguments": {"filename": safe_ppm}}) + "\n"
        s.sendall(req.encode("utf-8"))
        res = read_json_line(s, ["return", "error"])
        print("[BIOS Test] Screendump result:", res)
        time.sleep(1)
        s.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    if os.path.exists(dump_ppm) and os.path.getsize(dump_ppm) > 0:
        print(f"[BIOS Test] SUCCESS: BIOS screendump created ({os.path.getsize(dump_ppm)} bytes) at {dump_ppm}")
        return True
    else:
        print(f"[BIOS Test] FAILED: Screendump file not created or empty.")
        return False

if __name__ == "__main__":
    uefi_ok = test_uefi_boot()
    bios_ok = test_bios_boot()
    if uefi_ok and bios_ok:
        print("\n=== BOTH UEFI AND BIOS BOOT TESTS PASSED ===")
        sys.exit(0)
    else:
        print(f"\n=== TEST FAILED: uefi={uefi_ok}, bios={bios_ok} ===")
        sys.exit(1)
