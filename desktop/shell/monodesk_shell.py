#!/usr/bin/env python3
"""
MONODESK OS — Custom Desktop Shell Controller
Qt 6 / QML Desktop Shell Engine integrating:
- Desktop composition & wallpaper management
- MONODESK Dock with pinned & running apps
- Fullscreen / popup Application Launcher
- Universal Quick Search (Alt+Space)
- Unified Control Centre & Quick Settings
- Desktop Notification Centre
- Dot-Matrix System Telemetry Widgets
"""

import sys
import os
import subprocess
import signal
import json

# Setup Environment paths
SHELL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SHELL_DIR, "../.."))
QML_DIR = os.path.join(SHELL_DIR, "qml")

def check_qt_runtime():
    try:
        from PyQt6 import QtCore, QtGui, QtQml, QtQuick
        return "PyQt6"
    except ImportError:
        try:
            from PySide6 import QtCore, QtGui, QtQml, QtQuick
            return "PySide6"
        except ImportError:
            return None

runtime = check_qt_runtime()

if runtime == "PyQt6":
    from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QTimer, QUrl
    from PyQt6.QtGui import QGuiApplication
    from PyQt6.QtQml import QQmlApplicationEngine
elif runtime == "PySide6":
    from PySide6.QtCore import QObject, Signal as pyqtSignal, Slot as pyqtSlot, Property as pyqtProperty, QTimer, QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
else:
    # Graceful fallback handler if Qt6 is being configured in the chroot
    print("[MONODESK Shell] Notice: Qt 6 runtime not detected in current local python environment.")
    print("[MONODESK Shell] Ready for deployment in Debian Bookworm image with python3-pyqt6 / qml6-module-qtquick.")

class ShellBridge(QObject):
    """Bridge between QML desktop UI and underlying Linux system services."""
    cpuChanged = pyqtSignal(float)
    ramChanged = pyqtSignal(float, float, float) # pct, used_gb, total_gb
    batteryChanged = pyqtSignal(int, str)       # pct, status
    volumeChanged = pyqtSignal(int)
    brightnessChanged = pyqtSignal(int)
    wifiChanged = pyqtSignal(bool, str)
    bluetoothChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._prev_idle = 0
        self._prev_total = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_telemetry)
        self.timer.start(2000)
        self.poll_telemetry()

    @pyqtSlot()
    def poll_telemetry(self):
        # 1. CPU
        try:
            with open("/proc/stat", "r") as f:
                parts = [float(x) for x in f.readline().split()[1:8]]
                idle = parts[3] + parts[4]
                total = sum(parts)
                d_idle = idle - self._prev_idle
                d_total = total - self._prev_total
                self._prev_idle, self._prev_total = idle, total
                cpu_pct = 0.0
                if d_total > 0:
                    cpu_pct = (1.0 - (d_idle / d_total)) * 100.0
                self.cpuChanged.emit(max(0.0, min(100.0, cpu_pct)))
        except Exception:
            self.cpuChanged.emit(0.0)

        # 2. RAM
        try:
            mem = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    p = line.split(":")
                    if len(p) == 2:
                        mem[p[0].strip()] = int(p[1].strip().split()[0])
            total = mem.get("MemTotal", 1024 * 1024) / (1024 * 1024)
            avail = mem.get("MemAvailable", 512 * 1024) / (1024 * 1024)
            used = total - avail
            pct = (used / total) * 100.0 if total > 0 else 0.0
            self.ramChanged.emit(pct, round(used, 2), round(total, 2))
        except Exception:
            self.ramChanged.emit(0.0, 0.0, 1.0)

        # 3. Battery
        bat_dir = "/sys/class/power_supply/BAT0"
        if not os.path.exists(bat_dir):
            bat_dir = "/sys/class/power_supply/BAT1"
        if os.path.exists(bat_dir):
            try:
                cap = 100
                with open(f"{bat_dir}/capacity") as f:
                    cap = int(f.read().strip())
                status = "AC"
                with open(f"{bat_dir}/status") as f:
                    status = f.read().strip()
                self.batteryChanged.emit(cap, status)
            except Exception:
                self.batteryChanged.emit(100, "AC")
        else:
            self.batteryChanged.emit(100, "AC")

    @pyqtSlot(str)
    def launchApp(self, cmd):
        """Safely launch an application process detached from shell."""
        try:
            subprocess.Popen(cmd.split(), start_new_session=True)
        except Exception as e:
            print(f"[Shell] Failed to launch {cmd}: {e}")

    @pyqtSlot(str, str)
    def setSystemVolume(self, sink, volume_pct):
        try:
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume_pct}%"], check=False)
        except Exception:
            pass

    @pyqtSlot(int)
    def setBrightness(self, val):
        try:
            subprocess.run(["brightnessctl", "set", f"{val}%"], check=False)
        except Exception:
            pass

    @pyqtSlot(str)
    def setPowerProfile(self, profile):
        try:
            subprocess.run(["monodesk-profile-ctl", "set", profile], check=False)
        except Exception:
            pass

def main():
    if runtime is None:
        print("[MONODESK Shell] Error: Qt 6 (PyQt6 or PySide6) is required to run the native shell.")
        sys.exit(1)

    app = QGuiApplication(sys.argv)
    app.setApplicationName("MONODESK Shell")
    app.setOrganizationName("MONODESK OS")

    engine = QQmlApplicationEngine()
    bridge = ShellBridge()
    engine.rootContext().setContextProperty("shellBridge", bridge)

    main_qml = os.path.join(QML_DIR, "MainShell.qml")
    engine.load(QUrl.fromLocalFile(main_qml))

    if not engine.rootObjects():
        print("[MONODESK Shell] Failed to load MainShell.qml")
        sys.exit(1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
