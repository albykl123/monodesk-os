#!/usr/bin/env python3
"""
MONODESK OS — Comprehensive Application Test Suite
Validates application modules, telemetry extraction logic, security policies,
critical package protections, and hardware compatibility mappings.
"""

import unittest
import sys
import os
import re

# Add applications to path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/hardware-report"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/accounts"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/disk-manager"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/device-manager"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/privacy"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/backup"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/recovery"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/workspace"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/ai-assistant"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/update-manager"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/software-manager"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/system-monitor"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/welcome"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/settings"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/clipboard"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/compatibility"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/gaming"))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/developer-centre"))
sys.path.insert(0, os.path.join(REPO_ROOT, "desktop/widgets"))
sys.path.insert(0, os.path.join(REPO_ROOT, "system/power"))
sys.path.insert(0, os.path.join(REPO_ROOT, "system/hardware"))

class TestHardwareRedaction(unittest.TestCase):
    def test_mac_address_redaction(self):
        from monodesk_hardware_report import redact_sensitive_info
        raw = "Interface eth0 has MAC 00:1A:2B:3C:4D:5E and link UP"
        redacted = redact_sensitive_info(raw)
        self.assertNotIn("00:1A:2B:3C:4D:5E", redacted)
        self.assertIn("[REDACTED_MAC]", redacted)

    def test_uuid_redaction(self):
        from monodesk_hardware_report import redact_sensitive_info
        raw = "Disk UUID is e4d3a2b1-1234-5678-9abc-def012345678 on /dev/nvme0n1p2"
        redacted = redact_sensitive_info(raw)
        self.assertNotIn("e4d3a2b1-1234-5678-9abc-def012345678", redacted)
        self.assertIn("[REDACTED_UUID]", redacted)

    def test_serial_redaction(self):
        from monodesk_hardware_report import redact_sensitive_info
        raw = "System Serial Number: PF-3A1B2C-9981"
        redacted = redact_sensitive_info(raw)
        self.assertNotIn("PF-3A1B2C-9981", redacted)
        self.assertIn("[REDACTED_SERIAL]", redacted)

class TestDesktopWidget(unittest.TestCase):
    def test_cpu_usage_function(self):
        from monodesk_widget import get_cpu_usage
        idle, total = get_cpu_usage()
        self.assertIsInstance(idle, (int, float))
        self.assertIsInstance(total, (int, float))
        self.assertGreater(total, 0)

    def test_ram_usage_function(self):
        from monodesk_widget import get_ram_usage
        pct, used, total = get_ram_usage()
        self.assertIsInstance(pct, (int, float))
        self.assertGreaterEqual(pct, 0.0)
        self.assertLessEqual(pct, 100.0)

class TestProfileController(unittest.TestCase):
    def test_profile_ctl_exists(self):
        ctl_path = os.path.join(REPO_ROOT, "system/power/monodesk-profile-ctl")
        self.assertTrue(os.path.isfile(ctl_path))

class TestAccountManager(unittest.TestCase):
    def test_get_local_users(self):
        from monodesk_accounts import get_local_users
        users = get_local_users()
        self.assertIsInstance(users, list)
        self.assertGreater(len(users), 0)
        self.assertIn("username", users[0])
        self.assertIn("home", users[0])

class TestDiskManager(unittest.TestCase):
    def test_get_block_devices(self):
        from monodesk_disk_manager import get_block_devices
        devs = get_block_devices()
        self.assertIsInstance(devs, list)
        self.assertGreater(len(devs), 0)
        self.assertIn("name", devs[0])

class TestDeviceManager(unittest.TestCase):
    def test_parse_lspci_devices(self):
        from monodesk_device_manager import parse_lspci_devices
        cats = parse_lspci_devices()
        self.assertIsInstance(cats, dict)
        self.assertIn("Display & Graphics (GPU)", cats)
        self.assertIn("Audio & Multimedia", cats)

class TestPrivacyDashboard(unittest.TestCase):
    def test_privacy_class_exists(self):
        from monodesk_privacy import MonodeskPrivacyDashboard
        app = MonodeskPrivacyDashboard()
        self.assertIsNotNone(app)

class TestBackupManager(unittest.TestCase):
    def test_backup_class_exists(self):
        from monodesk_backup import MonodeskBackupManager, BACKUP_INDEX_PATH
        self.assertTrue(len(BACKUP_INDEX_PATH) > 0)
        app = MonodeskBackupManager()
        self.assertIsNotNone(app)

class TestRecoveryCentre(unittest.TestCase):
    def test_recovery_class_exists(self):
        from monodesk_recovery import MonodeskRecoveryCentre
        app = MonodeskRecoveryCentre()
        self.assertIsNotNone(app)

