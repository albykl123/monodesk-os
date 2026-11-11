#!/usr/bin/env python3
"""
MONODESK OS — Application Test Suite
Validates application modules, telemetry extraction logic, and redaction.
"""

import unittest
import sys
import os
import re

# Add applications to path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/hardware-report"))
sys.path.insert(0, os.path.join(REPO_ROOT, "desktop/widgets"))
sys.path.insert(0, os.path.join(REPO_ROOT, "system/power"))

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

if __name__ == "__main__":
    unittest.main()
