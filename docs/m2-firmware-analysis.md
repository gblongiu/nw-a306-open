# M2 firmware container analysis

Assessment: 2026-10-13. Static host investigation of the acquired Sony
container; no decryption or inner-image validation was achieved.

## Evidence preservation

All **13 original M1 artifacts** were present in the specified temporary
directory. They were copied, with their original filenames and bytes, into
`firmware-images/m1-20261013/`. This is a durable private directory under the
existing `firmware-images/` Git exclusion; the originals were retained.
Each source was hashed before copying; destination size/SHA-256 and a subsequent
source hash matched. No artifact was replaced or reconstructed.

| Preserved originals | Count | Bytes per file | Verification |
| --- | --- | --- | --- |
| `NW-A300Series_0000_info.xml` | 1 | 55,730 | Size and SHA-256 match |
| `NW-A300Series_0001_info.xml` | 1 | 4,991 | Size and SHA-256 match |
| `NW-A300Series_0002_info.xml` | 1 | 55,730 | Size and SHA-256 match |
| `NW-A300Series_0003_info.xml` | 1 | 55,729 | Size and SHA-256 match |
| `NW-A300Series_0000_V3_06_00_NW_WM_FW.UPG.header-4096` through the corresponding `0003` sample | 4 | 4,096 each | All four size/SHA-256 pairs match |
| `NW-A300Series_0002_V3_06_00_NW_WM_FW.UPG` | 1 | 1,589,253,264 | Size, SHA-256 and manifest MD5 match |
| `header-provenance.json` | 1 | 3,061 | Size and SHA-256 match |
| `manifest-provenance.json` | 1 | 8,953 | Size and SHA-256 match |
| `package-provenance.json` | 1 | 1,181 | Size and SHA-256 match |
| `static-inspection.json` | 1 | 600 | Size and SHA-256 match |

The additional private `preservation-manifest.json` records every original
filename, byte count, SHA-256, copy result and source-unchanged result, plus
private locations and verification time. Its SHA-256 is
`ca6842de8f7f3a2a438232cfad5570cbfce8a4ec5e37a8561d8c943d4fbea44d`.
It is a new custody record, not one of the 13 original artifacts.
Raw provenance and firmware remain private.

## Package size reconciliation

The **4,256-byte difference belongs to distinct Sony distribution variants**.
The preserved manifests supply different URLs, sizes and MD5 values for `0000`
and `0002`; the complete acquisition matches `0002` exactly. The Sony UK notice
also publishes the `0002` size. Sony Canada's notice recorded during M1 publishes
the `0000` size. Its M2 HTTP recheck returned 403; the preserved manifest evidence
and M1 notice finding remain independently identified. [F1, F2]

| Sony distribution | Manifest bytes | Manifest MD5 | Header decimal at 96-107 | Body minus decimal |
| --- | --- | --- | --- | --- |
| `0000` | 1,589,257,520 | `cf98cda7f2227a222fc23de27260e625` | 1,589,257,391 | 1 |
| `0001` | 1,595,425,312 | `4ab0b4dcdbcbe05a2b9ce532c4a4cab9` | 1,595,425,183 | 1 |
| `0002` | 1,589,253,264 | `a785c3d360bca2c0fd81f4182c9bec8b` | 1,589,253,124 | 12 |
| `0003` | 931,068,112 | `2172be1ded03f006cdbad31026846f62` | 931,067,971 | 13 |

Here “body” means the manifest file length minus the 128-byte prefix. Only
`0002` has a complete locally inspected body; other rows combine preserved
headers with the independently recorded range total/manifest size. For `0000`
and `0002`, URI paths identify their respective distribution names and
`contents/0012/`; `0003` uses `contents/0013/`. This establishes distribution
identity, not the internal reason their payload sizes differ. No wrapping or
padding correction was made. The package differences themselves have not been
decoded, and the correct distribution for the maintainer's unit remains unproven.
A product suffix is not sufficient evidence to select an update. [F1]

Complete candidate SHA-256:
`50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643`.
The copied package was independently streamed again by the M2 inspector and
matched its byte count, SHA-256 and manifest MD5. These checks establish
preservation and consistency with Sony's manifest, not signature verification.

## Observed container structure

Offsets below are zero-based, half-open ranges. All four preserved prefixes
share this profile; neither the profile name used by our tool nor the filename
constitutes a Sony format-version field. [F1, F3]

