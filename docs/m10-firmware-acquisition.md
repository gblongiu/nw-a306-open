# M10 acquisition candidate: standalone Sony OTA-material access

2026-10-15. **No new physical access capability, plaintext Sony OTA or boot-critical
image has been demonstrated. We still cannot extract `abl_a`/`abl_b` through a
demonstrated reader.** This increment tests one concrete alternative: a standalone
client for the actual Sony decryption-material API, independent of the updater
and its installation workflow. No device operation, HAL call, upload, privilege
change, Sony contact or additional-hardware requirement is involved in the work
reported here.

## The acquisition hypothesis

The acquired updater obtains decryption material from
`vendor.sony.securestorage@1.0::ISstorage/default`. The hypothesis is that its
business method may also admit the existing owner-authorized Android shell
identity. If it does, a standalone request could obtain the material for
**host-only decoding of the preserved official UPG**, without starting an update.
This is a specific information-access hypothesis, not a demonstrated flaw.

It ranks above another fastboot/EDL probe for the current device because we have
authentic Sony client bytes defining the request and its intended decoder consumer.
Fastboot has no acquired Sony read handler; EDL has no accepted, compatible reader
or demonstrated return. Neither was reprobed. Native service implementation and
compiled caller policy are still missing; their absence does not establish that
access is permitted or impossible. No Sony-approved export feature is assumed.

## New protocol result from authentic Sony bytes

Input: APK1's unchanged `automagic.apk`, 1,337,774 bytes, SHA-256
`1d23a544bfa3f4cdbf9d8ef0514dbaaad985c6fa7ef70fdb52f786b4f2485b68`;
`classes.dex`, 741,404 bytes, SHA-256
`155e04c332c4399c09473c6b4f92aba7a4d0ab5fe2982aee985f3ae76e9d2e17`.
Original device acquisition/provenance remains in the
[APK1 report](m10-updater-analysis.md). Offsets below address this DEX, not RAM.

| Exact implementation locator | Verified result |
| --- | --- |
| `ISstorage$Proxy.getKey`, code item `0x06a758`; token write `0x06a776` | The request parcel writes only the public interface descriptor. It contains no package-name argument, updater object, installation request or separate app-signature credential. |
| `0x06a78a`, `0x06a78c`, `0x06a78e` | Transaction code **1**, synchronous flags **0**, with the request/reply parcels. All request-method instructions were checked, not just a matching string. |
| `0x06a794`, `0x06a7a0`, `0x06a7a8`, `0x06a7b0`, `0x06a7b8` | Verifies transport success, reads an application `int32` status and two byte vectors, then passes all three to the callback. Vector lengths and the application's status-code semantics are not specified by this proxy. |
| `ISstorage.getService()`, `0x06a864`; `getService(String)`, `0x06a884` | Selects instance `default`, calls framework `HwBinder.getService(descriptor, instance)` and then `asInterface`. The independent client omits the generated Java convenience wrapper, but AOSP Android 14 native lookup itself validates the interface using `interfaceChain`; see the proposal's pinned framework locators. |
| `UpdateProperties.<init>`, `0x069e94`; `0x069ed6–0x069f00` | The updater consumes the returned vectors as its key/IV. These bytes cross into client-process memory rather than remaining solely an opaque hardware key handle. Active provisioning and server-side storage are unknown. |

**Authorization is not encoded solely in the parcel.** Binder carries caller
identity separately; SELinux service discovery/call rules and the server's own
UID/domain checks can still deny the independent client. Reusing the descriptor
does not bypass them. No server-side authentication weakness has been proved.

The original-DEX ABI oracle resolves the method through class-data/method tables,
walks its bounded instruction body and verifies the exact transaction and reply
operations. Six altered-request/response controls are rejected. Its initial
missing `invoke-direct` decoder case was corrected; that was a host-oracle limit,
not malformed Sony code. No APK code or service is executed by this check.

## Concrete independent client and what its tests establish

Created private original-source `SonyOtaKeyProbe.java`, using framework HIDL APIs
through reflection. Its default invocation is inert. Its explicit candidate run:

- Requires UID **2000** and SELinux context **`u:r:shell:s0`** before lookup.
- Performs one lookup for the fixed descriptor/default instance and at most one
  business transaction, code 1/flags 0. No updater class, `UpdateProperties`,
  UpdateEngine or alternate service is used. The framework lookup can generate
  discovery and `interfaceChain` traffic; one explicit business call is not a
  claim of one total IPC transaction.
- Requires transport success, conservatively accepts application status zero,
  and requires 32/16-byte vectors with a nonzero key. Zero's Sony semantics and
  actual provisioned lengths remain to be validated; unexpected values stop.
- Emits exactly one 64-byte binary record only after those checks. Errors report
  a fixed stage and any nonzero application status, never vector contents or
  exception messages. All material would remain in ignored private evidence.

