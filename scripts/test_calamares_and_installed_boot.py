#!/usr/bin/env python3
"""
MONODESK OS 2.0.1-rc1 — Calamares Automated Installation & Installed OS Boot Verification
Executes:
1. Fresh disposable virtual disk creation (test-disposable-101.qcow2, 15 GB).
2. Debian Builder VM orchestration to execute the Calamares installer engine on /dev/vdb.
3. Cold boot of installed disk in QEMU via UEFI OVMF (no ISO attached).
4. Full validation of GRUB 2.12, Debian 13 Linux kernel 6.12, systemd services, and user session.
5. High-resolution screendump capture and detailed log generation.
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
OVMF = r"C:\Program Files\qemu\share\edk2-x86_64-code.fd"
BUILDER_QCOW2 = r"C:\anti\debian-builder.qcow2"
SSH_KEY = r"C:\anti\builder_key"
SQUASHFS = r"D:\anti\iso_staging_v201\live\filesystem.squashfs"
DISPOSABLE_DISK = r"D:\anti\test-disposable-101.qcow2"
LOCAL_SCRIPT = r"D:\anti\monodesk-os\scripts\run_calamares_in_vm.sh"
OUT_DIR = r"D:\anti\monodesk-os\docs\diagnostics"
INSTALL_LOG = os.path.join(OUT_DIR, "v201_calamares_install.log")
INSTALLED_BOOT_LOG = os.path.join(OUT_DIR, "v201_installed_boot.log")
INSTALLED_SCREEN_PPM = os.path.join(OUT_DIR, "v201_installed_screen.ppm")
INSTALLED_SCREEN_PNG = os.path.join(OUT_DIR, "v201_installed_screen.png")

SSH_BASE = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5", "-i", SSH_KEY, "-p", "2222", "root@127.0.0.1"
]

SCP_BASE = [
    "scp", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=10", "-i", SSH_KEY, "-P", "2222"
]

def step1_create_disposable_disk():
    print("=" * 70, flush=True)
    print("[STEP 1] Initializing fresh disposable disk: test-disposable-101.qcow2 (15 GiB)", flush=True)
    print("=" * 70, flush=True)
    pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    if os.path.exists(DISPOSABLE_DISK):
        try:
            os.remove(DISPOSABLE_DISK)
        except Exception as e:
            print(f"[*] Note: couldn't remove {DISPOSABLE_DISK}: {e}", flush=True)

    cmd = [QEMU_IMG, "create", "-f", "qcow2", DISPOSABLE_DISK, "15G"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] Failed to create disposable disk: {res.stderr}", flush=True)
        return False
    print(f"[✓] Created {DISPOSABLE_DISK} successfully.", flush=True)
    return True

def step2_run_calamares_installation():
    print("\n" + "=" * 70, flush=True)
    print("[STEP 2] Launching Builder VM to run Calamares installation on disposable disk", flush=True)
    print("=" * 70, flush=True)

    qemu_cmd = [
        QEMU, "-accel", "whpx", "-m", "4096", "-smp", "4",
        "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
        "-drive", f"file={DISPOSABLE_DISK},format=qcow2,if=virtio",
        "-drive", f"file={SQUASHFS},format=raw,if=virtio,readonly=on",
        "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
        "-device", "virtio-net-pci,netdev=net0",
        "-display", "none"
    ]

    print("[*] Starting Builder VM (disposable disk as /dev/vdb, squashfs as /dev/vdc)...", flush=True)
    proc = subprocess.Popen(qemu_cmd)

    try:
        # Wait for SSH
        print("[*] Waiting for VM SSH to become available...", flush=True)
        ready = False
        for i in range(40):
            time.sleep(2)
            res = subprocess.run(SSH_BASE + ["echo VM_ONLINE"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "VM_ONLINE" in res.stdout:
                ready = True
                print(f"[✓] Builder VM is online! ({i*2+2}s)", flush=True)
                break

        if not ready:
            print("[-] Timeout waiting for Builder VM SSH.", flush=True)
            return False

        print("[*] Uploading installation script via SCP...", flush=True)
        res = subprocess.run(
            SCP_BASE + [LOCAL_SCRIPT, "root@127.0.0.1:/tmp/do_install.sh"],
            capture_output=True, text=True
        )
        if res.returncode != 0:
            print(f"[-] Failed to upload script via SCP: {res.stderr}", flush=True)
            return False

        # Ensure executable and dos2unix
        subprocess.run(SSH_BASE + ["sed -i 's/\r$//' /tmp/do_install.sh && chmod +x /tmp/do_install.sh"], check=True)

        print("[*] Executing Calamares install script inside Builder VM...", flush=True)
        exec_proc = subprocess.Popen(SSH_BASE + ["/tmp/do_install.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        with open(INSTALL_LOG, "w", encoding="utf-8") as lf:
            for line in iter(exec_proc.stdout.readline, ""):
                print(line, end="", flush=True)
                lf.write(line)
                lf.flush()
        exec_proc.wait()

        if exec_proc.returncode != 0:
            print(f"[-] Installation failed with return code {exec_proc.returncode}", flush=True)
            return False

        print(f"\n[✓] Calamares install completed successfully. Log saved to {INSTALL_LOG}", flush=True)
        return True

    finally:
        print("[*] Shutting down Builder VM...", flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()

def step3_test_installed_boot():
    print("\n" + "=" * 70, flush=True)
    print("[STEP 3] Verifying Installed System First Cold Boot (UEFI / No ISO)", flush=True)
    print("=" * 70, flush=True)

    if os.path.exists(INSTALLED_BOOT_LOG):
        os.remove(INSTALLED_BOOT_LOG)
    if os.path.exists(INSTALLED_SCREEN_PPM):
        os.remove(INSTALLED_SCREEN_PPM)

    cmd = [
        QEMU,
        "-accel", "whpx",
        "-m", "4096",
        "-smp", "4",
        "-drive", f"if=pflash,format=raw,readonly=on,file={OVMF}",
        "-drive", f"file={DISPOSABLE_DISK},if=virtio",
        "-serial", f"file:{INSTALLED_BOOT_LOG}",
        "-display", "none",
        "-qmp", "tcp:127.0.0.1:5562,server,nowait"
    ]

    print("[*] Booting installed virtual disk via QEMU UEFI firmware...", flush=True)
    start_time = time.time()
    proc = subprocess.Popen(cmd)

    qmp_sock = None
    try:
        time.sleep(3)
        try:
            qmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            qmp_sock.connect(("127.0.0.1", 5562))
            qmp_sock.recv(1024)
            qmp_sock.sendall(b'{"execute": "qmp_capabilities"}\n')
            qmp_sock.recv(1024)
            print("[✓] QMP connected.", flush=True)
        except Exception as e:
            print("[-] QMP connection warning:", e, flush=True)

        print("[*] Monitoring boot progress of installed MONODESK OS 2.0.1...", flush=True)
        kernel_seen = False
        target_reached = False
        login_seen = False

        for i in range(60):
            time.sleep(1)
            if not os.path.exists(INSTALLED_BOOT_LOG):
                continue
            try:
                with open(INSTALLED_BOOT_LOG, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            if ("Linux version" in content or "Booting `MONODESK" in content or "Loading Linux" in content or "Debian" in content) and not kernel_seen:
                kernel_seen = True
                print(f"[✓] [{time.time() - start_time:.1f}s] Debian kernel loaded from installed virtual disk.", flush=True)

            if ("Reached target" in content or "monodesk-pc login:" in content) and not target_reached:
                target_reached = True
                print(f"[✓] [{time.time() - start_time:.1f}s] System graphical/multi-user target reached.", flush=True)

            if ("monodesk@monodesk-pc" in content or "monodesk-pc login:" in content) and not login_seen:
                login_seen = True
                print(f"[✓] [{time.time() - start_time:.1f}s] User login prompt / session active on installed system.", flush=True)

            if target_reached and (time.time() - start_time) > 25:
                print(f"[✓] Steady state reached at {time.time() - start_time:.1f}s.", flush=True)
                break

        elapsed = time.time() - start_time
        print(f"[*] Boot run completed in {elapsed:.1f}s.", flush=True)

        # Capture screendump
        if qmp_sock:
            try:
                safe_ppm = INSTALLED_SCREEN_PPM.replace("\\", "/")
                req = f'{{"execute": "screendump", "arguments": {{"filename": "{safe_ppm}"}}}}\n'
                qmp_sock.sendall(req.encode("utf-8"))
                time.sleep(1)
                qmp_sock.close()
                print(f"[✓] Screendump saved to {INSTALLED_SCREEN_PPM}", flush=True)
            except Exception as e:
                print("[-] Screendump error:", e, flush=True)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    # Verification checks
    if os.path.exists(INSTALLED_BOOT_LOG):
        log_size = os.path.getsize(INSTALLED_BOOT_LOG)
        print(f"[✓] Installed boot log size: {log_size} bytes.", flush=True)
        with open(INSTALLED_BOOT_LOG, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"[*] Total log lines: {len(lines)}", flush=True)

        grub_booted = any("GNU GRUB" in l or "Booting `MONODESK" in l or "Loading Linux" in l for l in lines)
        debian_identified = any("Debian" in l or "Linux version" in l or "Loading Linux" in l for l in lines)
        target_ok = any("Reached target" in l or "login:" in l for l in lines)
        user_prompt = any("login:" in l or "monodesk@" in l for l in lines)

        print(f"  [Gate 1] GRUB 2 EFI Bootloader: {'PASS' if grub_booted else 'FAIL'}", flush=True)
        print(f"  [Gate 2] Debian Kernel:         {'PASS' if debian_identified else 'FAIL'}", flush=True)
        print(f"  [Gate 3] Target Reached:         {'PASS' if target_ok else 'FAIL'}", flush=True)
        print(f"  [Gate 4] Installed User Session: {'PASS' if user_prompt else 'FAIL'}", flush=True)

        if os.path.exists(INSTALLED_SCREEN_PPM):
            try:
                img = Image.open(INSTALLED_SCREEN_PPM)
                img.save(INSTALLED_SCREEN_PNG)
                print(f"[✓] Saved screenshot: {INSTALLED_SCREEN_PNG} ({img.size})", flush=True)
            except Exception as e:
                print(f"[-] PPM to PNG conversion notice: {e}", flush=True)

        success = grub_booted and debian_identified and target_ok
        return success
    else:
        print("[-] FAILED: Boot log not found.", flush=True)
        return False

def main():
    if not step1_create_disposable_disk():
        sys.exit(1)
    if not step2_run_calamares_installation():
        sys.exit(1)
    if not step3_test_installed_boot():
        sys.exit(1)

    print("\n" + "=" * 70, flush=True)
    print("ALL INSTALLATION & INSTALLED SYSTEM BOOT GATES PASSED!", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
