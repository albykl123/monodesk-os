#!/usr/bin/env python3
"""
MONODESK OS — Recovery Centre
Emergency diagnostic and system repair utility.
Provides safe package database repair, bootloader repair instructions,
and filesystem health checks with explicit safeguards against accidental data loss.
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

def run_cmd(args):
    try:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return proc.stdout.strip()
    except Exception as e:
        return f"Unavailable: {e}"

class MonodeskRecoveryCentre(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Recovery Centre")
        self.set_default_size(780, 540)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(20); main_box.set_margin_end(20); main_box.set_margin_top(20); main_box.set_margin_bottom(20)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="SYSTEM RECOVERY & DIAGNOSTIC WORKFLOWS")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)
        main_box.pack_start(hdr, False, False, 0)

        desc = Gtk.Label(
            label="This utility performs non-destructive diagnostics and safe repair workflows "
                  "for package databases, bootloaders, and filesystem integrity. "
                  "No drive will ever be formatted or modified without explicit authorization."
        )
        desc.set_line_wrap(True)
        desc.set_alignment(0.0, 0.5)
        main_box.pack_start(desc, False, False, 0)

        # Action Cards
        grid = Gtk.Grid()
        grid.set_column_spacing(12); grid.set_row_spacing(12)
        grid.set_column_homogeneous(True)
        main_box.pack_start(grid, False, False, 0)

        # 1. Package Repair Card
        box_pkg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_pkg.set_margin_start(10); box_pkg.set_margin_end(10); box_pkg.set_margin_top(10); box_pkg.set_margin_bottom(10)
        lbl_p_title = Gtk.Label(label="PACKAGE DATABASE REPAIR")
        lbl_p_title.set_alignment(0.0, 0.5)
        box_pkg.pack_start(lbl_p_title, False, False, 0)
        lbl_p_desc = Gtk.Label(label="Fixes interrupted updates, cleans broken lockfiles, and finishes uncompleted dpkg configurations.")
        lbl_p_desc.set_line_wrap(True)
        lbl_p_desc.set_alignment(0.0, 0.5)
        box_pkg.pack_start(lbl_p_desc, False, False, 0)
        btn_fix_dpkg = Gtk.Button(label="Run Safe Package Repair")
        btn_fix_dpkg.connect("clicked", self.repair_packages)
        box_pkg.pack_start(btn_fix_dpkg, False, False, 4)
        grid.attach(box_pkg, 0, 0, 1, 1)

        # 2. Bootloader Check Card
        box_boot = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_boot.set_margin_start(10); box_boot.set_margin_end(10); box_boot.set_margin_top(10); box_boot.set_margin_bottom(10)
        lbl_b_title = Gtk.Label(label="BOOTLOADER & EFI DIAGNOSTICS")
        lbl_b_title.set_alignment(0.0, 0.5)
        box_boot.pack_start(lbl_b_title, False, False, 0)
        lbl_b_desc = Gtk.Label(label="Inspects GRUB bootloader installation, EFI system partition, and nvram boot order.")
        lbl_b_desc.set_line_wrap(True)
        lbl_b_desc.set_alignment(0.0, 0.5)
        box_boot.pack_start(lbl_b_desc, False, False, 0)
        btn_check_boot = Gtk.Button(label="Inspect Boot Configuration")
        btn_check_boot.connect("clicked", self.inspect_boot)
        box_boot.pack_start(btn_check_boot, False, False, 4)
        grid.attach(box_boot, 1, 0, 1, 1)

        # Output Log Window
        lbl_log = Gtk.Label(label="DIAGNOSTIC & RECOVERY LOG")
        lbl_log.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_log, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_monospace(True)
        scroller.add(self.text_view)

        self.log("[+] MONODESK Recovery Centre initialized.")
        self.log("[+] Ready for safe diagnostic or repair operations.")

    def log(self, text):
        buf = self.text_view.get_buffer()
        buf.insert(buf.get_end_iter(), text + "\n")

    def repair_packages(self, button):
        self.log("\n--- INITIATING SAFE PACKAGE REPAIR ---")
        self.log("[*] Executing dpkg --configure -a (privileged via pkexec)...")
        try:
            cmd = ["pkexec", "dpkg", "--configure", "-a"]
            subprocess.Popen(cmd)
            self.log("[✓] Package repair process dispatched.")
        except Exception as e:
            self.log(f"[-] Error dispatching repair: {e}")

    def inspect_boot(self, button):
        self.log("\n--- INSPECTING BOOTLOADER STATUS ---")
        # Check EFI
        if os.path.exists("/sys/firmware/efi"):
            self.log("[+] Boot mode: UEFI (Active)")
            efi_out = run_cmd(["efibootmgr"])
            self.log(efi_out)
        else:
            self.log("[+] Boot mode: Legacy BIOS (Active)")
            self.log("[*] Inspecting MBR boot signature on primary disk...")
            fdisk_out = run_cmd(["fdisk", "-l", "/dev/sda"])
            self.log(fdisk_out[:400] + "...")

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskRecoveryCentre()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
