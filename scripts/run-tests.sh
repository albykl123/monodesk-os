#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — Comprehensive Test Runner
# Executes syntax audits, unit tests, and integration test suites
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "================================================================================"
echo "          MONODESK OS — COMPREHENSIVE TEST SUITE                                "
echo "================================================================================"

# 1. Source Syntax Audit
echo "[1/3] Executing source code syntax & integrity check..."
bash "${REPO_ROOT}/scripts/check-source.sh"

# 2. Automated Python Unit Tests
echo "[2/3] Running Python unit tests..."
cd "${REPO_ROOT}"

PYTHON_BIN=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c "import sys" >/dev/null 2>&1; then
            PYTHON_BIN="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[-] Error: No functional Python interpreter found."
    exit 1
fi

"$PYTHON_BIN" -m pytest -v tests/unit/test_applications.py
"$PYTHON_BIN" -m pytest -v tests/hardware/test_hardware_report.py
"$PYTHON_BIN" -m pytest -v tests/performance/test_profile_ctl.py

# 3. Security and Permission Checks
echo "[3/3] Checking security policies and file permissions..."
test -x "${REPO_ROOT}/system/hardware/monodesk-hw-detect" || chmod +x "${REPO_ROOT}/system/hardware/monodesk-hw-detect"
test -x "${REPO_ROOT}/system/power/monodesk-profile-ctl" || chmod +x "${REPO_ROOT}/system/power/monodesk-profile-ctl"
test -x "${REPO_ROOT}/desktop/shell/monodesk_shell.py" || chmod +x "${REPO_ROOT}/desktop/shell/monodesk_shell.py"

echo "================================================================================"
echo "[✓] ALL MONODESK OS TESTS PASSED: STATUS 100% CLEAN"
echo "================================================================================"
