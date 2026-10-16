# M10 Sony ABL acquisition: tested decoding dependency and readback gate

2026-10-15. **No NW-A306 ABL acquired. No device or ADB-server request made.**
P1, N1/N2 and their original captures, approvals and failure records are
preserved. This increment tests a specific previously untested artifact lead;
it does not reopen reference-loader analysis or claim M10 completion.

## Official firmware: a finite extraction experiment

Engineering question: can the test material embedded in the acquired updater
decode the preserved official 3.06 package sufficiently to expose its OTA
partition manifest and original ABL? Acceptance requires a valid decrypted ZIP,
the decoder's full SHA-224 match, then validated payload metadata and image
reconstruction. Padding or a signature-like byte sequence alone is insufficient.

Inputs, all preserved:

| Official distribution | Advertised UPG bytes | Available before this increment | New bounded evidence / exact-pair result |
| --- | ---: | --- | --- |
| 0000 | 1,589,257,520 | Manifest and 4,096-byte prefix | Final 32 ciphertext bytes; invalid padding |
| 0001 | 1,595,425,312 | Manifest and 4,096-byte prefix | Final 32 ciphertext bytes; invalid padding |
| 0002 | 1,589,253,264 | Complete original UPG, manifest and prefix | Local final block; invalid padding |
| 0003 | 931,068,112 | Manifest and 4,096-byte prefix | Final 32 bytes give one-byte padding; final 65,600 bytes contain no ZIP end record |

