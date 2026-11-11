#!/usr/bin/env python3
"""
MONODESK OS — Hardware Diagnostic Report Generator
Detects CPU, GPU, RAM, Storage, Network, Audio, Kernel, and Driver status.
Exports diagnostic reports with private identifiers (MAC, Serials, UUIDs) redacted.
"""

import sys
import os
import re
import json
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

def run_command_safe(args):
    try:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return proc.stdout.strip()
    except Exception as e:
        return f"Unavailable: {e}"

def redact_sensitive_info(text):
    # Redact MAC addresses (00:1A:2B:3C:4D:5E)
    text = re.sub(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', '[REDACTED_MAC]', text)
    # Redact UUIDs
    text = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '[REDACTED_UUID]', text)
    # Redact Serial numbers
    text = re.sub(r'(Serial Number|Serial|serial):\s*[\w\d-]+', r'\1: [REDACTED_SERIAL]', text, flags=re.IGNORECASE)
    # Redact IPv4 addresses (excluding localhost)
    text = re.sub(r'\b(?!127\.0\.0\.1)(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[REDACTED_IP]', text)
    return text

def collect_hardware_data():
    data = {}

    # OS & Kernel
    data["os"] = "MONODESK OS 1.0 (Universal PC Edition)"
    data["kernel"] = run_command_safe(["uname", "-r"])
    data["arch"] = run_command_safe(["uname", "-m"])

    # CPU
    cpu_info = "Unknown CPU"
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    cpu_info = line.split(":", 1)[1].strip()
                    break
    except Exception:
        pass
    data["cpu"] = cpu_info
    data["cpu_cores"] = os.cpu_count() or 1

    # Memory
    mem_total = 0
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if "MemTotal" in line:
                    mem_total = int(line.split()[1]) / (1024 * 1024)
                    break
    except Exception:
        pass
    data["ram_gb"] = round(mem_total, 2)

    # GPU
    lspci_out = run_command_safe(["lspci", "-nnk"])
    gpu_list = []
    for line in lspci_out.splitlines():
        if "VGA compatible controller" in line or "3D controller" in line or "Display controller" in line:
            gpu_list.append(line.strip())
    data["gpu"] = gpu_list if gpu_list else ["Integrated / Basic Display Controller"]

    # Storage
    lsblk_out = run_command_safe(["lsblk", "-d", "-o", "NAME,SIZE,MODEL,TYPE"])
    data["storage"] = redact_sensitive_info(lsblk_out)

    # Network
    ip_link = run_command_safe(["ip", "-br", "link"])
    data["network_devices"] = redact_sensitive_info(ip_link)

    # Audio
    data["audio"] = run_command_safe(["lspci", "-nnk"]).split("Audio device:")[-1].splitlines()[0].strip() if "Audio device:" in lspci_out else "PipeWire HD Audio"

    # Microcode
    dmesg_microcode = run_command_safe(["dmesg"]).lower()
    data["microcode_status"] = "Active" if "microcode" in dmesg_microcode else "Default BIOS Revision"

    return data

class MonodeskHardwareReportWindow(WindowBase):
    def __init__(self):
        super().__init__(title="MONODESK Hardware Diagnostic Report")
        self.set_default_size(720, 580)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="SYSTEM & HARDWARE DIAGNOSTICS")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)

        btn_refresh = Gtk.Button(label="Rescan")
        btn_refresh.connect("clicked", lambda b: self.refresh_report())
        hdr.pack_end(btn_refresh, False, False, 0)
        main_box.pack_start(hdr, False, False, 0)

        # Text View for Diagnostic
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_monospace(True)
        self.text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        scroller.add(self.text_view)

        # Actions
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(btn_box, False, False, 0)

        btn_export = Gtk.Button(label="Export Redacted Report (JSON)")
        btn_export.connect("clicked", self.export_json)
        btn_box.pack_start(btn_export, False, False, 0)

        btn_copy = Gtk.Button(label="Copy Report to Clipboard")
        btn_copy.connect("clicked", self.copy_to_clipboard)
        btn_box.pack_start(btn_copy, False, False, 0)

        self.report_data = {}
        self.refresh_report()

    def refresh_report(self):
        self.report_data = collect_hardware_data()
        lines = [
            "================================================================================",
            "                   MONODESK OS 1.0 — HARDWARE COMPATIBILITY REPORT              ",
            "================================================================================",
            f"OPERATING SYSTEM:     {self.report_data.get('os')}",
            f"KERNEL VERSION:       {self.report_data.get('kernel')} ({self.report_data.get('arch')})",
            f"CPU PROCESSOR:        {self.report_data.get('cpu')} ({self.report_data.get('cpu_cores')} Cores)",
            f"SYSTEM MEMORY:        {self.report_data.get('ram_gb')} GB Physical RAM",
            f"MICROCODE STATUS:     {self.report_data.get('microcode_status')}",
            "",
            "--- GRAPHICS ACCELERATION ---",
        ]
        for g in self.report_data.get("gpu", []):
            lines.append(f"  • {g}")
        lines.extend([
            "",
            "--- STORAGE DEVICES ---",
            self.report_data.get("storage", "None detected"),
            "",
            "--- NETWORK CONTROLLERS ---",
            self.report_data.get("network_devices", "None detected"),
            "",
            "--- AUDIO SUBSYSTEM ---",
            f"  • {self.report_data.get('audio')}",
            "================================================================================",
            "NOTICE: Private hardware identifiers (MAC, Serial, UUIDs) are automatically redacted.",
        ])

        buf = self.text_view.get_buffer()
        buf.set_text("\n".join(lines))

    def export_json(self, widget):
        chooser = Gtk.FileChooserDialog(
            title="Export Redacted Diagnostic Report",
            parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        chooser.set_current_name("monodesk-hardware-report.json")
        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            path = chooser.get_filename()
            with open(path, "w") as f:
                json.dump(self.report_data, f, indent=2)
        chooser.destroy()

    def copy_to_clipboard(self, widget):
        buf = self.text_view.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)

if __name__ == "__main__":
    app = MonodeskHardwareReportWindow()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
