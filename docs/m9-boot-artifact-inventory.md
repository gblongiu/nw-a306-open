# M9 boot-artifact and selected-board inventory

2026-10-14. Host-only investigation. No selected Sony boot,
DT or AVB image was obtained. M9 acquired fresh official update metadata and
examined shared-source initialization/authentication code. The
inventory remains partial: known partition names, an authentic opaque update,
published source and external distribution metadata, not a factory image set.

Evidence classes: **S** applicable Sony document or historical observation;
**H** FCC certification sample; **P** shared-source/component/platform evidence;
**I** engineering requirement/inference; **U** unresolved. Authentic Sony GPL
publication is P for runtime selection: it does not establish the owner's build.

## Acquisition and applicability matrix

New acquisitions are private under ignored `build/m9/public-acquisitions/` and
`build/m9/primary/`, acquired 2026-10-14. Original bytes and provenance JSON are
preserved. Public Sony metadata carries no assumed redistribution license;
only findings/hashes are published. No firmware binary was newly downloaded.

| Artifact / exact origin | Bytes / SHA-256 | Verified information / completeness |
| --- | --- | --- |
| [0000 manifest](https://info.update.sony.net/PA001/NW-A300Series_0000/info/info.xml) | 55,730; `78512827cbc169547091baa271d6019ec0701c7ab906d2c9e14c6be64e7b153b` | S distribution 0000, version 3.06, size 1,589,257,520; byte-identical to M1, no inner members |
| [0001 manifest](https://info.update.sony.net/PA001/NW-A300Series_0001/info/info.xml) | 4,991; `df720c1e603a30c03dbc795b9ff4405de154cd4c026329979526951646fdd39f` | S distribution 0001, version 3.06, size 1,595,425,312; byte-identical to M1 |
| [0002 manifest](https://info.update.sony.net/PA001/NW-A300Series_0002/info/info.xml) | 55,730; `94ed7dc95dfc1d60d46fc34e5ea1716afe3a558a68ed697c0ac10e92e91cfb77` | S distribution 0002, version 3.06, size 1,589,253,264; byte-identical to M1 and matches preserved complete package's external metadata |
| [0003 manifest](https://info.update.sony.net/PA001/NW-A300Series_0003/info/info.xml) | 55,729; `fe0504ae7f7e9cad40500da24602f4d95f2f0cb139a9fa216806e6112120ee34` | S distribution 0003, version 3.06, size 931,068,112; byte-identical to M1 |
| Preserved M1 complete `NW-A300Series_0002_V3_06_00_NW_WM_FW.UPG` | 1,589,253,264; `50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643` | S authentic transport candidate; NWWM outer profile only, inner image/partition inventory U. Original unchanged |
| D1 historical preflight, `.local-references/vcapblock/diagnostics/vCapBlock-root-preflight.txt` | 1,558; `af61015a3302e62b6ceaa7e6660ae8d8dbf356ce462263b97d4037909bca8496` | S UTF-16LE text, model `icx1301`, Android 14/3.06.00/build 27, QCS2290, locked/green, flavor `icx1301_002`, slot `_b` then; no current device query or image bytes |
| Sony GPL S, [20260716 shared publication](https://oss.sony.net/Products/Linux/Audio/NW-A300-NW-ZX700_%2820260716%29.html) | SHA-256 `5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477` | P shared NW-A300/NW-ZX700 source, component licenses apply; 13 additional members inspected, no duplicate archive acquisition or selected board set |

The manifest XML begins after the established 67-byte envelope. Bounded reads
were capped at 128 KiB. Parsed `Distribution` attributes and `Rules/Rule` show
version eligibility `>=1.00`, `<3.06`; these are update selection rules, not AVB
rollback indexes. The 0002 root `InformationFile` has `LastUpdate`
`2026-06-17T04:23:58Z`. Nothing in the inspected attributes provides a selected
DT, signature graph or authoritative `icx1301_002` to 0002 mapping. The latter
remains an unresolved M1 question, not a new matching claim. No same-version
reinstall or cross-region applicability is established.

## Actual selected-image inventory

| Item | Obtained, identified or unavailable | Precise verification limit |
| --- | --- | --- |
| `boot_a/b`, `recovery_a/b` | Names identified in historical D1; images unavailable | Header version, kernel/ramdisk sizes, build IDs and independent recovery placement U |
| DTB | Selected bytes/location unavailable | No root compatible, memory/reserved-memory, `/chosen` or board binding verified |
| `dtbo_a/b` | Historical names identified; bytes unavailable | Overlay IDs, revision selection, order, applicability and signature coverage U |
| `vbmeta_a/b`, `vbmeta_system_a/b` | Historical names identified; bytes unavailable | Algorithms, keys, hash/hashtree/chain descriptors, authenticated ranges and rollback locations U |
| `vendor_boot`, `init_boot`, bootconfig | Use not established for this model/build | No such image acquired; Android 14 alone cannot select packaging or imply these partition types |
| Kernel configuration / modules | Shared published defconfig/source obtained | Final `.config`, exact image provenance, modules list, symbols, ABI and accepted keys U |
| Command line / rootfs / fstab / init | Kernel implementation obtained; selected input files unavailable | Historical Android properties are not bootargs, ramdisk or a mount/service manifest |
| A/B and super metadata | Historical A/B/dynamic properties and names | No GPT sectors, slot control record, super extent map, fallback policy or restoration layout |
| Peripheral firmware / calibration | Shared consumer code obtained | Selected firmware files, accepted versions, tables, permissions and provisioning interfaces U |
| Early loaders / service set | No applicable image/programmer/tool acquired | Stage identities, signatures, ROM entry and same-board repair coverage U |

No row establishes a complete set. The [M8 hardware distinctions](m8-boot-storage-architecture.md)
remain: eMMC boot regions, Android slots, GPT, super and RPMB are separate.
SODAGREEN 1.03/PM4125/KLMBG2JETD belong to H, not necessarily the owner's board.

## Bounded acquisition routes and eliminated false leads

| Question / examined sources and method | Result / applicability / decisive input |
| --- | --- |
| Does supplied private evidence already contain selected images? Enumerated 392 files across `firmware-images`, `.local-references/vcapblock` and `.local-references/sony-nw-a306`; matched `.img/.dtb/.dtbo/.mbn/.elf` suffixes | No matches. Exact scope only; opaque UPG and other unrelated archives are not decoded by a suffix search. Need provenance-bound selected members, not another name listing |
| Does current S contain a selected bundle or Android first-stage source? Streamed archive filename inventory for image suffixes, `icx1301`, `sodagreen`, `BoardConfig`, `system/core/init`, `system/core/fs_mgr`, `external/avb` | Two `.dtb` members are **DTC fuzz corpus** (`quirks.dtb`, `meson-g12a-sei510-android.dtb`); `scripts/Makefile.dtbo` is a build recipe. None is selected Sony DT evidence. No matching selected image/first-stage path; no exhaustive content absence claim |
| Does Sony's public distribution add board/image metadata? [Audio source catalog](https://oss.sony.net/Products/Linux/Audio/category01.html), current release page, [US notice](https://www.sony.com/electronics/support/software/00292253), [UK notice](https://www.sony.co.uk/electronics/support/digital-music-players-nw-nwz-a-series/nw-a306/software/00292251), four freshly acquired manifests | Source/update publications and unchanged external metadata; no selected bundle surfaced. Do not combine shared releases or regional payloads to manufacture one |
| Do focused public searches surface an applicable dump or DTS? Queries `Sony NW-A306 boot image firmware extraction kernel`, `Sony NW-A306 Linux device tree source stock boot`, `NW-A306 init_boot`, `NW-A306 vbmeta`, and Sony Xperia DTS repository + `icx1301` | No provenance-bound Sony bundle in reviewed results. Generic extraction, older A100, Xperia and other DAP results are excluded; matching an owner's gear-list text does not establish applicability. No third party contacted or unverified dump downloaded |
| Is new NWWM analysis justified? Compare fresh manifest bytes and M8 preserved observations | No new container evidence. M8's three rejected stored-byte SHA-224 hypotheses preserved, **not rerun**. Need an applicable format specification or legitimately supplied decoded member/manifest with provenance. Signing secrets are neither needed nor sought |

Public searches are bounded negative results, not proof that artifacts do not
exist. M7 regulatory photographs/document classifications and M6 source-release
comparison were reused; no repeat traversal of 594 PDF pages or source-archive
bulk extraction. The detailed [userspace audit](m9-stock-kernel-userspace.md)
and [authentication model](m9-authentication-boundaries.md) identify productive
contracts despite the acquisition limit.
