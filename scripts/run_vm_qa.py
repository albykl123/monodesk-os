import subprocess
import time
import os
import shutil

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
BUILDER_QCOW2 = r"C:\anti\debian-builder.qcow2"
SSH_KEY = r"C:\anti\builder_key"
LOCAL_RUNNER = r"D:\anti\monodesk-os\scripts\vm_qa_runner.py"
OUT_DIR = r"D:\anti\monodesk-os\artifacts\qa"

SSH_BASE = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5", "-i", SSH_KEY, "-p", "2222", "root@127.0.0.1"
]
SCP_BASE = [
    "scp", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=10", "-i", SSH_KEY, "-P", "2222"
]

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # 1. Check if VM is already running on port 2222
    vm_already_up = False
    chk = subprocess.run(SSH_BASE + ["echo VM_ALIVE"], capture_output=True, text=True)
    if "VM_ALIVE" in chk.stdout:
        print("[✓] Builder VM is already running!", flush=True)
        vm_already_up = True
        proc = None
    else:
        print("[*] Launching Builder VM...", flush=True)
        qemu_cmd = [
            QEMU, "-accel", "whpx", "-m", "4096", "-smp", "4",
            "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
            "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
            "-device", "virtio-net-pci,netdev=net0",
            "-display", "none"
        ]
        proc = subprocess.Popen(qemu_cmd)
        for i in range(25):
            time.sleep(2)
            chk = subprocess.run(SSH_BASE + ["echo VM_ALIVE"], capture_output=True, text=True)
            if "VM_ALIVE" in chk.stdout:
                print(f"[✓] Builder VM is online ({i*2+2}s)!", flush=True)
                break

    try:
        # Upload staged assets
        print("[*] Uploading shell assets...", flush=True)
        subprocess.run(SCP_BASE + ["D:/anti/monodesk_shell_staging.tar.gz", "root@127.0.0.1:/tmp/"], check=True)
        subprocess.run(SSH_BASE + [
            "mkdir -p /usr/share/monodesk /usr/share/backgrounds/monodesk /usr/share/applications && "
            "tar -xzf /tmp/monodesk_shell_staging.tar.gz -C /usr/share/monodesk/ && "
            "cp -r /usr/share/monodesk/desktop/* /usr/share/monodesk/ 2>/dev/null || true; "
            "cp -r /usr/share/monodesk/branding/wallpapers/* /usr/share/backgrounds/monodesk/ 2>/dev/null || true; "
            "mkdir -p /etc/monodesk && echo 'PROFILE=standard' > /etc/monodesk/profile.conf"
        ], check=True)

        # Upload runner
        print("[*] Uploading QA runner script...", flush=True)
        subprocess.run(SCP_BASE + [LOCAL_RUNNER, "root@127.0.0.1:/tmp/vm_qa_runner.py"], check=True)
        subprocess.run(SSH_BASE + ["chmod +x /tmp/vm_qa_runner.py"], check=True)

        # Execute QA
        print("[*] Running GUI QA runner in VM...", flush=True)
        p = subprocess.Popen(SSH_BASE + ["python3 /tmp/vm_qa_runner.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(p.stdout.readline, ""):
            print("  ", line, end="", flush=True)
        p.wait()

        if p.returncode != 0:
            print(f"[-] QA runner failed with code {p.returncode}")
            return False

        # Download tarball
        local_tar = "artifacts/qa/qa_screens.tar.gz"
        print("[*] Downloading captured screenshots...", flush=True)
        subprocess.run(SCP_BASE + ["root@127.0.0.1:/tmp/qa_screens.tar.gz", local_tar], check=True)
        subprocess.run(["tar", "-xzf", local_tar, "-C", "artifacts/qa"], check=True)

        sub_dir = os.path.join(OUT_DIR, "qa_screens")
        if os.path.exists(sub_dir):
            for f in os.listdir(sub_dir):
                shutil.move(os.path.join(sub_dir, f), os.path.join(OUT_DIR, f))
            os.rmdir(sub_dir)

        print("[✓] All QA screenshots successfully extracted to artifacts/qa/!")
        return True

    finally:
        if proc:
            print("[*] Shutting down Builder VM...", flush=True)
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except Exception:
                proc.kill()

if __name__ == "__main__":
    main()
