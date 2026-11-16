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
import re

# Setup Environment paths
SHELL_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(SHELL_DIR, "qml")) and os.path.exists("/usr/share/monodesk/shell/qml"):
    SHELL_DIR = "/usr/share/monodesk/shell"
REPO_ROOT = os.path.abspath(os.path.join(SHELL_DIR, "../.."))
QML_DIR = os.path.join(SHELL_DIR, "qml")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

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
    from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QTimer, QUrl, QSize, Qt
    from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap, QColor, QPainter, QFont
    from PyQt6.QtQml import QQmlApplicationEngine
    from PyQt6.QtQuick import QQuickImageProvider
elif runtime == "PySide6":
    from PySide6.QtCore import QObject, Signal as pyqtSignal, Slot as pyqtSlot, Property as pyqtProperty, QTimer, QUrl, QSize, Qt
    from PySide6.QtGui import QGuiApplication, QIcon, QPixmap, QColor, QPainter, QFont
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuick import QQuickImageProvider
else:
    # Graceful fallback handler if Qt6 is being configured in the chroot
    print("[MONODESK Shell] Notice: Qt 6 runtime not detected in current local python environment.")
    print("[MONODESK Shell] Ready for deployment in Debian Bookworm image with python3-pyqt6 / qml6-module-qtquick.")
    QObject = object
    def pyqtSignal(*args, **kwargs):
        return None
    def pyqtSlot(*args, **kwargs):
        return lambda fn: fn
    def pyqtProperty(*args, **kwargs):
        return lambda fn: fn
    QTimer = object
    QUrl = object
    QGuiApplication = object
    QQmlApplicationEngine = object

def discover_installed_applications():
    app_dirs = [
        "/usr/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        os.path.join(REPO_ROOT, "applications")
    ]
    apps = []
    seen = set()
    for app_dir in app_dirs:
        if not os.path.exists(app_dir):
            continue
        for root, _, files in os.walk(app_dir):
            for file in files:
                if not file.endswith(".desktop"):
                    continue
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        name, exec_cmd, icon, comment, cat, nodisplay = None, None, "application-x-executable", "", "System", False
                        in_desktop = False
                        for line in f:
                            line = line.strip()
                            if line == "[Desktop Entry]":
                                in_desktop = True
                                continue
                            elif line.startswith("[") and in_desktop:
                                break
                            if not in_desktop or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip()
                            if k == "Name" and not name:
                                name = v
                            elif k == "Exec" and not exec_cmd:
                                exec_cmd = re.sub(r"%[a-zA-Z]", "", v).strip()
                            elif k == "Icon" and icon == "application-x-executable":
                                icon = v
                            elif k == "Comment" and not comment:
                                comment = v
                            elif k == "Categories" and cat == "System":
                                cat_list = [c.strip() for c in v.split(";") if c.strip()]
                                if cat_list:
                                    cat = cat_list[0]
                            elif k == "NoDisplay" and v.lower() == "true":
                                nodisplay = True
                        if nodisplay or not name or not exec_cmd:
                            continue
                        if name in seen:
                            continue
                        seen.add(name)
                        apps.append({
                            "name": name,
                            "exec": exec_cmd,
                            "icon": icon,
                            "desc": comment or name,
                            "category": cat
                        })
                except Exception:
                    pass
    if not apps:
        apps = [
            {"name": "Files", "exec": "thunar", "icon": "system-file-manager", "desc": "File Manager", "category": "System"},
            {"name": "Terminal", "exec": "xfce4-terminal", "icon": "utilities-terminal", "desc": "Terminal Emulator", "category": "Development"},
            {"name": "Web Browser", "exec": "firefox-esr", "icon": "firefox-esr", "desc": "Web Browser", "category": "Internet"},
            {"name": "Text Editor", "exec": "mousepad", "icon": "accessories-text-editor", "desc": "Text Editor", "category": "Accessories"},
            {"name": "Calculator", "exec": "galculator", "icon": "accessories-calculator", "desc": "Scientific Calculator", "category": "Accessories"},
            {"name": "Document Viewer", "exec": "qpdfview", "icon": "x-office-document", "desc": "Document & PDF Viewer", "category": "Office"},
            {"name": "Image Viewer", "exec": "ristretto", "icon": "image-x-generic", "desc": "Image Viewer", "category": "Graphics"},
            {"name": "Archive Manager", "exec": "file-roller", "icon": "package-x-generic", "desc": "Archive & Compression Manager", "category": "System"},
            {"name": "Screenshot", "exec": "xfce4-screenshooter", "icon": "applets-screenshooter", "desc": "Screenshot Utility", "category": "Accessories"},
            {"name": "System Monitor", "exec": "monodesk-system-monitor", "icon": "utilities-system-monitor", "desc": "Resource Monitor", "category": "System"},
            {"name": "Software Store", "exec": "monodesk-store", "icon": "system-software-install", "desc": "Discover & Install Apps", "category": "System"},
            {"name": "System Settings", "exec": "monodesk-settings", "icon": "preferences-system", "desc": "Central Configuration Hub", "category": "Settings"},
            {"name": "Hardware Centre", "exec": "monodesk-hardware-centre", "icon": "hardware", "desc": "Diagnostics & Telemetry", "category": "System"},
            {"name": "Install MONODESK OS", "exec": "calamares", "icon": "calamares", "desc": "Universal PC Installer", "category": "System"}
        ]
    return sorted(apps, key=lambda x: x["name"].lower())

