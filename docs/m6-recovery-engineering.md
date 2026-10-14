# M6 original-board recovery requirements

2026-10-14. **Original-board recovery from unbootable Android is unverified.**
The M5 US exchange finding remains intact; an exchange can replace a
failed product without restoring the original board or its unique state.

## Documented capability and unsuccessful acquisition

Sony documents [factory formatting](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733530.html)
through Android settings and [restart](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733532.html)
for unstable operation. Neither establishes replacement of damaged boot images.
Authentic ordinary updates and their variant-specific sizes/hashes are preserved
in [M1/M2](m2-firmware-analysis.md); their payload is still opaque. Update
availability does not establish same-version reinstall or factory reconstruction.

The model-specific [US service document](https://research.encompass.com/SON/rr/NWA306_B.pdf),
2024-06-15, p. 2, documents product exchange. Its two pages provide no restoration
image or procedure. The prior PDF hash/visual review are retained in
[M5](m5-boot-recovery-paths.md#new-model-specific-service-evidence).
M6's candidate Japanese reference-guide URL
`https://www.sony.jp/ServiceArea/impdf/pdf/50426710M-JP.pdf` returned a **1,420-byte
HTML redirect**, not a PDF (SHA-256
`be0c41aaf95e245d18d56c6925380b05019531e8426886946686413969665f41`).
No Japanese repair policy was inferred from a search snippet or that response.
Regional same-board capabilities still need confirmation.

The newly located regulatory schematic title identifies a specific document
to request, but neither its inaccessible metadata nor public photographs supply
a signed service programmer, provisioning policy or restoration sequence.
See the [artifact inventory](m6-board-artifact-inventory.md).

## Failure-state coverage matrix

“Candidate interface” is conditional on surviving stages and Sony support.
No row below is a tested restoration procedure or a device-operation instruction.

| Failure state | Candidate remaining interface and status | Genuine resources / authorization needed | Original-board and unique-state coverage |
| --- | --- | --- | --- |
| Android operational | Official settings reset/update documented; ordinary update is not arbitrary reinstall | Correct model/region/build update, supported version/rollback rules and updater validation | Reset deletes user state; it does not reconstruct boot/GPT. Calibration/provisioning effects and same-version reinstall need a model-specific answer |
| Android unusable, stock recovery intact | Recovery-mode reinstall is an **unverified candidate**; no applicable entry/accepted-package procedure established | Authentic accepted recovery package, signature/model/version policy, independently documented entry and update coverage | Must distinguish data reset from image reinstall. Ask which boot/shared partitions are restored and whether unique data remains intact |
| Both Android boot slots fail | A separately intact recovery/bootloader might help; A/B names alone prove no reachable independent path | Actual recovery placement/dependencies and loader fallback policy, matching signed boot/DT/AVB images and permitted service interface | A fallback slot is not a guarantee if both slots or shared metadata fail. Same-board service coverage must explicitly include this state |
| Recovery or AVB metadata damaged | Bootloader service interface only if it survives and authorizes restoration; fastbootd may depend on recovery | Accepted matching recovery/vbmeta chain, rollback-compatible images, authorized repair of affected state, entry independent of damaged recovery | A stock UPG cannot currently be shown to repair these objects. Replacing board/product is a different outcome |
| GPT/dynamic partition metadata corrupted | Early service entry independent of partition discovery is only a hypothesis | Exact storage/controller/layout, authenticated full image/programming manifest, partition reconstruction and unique-area exclusions | Need confirmation that the original storage can be reconstructed without losing unrecoverable calibration/provisioning. Raw capacity or another unit's GPT is insufficient |
| Low-level boot stage fails | ROM/service entry, if enabled/reachable and able to authenticate a matching loader, is unverified | Genuine Sony-accepted programmer/tool, hardware/OEM/software binding, credentials, compatible boot stages, rollback and stable power constraints | Generic Qualcomm EDL documentation establishes no A306 recovery. Damaged provisioning/storage hardware may instead require board replacement; ask service to distinguish these cases |
| Unique calibration/security provisioning lost (cross-cutting) | No valid preservation/regeneration method established | Sony's classification of per-device versus replaceable data, permitted backup/restore/regeneration procedure and verification criteria | Another board's calibration, keys or RPMB state cannot be assumed transferable. Do not request secret keys; request ownership and restoration guarantees |

Generic architecture references: [AOSP A/B](https://source.android.com/docs/core/ota/ab)
describes fallback behavior, not Sony's measured policy;
[fastbootd](https://source.android.com/docs/core/architecture/bootloader/fastbootd)
explains recovery dependencies; [Qualcomm secure-boot overview](https://www.qualcomm.com/media/documents/files/secure-boot-and-image-authentication-technical-overview-v2-0.pdf),
sections 3-5, explains identity/signature constraints without specifying this
unit's provisioning. None supplies a usable NW-A306 restoration image.

Factory reset, ordinary update, recovery reinstall, authenticated service restore,
board replacement and ROM-level recovery have different entry and data-survival
requirements. A claim that service “repairs” or “resets” the player is insufficient
until the interface, original-board outcome and covered failure states are named.

## Acceptance record required before a future experiment

A reviewed recovery plan must bind model/region/revision, current security/build
state, exact permitted tool/image hashes and access terms to the intended failure
states above. It must identify entry that survives the proposed failure, unique
state preserved or regenerated, power/safety requirements, and objective return
to genuine stock. Same-version/rollback restrictions and remaining uncovered
states must be explicit. A spare reduces primary-unit exposure but proves no
recovery capability before a separately authorized validation.

Prioritize written service capability and supplied-artifact audit. Do not begin
with slot changes, presumed readback, alternate programmers or speculative ROM
entry. No device command list, programmer or firmware writer was created.

## Sony inquiry (unsent)

**Subject: NW-A306 original-board restoration and supported Linux development**

Please route this host-only Linux/Rockbox research inquiry to service/platform
engineering. We have not modified the player.

1. For our sales region and NW-A306/YY1301B1 board revision, can Sony restore
   the **original board**, or is service limited to product/board exchange?
   The US service document dated 2024-06-15 specifies product exchange.
2. Which supported restoration entry, tool/image IDs and authentication cover:
   Android failure with intact recovery; both boot slots failed; damaged
   recovery/AVB; corrupt partition metadata; and an early boot-stage failure?
   Please state same-version/rollback limits and owner/development-partner access.
3. Which calibration/provisioning data is per-device, preserved, regenerated
   or irrecoverable? How is successful original-board restoration verified?
   We are asking for interfaces and policy, not device secrets.
4. Does this model support an authorized development image, alternate-kernel
   temporary boot, unlock or owner-key enrollment? Which signature, image/DT
   and persistent-state requirements apply? Xperia guidance does not establish
   Walkman support.
5. Can Sony provide permitted-use board/build resources: the applicability of
   `YY1301B_Schematic diagram and Block _r103_20220314a_bom`, selected DT/DTBO,
   final kernel/module/signature metadata, required firmware/calibration
   interfaces, and panel/input/charging/thermal/watchdog policy? Can it provide
   NWWM package/provisioning documentation or an approved matching image set?

No identifier, private log, calibration or firmware attachment is included.
The maintainer can supply sales-region/build details privately after approving
contact. The existing [official regional routing](m5-boot-recovery-paths.md#new-model-specific-service-evidence)
remains the proposed channel; no email, form, chat or support case was sent.
The questions distinguish original-board restoration and supported independent
execution from product exchange. Contact requires separate approval.
