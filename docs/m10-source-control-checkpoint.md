# M10 source-control checkpoint inventory

2026-10-15. **SK1 offline reconciliation complete; nothing staged or committed.**
All 61 candidates in the previous public ledger matched before this work. Three
existing SK1 additions bring the exact review boundary to 64 candidates. Earlier
ledgers, test runs, captures and original document/runner bytes are preserved.

## Exact public boundary

There are **64 candidates: one tracked roadmap modification and 63 untracked
UTF-8 files** (29 Markdown documents, 18 Python tools and 17 Python tests).
This reconciliation changes only `docs/roadmap.md`,
`docs/m10-firmware-acquisition.md`, `docs/m10-sony-ota-key-proposal.md` and this
inventory in the public boundary. The three SK1 additions are
`tools/acquire_sony_ota_material.py`, `tools/run_sony_ota_material_once.py` and
`tests/test_acquire_sony_ota_material.py`; their implementation bytes are unchanged.
No prior grant or physical report is regenerated or altered.

The sole entry is `tools/run_sony_ota_material_once.py`; its canonical bundle
integrity check is retained. The private duplicate now refuses execution; its
former byte-exact implementation is retained as evidence, not an alternate entry.
The original Java source, frozen DEX, synthetic fixtures, expected identity,
approval proposal, host evidence and compiled outputs remain private and ignored.

No tracked or candidate path is under `build/`, `.local-references/`,
`firmware-images/`, `device-dumps/` or `proprietary/`. `AGENTS.md` and
`docs/m10-execution-plan.md` remain ignored. No proprietary code, private capture,
identifier, cryptographic material, executable or temporary build product is in
this inventory. Do not force-add private roots or stage a directory wholesale.

Private full hashes and byte counts, including this inventory, are in
`build/m10/sk1-reconciliation-20261015-01/source-control-checkpoint.json`.
`work-products.json` records every new private artifact and intentional edit.
The unapproved `SK1-offline-review-20261015-01` package is in
`build/m10/sk1-preparation-20261015-01/`: `execution-bundle.json`,
`reviewed-plan.json` and `approval-proposal.json`. The bundle binds the exact
scope, canonical code, transitive project dependencies, tests, expected profile,
build/runtime evidence and private boundaries. No actual approval, readiness or
live-attempt record is created. Freeze is identification, not consent or proof
of physical safety. Prior known-identifier/material scans are repeated over HEAD
files and all candidates; this is targeted checking, not universal secret detection.

## Exact candidate inventory

` M` is the tracked roadmap modification; `??` means untracked. The private ledger
contains full hashes. This inventory's own hash is stored only in that ledger.

### docs

| Path | Status | SHA-256 prefix |
| --- | --- | --- |
| `docs/roadmap.md` | ` M` | `78c524db9a81` |
| `docs/m10-advanced-acquisition.md` | `??` | `1cdac848b628` |
| `docs/m10-boot-execution-analysis.md` | `??` | `f3a5b7bfa0a9` |
| `docs/m10-boot-feasibility.md` | `??` | `d12992403817` |
| `docs/m10-c1-results.md` | `??` | `d79252a3e2b0` |
| `docs/m10-characterization-authorization.md` | `??` | `01e8800e28cf` |
| `docs/m10-execution-pivot.md` | `??` | `41c1851e6a64` |
| `docs/m10-fastboot-reconciliation.md` | `??` | `5fe79291fc35` |
| `docs/m10-firmware-acquisition.md` | `??` | `eada8b5ef64f` |
| `docs/m10-firmware-trust-boundaries.md` | `??` | `04e47cd97d32` |
| `docs/m10-kc1-results.md` | `??` | `c123d26d755d` |
| `docs/m10-kernel-config-authorization.md` | `??` | `9bddb00b184f` |
| `docs/m10-n1-results.md` | `??` | `975892bf786b` |
| `docs/m10-n2-authorization.md` | `??` | `9538e8b47cdf` |
| `docs/m10-n2-results.md` | `??` | `59f10a5869cb` |
| `docs/m10-p1-execution.md` | `??` | `f9f1ce8ed4a1` |
| `docs/m10-p1-results.md` | `??` | `c0a52cfb36e4` |
| `docs/m10-physical-boot-investigation.md` | `??` | `985c615629fb` |
| `docs/m10-readonly-standing-authorization.md` | `??` | `4ebcc03041fc` |
| `docs/m10-single-device-investigation.md` | `??` | `619fce2c15da` |
| `docs/m10-sony-abl-acquisition.md` | `??` | `4d12da5b5fe8` |
| `docs/m10-sony-host-evidence.md` | `??` | `93f25d7c1613` |
| `docs/m10-sony-ota-key-proposal.md` | `??` | `2038a87a6c39` |
| `docs/m10-source-control-checkpoint.md` | `??` | `private final ledger` |
| `docs/m10-stage-b2-authorization.md` | `??` | `a7a808c8fcdb` |
| `docs/m10-standing-readonly-results.md` | `??` | `bc7ca0537159` |
| `docs/m10-storage-acquisition.md` | `??` | `6b2a0439cca5` |
| `docs/m10-transport-validation.md` | `??` | `cbdebba78754` |
| `docs/m10-updater-analysis.md` | `??` | `9d50fe762fdf` |

### tools

