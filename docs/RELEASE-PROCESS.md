# MONODESK OS — Public Release & Maintenance Process

---

### 1. Release Classification Lifecycle

To maintain absolute transparency and prevent marketing inflation, all MONODESK OS builds adhere to strict semantic release gates:

```
[Development Build] ──► [Alpha] ──► [Beta] ──► [Release Candidate] ──► [Stable 1.0.0]
```

1. **Development:** Actively changing source tree. Nightly builds may be unstable.
2. **Alpha:** Core platform operational; certain subsystems incomplete or unverified.
3. **Beta:** Feature-complete codebase; all 12 major subsystems implemented; undergoing VM and multi-hardware QA.
4. **Release Candidate (RC):** All unit and integration tests passing; ISO generation verified; installer and QEMU boot passing.
5. **Stable (1.0.0):** Every mandatory release gate passed, verified on physical hardware targets (Lenovo IdeaPad Slim 5 and Lenovo B590), and signed with official GPG keys.

---

### 2. Mandatory Release Gates

1. **Source Gate:** All Python scripts compile cleanly (`py_compile`); all shell scripts pass `bash -n`; all desktop entries pass `desktop-file-validate`.
2. **Build Gate:** Live-build produces hybrid ISO without errors; actual file size is measured; `SHA256SUMS` generated.
3. **Boot Gate:** ISO boots in QEMU in both UEFI (`OVMF`) and Legacy BIOS (`i386-pc`) modes.
4. **Installer Gate:** Calamares installs successfully into a 25GB disposable QEMU virtual disk; post-install system reboots into desktop cleanly.
5. **Security Gate:** Zero telemetry verified; UFW active by default; least privilege enforced.
6. **Hardware Gate:** Documented compatibility matrix with zero fabricated claims.

---

### 3. Public GitHub Release Structure

Every release tag (e.g. `v1.0.0`) must publish the following verifiable artifacts:
- `monodesk-os-1.0.0-universal-amd64.iso`
- `monodesk-os-1.0.0-universal-amd64.iso.sha256`
- `BUILD-MANIFEST.txt`
- `PACKAGE-MANIFEST.txt`
- Complete source code archive (`.tar.gz`)
