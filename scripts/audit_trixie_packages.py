import os
import glob
import subprocess
import sys

manifest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../build/live-build/config/package-lists"))
manifests = sorted(glob.glob(os.path.join(manifest_dir, "*.list.chroot")))

all_packages = {}
for m in manifests:
    name = os.path.basename(m)
    pkgs = []
    with open(m, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pkgs.append(line)
    all_packages[name] = pkgs

unique_packages = sorted(list(set(p for pkgs in all_packages.values() for p in pkgs)))
print(f"Auditing {len(unique_packages)} unique package names across 13 manifests...")

remote_py = """
import subprocess
import sys

packages = sys.argv[1:]
available = []
missing = []

for p in packages:
    res = subprocess.run(['apt-cache', 'policy', p], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if 'Candidate:' in res.stdout:
        candidate = ''
        for line in res.stdout.splitlines():
            if 'Candidate:' in line:
                candidate = line.split('Candidate:')[1].strip()
                break
        if candidate and candidate != '(none)':
            available.append((p, candidate))
        else:
            missing.append(p)
    else:
        missing.append(p)

print(f"SUMMARY: AVAILABLE={len(available)} MISSING={len(missing)}")
if missing:
    print("MISSING:" + ",".join(missing))

print("Simulating unified dependency resolution (apt-get -s install)...")
cmd = ['apt-get', '-s', 'install', '-t', 'trixie', '--no-install-recommends', '-y'] + [p[0] for p in available]
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res.returncode == 0:
    print("[SUCCESS] All packages resolve cleanly together without conflicting dependencies!")
    for line in res.stdout.splitlines():
        if 'upgraded' in line or 'newly installed' in line:
            print("RESOLVED_STAT:", line)
else:
    print("[FAILED] Dependency resolution error:")
    print(res.stderr[:500])
"""

import tempfile
script_file = os.path.join(tempfile.gettempdir(), "check_pkgs.py")
with open(script_file, "w", encoding="utf-8") as f:
    f.write(remote_py)

scp_cmd = [
    "scp", "-i", r"C:\anti\builder_key", "-o", "StrictHostKeyChecking=no",
    "-P", "2222", script_file, "root@127.0.0.1:/tmp/check_pkgs.py"
]
subprocess.run(scp_cmd, check=True)

ssh_cmd = [
    "ssh", "-i", r"C:\anti\builder_key", "-o", "StrictHostKeyChecking=no",
    "-p", "2222", "root@127.0.0.1", "python3 /tmp/check_pkgs.py " + " ".join(unique_packages)
]
proc = subprocess.run(ssh_cmd, capture_output=True, text=True)
print("--- AUDIT RESULT ---")
print(proc.stdout)
if proc.stderr:
    print("STDERR:", proc.stderr)
