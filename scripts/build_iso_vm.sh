#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS 2.0 — Live-Build ISO Generation Script
# ==============================================================================
set -euo pipefail

REPO_DIR="/root/monodesk-os"
BUILD_DIR="${REPO_DIR}/build/live-build"
RELEASES_DIR="${REPO_DIR}/releases"
OUTPUT_ISO="${RELEASES_DIR}/monodesk-os-2.0.0-universal-amd64.iso"
LOG_FILE="${REPO_DIR}/build.log"

echo "[MONODESK Build] Starting live-build pipeline for MONODESK OS 2.0.0 Universal PC Edition..."
mkdir -p "${RELEASES_DIR}"

cd "${BUILD_DIR}"

# Ensure permissions and Unix line endings
chmod +x auto/* config/hooks/live/* 2>/dev/null || true

echo "[MONODESK Build] Configuring live-build tree..."
lb clean
lb config

# Seed package cache if available
mkdir -p "${BUILD_DIR}/cache/packages.chroot" "${BUILD_DIR}/cache/packages.bootstrap"
cp -n /var/cache/apt/archives/*.deb "${BUILD_DIR}/cache/packages.chroot/" 2>/dev/null || true
cp -n /var/cache/apt/archives/*.deb "${BUILD_DIR}/cache/packages.bootstrap/" 2>/dev/null || true
echo "[MONODESK Build] Pre-seeded $(ls "${BUILD_DIR}/cache/packages.chroot" | wc -l) packages into build cache."

echo "[MONODESK Build] Executing lb build (bootstrap, chroot, binary)..."
lb build 2>&1 | tee "${LOG_FILE}"

echo "[MONODESK Build] Checking for generated ISO image..."
GENERATED_ISO=$(ls -1 live-image-amd64*.iso 2>/dev/null | head -n 1 || true)

if [ -z "${GENERATED_ISO}" ] || [ ! -f "${GENERATED_ISO}" ]; then
    echo "[MONODESK Build] ERROR: No ISO file produced by live-build!" >&2
    exit 1
fi

echo "[MONODESK Build] Found generated ISO: ${GENERATED_ISO} ($(stat -c %s "${GENERATED_ISO}") bytes)"
cp "${GENERATED_ISO}" "${OUTPUT_ISO}"
echo "[MONODESK Build] Released ISO to: ${OUTPUT_ISO}"

echo "[MONODESK Build] Computing SHA-256 checksum..."
sha256sum "${OUTPUT_ISO}" | tee "${OUTPUT_ISO}.sha256"

echo "[MONODESK Build] Inspecting El Torito boot records..."
xorriso -indev "${OUTPUT_ISO}" -report_el_torito as_mkisofs 2>&1 | tee "${OUTPUT_ISO}.boot_report.txt"

echo "[MONODESK Build] Build pipeline completed successfully!"