class ShellBridge(QObject):
    """Bridge between QML desktop UI and underlying Linux system services."""
    cpuChanged = pyqtSignal(float)
    ramChanged = pyqtSignal(float, float, float) # pct, used_gb, total_gb
    batteryChanged = pyqtSignal(int, str)       # pct, status
    volumeChanged = pyqtSignal(int)
    brightnessChanged = pyqtSignal(int)
    wifiChanged = pyqtSignal(bool, str)
    bluetoothChanged = pyqtSignal(bool)
    wallpaperChanged = pyqtSignal(str)
    installedAppsChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._prev_idle = 0
        self._prev_total = 1
        self._installed_apps = discover_installed_applications()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_telemetry)
        self.timer.start(2000)
        self.poll_telemetry()
        self.poll_network()
        self.poll_bluetooth()

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

    @pyqtSlot()
    def poll_network(self):
        try:
            res = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"], stdout=subprocess.PIPE, text=True, check=False)
            connected = False
            ssid = "Disconnected"
            for line in res.stdout.splitlines():
                if line.startswith("yes:"):
                    connected = True
                    ssid = line.split(":", 1)[1].strip() or "Connected"
                    break
            self.wifiChanged.emit(connected, ssid)
        except Exception:
            self.wifiChanged.emit(False, "Offline")

    @pyqtSlot()
    def poll_bluetooth(self):
        try:
            res = subprocess.run(["bluetoothctl", "show"], stdout=subprocess.PIPE, text=True, check=False)
            powered = "Powered: yes" in res.stdout
            self.bluetoothChanged.emit(powered)
        except Exception:
            self.bluetoothChanged.emit(False)

    @pyqtSlot(result="QVariant")
    def getInstalledApps(self):
        self._installed_apps = discover_installed_applications()
        return self._installed_apps

    @pyqtSlot(result="QVariant")
    def getWallpapers(self):
        wallpapers = []
        wp_dir = "/usr/share/backgrounds/monodesk"
        if os.path.exists(wp_dir):
            for f in sorted(os.listdir(wp_dir)):
                if f.endswith((".svg", ".png", ".jpg")):
                    wallpapers.append(os.path.join(wp_dir, f))
        if not wallpapers:
            wallpapers = [
                "/usr/share/backgrounds/monodesk/monodesk-dark-dotmatrix.svg",
                "/usr/share/backgrounds/monodesk/monodesk-light-dotmatrix.svg"
            ]
        return wallpapers

    @pyqtSlot(str)
    def setWallpaper(self, path):
        try:
            os.makedirs("/etc/monodesk", exist_ok=True)
            with open("/etc/monodesk/wallpaper.conf", "w") as f:
                f.write(f"WALLPAPER={path}\n")
        except Exception:
            pass
        self.wallpaperChanged.emit(path)

    @pyqtSlot()
    def lockScreen(self):
        for cmd in [["loginctl", "lock-session"], ["xflock4"]]:
            try:
                subprocess.Popen(cmd)
                break
            except Exception:
                continue

    @pyqtSlot()
    def logoutSession(self):
        for cmd in [["xfce4-session-logout", "--logout", "--fast"], ["loginctl", "terminate-session", "self"]]:
            try:
                subprocess.Popen(cmd)
                break
            except Exception:
                continue

    @pyqtSlot()
    def restartSystem(self):
        subprocess.Popen(["systemctl", "reboot"])

    @pyqtSlot()
    def shutdownSystem(self):
        subprocess.Popen(["systemctl", "poweroff"])

    @pyqtSlot(bool)
    def toggleWifi(self, enable):
        state = "on" if enable else "off"
        try:
            subprocess.run(["nmcli", "radio", "wifi", state], check=False)
            self.poll_network()
        except Exception:
            pass

    @pyqtSlot(bool)
    def toggleBluetooth(self, enable):
        state = "on" if enable else "off"
        try:
            subprocess.run(["bluetoothctl", "power", state], check=False)
            self.poll_bluetooth()
        except Exception:
            pass

    @pyqtSlot(int)
    def switchWorkspace(self, idx):
        try:
            subprocess.run(["wmctrl", "-s", str(idx)], check=False)
        except Exception:
            try:
                subprocess.run(["xdotool", "set_desktop", str(idx)], check=False)
            except Exception:
                pass

