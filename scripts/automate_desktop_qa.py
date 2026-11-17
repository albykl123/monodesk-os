import subprocess
import time
import os

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

AUTOMATION_SCRIPT = """#!/usr/bin/env bash
set -e

export DISPLAY=:99
mkdir -p /tmp/qa_screens

# Ensure packages for testing
apt-get install -y imagemagick x11-utils python3-gi gir1.2-gtk-3.0 >/dev/null 2>&1 || true

# Kill any existing Xvfb
killall Xvfb 2>/dev/null || true
sleep 1

# Start Xvfb at 1280x800
Xvfb :99 -screen 0 1280x800x24 &
XVFB_PID=$!
sleep 2

# Start xfwm4 compositor
xfwm4 --compositor=on &
XFWM_PID=$!
sleep 2

echo "[QA] Starting MONODESK Shell..."
python3 /usr/share/monodesk/desktop/shell/monodesk_shell.py &
SHELL_PID=$!
sleep 4

echo "[QA 1] Capturing Clean Desktop..."
import -window root -display :99 /tmp/qa_screens/01_desktop_clean.png

echo "[QA 2] Triggering Launcher via xdotool (Super key)..."
xdotool key Super
sleep 2
import -window root -display :99 /tmp/qa_screens/02_launcher_open.png

echo "[QA 3] Typing search query in Launcher..."
xdotool type "Setting"
sleep 1
import -window root -display :99 /tmp/qa_screens/03_launcher_search.png

echo "[QA 4] Dismissing Launcher and opening Control Centre..."
xdotool key Escape
sleep 1
# Click control centre icon at bottom right of dock (approx x=710, y=750) or toggle
xdotool mousemove 710 750 click 1
sleep 2
import -window root -display :99 /tmp/qa_screens/04_control_centre.png

echo "[QA 5] Launching Settings Hub..."
python3 /usr/share/monodesk/applications/settings/monodesk_settings.py &
SETTINGS_PID=$!
sleep 3
import -window root -display :99 /tmp/qa_screens/05_settings_hub.png

echo "[QA 6] Navigating Settings Hub..."
xdotool mousemove 100 220 click 1 # Click Audio
sleep 1
import -window root -display :99 /tmp/qa_screens/06_settings_audio.png

xdotool mousemove 100 480 click 1 # Click About MONODESK
sleep 1
import -window root -display :99 /tmp/qa_screens/07_settings_about.png

kill $SETTINGS_PID 2>/dev/null || true
sleep 1

echo "[QA 7] Launching Software Store..."
python3 /usr/share/monodesk/applications/software-manager/monodesk_software_manager.py &
STORE_PID=$!
sleep 3
import -window root -display :99 /tmp/qa_screens/08_software_store.png

kill $STORE_PID 2>/dev/null || true
kill $SHELL_PID 2>/dev/null || true
kill $XFWM_PID 2>/dev/null || true
kill $XVFB_PID 2>/dev/null || true

echo "[QA] All captures completed successfully!"
ls -la /tmp/qa_screens/
"""

def run_qa():
    qemu_cmd = [
        QEMU, "-accel", "whpx", "-m", "4096", "-smp", "4",
        "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
        "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
        "-device", "virtio-net-pci,netdev=net0",
        "-display", "none"
    ]
    print("[*] Launching Builder VM for GUI Automation QA...", flush=True)
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

        # Upload staged files
        subprocess.run(SCP_BASE + ["D:/anti/monodesk_shell_staging.tar.gz", "root@127.0.0.1:/tmp/"], check=True)
        subprocess.run(SSH_BASE + [
            "mkdir -p /usr/share/monodesk /usr/share/backgrounds/monodesk /usr/share/applications && "
            "tar -xzf /tmp/monodesk_shell_staging.tar.gz -C /usr/share/monodesk/ && "
            "cp -r /usr/share/monodesk/desktop/* /usr/share/monodesk/ 2>/dev/null || true; "
            "cp -r /usr/share/monodesk/branding/wallpapers/* /usr/share/backgrounds/monodesk/ 2>/dev/null || true; "
            "cp -r /usr/share/monodesk/desktop/applications/entries/* /usr/share/applications/ 2>/dev/null || true; "
            "mkdir -p /etc/monodesk && echo 'PROFILE=standard' > /etc/monodesk/profile.conf"
        ], check=True)

        # Upload automation script
        with open("D:/anti/run_qa_vm.sh", "w", newline="\n", encoding="utf-8") as f:
            f.write(AUTOMATION_SCRIPT)

        subprocess.run(SCP_BASE + ["D:/anti/run_qa_vm.sh", "root@127.0.0.1:/tmp/do_qa.sh"], check=True)
        subprocess.run(SSH_BASE + ["chmod +x /tmp/do_qa.sh"], check=True)

        print("[*] Executing GUI QA automation script in VM...", flush=True)
        qa_proc = subprocess.Popen(SSH_BASE + ["/tmp/do_qa.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(qa_proc.stdout.readline, ""):
            print("  [VM]", line, end="", flush=True)
        qa_proc.wait()

        # Download screenshots
        out_dir = r"D:\anti\monodesk-os\artifacts\qa"
        os.makedirs(out_dir, exist_ok=True)
        print("[*] Downloading captured QA screenshots...", flush=True)
        subprocess.run(SCP_BASE + ["root@127.0.0.1:/tmp/qa_screens/*.png", out_dir], check=False)

    finally:
        print("[*] Shutting down Builder VM...", flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    run_qa()
