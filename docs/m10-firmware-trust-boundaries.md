# M10 firmware acceptance and independent boot feasibility

2026-10-14, with acquisitions through 2026-10-15 UTC. Host-only investigation;
no device command, service invocation, update attempt or boot transition.
The acquired updater APK was reused, not reacquired or re-disassembled.

**Decision:** prioritize the actual bootloader acceptance policy and an
independently surviving restoration entry. Sony's updater remains an artifact
acquisition lead, but is not an established independent execution interface.
Repacking NWWM, using a client debug-file branch, or preserving the kernel while
changing its ramdisk does not establish acceptance. No available route is ready
for a physical independent-Linux boot experiment. This narrows the investigation;
it does not prove that an owner-controlled boot route is impossible.

## Question, acceptance criteria and evidence classes

Question: which authority would have to accept changed Linux boot inputs, and
does existing evidence identify a route that avoids that authority?
The bounded offline acceptance criteria were to locate the Android 14 verifier
and writer decisions; distinguish decoding, OTA and boot trust; establish what
authentic images can actually be obtained; and give each candidate a decisive
next input and recovery requirement. These criteria are satisfied below.
Sony-native enforcement and accepted custom execution remain unresolved; M10
and hardware deployment are not complete.

Classes used here:

- **Physical:** demonstrated on the owner's NW-A306 in preserved sessions.
- **Artifact:** verified from device-specific artifacts, including static code;
  not a demonstration that the code path ran.
- **Virtual:** verified only in the ARM64 prototype.
- **Platform:** established in public platform/shared source, not the Sony build.
- **Hypothesis:** plausible but unverified.
- **Unknown:** missing artifact, policy or observation.

Physical locked/green observations, Android 14 and the 4.19.157-perf+ kernel
remain as previously recorded. Virtual Rockbox playback supplies no boot-entry
or Sony board-driver evidence. Prior failed reads and H1 quarantine remain in
effect. See [physical evidence](m10-standing-readonly-results.md) and
[APK findings](m10-updater-analysis.md).

## Android 14 native trust trace

There is **no build-matched Sony native UpdateEngine binary/source in the
available evidence**. Android 14 and APK SDK 34 justify an Android 14 comparison,
not binary equivalence. The pinned `android-14.0.0_r1` UpdateEngine commit is
`aae85a0fada547ac7d48fd1065db143514a0d6c9`. The separately resolved public
`android-security-14.0.0_r24` through `_r30` tags select that same repository
commit. This is component revision identity, not a claim that Sony applied every
security patch or used this source. QPR tag `android-14.0.0_r75` selects
`2d86d26065ac5e3bf0a09ad6cc8ab1d37093a51b` and was compared separately.

All following native behavior is **Platform**. Private originals, full source
URLs, sizes, hashes, failed fetches and comparison diffs are under ignored
`build/m10/trust-boundaries-20261014-01/`. No upstream implementation was copied
into the public project. Line numbers below use the first pinned commit.

