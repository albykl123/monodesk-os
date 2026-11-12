"""Unit tests for MONODESK Shell Qt6/QML packaging, XFCE fallback, and security cleanup."""

import importlib.util
import pathlib
import sys
import unittest
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestMonodeskShellAndSecurity(unittest.TestCase):
    def test_qml_modules_and_theme_imports(self):
        self.assertTrue((REPO_ROOT / "themes" / "qmldir").is_file())
        self.assertTrue((REPO_ROOT / "desktop" / "shell" / "qml" / "MainShell.qml").is_file())
        for comp in ("dock", "launcher", "quick-search", "control-centre", "notifications", "widgets"):
            qml_dir = REPO_ROOT / "desktop" / comp / "qml"
            self.assertTrue((qml_dir / "qmldir").is_file(), f"Missing qmldir in {comp}")
            qml_files = list(qml_dir.glob("*.qml"))
            self.assertTrue(qml_files, f"No QML files in {comp}")
            for qml in qml_files:
                txt = qml.read_text(encoding="utf-8")
                if "themes" in txt:
                    self.assertIn('../../themes', txt, f"Relative theme import wrong in {qml}")
                    self.assertNotIn('../../../themes', txt)

    def test_shell_fallback_when_qt6_missing(self):
        shell_path = REPO_ROOT / "desktop" / "shell" / "monodesk_shell.py"
        spec = importlib.util.spec_from_file_location("monodesk_shell_noqt", shell_path)
        mod = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"PyQt6": None, "PyQt6.QtCore": None, "PyQt6.QtGui": None, "PyQt6.QtQml": None, "PyQt6.QtQuick": None, "PySide6": None}):
            spec.loader.exec_module(mod)
            self.assertIsNone(mod.runtime)
            with patch.object(mod, "fallback_to_xfce") as mock_fb:
                with patch.object(sys, "argv", ["monodesk-shell"]):
                    rc = mod.main()
                    self.assertEqual(rc, 0)
                    mock_fb.assert_called_once()
                mock_fb.reset_mock()
                with patch.object(sys, "argv", ["monodesk-shell", "--check"]):
                    rc_chk = mod.main()
                    self.assertEqual(rc_chk, 1)
                    mock_fb.assert_called_once()

    def test_package_lists_and_calamares_cleanup(self):
        core_list = (REPO_ROOT / "build/live-build/config/package-lists/01-core.list.chroot").read_text(encoding="utf-8")
        desktop_list = (REPO_ROOT / "build/live-build/config/package-lists/02-desktop.list.chroot").read_text(encoding="utf-8")
        self.assertIn("user-setup", core_list)
        self.assertIn("python3-pyqt6.qtquick", desktop_list)
        self.assertIn("python3-pyqt6.qtqml", desktop_list)

        settings = (REPO_ROOT / "build/live-build/config/includes.chroot/etc/calamares/settings.conf").read_text(encoding="utf-8")
        cleanup = (REPO_ROOT / "build/live-build/config/includes.chroot/etc/calamares/modules/shellprocess-cleanup.conf").read_text(encoding="utf-8")
        self.assertIn("shellprocess@cleanup", settings)
        self.assertIn("getty@tty1.service.d", cleanup)
        self.assertIn("passwd -l root", cleanup)


if __name__ == "__main__":
    unittest.main()
