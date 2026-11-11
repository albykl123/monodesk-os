#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — Build Dependencies Installation Script
# Prepares the Debian/Ubuntu build environment for live-build and ISO mastering
# ==============================================================================

set -euo pipefail

echo "=== [MONODESK OS] Installing Build Prerequisites ==="

if [[ $EUID -ne 0 ]]; then
    echo "[-] Error: Please run this script with root/sudo privileges."
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update -qq

# Essential ISO building tools
apt-get install -y --no-install-recommends \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    isolinux \
    syslinux-common \
    syslinux-efi \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    rsync \
    git \
    python3 \
    python3-pytest \
    desktop-file-utils \
    shellcheck

echo "[✓] All build dependencies successfully installed."