| Range | Observed contents | Interpretation limit |
| --- | --- | --- |
| `[0,4)` | ASCII `NWWM` | Container magic |
| `[4,60)` | 56 ASCII hexadecimal characters | Digest-shaped field; algorithm/covered data not verified for NW-A306 |
| `[60,96)` | 36 ASCII `0` characters | Meaning unknown; not binary zero padding |
| `[96,108)` | 12 ASCII decimal digits | Length-like field; values in the table above |
| `[108,128)` | 20 ASCII `f` characters | Meaning unknown |
| `[128,EOF)` | Opaque body; `0002` length 1,589,253,136, divisible by 16 | No decoded entry table or file inventory |

The `0002` hexadecimal field is
`3b45c459df5c9a1b36c9370931e87b16f7ccd95d20ad3945bd634dd7`.
Its declared decimal is 12 bytes shorter than the body. All four length
relationships fit 16-byte block padding of 1-16 bytes, consistent with a
plaintext-length field and PKCS padding. That is a hypothesis supported by the
historical lead below, not a decrypted or authenticated measurement. **Offset
140 is not an established payload boundary.** Subtracting 140 merely reproduces
this candidate's decimal; historical source instead starts at 128.

Fixed 64-KiB body samples at offsets 128, 140, 536870912 and 1589187728
had Shannon entropy approximately 7.997 bits/byte.
A streamed full-file signature search found no `ANDROID!`, `AVB0`, DTB magic or
ELF magic. It found one `CrAU` at 445,087,176 and one ZIP local-header marker at
409,025,425; neither establishes a container. The following `CrAU` big-endian
version is 11,936,541,499,511,433,538; its manifest length is
4,897,814,205,270,957,736 bytes, beyond the 1,144,166,088 bytes remaining in
the file. It cannot be a valid directly readable payload header at that offset.
The ZIP marker has implausible header fields and no end-of-central-directory
marker was found. Eighty-four three-byte gzip markers are also insufficient to
identify compressed members. High entropy and isolated short signatures cannot
distinguish encryption from compression or random-looking encapsulation. [F3, F6]

## Historical formats and decoding limits

Pinned Rockbox `upgtools` describes older V1/V2 formats starting with a binary
16-byte MD5, then an encrypted model/file-count header and file offset/size
entries. The present visible `NWWM`/ASCII prefix does not match that framing.
No parser assumptions, keys or entry layouts from those tools were reused, and
the tools were not executed. [F4]

An author-published 2019 Android Walkman project supplies a closer comparison.
At pinned revision `1b316da17a6f4c50511f46498de0a16dd53231d9`,
`UpdateDataDecipher.java` reads 128 bytes, recognizes `NWWM`, uses AES-CBC with
padding from offset 128, and checks SHA-224 over decrypted output. Its metadata
parser reads the 56-character field at offset 4. `UpdateProperties.java` splits
a caller-supplied ASCII string into a 32-byte key and 16-byte IV. The project's
README describes Android OTA ZIP contents for NW-A100/NW-ZX500. [F5]

This is a credible **format-family lead**, not an NW-A306 decoder. Prefix shape,
body alignment and length arithmetic agree; cipher, key/IV, digest semantics
and inner OTA compatibility have not been demonstrated on this package. No
key was acquired, no Java utility or extracted payload executed, and no
decryption attempted. We did not import this historical source, whose
redistribution provenance would need separate review before reuse.

| Requested image / metadata | M2 result |
| --- | --- |
| Boot, recovery | No verified image located in the opaque package; historical partition names in D1 are separate evidence |
| Vendor, system, super / dynamic partitions | No decoded image or filesystem; presence and full-versus-delta status unknown |
| DTB, DTBO | No verified tree or overlay recovered |
| vbmeta, vbmeta_system / AVB | No image, public key, descriptors or rollback index recovered |
| Firmware / calibration / early loaders | No verified member inventory; required binaries and target binding remain unknown |
| Internal model, region, version restrictions | No decoded restriction table; filename/manifest identify distribution and release externally |
| Compression, encryption, signatures | AES-CBC is a historical hypothesis; compression, signature layout and trust chain unverified |

The manifest's `Version=3.06`, filename `V3_06_00`, and eligibility rules
`>=1.00` and `<3.06` are external metadata, not boot-image or hardware acceptance
proof. The manifest's own envelope digest remains unexplained, as recorded in
M1. Without authoritative format documentation or lawfully supplied matching
key/material, the inner ZIP/payload, partition contents and cryptographic
authentication cannot be verified from current evidence. A decryption key,
if eventually available, would not grant signing or custom-boot authorization.

## Minimal read-only inspector

[`tools/inspect_upg.py`](../tools/inspect_upg.py) implements only the fixed
observed header profile. It checks magic, ASCII field syntax, observed reserved
bytes, nonzero/aligned body size and length consistency; an unfamiliar profile
fails closed. This deliberately rejects other possible Sony formats rather
than inventing support. Header samples alone are not complete packages and
fail the full-file length check.

