import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

class TestNebulaAndDebian13Integration(unittest.TestCase):
    def test_third_party_snapshots_and_licenses(self):
        nebula_license = REPO_ROOT / "third_party/nebula/LICENSE"
        m3shapes_license = REPO_ROOT / "third_party/m3shapes/LICENSE"
        self.assertTrue(nebula_license.is_file(), "third_party/nebula/LICENSE must exist")
        self.assertTrue(m3shapes_license.is_file(), "third_party/m3shapes/LICENSE must exist")
        
        nebula_text = nebula_license.read_text(encoding="utf-8")
        self.assertIn("AFFERO GENERAL PUBLIC LICENSE", nebula_text)
        
        m3shapes_text = m3shapes_license.read_text(encoding="utf-8")
        self.assertIn("Apache License", m3shapes_text)

    def test_docs_compliance(self):
        audit_doc = REPO_ROOT / "docs/NEBULA_UPSTREAM_AUDIT.md"
        port_doc = REPO_ROOT / "docs/NEBULA_DEBIAN_PORT.md"
        licenses_doc = REPO_ROOT / "docs/THIRD_PARTY_LICENSES.md"
        
        self.assertTrue(audit_doc.is_file(), "docs/NEBULA_UPSTREAM_AUDIT.md must exist")
        self.assertTrue(port_doc.is_file(), "docs/NEBULA_DEBIAN_PORT.md must exist")
        self.assertTrue(licenses_doc.is_file(), "docs/THIRD_PARTY_LICENSES.md must exist")
        
        self.assertIn("9749c30402b4e6712d0222c48b645fa357d0217e", audit_doc.read_text(encoding="utf-8"))
        self.assertIn("Debian 13 Trixie", port_doc.read_text(encoding="utf-8"))
        self.assertIn("AGPL-3.0", licenses_doc.read_text(encoding="utf-8"))

    def test_compositor_and_sessions(self):
        session_router = REPO_ROOT / "compositor/sessions/monodesk-session"
        wayland_desktop = REPO_ROOT / "compositor/sessions/monodesk-wayland.desktop"
        recovery_desktop = REPO_ROOT / "compositor/sessions/monodesk-recovery.desktop"
        hypr_conf = REPO_ROOT / "compositor/hyprland/hyprland.conf"
        
        self.assertTrue(session_router.is_file(), "compositor/sessions/monodesk-session must exist")
        self.assertTrue(wayland_desktop.is_file(), "compositor/sessions/monodesk-wayland.desktop must exist")
        self.assertTrue(recovery_desktop.is_file(), "compositor/sessions/monodesk-recovery.desktop must exist")
        self.assertTrue(hypr_conf.is_file(), "compositor/hyprland/hyprland.conf must exist")
        
        self.assertIn("monodesk-session wayland", wayland_desktop.read_text(encoding="utf-8"))
        self.assertIn("monodesk-session x11", recovery_desktop.read_text(encoding="utf-8"))
        self.assertIn("quickshell", hypr_conf.read_text(encoding="utf-8"))

    def test_debian13_manifests(self):
        pkg_dir = REPO_ROOT / "build/live-build/config/package-lists"
        expected = [
            "01-core.list.chroot", "02-networking.list.chroot", "03-bluetooth.list.chroot",
            "04-audio-multimedia.list.chroot", "05-wayland-portals.list.chroot",
            "06-hyprland.list.chroot", "07-qt-dependencies.list.chroot",
            "08-quickshell.list.chroot", "09-hardware-detection.list.chroot",
            "10-applications.list.chroot", "11-installer.list.chroot",
            "12-recovery.list.chroot", "13-firmware.list.chroot"
        ]
        for name in expected:
            p = pkg_dir / name
            self.assertTrue(p.is_file(), f"Package list {name} must exist")
            self.assertGreater(len(p.read_text(encoding="utf-8").strip()), 10, f"{name} must not be empty")

        auto_config = (REPO_ROOT / "build/live-build/auto/config").read_text(encoding="utf-8")
        self.assertIn("--distribution trixie", auto_config)

if __name__ == "__main__":
    unittest.main()
