import subprocess
import time
import os
import tarfile
import io

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
BUILDER_QCOW2 = r"C:\anti\debian-builder.qcow2"
SSH_KEY = r"C:\anti\builder_key"
OUT_DIR = r"D:\anti\monodesk-os\artifacts\qa"

SSH_BASE = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5", "-i", SSH_KEY, "-p", "2222", "root@127.0.0.1"
]
SCP_BASE = [
    "scp", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=10", "-i", SSH_KEY, "-P", "2222"
]

AUTOMATION_SCRIPT = """#!/usr/bin/env bash
set -e

export DISPLAY=:99
mkdir -p /tmp/qa_screens

echo "[QA] Checking dependencies..."
apt-get update >/dev/null 2>&1 || true
apt-get install -y imagemagick x11-utils python3-gi gir1.2-gtk-3.0 xdotool libxcb-cursor0 >/dev/null 2>&1 || true

# Kill any existing Xvfb or previous processes
killall Xvfb xfwm4 python3 2>/dev/null || true
sleep 1

# Start Xvfb at 1280x800
echo "[QA] Starting Xvfb at 1280x800..."
Xvfb :99 -screen 0 1280x800x24 -ac &
XVFB_PID=$!
sleep 2

# Start xfwm4 compositor
echo "[QA] Starting xfwm4 compositor..."
xfwm4 --compositor=on &
XFWM_PID=$!
sleep 2

echo "[QA] Starting MONODESK Shell..."
python3 /usr/share/monodesk/desktop/shell/monodesk_shell.py > /tmp/shell.log 2>&1 &
SHELL_PID=$!
sleep 4

echo "[QA] Shell Log:"
cat /tmp/shell.log

echo "[QA 1] Capturing Clean Desktop..."
import -window root -display :99 /tmp/qa_screens/01_desktop_clean.png

echo "[QA 2] Triggering Launcher via xdotool (Meta key)..."
xdotool key Super
sleep 2
import -window root -display :99 /tmp/qa_screens/02_launcher_open.png

echo "[QA 3] Typing search query in Launcher..."
xdotool type "Setting"
sleep 1
import -window root -display :99 /tmp/qa_screens/03_launcher_search.png

echo "[QA 4] Dismissing Launcher..."
xdotool key Escape
sleep 1

echo "[QA 5] Opening Control Centre (clicking toggle at bottom right)..."
xdotool mousemove 720 760 click 1
sleep 2
import -window root -display :99 /tmp/qa_screens/04_control_centre.png

echo "[QA 6] Launching Settings Hub..."
python3 /usr/share/monodesk/applications/settings/monodesk_settings.py > /tmp/settings.log 2>&1 &
SETTINGS_PID=$!
sleep 3
import -window root -display :99 /tmp/qa_screens/05_settings_hub.png

echo "[QA 7] Navigating Settings Hub..."
# Click Display category
xdotool mousemove 100 130 click 1
sleep 1
import -window root -display :99 /tmp/qa_screens/06_settings_display.png

# Click Audio category
xdotool mousemove 100 200 click 1
sleep 1
import -window root -display :99 /tmp/qa_screens/07_settings_audio.png

# Click Wi-Fi category
xdotool mousemove 100 260 click 1
sleep 1
import -window root -display :99 /tmp/qa_screens/08_settings_wifi.png

# Click About category
xdotool mousemove 100 560 click 1
sleep 1
import -window root -display :99 /tmp/qa_screens/09_settings_about.png

kill $SETTINGS_PID 2>/dev/null || true
sleep 1

echo "[QA 8] Launching Software Store..."
python3 /usr/share/monodesk/applications/software-manager/monodesk_software_manager.py > /tmp/store.log 2>&1 &
STORE_PID=$!
sleep 3
import -window root -display :99 /tmp/qa_screens/10_software_store.png

# Test search in software store
xdotool mousemove 450 40 click 1
xdotool type "firefox"
sleep 2
import -window root -display :99 /tmp/qa_screens/11_store_search.png

kill $STORE_PID 2>/dev/null || true
kill $SHELL_PID 2>/dev/null || true
kill $XFWM_PID 2>/dev/null || true
kill $XVFB_PID 2>/dev/null || true

echo "[QA] All captures completed successfully!"
ls -la /tmp/qa_screens/
"""

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    qemu_cmd = [
        QEMU, "-accel", "whpx", "-m", "4096", "-smp", "4",
        "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
        "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
        "-device", "virtio-net-pci,netdev=net0",
        "-display", "none"
    ]
    print("[*] Launching fresh Builder VM for GUI Automation QA...", flush=True)
    proc = subprocess.Popen(qemu_cmd)
    try:
        ready = False
        for i in range(25):
            time.sleep(2)
            chk = subprocess.run(SSH_BASE + ["echo VM_ONLINE"], capture_output=True, text=True)
            if "VM_ONLINE" in chk.stdout:
                ready = True
                print(f"[✓] Builder VM is online ({i*2+2}s)!", flush=True)
                break
        if not ready:
            print("[-] Builder VM failed to become online.")
            return False

        # Clean apt sources of any invalid repository lines
        subprocess.run(SSH_BASE + ["sed -i '/trixie/d' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true"], check=False)

        # Upload staged assets
        print("[*] Uploading shell and branding assets...", flush=True)
        subprocess.run(SCP_BASE + ["D:/anti/monodesk_shell_staging.tar.gz", "root@127.0.0.1:/tmp/"], check=True)
        subprocess.run(SSH_BASE + [
            "mkdir -p /usr/share/monodesk /usr/share/backgrounds/monodesk /usr/share/applications /usr/share/icons/hicolor/scalable/apps && "
            "tar -xzf /tmp/monodesk_shell_staging.tar.gz -C /usr/share/monodesk/ && "
            "cp -r /usr/share/monodesk/desktop/* /usr/share/monodesk/ 2>/dev/null || true; "
            "cp -r /usr/share/monodesk/branding/wallpapers/* /usr/share/backgrounds/monodesk/ 2>/dev/null || true; "
            "cp -r /usr/share/monodesk/branding/assets/* /usr/share/icons/hicolor/scalable/apps/ 2>/dev/null || true; "
            "cp -r /usr/share/monodesk/desktop/applications/entries/* /usr/share/applications/ 2>/dev/null || true; "
            "mkdir -p /etc/monodesk && echo 'PROFILE=standard' > /etc/monodesk/profile.conf"
        ], check=True)

        # Upload automation script
        print("[*] Uploading QA script...", flush=True)
        with open("D:/anti/run_qa_vm.sh", "w", newline="\n", encoding="utf-8") as f:
            f.write(AUTOMATION_SCRIPT)
        subprocess.run(SCP_BASE + ["D:/anti/run_qa_vm.sh", "root@127.0.0.1:/tmp/do_qa.sh"], check=True)
        subprocess.run(SSH_BASE + ["chmod +x /tmp/do_qa.sh"], check=True)

        # Execute QA
        print("[*] Executing QA Automation script in VM...", flush=True)
        p = subprocess.Popen(SSH_BASE + ["/tmp/do_qa.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(p.stdout.readline, ""):
            print("  [VM]", line, end="", flush=True)
        p.wait()

        # Stream tarball directly over SSH stdout
        print("[*] Streaming QA screenshots archive from VM...", flush=True)
        tar_stream = subprocess.run(
            SSH_BASE + ["tar -czf - -C /tmp/qa_screens ."],
            stdout=subprocess.PIPE, check=True
        )
        
        with tarfile.open(fileobj=io.BytesIO(tar_stream.stdout), mode="r:gz") as tar:
            tar.extractall(OUT_DIR)
        
        print("[✓] All screenshots successfully extracted directly to:", OUT_DIR, flush=True)
        for f in sorted(os.listdir(OUT_DIR)):
            if f.endswith(".png"):
                sz = os.path.getsize(os.path.join(OUT_DIR, f))
                print(f"  • {f} ({sz} bytes)")

        return True

    finally:
        print("[*] Shutting down Builder VM...", flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
