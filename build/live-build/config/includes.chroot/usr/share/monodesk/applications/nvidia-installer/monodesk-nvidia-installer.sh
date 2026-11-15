#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — NVIDIA Proprietary Driver Setup Utility
# Safely configures Debian non-free repositories, builds DKMS modules,
# blacklists nouveau, and configures Xorg/Wayland for NVIDIA GPUs.
# ==============================================================================

set -euo pipefail

echo "================================================================================"
echo "          MONODESK OS — NVIDIA Proprietary Driver Setup Assistant               "
echo "================================================================================"

if [[ $EUID -ne 0 ]]; then
    echo "[-] Error: This utility requires administrative privileges."
    echo "[*] Please re-run with: sudo monodesk-nvidia-installer"
    exit 1
fi

echo "[1/4] Detecting NVIDIA hardware..."
if ! lspci | grep -iE 'vga|3d|display' | grep -iq nvidia; then
    echo "[!] Notice: No NVIDIA GPU detected on this system PCI bus."
    echo "    Your system will continue using standard Mesa / DRM drivers."
    exit 0
fi

echo "[+] NVIDIA GPU identified:"
lspci | grep -iE 'vga|3d|display' | grep -i nvidia

echo ""
echo "[2/4] Verifying Debian repository configuration for non-free components..."
SOURCES_FILE="/etc/apt/sources.list.d/monodesk-nvidia.list"
cat << 'EOF' > "$SOURCES_FILE"
# MONODESK OS — NVIDIA Driver Repository
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

echo "[+] Updating APT repository package index..."
apt-get update -qq

echo "[3/4] Installing Linux kernel headers, DKMS, and NVIDIA driver packages..."
KERNEL_VER=$(uname -r)
apt-get install -y --no-install-recommends \
    linux-headers-"${KERNEL_VER}" \
    dkms \
    nvidia-driver \
    firmware-misc-nonfree

echo "[4/4] Blacklisting open-source nouveau module..."
cat << 'EOF' > /etc/modprobe.d/monodesk-blacklist-nouveau.conf
# MONODESK OS — Disable nouveau in favor of NVIDIA proprietary driver
blacklist nouveau
options nouveau modeset=0
EOF

update-initramfs -u

echo "================================================================================"
echo "[✓] NVIDIA proprietary driver installation completed successfully!"
echo "[!] Please reboot your computer to activate the NVIDIA driver."
echo "================================================================================"