class TestWorkspaceManager(unittest.TestCase):
    def test_workspace_class_exists(self):
        from monodesk_workspace import MonodeskWorkspaceManager
        app = MonodeskWorkspaceManager()
        self.assertIsNotNone(app)

class TestLocalAI(unittest.TestCase):
    def test_ai_endpoint(self):
        from monodesk_ai import LOCAL_ENDPOINT, MonodeskLocalAI
        self.assertEqual(LOCAL_ENDPOINT, "http://127.0.0.1:11434/api/generate")
        app = MonodeskLocalAI()
        self.assertIsNotNone(app)

class TestUpdateManager(unittest.TestCase):
    def test_critical_packages_whitelist(self):
        from monodesk_update_manager import CRITICAL_PACKAGES, MonodeskUpdateManager
        self.assertIn("systemd", CRITICAL_PACKAGES)
        self.assertIn("linux-image-amd64", CRITICAL_PACKAGES)
        self.assertIn("grub-efi-amd64", CRITICAL_PACKAGES)
        self.assertIn("xfce4-session", CRITICAL_PACKAGES)
        app = MonodeskUpdateManager()
        self.assertIsNotNone(app)

class TestSoftwareManager(unittest.TestCase):
    def test_featured_software_catalogue(self):
        from monodesk_software_manager import FEATURED_SOFTWARE, MonodeskSoftwareManager
        self.assertGreater(len(FEATURED_SOFTWARE), 5)
        for name, pkg, cat, desc in FEATURED_SOFTWARE:
            self.assertTrue(len(name) > 0)
            self.assertTrue(len(pkg) > 0)
        app = MonodeskSoftwareManager()
        self.assertIsNotNone(app)

class TestSystemMonitor(unittest.TestCase):
    def test_system_monitor_class_exists(self):
        from monodesk_system_monitor import MonodeskSystemMonitor
        win = MonodeskSystemMonitor()
        self.assertIsNotNone(win)

class TestWelcome(unittest.TestCase):
    def test_welcome_class_exists(self):
        from monodesk_welcome import MonodeskWelcome
        app = MonodeskWelcome()
        self.assertIsNotNone(app)

class TestSettings(unittest.TestCase):
    def test_settings_class_exists(self):
        from monodesk_settings import MonodeskSettings
        app = MonodeskSettings()
        self.assertIsNotNone(app)

class TestClipboard(unittest.TestCase):
    def test_clipboard_class_exists(self):
        from monodesk_clipboard import MonodeskClipboard
        app = MonodeskClipboard()
        self.assertIsNotNone(app)

class TestCompatibilityCentre(unittest.TestCase):
    def test_compatibility_matrix(self):
        from monodesk_compatibility import POPULAR_COMPAT_APPS, MonodeskCompatibilityCentre
        self.assertGreater(len(POPULAR_COMPAT_APPS), 0)
        app = MonodeskCompatibilityCentre()
        self.assertIsNotNone(app)

class TestGamingCentre(unittest.TestCase):
    def test_gaming_matrix(self):
        from monodesk_gaming import POPULAR_GAMES_COMPAT, MonodeskGamingCentre
        self.assertGreater(len(POPULAR_GAMES_COMPAT), 0)
        app = MonodeskGamingCentre()
        self.assertIsNotNone(app)

class TestDeveloperCentre(unittest.TestCase):
    def test_dev_stacks(self):
        from monodesk_developer import DEV_STACKS, MonodeskDeveloperCentre
        self.assertGreater(len(DEV_STACKS), 0)
        app = MonodeskDeveloperCentre()
        self.assertIsNotNone(app)

class TestHardwareDetectionService(unittest.TestCase):
    def setUp(self):
        import types
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader("monodesk_hw_detect", os.path.join(REPO_ROOT, "system/hardware/monodesk-hw-detect"))
        self.hw_mod = types.ModuleType("monodesk_hw_detect")
        loader.exec_module(self.hw_mod)

    def test_detect_all_structure(self):
        hw = self.hw_mod.detect_all()
        required_keys = ["cpu", "ram", "gpu", "network", "bluetooth", "audio", "storage", "display_input", "power", "firmware"]
        for k in required_keys:
            self.assertIn(k, hw)

    def test_cpu_detection_structure(self):
        cpu = self.hw_mod.detect_cpu()
        self.assertIn("arch", cpu)
        self.assertIn("cores", cpu)
        self.assertIn("threads", cpu)
        self.assertIn("flags", cpu)
        self.assertIsInstance(cpu["threads"], int)
        self.assertGreaterEqual(cpu["threads"], 1)

    def test_ram_detection_structure(self):
        ram = self.hw_mod.detect_ram()
        self.assertIn("total_mb", ram)
        self.assertIn("available_mb", ram)
        self.assertIsInstance(ram["total_mb"], int)
        self.assertGreater(ram["total_mb"], 0)

    def test_sensitive_data_redaction(self):
        raw = "Interface wlan0 MAC 11:22:33:44:55:66, UUID 12345678-1234-1234-1234-123456789abc, Serial Number: ABC-9999"
        redacted = self.hw_mod.redact_sensitive(raw)
        self.assertNotIn("11:22:33:44:55:66", redacted)
        self.assertNotIn("12345678-1234-1234-1234-123456789abc", redacted)
        self.assertNotIn("ABC-9999", redacted)
        self.assertIn("[REDACTED_MAC]", redacted)
        self.assertIn("[REDACTED_UUID]", redacted)

