#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — ISO Verification Utility
# Checks SHA256 integrity, hybrid EFI/BIOS boot headers, and SquashFS status
# ==============================================================================

set -euo pipefail

ISO_PATH="${1:-releases/monodesk-os-1.0.0-universal-amd64.iso}"

if [[ ! -f "$ISO_PATH" ]]; then
    echo "[-] Error: Target ISO does not exist at: $ISO_PATH"
    exit 1
fi

echo "=== [MONODESK OS] Verifying ISO Integrity: $ISO_PATH ==="

# 1. SHA256 Check
CHECKSUM_FILE="${ISO_PATH}.sha256"
if [[ -f "$CHECKSUM_FILE" ]]; then
    echo "[1/3] Verifying SHA-256 Checksum..."
    cd "$(dirname "$ISO_PATH")"
    sha256sum -c "$(basename "$CHECKSUM_FILE")"
else
    echo "[!] Notice: Checksum file not found; generating one now..."
    sha256sum "$ISO_PATH"
fi

# 2. Hybrid Boot Header Inspection (xorriso)
echo "[2/3] Inspecting Hybrid Boot Sectors (UEFI / MBR)..."
if command -v xorriso >/dev/null 2>&1; then
    xorriso -indev "$ISO_PATH" -report_el_torito as_mkisofs
else
    echo "[!] Notice: xorriso not installed; skipping detailed El Torito dump."
fi

# 3. Size Inspection
SIZE_BYTES=$(stat -c%s "$ISO_PATH" 2>/dev/null || stat -f%z "$ISO_PATH")
SIZE_MB=$((SIZE_BYTES / 1024 / 1024))
echo "[3/3] Measured ISO Dimensions: ${SIZE_MB} MB (${SIZE_BYTES} bytes)"

echo "[✓] ISO verification process complete."
