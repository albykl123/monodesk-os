#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — Official Checksum Generation Utility
# Calculates and verifies cryptographic hashes for release artifacts
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RELEASES_DIR="${REPO_ROOT}/releases"
ISO_NAME="monodesk-os-1.0.0-universal-amd64.iso"
TARGET_ISO="${RELEASES_DIR}/${ISO_NAME}"

if [[ ! -f "$TARGET_ISO" ]]; then
    echo "[-] Error: Release ISO not found at: ${TARGET_ISO}"
    exit 1
fi

echo "=== [MONODESK OS] Generating Release Checksums ==="
cd "${RELEASES_DIR}"

# Compute SHA-256
echo "[*] Computing SHA-256 for ${ISO_NAME}..."
sha256sum "${ISO_NAME}" > SHA256SUMS.txt
cp SHA256SUMS.txt "${ISO_NAME}.sha256"

# Verify generated checksum
echo "[*] Verifying checksum file..."
sha256sum -c SHA256SUMS.txt

echo "[✓] SHA256SUMS.txt generated and verified successfully:"
cat SHA256SUMS.txt
