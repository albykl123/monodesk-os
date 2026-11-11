#!/usr/bin/env python3
"""
MONODESK OS — System Monitor
Lightweight task manager and system resource monitor.
Samples CPU, RAM, Swap/zRAM, Disk, and active processes without external dependencies.
"""

import sys
import os
import time
import subprocess
import signal
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

class MonodeskSystemMonitor(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK System Monitor")
        self.set_default_size(840, 560)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        self.add(main_box)

        # Overview Metrics Grid
        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(8)
        grid.set_column_homogeneous(True)
        main_box.pack_start(grid, False, False, 0)

        # CPU Box
        self.lbl_cpu = Gtk.Label(label="CPU: Calculating...")
        self.bar_cpu = Gtk.LevelBar(min_value=0.0, max_value=100.0)
        grid.attach(self.lbl_cpu, 0, 0, 1, 1)
        grid.attach(self.bar_cpu, 0, 1, 1, 1)

        # RAM Box
        self.lbl_ram = Gtk.Label(label="RAM: Calculating...")
        self.bar_ram = Gtk.LevelBar(min_value=0.0, max_value=100.0)
        grid.attach(self.lbl_ram, 1, 0, 1, 1)
        grid.attach(self.bar_ram, 1, 1, 1, 1)

        # SWAP / zRAM Box
        self.lbl_swap = Gtk.Label(label="SWAP / zRAM: Calculating...")
        self.bar_swap = Gtk.LevelBar(min_value=0.0, max_value=100.0)
        grid.attach(self.lbl_swap, 2, 0, 1, 1)
        grid.attach(self.bar_swap, 2, 1, 1, 1)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(sep, False, False, 6)

        # Process List
        p_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        p_title = Gtk.Label(label="RUNNING PROCESSES")
        p_title.get_style_context().add_class("h3")
        p_hdr.pack_start(p_title, False, False, 0)

        self.btn_kill = Gtk.Button(label="End Process")
        self.btn_kill.get_style_context().add_class("destructive-action")
        self.btn_kill.connect("clicked", self.on_kill_process)
        p_hdr.pack_end(self.btn_kill, False, False, 0)
        main_box.pack_start(p_hdr, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        # Process TreeView: PID, Name, User, Status, Memory MB
        self.proc_store = Gtk.ListStore(int, str, str, str, float)
        self.tree_view = Gtk.TreeView(model=self.proc_store)
        self.tree_view.set_rules_hint(True)

        cols = [("PID", 0), ("Process Name", 1), ("User", 2), ("State", 3), ("Memory (MB)", 4)]
        for title, idx in cols:
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=idx)
            col.set_sort_column_id(idx)
            self.tree_view.append_column(col)

        scroller.add(self.tree_view)

        self.prev_idle = 0
        self.prev_total = 1
        self.refresh_stats()
        GLib.timeout_add_seconds(2, self.refresh_stats)

    def refresh_stats(self):
        # CPU
        try:
            with open("/proc/stat", "r") as f:
                parts = [float(x) for x in f.readline().split()[1:8]]
                idle = parts[3] + parts[4]
                total = sum(parts)
                d_idle = idle - self.prev_idle
                d_total = total - self.prev_total
                self.prev_idle, self.prev_total = idle, total
                cpu_pct = 0.0
                if d_total > 0:
                    cpu_pct = (1.0 - (d_idle / d_total)) * 100.0
                cpu_pct = max(0.0, min(100.0, cpu_pct))
                self.lbl_cpu.set_text(f"CPU Load: {cpu_pct:.1f}%")
                self.bar_cpu.set_value(cpu_pct)
        except Exception:
            pass

        # Memory & Swap
        try:
            mem = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    p = line.split(":")
                    if len(p) == 2:
                        mem[p[0].strip()] = int(p[1].strip().split()[0])
            total = mem.get("MemTotal", 1024)
            avail = mem.get("MemAvailable", 512)
            used = total - avail
            ram_pct = (used / total) * 100.0
            self.lbl_ram.set_text(f"RAM: {used/1024:.0f} / {total/1024:.0f} MB ({ram_pct:.0f}%)")
            self.bar_ram.set_value(ram_pct)

            sw_total = mem.get("SwapTotal", 0)
            sw_free = mem.get("SwapFree", 0)
            if sw_total > 0:
                sw_used = sw_total - sw_free
                sw_pct = (sw_used / sw_total) * 100.0
                self.lbl_swap.set_text(f"SWAP/zRAM: {sw_used/1024:.0f} / {sw_total/1024:.0f} MB")
                self.bar_swap.set_value(sw_pct)
            else:
                self.lbl_swap.set_text("SWAP/zRAM: Inactive")
                self.bar_swap.set_value(0)
        except Exception:
            pass

        # Refresh processes (top 50 by memory)
        self.refresh_processes()
        return True

    def refresh_processes(self):
        procs = []
        try:
            for pid_dir in os.listdir("/proc"):
                if not pid_dir.isdigit():
                    continue
                pid = int(pid_dir)
                try:
                    stat_path = f"/proc/{pid}/stat"
                    status_path = f"/proc/{pid}/status"
                    name = "unknown"
                    state = "?"
                    mem_mb = 0.0
                    user = "root"

                    with open(status_path, "r") as f:
                        for line in f:
                            if line.startswith("Name:"):
                                name = line.split(":", 1)[1].strip()
                            elif line.startswith("State:"):
                                state = line.split(":", 1)[1].strip().split()[0]
                            elif line.startswith("VmRSS:"):
                                mem_mb = int(line.split()[1]) / 1024.0
                    procs.append((pid, name, "user", state, round(mem_mb, 1)))
                except (FileNotFoundError, PermissionError):
                    continue
        except Exception:
            pass

        procs.sort(key=lambda x: x[4], reverse=True)
        self.proc_store.clear()
        for p in procs[:60]:
            self.proc_store.append(list(p))

    def on_kill_process(self, widget):
        selection = self.tree_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            pid = model[treeiter][0]
            try:
                os.kill(pid, signal.SIGTERM)
                self.refresh_processes()
            except Exception as e:
                pass

if __name__ == "__main__":
    if Gtk is not None:
        win = MonodeskSystemMonitor()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
