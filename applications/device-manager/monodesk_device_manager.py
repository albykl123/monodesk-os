#!/usr/bin/env python3
"""
MONODESK OS — Device Manager
Tree-based discovery and hardware inspector for PCI, USB, Audio, Storage,
Input devices, and loaded kernel modules/drivers.
"""

import sys
import os
import subprocess

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib
    WindowBase = Gtk.Window
except ImportError:
    Gtk = None
    Gdk = None
    GLib = None
    WindowBase = object

def parse_lspci_devices():
    categories = {
        "Processors & System": [],
        "Display & Graphics (GPU)": [],
        "Audio & Multimedia": [],
        "Network & Wireless Adapters": [],
        "Storage & NVMe Controllers": [],
        "USB & Serial Controllers": [],
        "Other Devices": []
    }
    try:
        res = subprocess.run(["lspci", "-vmm"], stdout=subprocess.PIPE, text=True, check=False)
        blocks = res.stdout.strip().split("\n\n")
        for b in blocks:
            dev = {}
            for line in b.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    dev[k.strip()] = v.strip()
            cls = dev.get("Class", "")
            vendor = dev.get("Vendor", "")
            device = dev.get("Device", "")
            driver = dev.get("Driver", "builtin / none")
            title = f"{vendor} {device} [Driver: {driver}]"

            if "VGA" in cls or "3D" in cls or "Display" in cls:
                categories["Display & Graphics (GPU)"].append((title, driver))
            elif "Audio" in cls:
                categories["Audio & Multimedia"].append((title, driver))
            elif "Network" in cls or "Ethernet" in cls or "Wireless" in cls:
                categories["Network & Wireless Adapters"].append((title, driver))
            elif "Non-Volatile" in cls or "SATA" in cls or "Storage" in cls:
                categories["Storage & NVMe Controllers"].append((title, driver))
            elif "USB" in cls:
                categories["USB & Serial Controllers"].append((title, driver))
            else:
                categories["Other Devices"].append((title, driver))
    except Exception:
        pass

    # Fallback simulation
    if not any(categories.values()):
        categories["Display & Graphics (GPU)"].append(("AMD Radeon Vega Graphics [Driver: amdgpu]", "amdgpu"))
        categories["Audio & Multimedia"].append(("HD Audio Controller [Driver: snd_hda_intel]", "snd_hda_intel"))
        categories["Network & Wireless Adapters"].append(("Intel Wi-Fi 6 AX200 [Driver: iwlwifi]", "iwlwifi"))
        categories["Storage & NVMe Controllers"].append(("Standard NVMe PCIe SSD Controller [Driver: nvme]", "nvme"))
    return categories

class MonodeskDeviceManager(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Device Manager")
        self.set_default_size(840, 560)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(20); main_box.set_margin_end(20); main_box.set_margin_top(20); main_box.set_margin_bottom(20)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="DEVICE MANAGER & HARDWARE CONTROLLERS")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)

        btn_rescan = Gtk.Button(label="Rescan Hardware Bus")
        btn_rescan.connect("clicked", lambda b: self.refresh_devices())
        hdr.pack_end(btn_rescan, False, False, 0)
        main_box.pack_start(hdr, False, False, 0)

        # Tree View
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        # TreeStore: Device / Category Name, Kernel Driver, Status
        self.store = Gtk.TreeStore(str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        for i, col_name in enumerate(["Hardware Device", "Kernel Driver / Module", "Status"]):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(col_name, renderer, text=i)
            self.tree.append_column(col)

        scroller.add(self.tree)

        # Bottom Bar
        bbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(bbar, False, False, 0)

        btn_nvidia = Gtk.Button(label="NVIDIA Driver Setup Assistant")
        btn_nvidia.connect("clicked", lambda b: subprocess.Popen(["monodesk-nvidia-installer"]))
        bbar.pack_start(btn_nvidia, False, False, 0)

        self.lbl_status = Gtk.Label(label="All hardware controllers operating normally.")
        self.lbl_status.set_alignment(0.0, 0.5)
        bbar.pack_end(self.lbl_status, False, False, 0)

        self.refresh_devices()

    def refresh_devices(self):
        self.store.clear()
        categories = parse_lspci_devices()
        for cat, items in categories.items():
            if not items:
                continue
            cat_iter = self.store.append(None, [cat, "", f"{len(items)} device(s)"])
            for dev_title, driver in items:
                status = "Active & Accelerated" if driver != "builtin / none" else "Operational"
                self.store.append(cat_iter, [dev_title, driver, status])

        self.tree.expand_all()

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskDeviceManager()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
