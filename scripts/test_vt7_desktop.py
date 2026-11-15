import time
import socket
import json
import subprocess
import os
from PIL import Image

qemu_exe = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
iso = r"D:\anti\monodesk-os\releases\monodesk-os-2.0.0-universal-amd64.iso"
kernel = r"C:\anti\iso_boot_test\vmlinuz-6.12.117+deb13-amd64"
initrd = r"C:\anti\iso_boot_test\initrd.img-6.12.117+deb13-amd64"
out_ppm = r"C:\anti\iso_boot_test\vt7_desktop.ppm"

cmd = [
    qemu_exe,
    "-accel", "whpx",
    "-m", "4096",
    "-smp", "4",
    "-kernel", kernel,
    "-initrd", initrd,
    "-cdrom", iso,
    "-append", "boot=live components username=monodesk console=ttyS0 console=tty1",
    "-display", "none",
    "-qmp", "tcp:127.0.0.1:5561,server,nowait"
]

print("Starting QEMU...")
proc = subprocess.Popen(cmd)
try:
    time.sleep(2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 5561))
    s.recv(1024)
    s.sendall(b'{"execute": "qmp_capabilities"}\n')
    s.recv(1024)

    print("Waiting 28 seconds for boot and LightDM...")
    time.sleep(28)

    # Send Ctrl+Alt+F7 to switch to VT7
    print("Sending Ctrl+Alt+F7...")
    switch_cmd = {
        "execute": "send-key",
        "arguments": {
            "keys": [
                {"type": "qcode", "data": "ctrl"},
                {"type": "qcode", "data": "alt"},
                {"type": "qcode", "data": "f7"}
            ]
        }
    }
    s.sendall((json.dumps(switch_cmd) + "\n").encode("utf-8"))
    time.sleep(2)
    s.recv(2048)

    safe_ppm = out_ppm.replace("\\", "/")
    req = json.dumps({"execute": "screendump", "arguments": {"filename": safe_ppm}}) + "\n"
    s.sendall(req.encode("utf-8"))
    time.sleep(1)
    s.close()
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

if os.path.exists(out_ppm):
    img = Image.open(out_ppm)
    png_path = out_ppm.replace(".ppm", ".png")
    img.save(png_path)
    print(f"Captured VT7 screen! Saved to {png_path}, size={img.size}")
    colors = img.getcolors(maxcolors=256*256*256)
    print(f"Unique colors: {len(colors) if colors else 'many'}")
else:
    print("No screendump captured.")
