# M9 completion and next engineering decision

2026-10-14. No accepted alternate boot,
selected Sony image bundle, hardware compatibility or original-board restoration
was demonstrated. The long-term Android-free Rockbox objective is retained.

## What advanced

The [artifact inventory](m9-boot-artifact-inventory.md) records four newly
acquired official manifests, each byte-identical to M1, and a bounded search of
392 supplied local files plus selected S archive names. The only compiled DT
paths found in S are DTC fuzz corpus, not selected Sony trees. No new boot
binary, DT/AVB image or service set was obtained. M8's NWWM hypotheses and all
original firmware/source evidence remain unchanged; unsupported experiments
were not repeated.

The [userspace audit](m9-stock-kernel-userspace.md) resolves concrete source
questions: module autoload can be a successful no-op under published helper
settings; actual readiness must replace assumed modprobe success. Device-node
and deferred-probe handling are explicit dependencies. Userspace thermal options
and conditional watchdog interfaces mean kernel driver availability alone does
not establish protection ownership. FDT header/CRC validation is separate from
cryptographic acceptance. Actual selected modules, firmware and policy remain U.

A 13-role source-attributed dependency specification and host verifier now
reject missing prerequisites, cycles and safety/firmware-order bypass, propagate
failure and expose desired shutdown ordering without any device action. Its
synthetic readiness does not establish deployment readiness. The contract models
unselected dependencies; it supplies no Sony board configuration.

The [authentication model](m9-authentication-boundaries.md) adds pinned AOSP
structure references and separates boot/ramdisk/DT inputs, module signatures,
peripheral authentication and rollback policy. No actual Sony descriptor values
were parsed. The [recovery matrix](m9-recovery-readiness.md) ties candidate routes
to independently surviving restoration requirements; published US exchange
policy still establishes no original-board capability.

## Acquisition priority

The immediate priority is independent acquisition of authentic selected
artifacts: an applicable updater consumer, provenance-bound boot/DT/AVB bytes,
or running-board resource descriptions under a separately reviewed collection
plan. Manufacturer cooperation is optional.

M9 originally recommended a model/build-specific Sony service inquiry to
clarify independent-init selection and original-board recovery. The
[historical questions](m6-recovery-engineering.md#sony-inquiry-unsent) remain
useful evidence requirements; the inquiry was not sent.

## Proposed artifact audit

Obtain and statically audit one **provenance-bound selected boot/DT/AVB package
or an applicable supported-init/restoration capability statement**. Prefer an
already available permitted artifact or public release. If separate contact
authorization is granted, ask for exact artifact/tool IDs, model/region/build
binding, supported init/root selection and original-board failure coverage.
Do not ask for signing secrets or another unit's calibration/provisioning.

Success would establish actual kernel/ramdisk/DT placement and authenticated
ranges, or an applicable policy deciding whether stock-kernel independent init
can be accepted. Restoration remains a separate proof. If a statement rules
out owner-selected stock userspace, prioritize a supported engineering-image
route; absence of a public mechanism is not proof of impossibility.

Acquisition routes exhausted **within M9's finite scope**: supplied local image
suffix inventory; current Sony GPL filename inventory and 13 targeted source
members; source catalog/current release and regional update notices; all four
live manifests; focused public selected-image/DT searches. They supply no new
container hypothesis or complete image set. No global absence claim is made.

Further host work can independently audit authentic firmware/module/bootstrap
dependency metadata when supplied, or validate a newly identified structure.
It should answer a concrete missing edge rather than add generic simulators or
another all-unknown profile. Physical characterization requires its own bounded
operation plan and approval; custom execution also needs acceptance, compatibility
and restoration proof. A spare alone supplies none of those proofs.

## Validation and preservation

All 94 entries in M8's ignored work-product ledger, M8's
public-result hashes, 142 M7 private records and 2,060 reused integrity records
were verified. M0's 318 records, all 13 M1 artifacts and pinned original archives
also matched. All **56 public files** were copied and verified in ignored
`build/m9-baseline-20261014/`; manifest SHA-256:
`1fd3a418e0274877138b3a91462b1d1cb46b25f384e6270e243367c478c5fbcc`.
Large archives/snapshots were not duplicated or rebuilt.

Executed checks:

- Windows unittest discovery: **42 pass**: 9 M9 contract, 8 EXT_CSD, 8 inventory,
  10 UPG and 7 safety tests. All 9 new tests also pass under WSL Python.
- The current no-state contract intentionally reports every role blocked, exit 1;
  malformed input exits 2; a synthetic fully ready model exits 0 while retaining
  `deployment_authorized: false`. CLI exit cases are exercised in tests.
- All 42 preserved M6 build outputs, 15 locked toolchain packages and 20 locked
  Linux inputs match hashes. Preserved DRM/PCM/touch/error/shutdown results
  revalidate using existing checks into new ignored M9 records. No new VM boot,
  codec benchmark or ARM64 sanitizer pass is claimed.
- Earlier FCC classifications remain 43 PDFs/594 historically validated pages,
  31 catalog SHA matches (29 with the two-byte size-metadata conflict), 12 without
  catalog hashes. Preservation hashes pass; page traversal was not repeated.

Private acquisition, inspection and preservation records are inventoried in
`build/m9/work-products.json`.
