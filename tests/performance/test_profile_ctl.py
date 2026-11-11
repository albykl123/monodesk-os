#!/usr/bin/env python3
"""
MONODESK OS — Performance Profile Toggling Test
"""

import unittest
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "system/power"))

class TestProfileCtlLogic(unittest.TestCase):
    def test_default_profile(self):
        import importlib.util
        import importlib.machinery
        script_path = os.path.join(REPO_ROOT, "system/power/monodesk-profile-ctl")
        loader = importlib.machinery.SourceFileLoader("profile_ctl", script_path)
        spec = importlib.util.spec_from_loader("profile_ctl", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        cur = mod.get_current_profile()
        self.assertIn(cur, ["lite", "standard"])

if __name__ == "__main__":
    unittest.main()