Eighteen host-stub cases pass: inert default, invalid arguments, wrong UID/domain,
missing service, valid synthetic reply, transaction denial, nonzero status,
wrong vector lengths, zero key, transport status, null elements/vectors, parcel
construction/token failures and temporary-storage/parcel-release failures.
Cleanup attempts continue after a release failure, and material is withheld until
cleanup succeeds. Tests verify explicit client call counts and binary output;
the stub does not model native framework lookup traffic.
This is **not an Android-runtime, SELinux or real-HAL access test**. Java reflection,
runtime availability and the actual server's behavior remain unverified.

JDK 17 compiled the helper and the existing Android SDK D8 built a standalone
API-34 DEX: **4,904 bytes**, SHA-256
`2c65d860fc848640e8f46015b4600fa0adeffd3e4df7619575c2c75874af7c5b`.
This supersedes the preserved earlier 4,648-byte candidate. Current Java source
SHA-256 is `28919bf026aebe6189e140cb88e5eda40466de75cb4e6397b057f28d90f2c86d`.
Synthetic Android classes are excluded from it. The DEX was not uploaded or run
on the player. Code, test fixtures/results, tool hashes, exact build arguments
and earlier host build outputs remain private under
`build/m10/firmware-acquisition-20261015-01/` and
`build/m10/sk1-preparation-20261015-01/`. The current frozen DEX is
`key-probe-frozen/key-probe-dex/classes.dex` beneath the latter directory.
Fresh rebuild receipts and regression logs are preserved in
`build/m10/sk1-reconciliation-20261015-01/`.

## The specific experiment that could establish access

**SK1: one independently captured standalone getKey request under the existing
shell identity**, followed entirely offline by validating the result against the
preserved official ciphertext. The [separate proposal](m10-sony-ota-key-proposal.md)
specifies helper delivery, exact commands, guards, evidence, risks and stops.
The canonical host admission wrapper is `tools/run_sony_ota_material_once.py`,
with `tools/acquire_sony_ota_material.py` and its 20-test synthetic suite.
The unapproved review package now binds its inputs, identity profile and exact
scope. The private duplicate runner is retired, with its original bytes retained.
New explicit owner authorization and fresh readiness are still absent.
No physical request is made here.

The decisive missing prerequisite is actual server admission of this UID/domain,
plus usable provisioned material. Server implementation/policy review would reduce
the sole-device risk and is desirable before approval. The scope must account
for possible lazy service activation, unknown getter side effects, unbounded
native reply allocation and a blocking transaction. The method name alone does
not prove a read-only implementation. No safe-return/recovery promise is inferred.

A valid-looking reply is not acquisition success. Require bounded host-only
AES-CBC/PKCS padding decoding, the consumer's full SHA-224 match, valid complete
ZIP structure, and then authentic payload/manifest signature and extent checks.
Do not run the decoder on Android, invoke UpdateEngine or try the old embedded
test material. A denial/unknown status/malformed reply ends this candidate test;
it does not authorize retries, another UID or bypass experiments.

Successful decoding could yield distribution ABL/boot/DT/AVB images **if actually
present**. Delta operations may require exact base bytes. Distribution provenance
does not prove equality with installed slots, expose unchanged components or
preserve unique device state. Complete raw storage acquisition still needs a
reader with trustworthy extents and rights. Firmware extraction would not itself
permit unsigned execution or establish an accepted restoration writer.

## Recorded updater limit and preservation

The prior work in this increment established that the selected normal decoded
success paths continue into `UpdateEngine.applyPayload`, without another owner
pause. Exact new callback locators are `0x064af0 → 0x062224 → 0x062ba4 → 0x063238`;
the final framework call is `0x063e78`. That finding is recorded and closed here.
The original-DEX oracle checked eight definitions, 17 calls and three success
blocks; six groups passed with 16 rejected mutation/bounds cases. It is not a
reason to stimulate an update or continue mapping refusal paths.

Both acquisition targets remain: a source/slot/length-bound boot-critical set
with raw completeness/hash/format checks, and broader consistent user/boot/GP-area
preservation with actual GPT/super metadata and unique-state accounting. Existing
[P1](m10-p1-execution.md) and [storage requirements](m10-storage-acquisition.md)
remain applicable. No capacity is inferred from major/minor numbers. RPMB,
SoC-bound secrets/fuses, rollback state and encryption-key continuity are not
supplied by ordinary imaging; a backup still is not demonstrated restoration.

The original acquisition checkpoint's 59-file comparison and 8,389-file baseline
remain historical evidence. Before this reconciliation, all 61 candidates in
that checkpoint still matched their ledger; the three SK1 source/test additions
bring the current inventory to 64. This reconciliation preserves 8,898 baseline
files, excluding caches, and changes only the proposal, this report, roadmap,
checkpoint and the retired private runner. Original bytes are retained privately.
Fresh test results, disclosure checks and the exact final inventory are in the
[checkpoint](m10-source-control-checkpoint.md); full private hashes and evidence
are in `build/m10/sk1-reconciliation-20261015-01/`. No source capability was added,
no consent was generated, and no staging/history/remote or device operation
occurred. Offline preparation stops for separate human safety and authorization
review; Sony admission, extraction, execution and restoration remain unverified.
