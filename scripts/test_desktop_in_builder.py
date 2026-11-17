import subprocess
import time
import os
import pathlib

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
BUILDER_QCOW2 = r"C:\anti\debian-builder.qcow2"
SSH_KEY = r"C:\anti\builder_key"

SSH_BASE = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5", "-i", SSH_KEY, "-p", "2222", "root@127.0.0.1"
]
SCP_BASE = [
    "scp", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=10", "-i", SSH_KEY, "-P", "2222"
]

def run_test():
    qemu_cmd = [
        QEMU, "-accel", "whpx", "-m", "4096", "-smp", "4",
        "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
        "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
        "-device", "virtio-net-pci,netdev=net0",
        "-display", "none"
    ]
    print("[*] Starting Builder VM for Desktop & QML verification...", flush=True)
    proc = subprocess.Popen(qemu_cmd)
    try:
        ready = False
        for i in range(25):
            time.sleep(2)
            res = subprocess.run(SSH_BASE + ["echo BUILDER_READY"], capture_output=True, text=True)
            if "BUILDER_READY" in res.stdout:
                ready = True
                print(f"[✓] Builder VM online after {i*2+2}s!", flush=True)
                break
        if not ready:
            print("[-] Builder VM failed to respond to SSH.")
            return

        # 1. Package check
        res = subprocess.run(SSH_BASE + ["dpkg -l | grep -E 'pyqt6|qml6|xvfb|xdotool|imagemagick'"], capture_output=True, text=True)
        print("[*] Packages in Builder VM:\n", res.stdout)

        # 2. Check if xvfb is installed, if not install it
        if "xvfb" not in res.stdout:
            print("[*] Installing xvfb and xdotool in Builder VM...", flush=True)
            subprocess.run(SSH_BASE + ["apt-get update && apt-get install -y xvfb xdotool"], check=False)

        # 3. Create /usr/share/monodesk directory structure
        subprocess.run(SSH_BASE + ["mkdir -p /usr/share/monodesk /usr/share/backgrounds/monodesk /artifacts/qa"], check=True)

        # 4. Upload local monodesk shell and applications
        print("[*] Packaging repository shell assets and uploading to VM...", flush=True)
        tar_cmd = ["tar", "-czf", "D:/anti/monodesk_shell_staging.tar.gz",
                   "-C", "D:/anti/monodesk-os", "desktop", "themes", "shell", "branding", "applications"]
        subprocess.run(tar_cmd, check=True)

        subprocess.run(SCP_BASE + ["D:/anti/monodesk_shell_staging.tar.gz", "root@127.0.0.1:/tmp/"], check=True)
        subprocess.run(SSH_BASE + ["tar -xzf /tmp/monodesk_shell_staging.tar.gz -C /usr/share/monodesk/"], check=True)
        subprocess.run(SSH_BASE + [
            "cp -r /usr/share/monodesk/desktop/* /usr/share/monodesk/ 2>/dev/null || true;"
            "cp -r /usr/share/monodesk/branding/wallpapers/* /usr/share/backgrounds/monodesk/ 2>/dev/null || true;"
            "mkdir -p /etc/monodesk && echo 'PROFILE=standard' > /etc/monodesk/profile.conf"
        ], check=True)

        # 5. Run --check on monodesk_shell.py
        print("[*] Running monodesk_shell.py --check...", flush=True)
        res = subprocess.run(SSH_BASE + [
            "python3 /usr/share/monodesk/desktop/shell/monodesk_shell.py --check"
        ], capture_output=True, text=True)
        print("Stdout:\n", res.stdout)
        print("Stderr:\n", res.stderr)
        print(f"Exit code: {res.returncode}")

    finally:
        print("[*] Shutting down Builder VM...", flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    run_test()
