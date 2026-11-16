import os
import sys
import time
import json
import socket
import subprocess
from PIL import Image

QEMU_EXE = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
OVMF = r"C:\Program Files\qemu\share\edk2-x86_64-code.fd"
DISK = r"C:\anti\iso_boot_test\target_disk.qcow2"
OUT_DIR = r"C:\anti\iso_boot_test"
LOG_FILE = os.path.join(OUT_DIR, "installed_boot.log")
SCREEN_PPM = os.path.join(OUT_DIR, "installed_desktop.ppm")

def test_installed_boot():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.exists(SCREEN_PPM):
        os.remove(SCREEN_PPM)

    cmd = [
        QEMU_EXE,
        "-accel", "whpx",
        "-m", "4096",
        "-smp", "4",
        "-drive", f"if=pflash,format=raw,readonly=on,file={OVMF}",
        "-drive", f"file={DISK},if=virtio",
        "-serial", f"file:{LOG_FILE}",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5562,server,nowait"
    ]

    print("[Installed Boot Test] Starting QEMU booting installed disk (no ISO attached)...")
    start_time = time.time()
    proc = subprocess.Popen(cmd)

    qmp_sock = None
    try:
        time.sleep(2)
        try:
            qmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            qmp_sock.connect(("127.0.0.1", 5562))
            qmp_sock.recv(1024)
            qmp_sock.sendall(b'{"execute": "qmp_capabilities"}\n')
            qmp_sock.recv(1024)
            print("[Installed Boot Test] QMP connected.")
        except Exception as e:
            print("[Installed Boot Test] QMP connection notice:", e)

        print("[Installed Boot Test] Monitoring boot of installed OS...")
        kernel_seen = False
        target_reached = False
        services_seen = False

        for i in range(50):
            time.sleep(1)
            if not os.path.exists(LOG_FILE):
                continue
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            if ("Linux version" in content or "Booting `MONODESK'" in content or "Debian GNU/Linux" in content) and not kernel_seen:
                kernel_seen = True
                print(f"[Installed Boot Test] [{time.time() - start_time:.1f}s] Debian 13 kernel loaded from installed virtual disk.")

            if ("Reached target" in content or "monodesk-pc login:" in content) and not target_reached:
                target_reached = True
                print(f"[Installed Boot Test] [{time.time() - start_time:.1f}s] System target reached.")

            if any(s in content for s in ["lightdm", "pipewire", "monodesk", "login:"]) and not services_seen:
                services_seen = True
                print(f"[Installed Boot Test] [{time.time() - start_time:.1f}s] Core system services active on installed system.")

            if target_reached and (time.time() - start_time) > 25:
                print(f"[Installed Boot Test] Installed OS reached steady state at {time.time() - start_time:.1f}s.")
                break

        elapsed = time.time() - start_time
        print(f"[Installed Boot Test] Total run time: {elapsed:.1f}s.")

        # Capture screendump
        if qmp_sock:
            try:
                safe_ppm = SCREEN_PPM.replace("\\", "/")
                req = json.dumps({"execute": "screendump", "arguments": {"filename": safe_ppm}}) + "\n"
                qmp_sock.sendall(req.encode("utf-8"))
                time.sleep(1)
                qmp_sock.close()
            except Exception as e:
                print("[Installed Boot Test] Screendump request error:", e)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    if os.path.exists(LOG_FILE):
        log_size = os.path.getsize(LOG_FILE)
        print(f"[Installed Boot Test] Installed boot log captured: {log_size} bytes.")
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"[Installed Boot Test] Total lines: {len(lines)}")
        
        # Check success criteria
        grub_booted = any("GNU GRUB" in l for l in lines)
        login_reached = any("login:" in l for l in lines)
        debian_identified = any("Debian GNU/Linux 13" in l for l in lines)

        print(f"  GRUB 2 booted: {grub_booted}")
        print(f"  Debian 13 identified: {debian_identified}")
        print(f"  Login prompt reached: {login_reached}")

        if os.path.exists(SCREEN_PPM):
            img = Image.open(SCREEN_PPM)
            png_path = SCREEN_PPM.replace(".ppm", ".png")
            img.save(png_path)
            print(f"[Installed Boot Test] Framebuffer screendump saved: {png_path} ({img.size})")

        return grub_booted and login_reached and debian_identified
    else:
        print("[Installed Boot Test] FAILED: Log not found.")
        return False

if __name__ == "__main__":
    ok = test_installed_boot()
    sys.exit(0 if ok else 1)
