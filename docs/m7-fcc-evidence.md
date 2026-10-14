# M7 FCC evidence review

2026-10-14. The maintainer supplied 42 FCC exhibits plus the separate Sony US
service document after M6. M7 independently inspected their local bytes and
all ten internal-photo exhibits. M6's HTTP failures remain historical results;
the photographs were not available to that investigation. No original or
acquisition record in `.local-references/` was modified.

## Independent verification and a material log conflict

All **43 PDFs / 594 pages** parse with pypdf 6.10.0 in strict mode and independently
traverse with PDFium 156.0.8076.0 / pypdfium2 5.14.0, using the already installed
bundled runtime. Every actual size and SHA-256 matches the acquisition record.
The service PDF emits whitespace-in-object-header diagnostics but parses in
strict mode and renders; these diagnostics were not treated as fatal failures.
Logged page counts match when present; the two exact-metadata entries had null
page counts, which M7 independently resolves as one page each.

The supplied report's 14 ordinary successes and 29 “hash mismatch” entries
are **not** an accurate description of independent digest comparisons:

| M7 tier | Count | Verified result |
| --- | --- | --- |
| A | 2 | Actual SHA-256 and size both match catalog metadata |
| B | 29 | Actual SHA-256 **matches** the catalog digest; actual size is two bytes shorter than catalog size |
| C | 12 | No published digest/size supplied; local hash and PDF structure verified only |

There are **zero actual digest mismatches among the 31 catalogued digests**.
The read-only installer source at `install_nwa306_fcc_references.py:264-275,
308-315` requires both exact hash and exact size for its highest tier, then
unconditionally labels any remaining hashed entry a hash mismatch. This
explains the contradictory classification and `published_sha256_match: false`
flag; it does not explain the mirror's size metadata. The original log is
preserved, not silently corrected. No trailing bytes were added or removed.

