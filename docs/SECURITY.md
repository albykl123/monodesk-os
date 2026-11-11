# MONODESK OS 1.0 — Security Specification & Policy

---

### 1. Security Architecture Overview

MONODESK OS implements layered defense-in-depth across the operating system lifecycle:
- **Kernel & Microcode:** Linux 6.1 LTS kernel compiled with stack protector strong, strict memory layout randomization (KASLR), and runtime hardware errata mitigations via `intel-microcode` and `amd64-microcode`.
- **Least-Privilege Enforcement:** No graphical desktop applications or user shell processes execute with root permissions. Administrative tasks require explicit PolicyKit (`pkexec`) authorization.
- **Network Boundary Security:** The Uncomplicated Firewall (UFW) is active by default with an incoming `DROP` policy to reject unsolicited connection attempts from the local network or internet.
- **Cryptographic Package Verification:** All system packages and updates are downloaded from official Debian mirror infrastructures using GPG key signatures (`debian-archive-keyring`).
- **Filesystem & Swap Encryption:** The installer supports LUKS2 full-disk encryption, and memory swap is compressed in-RAM using zRAM (zstd) to prevent unencrypted paging to physical disk.

---

### 2. Vulnerability Reporting & Response

Security vulnerabilities should be reported directly via GitHub issues or security advisories. Upstream Debian security updates are automatically integrated through the `bookworm-security` repository.