| Decision | Exact source / result |
| --- | --- |
| Request to install plan | [aosp/update_attempter_android.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/aosp/update_attempter_android.cc), `ApplyPayload`, lines 215–294: parses size/hash/metadata-size properties, explicitly clears `public_key_rsa`, selects mandatory checks with `IsOfficialBuild`, and selects source/other target slot. Supplying properties does not enroll an owner key. |
| Official/development distinction | [aosp/hardware_android.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/aosp/hardware_android.cc), lines 128–157: official is `ro.secure`, default true; developer features use `ro.debuggable`, default false. USB debugging authorization does not establish either value. |
| Trusted key selection | [delta_performer.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/delta_performer.cc), `GetPublicKey`/`CreatePayloadVerifier`, lines 962–1001: an existing certificate ZIP takes priority; parsing failure does not fall through. Only when absent is the PEM/response-key path considered. Response keys require a nonofficial build; Android's `ApplyPayload` nevertheless clears that field. |
| Android default trust files | [aosp/platform_constants_android.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/aosp/platform_constants_android.cc), lines 31–32: certificate store is `/system/etc/security/otacerts.zip`; default standalone PEM path is **empty**. Do not substitute a ChromeOS PEM path for this Android implementation. Actual Sony store/configuration is unknown. |
| Metadata authentication | `delta_performer.cc`, `ParsePayloadMetadata`, lines 289–388: bounds/expected metadata size, verifier creation, signature verification, then protobuf parsing. Official/mandatory metadata failures stop. [payload_metadata.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/payload_metadata.cc), lines 156–222: SHA-256 over header plus manifest, verified against supplied raw signature or embedded Signatures protobuf; missing signatures are an error. |
| Key and signature interpretation | [certificate_parser_android.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/certificate_parser_android.cc), lines 30–110: reads matching `x509.pem` entries, parses X.509 and extracts public keys. [payload_verifier.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/payload_verifier.cc), lines 99–207: tries signatures against installed keys, RSA SHA-256 PKCS#1 v1.5 or EC verification. This is local trust-store selection, not trust in an APK signer or a downloaded replacement certificate. |
| Final payload authentication | `delta_performer.cc`, `VerifyPayload`, lines 1239–1287: checks downloaded size/hash, then signed hash/signature. Two hash contexts and `DiscardBuffer`, lines 1290–1298, distinguish whole payload hash from the signature-covered header/manifest/data; metadata-signature and final-signature blobs are excluded from the signed hash. |
| Missing-key qualification | `CreatePayloadVerifier` can return no verifier with verification disabled when no key exists. `VerifyPayload` then skips the final signature. **On official builds, the earlier mandatory metadata error still prevents this from becoming an unsigned-install route.** Nonofficial missing-key behavior is not demonstrated on Sony and still supplies no bootloader acceptance. |

The QPR comparison found `PayloadMetadata` and `PayloadVerifier` files
byte-identical. Four reviewed function bodies are also identical:
`GetPublicKey`, `CreatePayloadVerifier`, `VerifyPayload`, `IsOfficialBuild`.
`ParsePayloadMetadata` differs only in one diagnostic expression's formatting.
Other code differs; whole UpdateEngine versions are not equivalent.

### Write authority, ordering and later verification