| Path | Status | SHA-256 prefix |
| --- | --- | --- |
| `tools/acquire_kernel_config.py` | `??` | `883c6e5c12ff` |
| `tools/acquire_sony_ota_material.py` | `??` | `0e8e05167c97` |
| `tools/acquire_updater.py` | `??` | `aea6b994a0de` |
| `tools/adb_readonly.py` | `??` | `69b6fc373267` |
| `tools/characterization_b2.py` | `??` | `8e6f4c70664f` |
| `tools/characterization_c1.py` | `??` | `9e446bf36d54` |
| `tools/characterization_p1.py` | `??` | `775d64b5febe` |
| `tools/characterization_plan.py` | `??` | `70e7e89989d1` |
| `tools/characterization_transport.py` | `??` | `a0e4279ab279` |
| `tools/fastboot_n1.py` | `??` | `63a03325342f` |
| `tools/fastboot_n2.py` | `??` | `3123a8b24376` |
| `tools/fastboot_n2_plan.py` | `??` | `6561757d8fc3` |
| `tools/inspect_arm64_pe.py` | `??` | `7ffbaff4e44f` |
| `tools/inspect_gpt_capture.py` | `??` | `48748ef55aa4` |
| `tools/inspect_qcom_elf.py` | `??` | `6b90d4ac2a06` |
| `tools/inspect_sony_pc_updater.py` | `??` | `e043c415ddc1` |
| `tools/run_sony_ota_material_once.py` | `??` | `a36d23bda5d5` |
| `tools/standing_readonly.py` | `??` | `6d70dbe50e4b` |

### tests

| Path | Status | SHA-256 prefix |
| --- | --- | --- |
| `tests/test_acquire_kernel_config.py` | `??` | `5b83ca5bcefc` |
| `tests/test_acquire_sony_ota_material.py` | `??` | `ea06aa4bc969` |
| `tests/test_acquire_updater.py` | `??` | `64c87d78be4c` |
| `tests/test_adb_readonly.py` | `??` | `44c980d8685b` |
| `tests/test_characterization_b2.py` | `??` | `1b0f95b81139` |
| `tests/test_characterization_c1.py` | `??` | `e2e1a6228c80` |
| `tests/test_characterization_p1.py` | `??` | `3600d4c119c7` |
| `tests/test_characterization_plan.py` | `??` | `ec89628b3b22` |
| `tests/test_characterization_transport.py` | `??` | `8de04c8d785e` |
| `tests/test_fastboot_n1.py` | `??` | `8cb618073180` |
| `tests/test_fastboot_n2.py` | `??` | `832efa05c838` |
| `tests/test_fastboot_n2_plan.py` | `??` | `39c3f11c39b8` |
| `tests/test_inspect_arm64_pe.py` | `??` | `1186291a3752` |
| `tests/test_inspect_gpt_capture.py` | `??` | `d337fe5de5df` |
| `tests/test_inspect_qcom_elf.py` | `??` | `ed4d7a78b124` |
| `tests/test_inspect_sony_pc_updater.py` | `??` | `402060e8949b` |
| `tests/test_standing_readonly.py` | `??` | `e8026eb3b3da` |

## Fresh offline validation and evidence limits

- Current SK1 suite: **20 passed, zero failures/errors/skips**.
- Full repository suite: **273 run, 269 passed, zero failures/errors, four skips**.
  One skip is Windows symlink creation; three require optional Capstone 5.
- Current Java source: **18 synthetic host-stub cases passed**. A fresh JDK/D8
  rebuild reproduced the frozen standalone DEX byte for byte: **4,904 bytes**,
  SHA-256 `2c65d860fc848640e8f46015b4600fa0adeffd3e4df7619575c2c75874af7c5b`.
  The older 4,648-byte `bce8b6db00cf...` candidate is superseded and preserved.
- The first full-run validation harness had repository import-path and Windows
  subprocess-audit handling errors: 241 tests were reported with 15 errors and
  four skips. Those logs and initial harness bytes are preserved. After correcting
  only the private harness, the complete 273-test run passed as reported above.
  No real network or prohibited process attempt was recorded by the guard.
- The historical 271-test log (267 passes, four skips) predates two current SK1
  tests. It remains historical evidence; it is not substituted for the fresh run.
- The proposal includes framework discovery, native `interfaceChain` validation
  and possible lazy activation, with pinned AOSP Android 14 source locators.
  That comparator does not establish actual Sony runtime behavior. Host stubs
  do not model native lookup; entry tests mock Windows host guards.
- `git diff --check`, candidate UTF-8/header/SPDX/whitespace checks, exact private
  root exclusions and targeted disclosure scans pass. Source/artifact, review
  bundle and profile hashes agree in the final private validation record.
- Of **8,898 baseline files**, **8,893 remain byte-identical**. Only the four
  public documents above and the retired private runner change. Their original
  bytes are preserved. All prior grants, captures, Java/DEX artifacts and source
  evidence remain unchanged; caches are excluded from preservation accounting.

Final read-only Git status: **one tracked modification, 63 untracked files,
zero staged files**. No Git history/remote operation, physical communication,
helper deployment, HAL request, firmware decoding or Sony contact occurred.
Offline preparation is ready for separate human safety and authorization review.
Sony admission, getter effects, native reply allocation, runtime compatibility,
independent execution and damaged-state restoration remain unverified. No
approval or additional milestone/device operation is implied. Work stops here.
