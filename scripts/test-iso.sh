#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — QEMU Virtual Machine Test Harness
# Tests bootability, live desktop environment, and disposable VM installation
# ==============================================================================

set -euo pipefail

ISO_PATH="${1:-releases/monodesk-os-1.0.0-universal-amd64.iso}"
RAM_MB="${2:-4096}"  # Default: 4GB RAM (matches Lenovo B590 benchmark)
BOOT_MODE="${3:-uefi}" # uefi or bios
DISPOSABLE_DISK="vm-disposable-test.qcow2"

if [[ ! -f "$ISO_PATH" ]]; then
    echo "[-] Error: ISO image not found at: $ISO_PATH"
    echo "    Please build the image first using: sudo bash scripts/build-iso.sh"
    exit 1
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "[-] Error: qemu-system-x86_64 is not installed."
    echo "    Install with: sudo apt-get install -y qemu-system-x86 qemu-utils ovmf"
    exit 1
fi

echo "================================================================================"
echo "          MONODESK OS — QEMU TEST HARNESS                                       "
echo "================================================================================"
echo "[*] Target ISO:   $ISO_PATH"
echo "[*] Allocated RAM: ${RAM_MB} MB"
echo "[*] Boot Mode:    ${BOOT_MODE}"

# Create disposable 25GB virtual disk for installer testing
if [[ ! -f "$DISPOSABLE_DISK" ]]; then
    echo "[+] Creating 25GB disposable test disk ($DISPOSABLE_DISK)..."
    qemu-img create -f qcow2 "$DISPOSABLE_DISK" 25G
fi

# Detect KVM hardware virtualization acceleration if available
KVM_ARG=""
if [[ -e /dev/kvm ]] && [[ -r /dev/kvm ]] && [[ -w /dev/kvm ]]; then
    KVM_ARG="-enable-kvm"
    echo "[+] KVM hardware acceleration enabled."
else
    echo "[!] Notice: KVM not accessible; running in standard QEMU TCG mode."
fi

# UEFI OVMF firmware configuration
BIOS_ARG=""
if [[ "$BOOT_MODE" == "uefi" ]]; then
    OVMF_CODE="/usr/share/OVMF/OVMF_CODE.fd"
    if [[ -f "$OVMF_CODE" ]]; then
        BIOS_ARG="-bios $OVMF_CODE"
        echo "[+] Using OVMF UEFI firmware: $OVMF_CODE"
    else
        echo "[!] Notice: OVMF firmware not found at $OVMF_CODE; falling back to default BIOS."
    fi
fi

echo "[*] Spawning QEMU virtual machine test instance..."
echo "[*] Safe isolated environment: Host disk drives are completely untouched."

qemu-system-x86_64 \
    $KVM_ARG \
    $BIOS_ARG \
    -m "${RAM_MB}" \
    -smp 4 \
    -cdrom "$ISO_PATH" \
    -drive file="$DISPOSABLE_DISK",format=qcow2,if=virtio \
    -boot d \
    -vga virtio \
    -device virtio-net-pci,netdev=net0 \
    -netdev user,id=net0 \
    -display gtk \
    -name "MONODESK OS 1.0 (QEMU Test Environment)"

echo "[✓] QEMU test session terminated."