The native daemon is the writer, not the secure-storage client. AOSP
[update_engine.rc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/update_engine.rc)
starts it as root. Binder `applyPayload` delegates to `ApplyPayload`; the inspected
method contains no replacement-key enrollment. AOSP SELinux separately labels
the service, permits boot-control HAL use, and grants block-device access to
`update_engine_common`. The pinned sepolicy commit is
`7595d4f4c36d27150d247701f3f87fb512b68d18`; see
[public/update_engine_common.te](https://android.googlesource.com/platform/system/sepolicy/+/7595d4f4c36d27150d247701f3f87fb512b68d18/public/update_engine_common.te),
lines 5–9, 26 and 77–78. Sony's compiled policy and caller grants are unavailable.
APK privileged placement alone does not establish those grants.

Authenticated manifest partition names/sizes/operations are resolved through
the install plan and boot/dynamic-partition control. The actual manifest,
Sony resolver and layout are absent. No Sony partition allowlist can be derived
from these generic sources. `PartitionWriter::Init` opens the resolved target
with `O_RDWR`, lines 150–186 of
[partition_writer.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/partition_writer.cc).

**An update submission is not a read-only authentication experiment.**
[download_action.cc](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/download_action.cc),
lines 85–92, attempts to mark the target unbootable before download/metadata
validation. `ApplyPayload` can already alter preferences and update state.
Partition writes follow accepted metadata/operation checks, while final payload
signature verification is at download completion, line 250. A later rejection
does not imply zero persistent effects. No such submission was made.

[FilesystemVerifierAction](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/filesystem_verifier_action.cc),
lines 479–545, compares written partition hashes against manifest expectations;
it is not a new owner-key authority.
[PostinstallRunnerAction](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/postinstall_runner_action.cc),
lines 160–198, 390–450, mounts postinstall targets read-only, handles optional
failures, finishes the update and activates the target slot on success.
The vbmeta-digest helper logs failure and returns empty rather than itself
establishing boot acceptance (`hardware_android.cc`, lines 85–110, 300–303).
Partition hash verification, postinstall execution and loader AVB enforcement
must therefore remain separate claims.

Post-reboot AOSP
[update_verifier.cpp](https://android.googlesource.com/platform/bootable/recovery/+/2e6ff7bc40063d38fc5478389a47c0fafba20bfd/update_verifier/update_verifier.cpp),
lines 338–395, conditionally checks dm-verity/care-map blocks and marks boot
successful or defers it for checkpoints. Missing/disabled verity and missing
care-map branches exist. None demonstrates Sony's fallback or restoration.
Update timestamps/SPL checks also remain distinct from loader rollback indexes.

## Secure-storage dependency: decoding is not signing authority

**Artifact:** the preserved client trace already establishes
`UpdateProperties` → `ISstorage/default.getKey` → key/IV arrays → AES-CBC
NWWM decoder → SHA-224 comparison → ZIP → UpdateEngine. Exact DEX offsets and
locators remain in the [APK report](m10-updater-analysis.md), not duplicated here.
The available generated interface exposes `getKey` and HIDL plumbing; its proxy
is not the service implementation or a firmware-signing interface.

**Unknown:** actual service binary, VINTF declaration, init/service policy,
caller restrictions, provisioning and any internal authentication/state roles.
No device secret was requested. The previous selective 85,019-member GPL
filename inventory found no securestorage/sstorage/update_engine implementation;
it is reused rather than scanning the archive again. Targeted current inventory
also found no matching native binary, OTA trust store or AVB image in the 14
files under `firmware-images`; `proprietary` and `device-dumps` do not exist.
Cached platform references are not Sony native artifacts.

Even successful decoding would expose payload bytes, not confer OTA signing or
boot-signing authority. No evidence links the decoding arrays to private OTA or
boot signing keys. Investigating service provisioning or collecting secrets is
not the next engineering task. A lawfully available service binary/manifest could
be analyzed statically without calling it, but would rank below boot-entry and
accepted-image evidence unless it exposes a distinct authorization boundary.

## Authentic OTA and selected-image availability

**Artifact:** the complete preserved 0002 3.06 package is 1,589,253,264 bytes,
SHA-256 `50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643`.
Its provenance and all 13 original M1 artifacts were revalidated unchanged.
There is no decoded ZIP or usable boot/DT/AVB set. Four preserved official
manifests each name one UPG; private header captures identify NWWM, not a public
plaintext OTA archive. Their exact URIs were reused with HTTPS for **HEAD only**:

| Distribution | Advertised bytes | Current HTTPS result |
| --- | ---: | --- |
| 0000 | 1,589,257,520 | 200; Content-Length agrees |
| 0001 | 1,595,425,312 | 200; Content-Length agrees |
| 0002 | 1,589,253,264 | 200; Content-Length agrees; complete local original |
| 0003 | 931,068,112 | 200; Content-Length agrees |

HEAD establishes current availability, not payload signature validity. No
duplicate multi-gigabyte download was justified. Original bytes and earlier
manifest provenance remain untouched. The
[US release page](https://www.sony.com/electronics/support/software/00292253)
lists Android 14 history, May 2026 security level and 3.06.00; the
[UK release page](https://www.sony.co.uk/electronics/support/software/00292251)
matches the preserved 0002 size. Both describe Wi-Fi/Music Center update paths
and say earlier-version rollback is unsupported. These pages were readable
through the web tool; direct host downloads returned 403, recorded privately.
Regional size agreement does not prove this owner's distribution selection.
No plaintext OTA, target-files archive or same-board factory restore set was
identified in these official resources or the bounded local inventory.

Selected images remain **Unknown**: historical evidence names `boot_a/b`,
`recovery_a/b`, `dtbo_a/b`, `vbmeta_a/b`, `vbmeta_system_a/b`, but supplies no bytes.
`vendor_boot` and `init_boot` are not established. A decoded payload manifest
would identify full/delta/partial status, partition names and original-image
dependencies; image reconstruction must follow its actual operations.
An OTA need not include every early loader, GPT, hardware boot region or unique
state. Its presence is not completeness for recovery.

## Candidate execution paths and next discriminating evidence

Order is research priority, not a ranking of demonstrated availability. No
candidate has demonstrated independent Linux execution on this Sony.

| Candidate / established evidence | Unknown; decisive feasibility or rejection evidence | Persistence and required recovery | Next specific action |
| --- | --- | --- | --- |
| **1. Loader-supported RAM boot / owner-controlled boot policy.** Physical locked/green state; Platform concept only. | Actual loader entry, implemented commands, accepted signatures/owner-key policy and DT handoff. Reject unsigned RAM boot if the applicable locked loader requires a trusted signer with no owner enrollment; reject an unlock proposal if model policy disallows it. Empty `ro.oem_unlock_supported` is not a demonstrated denial. | RAM delivery could avoid installation, but image behavior can write or mismanage power. Unlock/key enrollment is persistent and may erase state. Need a known return to stock and a surviving repair entry covering intended failure classes before either experiment. | Obtain authentic loader/boot-policy artifacts or applicable primary documentation, then statically identify download/boot and unlock handlers. No boot-mode transition yet. |
| **2. Accepted stock kernel with independent init/root.** Platform source supports Linux init; Virtual prototype supplies userspace. | Selected boot/DT/AVB coverage and an actually permitted alternate-root/init input. Reject unchanged-signature ramdisk editing if actual descriptors bind the changed bytes and no supported selection route exists. | Volatile only if an accepted volatile input is proved; installed ramdisk/DT/root edits are persistent. Need stock boot/DT/AVB bytes and recovery independent of altered inputs. | Obtain authentic selected boot, DTBO and vbmeta graph; trace command-line/ramdisk authentication before building a Sony image. |
| **3. Sony updater delivering custom Linux.** Artifact client decodes and delegates; Platform native signatures traced above. | Sony verifier, public trust-store selection and loader image acceptance. A production trusted-key policy without owner enrollment rejects repacking as an ordinary supported custom-delivery route. Missing native artifacts prevent declaring actual Sony rejection. | Persistent slot/partition/update-state changes even if final verification fails. Need applicable full reconstruction set, same-version/rollback rules and surviving restoration outside damaged Android/slots. | Analyze installed native verifier and public OTA certificates if separately acquired, or an authentic decoded OTA supplied without secrets. Do not submit a test payload. |
| **4. Recovery sideload/custom recovery.** Historical partition names only; Platform AOSP recovery verifies the outer ZIP and delegates A/B payload installation. | Sony recovery implementation, entry independent of failed Android, accepted formats/keys and actual independence from damaged boot/AVB. Reject generic recovery as an assumed NWWM decoder or unsigned loader. | Updates/custom recovery are persistent; entering recovery also needs separate approval. Need accepted stock recovery/image set and lower surviving entry if it is damaged. | Inspect authentic recovery ramdisk/native verifier when available, not key combinations or an updater trial. |
| **5. Privileged stock-kernel handoff/kexec.** Platform ARM64 precedent; final Sony config/privilege unavailable. | Accepted privileged execution and enabled handoff, plus automatic power-on route. Without these, not executable; Android-assisted handoff alone fails the end objective. | Handoff may be volatile, but gaining privilege/installing startup hooks can be persistent. Need safe quiescence and stock restoration independent of the handoff. | Inspect final kernel config only when authentic bytes exist. No rooting/exploit work justified by current evidence. |
| **6. Qualcomm ROM/service execution or direct storage.** Platform precedent only. | Actual Sony accepted programmer, OEM/security/board match, permissions and complete restoration coverage. EDL visibility alone cannot establish arbitrary code execution; a vendor programmer may authorize only stock writes. | Mode entry can affect availability; service writes/direct storage are persistent. Need board-bound accepted original loaders/layout/provisioning treatment and demonstrated same-board restore. | Analyze an already lawful, model-specific service artifact if supplied. No generic programmer or EDL attempt. |

Sony's current [unlock documentation](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader)
is expressly for Xperia. The preserved
[Sony Open Devices supported list](https://github.com/sonyxperiadev/bug_tracker/blob/master/README.md)
contains no A306/icx1301. This is absence from inspected support material, not
proof that no Walkman engineering facility exists. Generic Xperia instructions
and informal recovery/fastboot anecdotes do not supply an A306 procedure.
Userspace fastbootd, DSU/another Android image, an app launcher and auxiliary
processor firmware are not established independent power-on paths for this goal.

AOSP recovery source at commit `2e6ff7bc40063d38fc5478389a47c0fafba20bfd`,
[install/install.cpp](https://android.googlesource.com/platform/bootable/recovery/+/2e6ff7bc40063d38fc5478389a47c0fafba20bfd/install/install.cpp),
lines 286–311 and 595–610, 713–733, verifies the package against installed
certificates and invokes `update_engine_sideload` for A/B. Sony recovery's use
of this code is unknown. This additional generic signature boundary does not
offer an unsigned route.

## Recovery requirement and next engineering input

No demonstrated restoration mechanism was added. The
[same-board recovery assessment](m9-recovery-readiness.md) still applies.
An official transport package, inactive slot and product-exchange service
statement do not restore damaged loaders, partition metadata or protected state.
The next boot experiment needs: an accepted entry and image format; selected
boot/DT/AVB and safety resources; a surviving entry outside the intended failure
scope; accepted complete restoration bytes/tools; rollback-compatible versions;
and preservation or lawful regeneration of board-specific state. None may be
substituted with another unit's provisioning.

**Next high-value input:** an authentic decoded boot/DT/AVB/loader set, or
model-specific loader-policy evidence. The installed native UpdateEngine and
public OTA certificate store are a narrower secondary acquisition that can
resolve the actual Sony OTA branch; they are not keys granting boot authority.
The standard AOSP file locations above are candidates, not confirmed Sony paths.
New device metadata/acquisition needs a separately approved bounded plan with
existing identity/transport/integrity guards; no extra command is authorized by
this report. It must not invoke UpdateEngine or secure-storage, collect secrets,
read raw partitions, retry denied paths, or transition boot modes. No additional
generic transport development is needed. Further static research can resume
immediately when one of these actual missing artifacts is available.

## Actual validation and changed work products

- 36 acquired platform source files rehashed successfully against provenance.
- 13 preserved M1 firmware artifacts rehashed unchanged, including complete UPG.
- 1,293 prior private evidence/provenance files checked against the preceding
  ledgers: zero mismatches. Stage A/B/B2/U1/H1/APK evidence and failures preserved.
- 63 host source-locator/preservation checks passed, zero failed. Four reviewed
  verifier/policy function bodies match across r1/r75. These are source checks,
  **not** compiled AOSP tests or physical verification.
- Four official firmware HEAD requests succeeded with matching sizes. No OTA
  body, APK, secret or additional device file was acquired in this increment.
- No production code changed; no synthetic parser, simulator or transport tests
  were added. Actual selected payload/images are absent, so another synthetic
  image parser would not resolve the blocked acceptance question.

Public changes in this increment: this report and a cross-reference appended
to `m10-physical-boot-investigation.md`. Private additions are confined to
`build/m10/trust-boundaries-20261014-01/`: pinned sources/provenance, QPR diffs,
OTA availability/local inventories, preservation results, reproducible
`check_evidence.py`, checks and a work-product ledger. Previous private artifacts
and source references were not modified. No Git history or presentation changes.
