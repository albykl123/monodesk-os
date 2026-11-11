#!/usr/bin/env python3
"""
MONODESK OS — Hardware Report Diagnostic Test
"""

import unittest
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "applications/hardware-report"))

class TestHardwareDataCollection(unittest.TestCase):
    def test_collect_data_structure(self):
        from monodesk_hardware_report import collect_hardware_data
        data = collect_hardware_data()
        self.assertIn("os", data)
        self.assertIn("kernel", data)
        self.assertIn("arch", data)
        self.assertIn("cpu", data)
        self.assertIn("ram_gb", data)
        self.assertIn("gpu", data)
        self.assertEqual(data["os"], "MONODESK OS 1.0 (Universal PC Edition)")

if __name__ == "__main__":
    unittest.main()