The complete 0002 package SHA-256 is
`50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643`.
Its preserved provenance identifies Sony's HTTPS distribution URL, exact
length and published MD5 match. MD5/provenance is not boot authorization.
The [official 3.06 release](https://www.sony.com/electronics/support/software/00292253)
documents a normal update, prohibits downgrade and does not provide a demonstrated
same-board repair procedure. Distribution selection for the owner remains
unverified; a shared version number does not settle applicability.

**Verified from device-specific APK evidence:** `classes.dex`, SHA-256
`155e04c332c4399c09473c6b4f92aba7a4d0ab5fe2982aee985f3ae76e9d2e17`,
`UpdateDataDecipher$UpdateMetaStore.<init>`, code item `0x69604`, contains
const-string instructions at `0x6961e` / `0x6962e` (indices `0x1b9b` /
`0x1b9c`). The following `String.getBytes` operations populate test fields.
The active assignments instead obtain `mKey` / `mIv` through
`UpdateProperties` at `0x69690`-`0x696a4`. Getters used by the active decoder
do not select the test fields. See [acquired updater analysis](m10-updater-analysis.md)
for the independent HAL, AES-CBC, SHA-224 and ZIP-consumer locators.

**New host-verified negative result:** tested exactly that one embedded
32-byte/16-byte pair, with no material values in public output. Decrypting
512 bytes at offset 128 in each preserved prefix yielded no ZIP local header.
The complete package's invalid PKCS padding is stronger than that prefix test.
Three one-shot HTTPS Range requests acquired the other distributions' final
32 bytes; each returned exact HTTP 206 extents and lengths. For 0003, valid-looking
padding prompted one distinct, bounded final-region acquisition, not a retry.
Its ETag and overlapping final bytes matched the first range.

0003's decrypted, unpadded tail is 65,583 bytes, covering the ZIP end-of-central-
directory record plus the maximum 65,535-byte ZIP comment. It contains no
`PK\x05\x06` at all. Thus the padding-positive result is not a usable decoded
ZIP. The pair fails the actual decoder/ZIP-consumer requirements across these
four artifacts. These CBC tail tests use the preceding ciphertext block as IV;
changing the initial IV would not repair their tail results. No other candidate,
key search, service invocation, full-body decryption or decoded-output promotion
was performed. The active HAL material and other extraction methods remain
unknown. This dated experiment supersedes only the older statement that the
embedded test pair had not been tried; historical reports remain unchanged.

**Not established:** whether any of these OTAs contains ABL, which ABL version,
full versus delta operations, or boot/recovery/DTBO/vbmeta coverage. No decoded
partition manifest is available. Do not claim ABL is absent from ciphertext.

If a legitimately obtained plaintext OTA becomes available, inspect its ZIP
and signed `payload.bin` manifest offline first. Look for actual partition
records, not assumed filenames. A logical `abl` update need not contain separate
`abl_a` and `abl_b` members: preserved AOSP source at commit
`aae85a0fada547ac7d48fd1065db143514a0d6c9`,
[`InstallPlan::LoadPartitionsFromSlots`, lines 151-175](https://android.googlesource.com/platform/system/update_engine/+/aae85a0fada547ac7d48fd1065db143514a0d6c9/payload_consumer/install_plan.cc#151),
resolves partition name and source/target slots separately. This is AOSP
behavior, not an observed Sony manifest. Delta reconstruction additionally
needs the exact old source bytes/hashes; a full-image record may not. Validate
operation extents, output size/hash and authentication separately. OTA target
image length is not automatically the physical partition capacity or its padding.

## Software readback: new Sony-specific lead, no accepted reader

A first-person [A306 report, June 28, 2024, post 4237](https://www.head-fi.org/threads/new-sony-walkman-nw-a300-series-android-12.966467/page-283)
describes EDL entry using a cable and a subsequent signed-loader obstacle.
The preceding post links the public QCM2290 loader catalog. **External
user-reported observation, plausible but unverified for our board/build.**
Search-index text exposed the post; direct retrieval returned a bot challenge
and the two diagnostic images could not be validated. The exact rejection,
ROM identity, trust hash, entry/return procedure and programmer tried are
therefore unavailable. This strengthens an investigation lead, not a repair
claim or permission to upload anything.

The linked catalog was inventoried through public HTTP metadata, without Git
synchronization: immutable tree `6c416255056a178f54ccd7ee9b67d04a5bdfa8e6`,
1,015 entries, nontruncated. It contains one QCM2290-labelled generic image and
one Sony-labelled file. No filename in this bounded catalog identified A306
or `icx1301`. Filename absence is not proof that compatible programmers cannot
exist elsewhere.

The sole Sony-labelled [catalog blob](https://api.github.com/repos/bkerler/Loaders/git/blobs/46e1ef8bd1de6660c2c524c122d1bd6ceb57c695)
was acquired privately, bounded at 128 KiB, checked against its Git blob ID,
and statically inspected: **60,140 bytes**, SHA-256
`a02b7c02834e66fa0010236e8de9d0f3e9230b482f21b0569885fcbeb64aa9b1`.
The existing ELF inspector correctly rejects its non-ELF format. No address
mapping, executable architecture or command policy was invented for it.
Bounded DER inspection found certificates at file offsets `53996`, `55171`
and `56174` (lengths `1175`, `1003`, `951`). Their subjects explicitly claim
Sony Mobile Communications / MSM8X30 and leaf HW_ID `007530E100010001`.
All three embedded-chain certificate signatures verify, including the root's
self-signature. This does not verify the executable signature, manufacturer
provenance, current certificate validity or a trusted root on the Walkman.
Its old-platform claims and absent board/trust match eliminate this file as a
justified NW-A306 upload candidate. No generic programmer was downloaded anew.

| Acquisition path | Established / decisive missing capability | Decision |
| --- | --- | --- |
| Offline official OTA reconstruction | Authentic encrypted UPG; exact embedded test pair rejected. Need legitimately available plaintext OTA or another demonstrated offline decoding dependency. | Best artifact route; presently blocked before its partition manifest. No secure-storage invocation or secret retrieval proposed. |
| Ordinary Android partition read | P1: root-owned 0600 loader nodes, shell uid 2000, enforcing state. | Do not repeat a raw read or bypass permissions. Need an independently evidenced authorized export mechanism. |
| Bootloader readback/export | N2 proves bootloader fastboot. No Sony read handler acquired or observed. | No accepted reader established. Standard host command availability cannot supply that evidence. |
| Userspace fastboot fetch | Previously inspected AOSP implementation requires debuggable/unlocked and allows vendor_boot; Sony is locked/user, endpoint is not fastbootd. | No justified ABL read route. Do not reopen this through a mode transition or a generic fetch probe. Sony extensions remain unknown. |
| Sony PC/MTP update services | Prior signed-host analysis establishes transfer and update-start behavior, not a partition export. | No readback established; do not invoke opcode `0x9402` or invent a read opcode. |
| ROM/download programmer | New external A306 entry report; available Sony catalog file is an unrelated-platform candidate. | Need board-applicable, accepted, read-capable programmer and bounded entry/return evidence. EDL visibility or signature presence alone grants no storage access. |
| Build-specific software access | No applicable authorized read/export implementation or demonstrated weakness found in available materials. | Unexplored possibilities remain; no privilege escalation or speculative invocation. |

## Exact acquisition specification, pending a demonstrated mechanism

**This is not an executable authorization or an instruction to read a block node.**

- Primary artifact: full original contents of P1 name `/dev/block/by-name/abl_b`,
  resolved block identity **179:29**, mode **0600**, owner/group **root:root**,
  context `u:object_r:vendor_custom_ab_block_device:s0`. Comparison `abl_a`,
  **179:28**, is a distinct capture requiring separate scope. Neither means
  disk offset, inode number or length. Android's observed `_b` makes this the
  first candidate; early-loader slot selection is unverified.
- Match the original physical profile, board/product and installed build
  3.06.00/build 27; confirm current slot and immutable identity independently
  in the approved reader's session. Do not rewrite the historical profile or
  substitute another board's firmware. OTA distribution/build compatibility
  requires separate evidence, not merely matching the filename's version.
- Obtain capacity independently through a reviewed read-capable interface's
  trusted block-size response (for example a proven read-only size ioctl),
  corroborated with actual GPT entry/sector bounds if available. No normal-shell
  ioctl, sysfs substitution or GPT read is authorized here. If two independent
  sources are unavailable, record that limitation and do not present size as verified.
- Provisional **32 MiB capture ceiling**, chosen to bound host inspection,
  **not** measured Sony partition capacity. Require known positive exact
  length within the ceiling before content access. Stop rather than truncate
  if larger, unknown or inconsistent. Read exactly that extent in binary,
  preserving partition padding as well as the executable; no text/PTTY conversion.
- Require bounded per-frame/chunk and total byte counts, EOF/completion status,
  source identity and size before/after, transport continuity, deadline and
  failure capture. Reject short, extra, reordered or interrupted output;
  preserve partial bytes as failed evidence, never as a completed ABL.
- Hash original raw frames, reconstructed bytes and stored artifact with
  SHA-256; preserve tool, profile, plan, build, slot and acquisition provenance.
  Transport hashes cannot prove a malicious or mistaken reader returned the
  right partition. Independently consistent source hash or a separately
  authorized second capture is needed to strengthen that claim; no automatic retry.
- Keep captures and identifiers ignored/private. Parse bounded structure,
  executable mappings, hash segments and certificate claims with the existing
  inspectors; unsupported format stops interpretation, not evidence retention.
  Distinguish Sony bytes by bound-device provenance or authenticated applicable
  OTA provenance, not by ELF format, certificate name or a Qualcomm-like string.
- A proven block read has no intended write. Reader upload/execution, download
  mode, privileged service calls and boot transitions have independent risks.
  No write-capable configuration, storage initialization, set-active, rollback
  operation or permission change is implied by this specification.

Once acquired, first trace the actual Sony dispatcher and locked `boot` path,
including all reachable GPT/slot/rollback writes before rejection. Then trace
image coverage, delegated verification and kernel handoff. Neither Qualcomm
reference implementation is a substitute for those bytes or equivalent evidence.

## Engineering decision and recovery gate

**Sony temporary-boot registration, locked-state rejection and authentication
ordering remain unknown.** This increment eliminates a concrete extraction
shortcut and an unsuitable catalogued programmer; it establishes no new
independent-execution capability. N1/N2/P1 remain successful physical results.

The next specific acquisition action is to obtain the original public A306 EDL
diagnostic images/transcript and identify any legitimately available Sony/QCS2290
programmer or plaintext applicable OTA they lead to. Inspect authentic bytes
before considering execution. The missing capability is a decoded OTA or a
demonstrated, board-applicable storage reader; knowing the node name does not
remove either barrier. No currently evidenced software readback path can be
called viable. Acquiring native UpdateEngine or additional public certificates
would not itself unlock ABL access, so that collection is not the next priority.

**No new physical operation is recommended for approval at this checkpoint.**
A metadata-only max-fetch query would not establish permission to read ABL;
entering EDL without an accepted reader and credible return would incur
availability risk without acquiring bytes. A future download-interface
characterization must first define exact entry/exit, independently bound USB
identity, allowed bounded Sahara requests, zero image upload/storage commands,
timeout/disconnect stops and supervised return. The external report is not
sufficient to supply a tested procedure. Do not improvise one on the sole player.

Original-board restoration still needs actual GPT/boot regions and boundaries;
applicable `abl_*`, `xbl_*`, `xbl_config_*`, `boot_*`, `recovery_*`, `dtbo_*`,
`vbmeta_*` / `vbmeta_system_*` and relevant firmware-volume images; verified
rollback/AVB compatibility; preservation treatment for provisioning/calibration
and unique state (including P1's `nvp`, `persist` and other actual candidates);
RPMB/SoC-bound state accounting; and a surviving accepted same-board repair
interface with demonstrated rights. ABL alone preserves none of that complete
restoration relationship. Normal fastboot Power return is not failed-image recovery.

## Reproducibility and checkpoint

Private work is under `build/m10/sony-abl-acquisition-20261015-01/`: finite-candidate
script/results, range bytes/provenance, ZIP-tail discriminator, loader catalog
and selected blob/certificate analysis, seven control tests, regression logs,
prior-file preservation and the final work-product ledger. No embedded material
values, proprietary bytes, private identifiers or raw captures are published.

Validation: **seven offline controls passed**, including the NIST SP800-38A
AES-256-CBC vector, whole-stream/tail agreement, maximum ZIP comment, misleading
padding/end signatures and exact downloaded ranges/hashes. Existing full suite:
**236 run, 235 passed, one Windows symlink-permission skip**, no failures/errors.
Three embedded certificate signatures passed; original complete UPG, GPL archive
and DEX hashes matched. `git diff --check` passed. Final preservation and text
checks are recorded with the [exact checkpoint inventory](m10-source-control-checkpoint.md).

Public changes in this increment: this new report and the refreshed checkpoint
inventory. No production transport, N1/N2/P1 implementation or tests were edited;
all new scripts, controls and acquired binary fragments remain private. The
roadmap's pre-existing modification is preserved. Nothing staged, committed,
pushed, synchronized or changed in Git history or the Pages presentation.