Current mirror metadata for [Part 8, 6141947](https://fccid.io/AK8YY1301B1/Internal-Photos/YY1301-Int-Photo-Part8-6141947)
and [Part 10, 6141960](https://fccid.io/AK8YY1301B1/Internal-Photos/YY1301-Int-Photo-Part10-6141960)
independently reproduces both the digest agreement and two-byte size conflict.
These are mirror-published checksums, not FCC signatures or independently
authenticated government originals. Tier B is exact digest agreement with an
unresolved size field, not merely parser acceptance and not full metadata agreement.

Part 8: 5,420,988 local bytes, three pages, SHA-256
`5d5265a246670b030b1d832167db99f2dee12cbac9497d26db63550931c7d16c`.
Part 10: 2,411,657 local bytes, two pages, SHA-256
`28c16fae83e2b7eb24dfc09b87c29f7529efa74645575f8d6c42690a0e64ce21`.
Private `build/m7/fcc-inventory.json` records all full hashes, sizes, source URLs,
page counts and separate comparison results; SHA-256
`4d199d2208817fb5e56fc12a6b2bfc87f7e1399b0e3d7ad6cca8950bda0a665f`.
The complete inventory follows; hash prefixes are abbreviated here only.

| Local filename | PDF pages | Actual bytes | SHA-256 prefix | Tier |
| --- | --- | --- | --- | --- |
| `01_Photos_Part01.pdf` | 2 | 5,007,711 | `56b4fea3677e` | B |
| `01_Photos_Part02.pdf` | 2 | 3,478,542 | `6d64ebabed8a` | B |
| `01_Photos_Part03.pdf` | 2 | 4,829,652 | `7560e69811fa` | B |
| `01_Photos_Part04.pdf` | 2 | 4,172,266 | `6bb73cf983e1` | B |
| `01_Photos_Part05.pdf` | 2 | 4,879,417 | `f438c4e444f4` | B |
| `01_Photos_Part06.pdf` | 2 | 5,385,609 | `8ebdf1cc31d7` | B |
| `01_Photos_Part07.pdf` | 2 | 4,507,397 | `740b8501f46a` | B |
| `01_Photos_Part08.pdf` | 3 | 5,420,988 | `5d5265a24667` | B |
| `01_Photos_Part09.pdf` | 3 | 4,527,973 | `1e68708ded8e` | B |
| `01_Photos_Part10.pdf` | 2 | 2,411,657 | `28c16fae83e2` | B |
| `02_Antenna_Specification.pdf` | 4 | 425,075 | `4a08b53a90d4` | B |
| `03_Antenna_Measurement.pdf` | 1 | 486,583 | `960c35fae2b3` | C |
| `04_Antenna_Measurement_Updated.pdf` | 1 | 243,702 | `bbe3305621bb` | C |
| `05_Confidentiality_Request.pdf` | 1 | 143,871 | `3df602ba9bf9` | B |
| `06_Sony_2024_Service_Manual.pdf` | 2 | 261,606 | `a8a0381fbcff` | C |
| `07_RF_2_4_GHz_Test_Part1.pdf` | 52 | 5,737,357 | `2e0d97f22298` | B |
| `07_RF_2_4_GHz_Test_Part2.pdf` | 23 | 3,565,675 | `2629c445b34a` | B |
| `07_RF_5_GHz_Test_Part1.pdf` | 102 | 5,636,122 | `4880011f07d1` | C |
| `07_RF_5_GHz_Test_Part2.pdf` | 23 | 1,291,614 | `e641d81aca35` | C |
| `07_RF_BLE_Test.pdf` | 52 | 2,255,507 | `1b1f23c88f31` | C |
| `07_RF_BT3_Test.pdf` | 72 | 3,580,908 | `9cc8c39e824a` | C |
| `07_RF_DFS_Test.pdf` | 24 | 1,928,567 | `04e1d58a4d59` | C |
| `08_SAR_Part1_New.pdf` | 49 | 5,650,200 | `711a35770c25` | C |
| `08_SAR_Part1_Updated.pdf` | 49 | 4,920,832 | `fd4a4258d954` | C |
| `08_SAR_Part2.pdf` | 31 | 5,718,483 | `1c16fa66c4db` | C |
| `08_SAR_Part3.pdf` | 39 | 5,642,996 | `1f1790a31daa` | B |
| `08_SAR_Part4.pdf` | 9 | 3,121,543 | `5b08e590aa38` | C |
| `09_Manual_Operating_Instructions.pdf` | 2 | 534,374 | `2b72e3ce40c9` | B |
| `09_Manual_Important_Information.pdf` | 12 | 194,539 | `849b611ed098` | B |
| `10_Internal_Exposure_Position.pdf` | 1 | 505,873 | `4b82d28f3c13` | B |
| `11_External_Photos.pdf` | 4 | 937,405 | `37291cc8bd83` | B |
| `12_Label_Nameplate.pdf` | 1 | 90,736 | `0742e082fb2f` | A |
| `12_Label_Location_Updated.pdf` | 2 | 343,189 | `838fa0949297` | B |
| `12_Label_Box.pdf` | 1 | 218,720 | `9bd00863b58a` | B |
| `13_Test_Setup_DFS.pdf` | 1 | 147,732 | `b33806b0de44` | B |
| `13_Test_Setup_ID.pdf` | 4 | 655,094 | `900f40cefeda` | B |
| `13_Test_Setup_SAR.pdf` | 3 | 251,076 | `f15ab77a6baf` | B |
| `14_Authorization_Sony.pdf` | 1 | 96,694 | `99a613134758` | B |
| `14_Agency_Sony.pdf` | 1 | 95,057 | `cfe62846bc70` | B |
| `14_Authorization_US.pdf` | 1 | 93,765 | `1cc8aa821deb` | A |
| `14_Authorization_ACB.pdf` | 1 | 76,043 | `f936c2566c1b` | B |
| `14_WiFi_Channels_12_13.pdf` | 1 | 134,438 | `3b084f02c9eb` | B |
| `14_Non_SDR_5G_WiFi.pdf` | 2 | 124,757 | `0f38df2a2fd1` | B |

## Visual observations and confidence

Page references below are one-based PDF pages, including covers. All 22 pages
of Parts 1-10 were rendered and visually reviewed; Parts 8-10 were also inspected
from native embedded photographs. Confidence is in the stated observation,
not in its applicability to every retail revision or in working Linux support.

| Ref / exact local filename and page | Observation | Confidence and limits |
| --- | --- | --- |
| F1 `01_Photos_Part08.pdf`, p. 2; overview Part 6 p. 2 | `SODAGREEN M/B REV:1.03`; adjacent `221412`, `H2-9`, `94V-0`, `E222034` markings | High for visible text. No date decoding, owner-board identity or netlist inferred |
| F2 `01_Photos_Part10.pdf`, p. 1, U1 | Qualcomm `QCS2290` marking | High. Corroborates historical D1 for the certification sample; no fuse/signature or pinmux information |
| F3 same page, U2 | Samsung package marked `KLMBG2JETD`; suffix not fully established | High for base marking; eMMC identification strongly supported by manufacturer's matching family publication. No runtime bus mode/boot configuration measured |
| F4 same page, U4 | Qualcomm `PM4125` marking, surrounded by inductors/passives | High for marking. Does not select charger subtypes, regulator constraints or battery profile |
| F5 same page, U3 | Micron logo on adjacent large package; small identification text insufficiently legible for a dependable full part decode | High for logo; RAM role plausible, exact density/type/bin unresolved. Do not report a guessed FBGA decode |
| F6 `01_Photos_Part09.pdf`, p. 1, U2504 | `3778` package marking; nearby metal-can markings `45.158` and `49.152` | High for text; correspondence to published CXD3778GF driver is a strong candidate, not proof of its exact type, clocks, routing or calibration |
| F7 Part 9 p. 3 / Part 10 p. 1, U190 | Qualcomm `WCN3950` marking in a separated RF area | High for component-family reading; agrees with withheld RF document title. No actual firmware/bus/regulatory configuration obtained |
| F8 `01_Photos_Part02.pdf`, p. 2; Parts 3-4 | Sony Li-ion label `LIS1650`, 3.7 V nominal, rated 1500 mAh, 4.2 V charge limit; separate protection PCB visible in Part 4 | High for label. Not a complete charging/thermal profile; do not program those values from the photo. Battery identifiers/QR data are omitted |
| F9 Parts 5 p. 1, 6 pp. 1-2, 7 pp. 1-2 and 9 p. 2 | USB-C, microSD socket, headphone jack, flex connectors, shields and exposed pads. Part 9 p. 2 labels include CON2401/CON2203/CON2101/CON2504 | High for location/text only. Pads are not identified as EDL, UART or test points with known nets; no electrical probing justified |
| F10 Part 7 p. 1; Part 8 pp. 2-3 | Display assembly/flex and `POWER-ON`/LED1 board markings | High for physical assembly/labels. Panel/controller, touch IC, DSI protocol, GPIO polarity, wake and backlight ownership remain unresolved |
| F11 `02_Antenna_Specification.pdf`, pp. 1-4 | INPAQ `RFMTA270500NNLB001`, customer part 1415-09DK000; A0 drawing release 2022-02-21, A1 top-layer footprint addition 2022-05-12 (p. 2) | High for antenna document; neither revision is a motherboard revision |
| F12 `07_RF_BT3_Test.pdf`, pp. 6-8 | Identifies Digital Media Player YY1301B1; sample type “Prototype production”; received July 2022; radio tests use Qualcomm Radio Control Toolkit 4.0.00185.0 | High for report. Resolves the mirror's headset-label conflict, and limits extrapolation to retail units. Toolkit operation is not a custom-boot or recovery interface |

The [Samsung-authored brief hosted by Avnet](https://www.avnet.com/fsp/opasdata/d120001/medias/docus/190/SAM-KLM8G1GETF-B041-Datasheet.pdf),
p. 1, identifies KLMBG2JETD-B041 as 32 GB eMMC 5.1. Its filename names a different
part; use its actual title/content, not the URL basename, for identity. Web text
was readable; direct acquisition returned HTTP 400, so no local PDF hash or
full suffix match is claimed. Current Samsung's old part URL redirects to a
family page. Do not use distributor guesses to decode the faint Micron marking.

## Revisions, withheld material and research-kit corrections

The FCC sample's 1.03 marking is consistent with, but does not prove equivalence
to, the metadata-only schematic `YY1301B_Schematic diagram and Block
_r103_20220314a_bom`. The schematic is absent. The owner's board revision remains
unknown. The kit's proposed **20220304 board date is unsupported** by the reviewed
image: the visible marking is `E222034`, with other separate codes. No manufacture
date is assigned. Antenna A0/A1, SAR Rev01, amended reports and Android versions
are different revision domains; no second mainboard revision was established.

`05_Confidentiality_Request.pdf`, p. 1, Sony letter dated 2022-09-01, visibly
requests permanent withholding of block diagrams, operational descriptions,
parts/BOM and schematics; photos receive short-term treatment. This explains
why more public photos cannot deliver the named schematic. The tune-up row is
not checked permanent. No inference of confidential contents or lawful access
is made beyond the letter. The US `06_Sony_2024_Service_Manual.pdf`, p. **2**,
states product exchange and supplies no original-board restoration procedure.
The original M6 report cited p. 1; the corrected locator is p. 2.

Raw photos, rendered/cropped inspection images, signatures, sample identifiers,
PDF text and full private provenance remain ignored. No photographs, proprietary
documents, firmware or calibration are republished. The research kit supplied
leads; its date and verification assertions were independently checked rather
than adopted as authority.

## Reproducible verification increment

`tools/evidence_inventory.py` reads catalog/acquisition metadata and streams
local hashes with no network or write operation. It reports size and digest
agreement independently, detects acquisition drift, and rejects duplicate,
missing, escaping and malformed paths/metadata. It does **not** parse PDFs or
authenticate Sony/FCC. Eight deterministic synthetic tests cover the real
classification failure and rejection paths; no new dependency is introduced.

```sh
python tools/evidence_inventory.py --root .local-references/sony-nw-a306/fcc-ak8yy1301b1
python -m unittest discover -s tests -p test_evidence_inventory.py
```

Independent strict PDF parsing/page counts and native-image extraction used the
existing bundled packages above; detailed scripts/results are private under
`build/m7/`. Structural acceptance is recorded separately from checksum and
identity evidence. The source catalog, downloader and original files remain
unchanged; the fix is a separate auditable inventory tool.
