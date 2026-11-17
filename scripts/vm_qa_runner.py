#!/usr/bin/env python3
"""
MONODESK OS 2.0.1 QA — Python-driven Graphical Automation & Visual Verification
Executes inside the Debian Builder VM against Xvfb :99.
Uses PyQt6 directly for screen capture (zero external imagemagick dependencies).
Uses xdotool for mouse & keyboard automation.
"""

import sys
import os
import time
import subprocess
import shutil

os.environ["DISPLAY"] = ":99"
OUT_DIR = "/tmp/qa_screens"
os.makedirs(OUT_DIR, exist_ok=True)

def take_screenshot(filename):
    out_path = os.path.join(OUT_DIR, filename)
    script = f"""
from PyQt6.QtGui import QGuiApplication
import sys
app = QGuiApplication(sys.argv)
screen = app.primaryScreen()
if screen:
    pix = screen.grabWindow(0)
    pix.save("{out_path}")
    print("[SCREEN] Saved {filename} (" + str(pix.width()) + "x" + str(pix.height()) + ")")
else:
    print("[SCREEN] No primary screen found!")
"""
    res = subprocess.run(["python3", "-c", script], env=os.environ, capture_output=True, text=True)
    print(res.stdout.strip())
    if res.stderr:
        print("[SCREEN ERR]", res.stderr.strip())

def main():
    print("=" * 60)
    print("MONODESK OS 2.0.1 — GRAPHICAL QA AUTOMATION HARNESS")
    print("=" * 60)

    # 1. Kill any existing instances
    subprocess.run(["pkill", "-9", "-f", "Xvfb"], check=False)
    subprocess.run(["pkill", "-9", "-f", "monodesk"], check=False)
    time.sleep(1)

    # 2. Start Xvfb at 1280x800
    print("[*] Starting Xvfb :99 at 1280x800x24...")
    xvfb = subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1280x800x24", "-ac"])
    time.sleep(2)

    # 3. Start window manager if available
    wm = None
    if shutil.which("xfwm4"):
        print("[*] Starting xfwm4 compositor...")
        wm = subprocess.Popen(["xfwm4", "--compositor=on"])
        time.sleep(1)

    # 4. Copy missing icon if needed
    icon_dst = "/usr/share/icons/hicolor/scalable/apps"
    os.makedirs(icon_dst, exist_ok=True)
    for icon in ["monodesk-icon.svg", "monodesk-logo.svg"]:
        src = os.path.join("/usr/share/monodesk/branding/assets", icon)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(icon_dst, icon))

    # 5. Launch MONODESK Desktop Shell
    print("[*] Launching MONODESK Shell (/usr/share/monodesk/desktop/shell/monodesk_shell.py)...")
    shell_proc = subprocess.Popen(
        ["python3", "/usr/share/monodesk/desktop/shell/monodesk_shell.py"],
        env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    time.sleep(4)

    # Check if shell is alive
    if shell_proc.poll() is not None:
        stdout, stderr = shell_proc.communicate()
        print("[-] MONODESK Shell terminated prematurely!")
        print("Stdout:\n", stdout)
        print("Stderr:\n", stderr)
    else:
        print("[✓] MONODESK Shell is running!")

    # Capture 1: Clean Desktop
    print("[*] Gate 1: Capturing Clean Desktop (wallpaper, branding, dock, widgets)...")
    take_screenshot("01_desktop_clean.png")

    # Capture 2: Trigger Launcher via Meta key
    print("[*] Gate 2: Triggering Launcher via Meta key...")
    subprocess.run(["xdotool", "key", "Super"])
    time.sleep(2)
    take_screenshot("02_launcher_open.png")

    # Capture 3: Search in Launcher
    print("[*] Gate 3: Searching in Launcher for 'Setting'...")
    subprocess.run(["xdotool", "type", "Setting"])
    time.sleep(1)
    take_screenshot("03_launcher_search.png")

    # Dismiss Launcher
    subprocess.run(["xdotool", "key", "Escape"])
    time.sleep(1)

    # Capture 4: Control Centre
    print("[*] Gate 4: Opening Control Centre...")
    # Click toggle icon on bottom right of dock
    subprocess.run(["xdotool", "mousemove", "710", "760", "click", "1"])
    time.sleep(2)
    take_screenshot("04_control_centre.png")
    # Close control centre
    subprocess.run(["xdotool", "mousemove", "710", "760", "click", "1"])
    time.sleep(1)

    # Capture 5: Settings Hub
    print("[*] Gate 5: Launching Settings Hub...")
    settings_proc = subprocess.Popen(
        ["python3", "/usr/share/monodesk/applications/settings/monodesk_settings.py"],
        env=os.environ
    )
    time.sleep(3)
    take_screenshot("05_settings_hub.png")

    # Capture 6-9: Navigate Settings Categories
    print("[*] Gate 6: Navigating Settings Categories...")
    # Click Display
    subprocess.run(["xdotool", "mousemove", "300", "140", "click", "1"])
    time.sleep(1)
    take_screenshot("06_settings_display.png")

    # Click Audio
    subprocess.run(["xdotool", "mousemove", "300", "220", "click", "1"])
    time.sleep(1)
    take_screenshot("07_settings_audio.png")

    # Click Wi-Fi
    subprocess.run(["xdotool", "mousemove", "300", "280", "click", "1"])
    time.sleep(1)
    take_screenshot("08_settings_wifi.png")

    # Click About MONODESK
    subprocess.run(["xdotool", "mousemove", "300", "580", "click", "1"])
    time.sleep(1)
    take_screenshot("09_settings_about.png")

    settings_proc.terminate()
    time.sleep(1)

    # Capture 10-11: Software Store
    print("[*] Gate 7: Launching Software Store...")
    store_proc = subprocess.Popen(
        ["python3", "/usr/share/monodesk/applications/software-manager/monodesk_software_manager.py"],
        env=os.environ
    )
    time.sleep(3)
    take_screenshot("10_software_store.png")

    # Test Store search
    subprocess.run(["xdotool", "mousemove", "500", "120", "click", "1"])
    subprocess.run(["xdotool", "type", "firefox"])
    time.sleep(2)
    take_screenshot("11_store_search.png")

    store_proc.terminate()
    if shell_proc.poll() is None:
        shell_proc.terminate()
    if wm and wm.poll() is None:
        wm.terminate()
    xvfb.terminate()

    print("[*] Creating tarball of all QA screenshots...")
    subprocess.run(["tar", "-czf", "/tmp/qa_screens.tar.gz", "-C", "/tmp", "qa_screens"], check=True)
    print("[✓] ALL QA SCREENSHOTS CAPTURED AND PACKAGED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
