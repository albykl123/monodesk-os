import subprocess
import time
import socket

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
BUILDER_QCOW2 = r"C:\anti\debian-builder.qcow2"
SSH_KEY = r"C:\anti\builder_key"

SSH_BASE = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5", "-i", SSH_KEY, "-p", "2222", "root@127.0.0.1"
]

def start_builder():
    qemu_cmd = [
        QEMU, "-accel", "whpx", "-m", "4096", "-smp", "4",
        "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
        "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
        "-device", "virtio-net-pci,netdev=net0",
        "-display", "none"
    ]
    print("[*] Starting Builder VM...", flush=True)
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

        # Check Hyprland, Qt6, quickshell inside Builder VM
        res = subprocess.run(SSH_BASE + ["which Hyprland hyprland quickshell qml6 python3 xfwm4 xfce4-panel 2>&1"], capture_output=True, text=True)
        print("[*] Installed binaries in Builder VM:\n", res.stdout)

        # Check PyQt6 in Python 3
        res = subprocess.run(SSH_BASE + ["python3 -c 'import PyQt6; print(PyQt6)' 2>&1"], capture_output=True, text=True)
        print("[*] Python3 PyQt6 check:\n", res.stdout)

    finally:
        print("[*] Shutting down Builder VM...", flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    start_builder()