def fallback_to_xfce(reason, launch_ui=True):
    """Safely fall back to XFCE panel & desktop when Qt 6 QML shell cannot start."""
    print(f"[MONODESK Shell] {reason} Safely falling back to XFCE desktop.")
    if launch_ui and os.environ.get("DISPLAY"):
        for binary in ("xfce4-panel", "xfdesktop"):
            try:
                chk = subprocess.run(["pgrep", "-x", binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if chk.returncode != 0:
                    subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                    print(f"[MONODESK Shell] Started XFCE fallback component: {binary}")
            except Exception as exc:
                print(f"[MONODESK Shell] Notice: could not start {binary}: {exc}")


if runtime in ("PyQt6", "PySide6"):
    class MonodeskIconProvider(QQuickImageProvider):
        """Resolve image://icon/<name> via QIcon theme lookup with crisp monochrome glyph fallback."""
        def __init__(self):
            super().__init__(QQuickImageProvider.ImageType.Pixmap)
            if not QIcon.themeName():
                for theme in ("Tango", "Adwaita", "hicolor"):
                    if os.path.isdir(f"/usr/share/icons/{theme}"):
                        QIcon.setThemeName(theme)
                        break

        def requestPixmap(self, icon_id, requested_size):
            w = requested_size.width() if requested_size.isValid() and requested_size.width() > 0 else 24
            h = requested_size.height() if requested_size.isValid() and requested_size.height() > 0 else 24
            candidates = [icon_id]
            if icon_id == "firefox-esr":
                candidates.extend(["web-browser", "internet-web-browser"])
            elif icon_id == "system-file-manager":
                candidates.extend(["folder", "inode-directory"])
            for cand in candidates:
                icon = QIcon.fromTheme(cand)
                if not icon.isNull():
                    pm = icon.pixmap(QSize(w, h))
                    if not pm.isNull():
                        return pm, pm.size()
            pm = QPixmap(w, h)
            pm.fill(QColor(0, 0, 0, 0))
            painter = QPainter(pm)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setBrush(QColor("#242426"))
            painter.setPen(QColor("#3A3A3D"))
            painter.drawRoundedRect(0, 0, w - 1, h - 1, 5, 5)
            painter.setPen(QColor("#F4F4F5"))
            painter.setFont(QFont("Sans", max(8, w // 2), QFont.Weight.Bold))
            label = (icon_id[:1] or "M").upper()
            painter.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, label)
            painter.end()
            return pm, pm.size()


def main():
    check_only = "--check" in sys.argv
    if runtime is None:
        fallback_to_xfce("Qt 6 (PyQt6 or PySide6) runtime is unavailable.", launch_ui=not check_only)
        return 0 if not check_only else 1

    app = QGuiApplication(sys.argv)
    app.setApplicationName("MONODESK Shell")
    app.setOrganizationName("MONODESK OS")

    # Prevent duplicate concurrent shell windows across session/autostart triggers
    lock_fh = None
    if not check_only and os.name == "posix":
        try:
            import fcntl
            lock_path = f"/tmp/monodesk-shell-{os.getuid()}.lock"
            lock_fh = open(lock_path, "w")
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("[MONODESK Shell] Another instance is already running.", flush=True)
            return 0

    qml_errors = []
    engine = QQmlApplicationEngine()
    engine.addImageProvider("icon", MonodeskIconProvider())
    engine.warnings.connect(lambda errs: qml_errors.extend(str(e.toString()) for e in errs))
    bridge = ShellBridge()
    engine.rootContext().setContextProperty("shellBridge", bridge)

    main_qml = os.path.join(QML_DIR, "MainShell.qml")
    engine.load(QUrl.fromLocalFile(main_qml))

    if not engine.rootObjects():
        details = "; ".join(qml_errors) if qml_errors else f"failed to load {main_qml}"
        fallback_to_xfce(f"QML initialization error ({details}).", launch_ui=not check_only)
        return 0 if not check_only else 1

    print("[MONODESK Shell] QML root window loaded successfully.", flush=True)
    if check_only:
        return 0

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
