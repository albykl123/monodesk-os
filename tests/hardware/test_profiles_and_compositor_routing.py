import os
import sys
import unittest
from pathlib import Path

# Add repo root to import path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "system/hardware"))

from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec

loader = SourceFileLoader("monodesk_hw_detect", str(REPO_ROOT / "system/hardware/monodesk-hw-detect"))
spec = spec_from_loader("monodesk_hw_detect", loader)
hw_mod = module_from_spec(spec)
loader.exec_module(hw_mod)

class TestHardwareProfileAndCompositorRouting(unittest.TestCase):
    def setUp(self):
        # 1. Lenovo IdeaPad Slim 5 (Modern AMD Benchmark)
        self.ideapad_slim_5 = {
            "cpu": {
                "arch": "x86_64",
                "vendor": "AuthenticAMD",
                "model": "AMD Ryzen 7 5700U with Radeon Graphics",
                "cores": 8,
                "threads": 16,
                "flags": ["avx", "avx2", "sse4_2"],
                "has_avx": True,
                "has_avx2": True,
                "has_sse4_2": True,
                "freq_mhz": 1800.0,
                "is_low_power": False
            },
            "ram": {
                "total_mb": 15280,
                "available_mb": 13400,
                "swap_total_mb": 8192,
                "zram_active": False
            },
            "gpu": {
                "devices": [{"device": "VGA compatible controller: AMD Radeon Lucienne", "driver": "amdgpu"}],
                "active_driver": "amdgpu",
                "acceleration": "hardware",
                "renderer": "AMD Radeon Graphics (radeonsi, renior, LLVM 19.1.7)",
                "vulkan_supported": True
            },
            "network": {
                "adapters": [{"name": "wlan0", "type": "wireless", "driver": "rtw89_8852ae", "state": "up"}],
                "has_wifi": True,
                "has_ethernet": False
            },
            "bluetooth": {
                "present": True,
                "controller": "Realtek Bluetooth 5.2",
                "powered": True
            },
            "audio": {
                "cards": ["HDA-Intel - HD-Audio Generic", "sof-renoir"],
                "pipewire_active": True
            },
            "storage": {
                "disks": [{
                    "name": "/dev/nvme0n1",
                    "size": "512G",
                    "is_rotational": False,
                    "is_ssd": True,
                    "transport": "nvme",
                    "model": "SAMSUNG MZVL2512HCJQ"
                }],
                "has_nvme": True,
                "has_ssd": True,
                "has_hdd": False
            },
            "display_input": {
                "displays": [{"output": "eDP-1", "resolution": "1920x1080", "primary": True}],
                "touchpad_present": True,
                "multitouch": True
            },
            "power": {
                "has_battery": True,
                "battery_pct": 85,
                "state": "Discharging",
                "ac_online": False
            },
            "firmware": {
                "boot_mode": "uefi",
                "secure_boot": "disabled"
            }
        }

        # 2. Lenovo B590 (Legacy Intel Benchmark)
        self.lenovo_b590 = {
            "cpu": {
                "arch": "x86_64",
                "vendor": "GenuineIntel",
                "model": "Intel(R) Core(TM) i3-2348M CPU @ 2.30GHz",
                "cores": 2,
                "threads": 4,
                "flags": ["sse4_2"],
                "has_avx": False,
                "has_avx2": False,
                "has_sse4_2": True,
                "freq_mhz": 2300.0,
                "is_low_power": True
            },
            "ram": {
                "total_mb": 3840,
                "available_mb": 2400,
                "swap_total_mb": 2048,
                "zram_active": True
            },
            "gpu": {
                "devices": [{"device": "VGA compatible controller: Intel 2nd Generation Core Processor Family", "driver": "i915"}],
                "active_driver": "i915",
                "acceleration": "software_rasterizer", # Sandy Bridge HD 3000 lacks modern DRM format modifiers
                "renderer": "llvmpipe (LLVM 19.1.7, 256 bits)",
                "vulkan_supported": False
            },
            "network": {
                "adapters": [
                    {"name": "eth0", "type": "ethernet", "driver": "r8169", "state": "up"},
                    {"name": "wlan0", "type": "wireless", "driver": "ath9k", "state": "up"}
                ],
                "has_wifi": True,
                "has_ethernet": True
            },
            "bluetooth": {
                "present": True,
                "controller": "Broadcom BCM20702",
                "powered": True
            },
            "audio": {
                "cards": ["HDA Intel PCH"],
                "pipewire_active": True
            },
            "storage": {
                "disks": [{
                    "name": "/dev/sda",
                    "size": "500G",
                    "is_rotational": True,
                    "is_ssd": False,
                    "transport": "sata",
                    "model": "WDC WD5000LPVT"
                }],
                "has_nvme": False,
                "has_ssd": False,
                "has_hdd": True
            },
            "display_input": {
                "displays": [{"output": "LVDS-1", "resolution": "1366x768", "primary": True}],
                "touchpad_present": True,
                "multitouch": True
            },
            "power": {
                "has_battery": True,
                "battery_pct": 90,
                "state": "Charging",
                "ac_online": True
            },
            "firmware": {
                "boot_mode": "bios",
                "secure_boot": "unsupported"
            }
        }

    def test_ideapad_slim_5_evaluation(self):
        """Lenovo IdeaPad Slim 5 must receive Standard profile and Wayland session."""
        profile, reasons = hw_mod.recommend_profile(self.ideapad_slim_5)
        self.assertEqual(profile, "standard")
        self.assertTrue(any("Ample RAM" in r for r in reasons))
        self.assertTrue(any("Hardware-accelerated graphics" in r for r in reasons))

        compositor = hw_mod.check_compositor(self.ideapad_slim_5)
        self.assertEqual(compositor, "wayland")

    def test_lenovo_b590_evaluation(self):
        """Lenovo B590 must receive Lite profile and fallback X11 session."""
        profile, reasons = hw_mod.recommend_profile(self.lenovo_b590)
        self.assertEqual(profile, "lite")
        self.assertTrue(any("below 6 GB threshold" in r for r in reasons))
        self.assertTrue(any("rotational HDD" in r for r in reasons))

        compositor = hw_mod.check_compositor(self.lenovo_b590)
        self.assertEqual(compositor, "x11")

if __name__ == "__main__":
    unittest.main()
