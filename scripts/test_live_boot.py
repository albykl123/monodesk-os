import os
import sys
import time
import json
import socket
import subprocess

QEMU_EXE = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
ISO = r"D:\anti\monodesk-os\releases\monodesk-os-2.0.0-universal-amd64.iso"
KERNEL = r"C:\anti\iso_boot_test\vmlinuz-6.12.117+deb13-amd64"
INITRD = r"C:\anti\iso_boot_test\initrd.img-6.12.117+deb13-amd64"
OUT_DIR = r"C:\anti\iso_boot_test"
SERIAL_LOG = os.path.join(OUT_DIR, "serial_boot.log")
SCREEN_PPM = os.path.join(OUT_DIR, "live_desktop.ppm")

def run_live_boot_test():
    if os.path.exists(SERIAL_LOG):
        os.remove(SERIAL_LOG)
    if os.path.exists(SCREEN_PPM):
        os.remove(SCREEN_PPM)

    cmd = [
        QEMU_EXE,
        "-accel", "whpx",
        "-m", "4096",
        "-smp", "4",
        "-kernel", KERNEL,
        "-initrd", INITRD,
        "-cdrom", ISO,
        "-append", "boot=live components console=tty0 console=ttyS0 loglevel=7 systemd.journald.forward_to_console=1",
        "-serial", f"file:{SERIAL_LOG}",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5560,server,nowait"
    ]

    print("[Live Boot] Launching QEMU with kernel, initrd, CD-ROM, and serial console capture...")
    start_time = time.time()
    proc = subprocess.Popen(cmd)
    
    qmp_sock = None
    try:
        time.sleep(2)
        try:
            qmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            qmp_sock.connect(("127.0.0.1", 5560))
            # Greeting
            data = qmp_sock.recv(1024)
            qmp_sock.sendall(b'{"execute": "qmp_capabilities"}\n')
            data = qmp_sock.recv(1024)
            print("[Live Boot] QMP connected and capabilities enabled.")
        except Exception as e:
            print("[Live Boot] QMP connection error (non-fatal):", e)

        # Monitor serial log until boot reaches target or timeout
        print("[Live Boot] Monitoring boot progress...")
        reached_target = False
        autologin_seen = False
        desktop_seen = False
        
        for i in range(90):  # up to 90 seconds
            time.sleep(1)
            if not os.path.exists(SERIAL_LOG):
                continue
            try:
                with open(SERIAL_LOG, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            if "Reached target" in content and not reached_target:
                reached_target = True
                print(f"[Live Boot] [{time.time() - start_time:.1f}s] Reached target detected.")

            if ("monodesk" in content or "login" in content or "autologin" in content) and not autologin_seen:
                if "login:" in content or "monodesk" in content:
                    autologin_seen = True
                    print(f"[Live Boot] [{time.time() - start_time:.1f}s] Autologin / user session activity detected.")

            if ("monodesk-session" in content or "quickshell" in content or "hyprland" in content or "openbox" in content) and not desktop_seen:
                desktop_seen = True
                print(f"[Live Boot] [{time.time() - start_time:.1f}s] Session routing / desktop process detected.")

            # If multi-user or graphical target reached and waited a bit
            if reached_target and (time.time() - start_time) > 35:
                print(f"[Live Boot] System reached steady state at {time.time() - start_time:.1f}s.")
                break

        boot_elapsed = time.time() - start_time
        print(f"[Live Boot] Boot test duration: {boot_elapsed:.1f} seconds.")

        # Take screendump
        if qmp_sock:
            try:
                safe_ppm = SCREEN_PPM.replace("\\", "/")
                req = json.dumps({"execute": "screendump", "arguments": {"filename": safe_ppm}}) + "\n"
                qmp_sock.sendall(req.encode("utf-8"))
                time.sleep(1)
                qmp_sock.close()
            except Exception as e:
                print("[Live Boot] Screendump request error:", e)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    # Analyze serial log
    if os.path.exists(SERIAL_LOG):
        log_size = os.path.getsize(SERIAL_LOG)
        print(f"[Live Boot] Serial log captured ({log_size} bytes).")
        with open(SERIAL_LOG, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"[Live Boot] Total serial log lines: {len(lines)}")
        
        # Look for key indicators
        warnings = [l.strip() for l in lines if "warning" in l.lower() or "fail" in l.lower()]
        acpi_notices = [l.strip() for l in lines if "acpi" in l.lower()]
        firmware_notices = [l.strip() for l in lines if "firmware" in l.lower()]
        session_lines = [l.strip() for l in lines if any(k in l.lower() for k in ["session", "monodesk", "lightdm", "autologin", "calamares", "profile"])]
        
        print("\n--- Boot Diagnostics Summary ---")
        print(f"Total lines: {len(lines)}")
        print(f"Firmware notices: {len(firmware_notices)}")
        print(f"ACPI notices: {len(acpi_notices)}")
        print(f"Warnings/Failures: {len(warnings)}")
        print(f"Session / Auth lines: {len(session_lines)}")
        
        return True
    else:
        print("[Live Boot] FAILED: No serial log created.")
        return False

if __name__ == "__main__":
    ok = run_live_boot_test()
    sys.exit(0 if ok else 1)
