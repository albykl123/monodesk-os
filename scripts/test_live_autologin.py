Created At: 2026-11-16T14:39:20+05:30
Completed At: 2026-11-16T14:39:20+05:30
Created At: 2026-11-16T14:39:20+05:30
Completed At: 2026-11-16T14:39:20+05:30
Showing lines 1-100 of 105
1: import os
2: import sys
3: import time
4: import socket
5: import json
6: import subprocess
7: from PIL import Image
8: 
9: QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
10: KERNEL = r"D:\anti\iso_staging_v201\live\vmlinuz"
11: INITRD = r"D:\anti\iso_staging_v201\live\initrd.img"
12: ISO = r"D:\anti\monodesk-os\releases\monodesk-os-2.0.1-rc2-universal-amd64.iso"
13: OUT_DIR = r"D:\anti\monodesk-os\artifacts\qa"
14: SERIAL_LOG = os.path.join(OUT_DIR, "live_autologin.log")
15: SCREEN_PPM = os.path.join(OUT_DIR, "live_autologin_screen.ppm")
16: SCREEN_PNG = os.path.join(OUT_DIR, "live_autologin_screen.png")
17: 
18: def test_autologin():
19:     os.makedirs(OUT_DIR, exist_ok=True)
20:     if os.path.exists(SERIAL_LOG):
21:         os.remove(SERIAL_LOG)
22:     if os.path.exists(SCREEN_PPM):
23:         os.remove(SCREEN_PPM)
24: 
25:     cmd = [
26:         QEMU,
27:         "-accel", "whpx",
28:         "-m", "4096",
29:         "-smp", "4",
30:         "-kernel", KERNEL,
31:         "-initrd", INITRD,
32:         "-cdrom", ISO,
33:         "-append", "boot=live components username=monodesk console=tty0 console=ttyS0 loglevel=7",
34:         "-vga", "virtio",
35:         "-serial", f"file:{SERIAL_LOG}",
36:         "-display", "none",
37:         "-qmp", "tcp:127.0.0.1:5567,server,nowait"
38:     ]
39: 
40:     print("[*] Launching QEMU with username=monodesk...", flush=True)
41:     start_t = time.time()
42:     proc = subprocess.Popen(cmd)
43:     qmp = None
44:     try:
45:         time.sleep(3)
46:         qmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
47:         qmp.connect(("127.0.0.1", 5567))
48:         qmp.recv(1024)
49:         qmp.sendall(b'{"execute": "qmp_capabilities"}\n')
50:         qmp.recv(1024)
51:         print("[✓] QMP connected.", flush=True)
52: 
53:         for i in range(50):
54:             time.sleep(1)
55:             elapsed = time.time() - start_t
56:             if os.path.exists(SERIAL_LOG):
57:                 try:
58:                     with open(SERIAL_LOG, "r", encoding="utf-8", errors="ignore") as f:
59:                         log_txt = f.read()
60:                     if "monodesk" in log_txt and ("session" in log_txt or "desktop" in log_txt or "lightdm" in log_txt):
61:                         print(f"[{elapsed:.1f}s] Activity in serial log: {len(log_txt)} bytes", flush=True)
62:                     if "graphical.target" in log_txt and elapsed > 25:
63:                         print(f"[✓] Reached graphical target after {elapsed:.1f}s!", flush=True)
64:                         break
65:                 except Exception:
66:                     pass
67: 
68:         # Wait an extra 8s for user session to initialize
69:         time.sleep(8)
70: 
71:         # Screendump
72:         safe_ppm = SCREEN_PPM.replace("\\", "/")
73:         req = json.dumps({"execute": "screendump", "arguments": {"filename": safe_ppm}}) + "\n"
74:         qmp.sendall(req.encode("utf-8"))
75:         res = qmp.recv(2048)
76:         print("[*] QMP screendump response:", res.decode("utf-8", errors="ignore").strip(), flush=True)
77:         time.sleep(2)
78:         qmp.close()
79: 
80:         if os.path.exists(SCREEN_PPM):
81:             img = Image.open(SCREEN_PPM)
82:             img.save(SCREEN_PNG)
83:             print(f"[✓] Screendump successfully saved: {SCREEN_PNG} ({img.size})", flush=True)
84:         else:
85:             print("[-] Screendump PPM not found on disk.", flush=True)
86: 
87:     finally:
88:         proc.terminate()
89:         try:
90:             proc.wait(timeout=5)
91:         except Exception:
92:             proc.kill()
93: 
94:     if os.path.exists(SERIAL_LOG):
95:         print(f"[✓] Serial log captured: {os.path.getsize(SERIAL_LOG)} bytes", flush=True)
96:         with open(SERIAL_LOG, "r", encoding="utf-8", errors="ignore") as f:
97:             lines = f.readlines()
98:         print(f"[*] Total log lines: {len(lines)}", flush=True)
99:         user_setup_lines = [l.strip() for l in lines if any(k in l.lower() for k in ["user-setup", "monodesk", "lightdm", "hyprland", "quickshell"])]
100:         print(f"[*] Filtered key events ({len(user_setup_lines)} lines):")