It opens a regular file read-only, reads only 128 bytes by default and optionally
streams full-file hashes in at most 1-MiB chunks. Region reads reject negative,
oversized and out-of-file offsets/lengths before seeking. Hashing is bounded by
the initial file size and detects truncation, growth and size/mtime changes.
It has no extraction, decompression, key handling, payload execution or device
interface. JSON reports observations and explicitly unverified authentication;
unsupported/malformed input produces an error and exit status 2.

From the project root, using existing Python 3.12.10:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/inspect_upg.py firmware-images/m1-20261013/NW-A300Series_0002_V3_06_00_NW_WM_FW.UPG --hash
```

Result: **10 tests pass**. Synthetic fixtures cover every padding-sized length
difference, valid metadata/hashes and unchanged input, truncated headers,
unsupported magic/reserved fields, malformed hex/decimal, bad body lengths,
invalid offsets rejected before I/O, short reads, >4-GiB arithmetic without
allocation, bounded streamed hashing, and rejection of directories. The real
candidate yields the exact size/hashes above; no decoded image claim is made.

The suite also passed under WSL Python 3.12.3. A separate CLI check on a
four-byte synthetic `NWWM` file returned status 2 with a bounds error and left
its bytes unchanged.

## Integrity checks

All 13 original artifacts and copies matched the private size/hash ledger.
The three pinned source archives and 318 M0 evidence records also matched.
The M1 source register remained intact; the package-size interpretation above
resolves its distribution question without changing the acquired bytes.

## Next investigation

The update provides a verified transport/header profile and a specific older
Android-container lead; it has not yet supplied usable DT, firmware or boot
images. Seek authoritative NW-A300 container documentation or legitimately
available matching keys through existing public/source material or Sony service
cooperation. Validate decryption and
plaintext hash on a private copy before designing any inner-container reader.
Inspect OTA manifests/signatures and member bounds before selective image
analysis. Do not assume a full factory image or replace the original evidence.
The separate [architecture report](m2-host-architecture.md) describes progress
that remains possible without these inputs.

## Source locators

M0/M1 registers, archive hashes and research findings are preserved. These
locators extend them; public links contain no private artifacts.

| Ref | Exact evidence and scope |
| --- | --- |
| F1 | Preserved M1 H1-H3, [source register](recovery-provenance.md#source-register). Four `https://info.update.sony.net/PA001/NW-A300Series_000N/info/info.xml` endpoints (`N=0..3`); XML `Distributions/Distribution/@Size`, `@MAC`, `@URI`, `@Version` and eligibility rules after the 67-byte envelope. Four header samples and full `0002` acquisition. Direct private host evidence. |
| F2 | [Sony UK File Info](https://www.sony.co.uk/electronics/support/digital-music-players-nw-nwz-a-series/nw-a306/software/00292251), version/size/date, rechecked in M2; [Sony Canada notice](https://www.sony.ca/en/electronics/support/software/00292253), M1 P2, File Info. Canada HTTP 403 on M2 recheck; variant reconciliation also uses preserved manifests. |
| F3 | Direct bounded reads of preserved `0002`: header 0-127, 64-KiB entropy samples and streamed full-file signature/hash passes. Candidate-marker follow-up reads: 40 bytes at offsets 445087176 and 409025425. Reproducible header/hash result from the project inspector. |
| F4 | R revision `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09`, `utils/nwztools/upgtools/upg.h:26-79`, V1/V2 framing/structures; `upg.c:151-187`, MD5/header-decryption path. Source inspection only. |
| F5 | [Historical project's pinned source](https://github.com/97lily/2019_android_walkman/tree/1b316da17a6f4c50511f46498de0a16dd53231d9): `nwwmdecrypt/src/com/sony/walkman/systemupdater/util/UpdateDataDecipher.java:34-58,85-117,154-169`; SHA-256 `5f159dab828cf8f88339142020fa8b11e287f3165a02b26ca876dec517f28cbb`. `UpdateProperties.java:10-13`; SHA-256 `1ad08a9dc99158dc96bfbf4b638513d61baf0fc6b683c9372c5921d48e77b3d8`. `README.md:55-68`, author-reported older models. Source read, not execution or A306 verification. |
| F6 | AOSP [update payload definition](https://android.googlesource.com/platform/system/update_engine/+/refs/heads/main/update_metadata.proto), `DeltaArchiveManifest` and preceding payload-file-format comment; [payload metadata reader](https://android.googlesource.com/platform/system/update_engine/+/refs/heads/main/payload_consumer/payload_metadata.cc), `ParsePayloadHeader`, version/manifest offsets and big-endian conversion. Generic format discriminator only. |