class TestAdaptiveProfileRecommendation(unittest.TestCase):
    def setUp(self):
        import types
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader("monodesk_hw_detect", os.path.join(REPO_ROOT, "system/hardware/monodesk-hw-detect"))
        self.hw_mod = types.ModuleType("monodesk_hw_detect")
        loader.exec_module(self.hw_mod)

    def test_recommend_lite_profile_low_spec_hardware(self):
        mock_hw = {
            "ram": {"total_mb": 3800, "available_mb": 2200, "swap_total_mb": 0, "zram_active": False},
            "cpu": {"model": "Intel Core i3-2348M", "arch": "x86_64", "cores": 2, "threads": 2, "flags": ["sse4_1"], "has_avx": False, "has_avx2": False, "has_sse4_2": False, "is_low_power": True, "freq_mhz": 2300.0},
            "gpu": {"devices": [{"device": "Intel HD 3000", "driver": "i915"}], "active_driver": "i915", "acceleration": "software_rasterizer", "renderer": "llvmpipe", "vulkan_supported": False},
            "network": {"adapters": [], "has_wifi": True, "has_ethernet": True},
            "bluetooth": {"present": False, "controller": "none", "powered": False},
            "audio": {"cards": ["Intel HDA"], "pipewire_active": True},
            "storage": {"disks": [{"name": "/dev/sda", "size": "500G", "is_rotational": True, "is_ssd": False, "transport": "sata", "model": "Hitachi HDD"}], "has_nvme": False, "has_ssd": False, "has_hdd": True},
            "display_input": {"displays": [{"output": "eDP-1", "resolution": "1366x768", "primary": True}], "touchpad_present": True, "multitouch": True},
            "power": {"has_battery": True, "battery_pct": 80, "state": "Discharging", "ac_online": False},
            "firmware": {"boot_mode": "bios", "secure_boot": "unsupported"}
        }
        profile, reasons = self.hw_mod.recommend_profile(mock_hw)
        self.assertEqual(profile, "lite")
        self.assertGreater(len(reasons), 0)

    def test_recommend_standard_profile_modern_hardware(self):
        mock_hw = {
            "ram": {"total_mb": 16384, "available_mb": 12000, "swap_total_mb": 2048, "zram_active": True},
            "cpu": {"model": "AMD Ryzen 7 5700U", "arch": "x86_64", "cores": 8, "threads": 16, "flags": ["avx", "avx2", "sse4_2"], "has_avx": True, "has_avx2": True, "has_sse4_2": True, "is_low_power": False, "freq_mhz": 1800.0},
            "gpu": {"devices": [{"device": "AMD Radeon Vega 8", "driver": "amdgpu"}], "active_driver": "amdgpu", "acceleration": "hardware", "renderer": "AMD Radeon Graphics", "vulkan_supported": True},
            "network": {"adapters": [], "has_wifi": True, "has_ethernet": True},
            "bluetooth": {"present": True, "controller": "hci0", "powered": True},
            "audio": {"cards": ["HD-Audio Generic"], "pipewire_active": True},
            "storage": {"disks": [{"name": "/dev/nvme0n1", "size": "512G", "is_rotational": False, "is_ssd": True, "transport": "nvme", "model": "Samsung SSD"}], "has_nvme": True, "has_ssd": True, "has_hdd": False},
            "display_input": {"displays": [{"output": "eDP-1", "resolution": "1920x1080", "primary": True}], "touchpad_present": True, "multitouch": True},
            "power": {"has_battery": True, "battery_pct": 98, "state": "Full", "ac_online": True},
            "firmware": {"boot_mode": "uefi", "secure_boot": "enabled"}
        }
        profile, reasons = self.hw_mod.recommend_profile(mock_hw)
        self.assertEqual(profile, "standard")
        self.assertGreater(len(reasons), 0)

    def test_generate_report_formatting(self):
        hw = self.hw_mod.detect_all()
        report = self.hw_mod.generate_report(hw)
        self.assertIn("MONODESK OS 1.0 — HARDWARE DETECTION & ADAPTIVE PROFILE REPORT", report)
        self.assertIn("ADAPTIVE PROFILE RECOMMENDATION:", report)

if __name__ == "__main__":
    unittest.main()
