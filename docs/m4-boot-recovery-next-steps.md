# M4 boot authorization and recovery next steps

Date: 2026-10-14. This is the deployment track, separate from the working
[generic AArch64 playback track](m4-playback-validation.md). The [M1 register](recovery-provenance.md#source-register)
and [M3 findings](m3-board-dependencies.md) remain preserved.

## New verification and its limits

Sony's current [product downloads page](https://www.sony.com/electronics/support/product/nw-a306/downloads)
lists firmware 3.06.00 dated 2026-07-16. A legacy category-routed search result
still shows 3.05.00. The current product page corroborates the preserved update
baseline; neither listing supplies a factory image set or custom-boot policy.
This is a concrete reason to request exact artifact IDs rather than rely on
a support-page title, regional redirect or cached listing.

The [NW-A306 Help Guide](https://helpguide.sony.net/dmp/1301/v1/en/index.html)
labels its regulatory model YY1301B1. That is useful identification context for
a Sony inquiry, not proof of a DT compatible or hardware-revision match to the
historically observed `icx1301` platform name.

Sony's [restart page](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733532.html)
describes restarting a frozen player; its
[formatting page](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733530.html)
describes an Android Settings factory reset. Neither documents rebuilding boot,
recovery, AVB or partition metadata when Android cannot start. The
[initial-setup note](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733584.html)
still describes paid repair/reformatting for a forgotten screen lock; that
limited repair statement does not establish recovery from damaged firmware.
These pages were reviewed, not executed as procedures.

No new applicable NWWM specification, authenticated service programmer,
matching factory package or supported Walkman unlock/temporary-boot mechanism
was established. Public anecdotes and generic Xperia/Qualcomm procedures do
not change that conclusion. Existing locked/green evidence describes the stock
state; an OEM UI switch does not establish custom execution. The candidate UPG
remains authentic at the distribution/hash level and opaque internally. No
image inventory or image-acceptance claim is added.

## Ranked investigations and prerequisites

| Rank | Smallest useful next action | Prerequisite and decision it can resolve |
| --- | --- | --- |
| 1 | Clarify the service questions below using applicable documentation or a reviewed inquiry | Written confirmation of recoverable failure states, exact service/artifact identity and development-interface applicability; no device operation needed |
| 2 | Obtain matching factory/boot/DT artifacts or board documentation lawfully, with hashes and model/region/revision provenance | Enables static boot-header/DT/module/firmware audit. An OTA alone is insufficient; do not reconstruct absent evidence or attempt key recovery |
| 3 | Review a tightly bounded characterization plan for a normally booted matching device | Separate explicit approval and privacy/command whitelist. Can identify bound drivers and selected DT; cannot prove restoration or custom acceptance |
| 4 | Identify a matching spare and service coverage for the proposed failures | Match regulatory/platform identity, region, board revision and starting build; preserve its own unique data. Purchase or possession alone authorizes no experiment |
| 5 | Assess a documented accepted temporary-boot/development mechanism | Need Sony-specific authorization, container/handoff and failure coverage. A RAM payload can still change storage/power hardware; reversible execution remains unproven |

The historical M4 recommendation was a service-capability inquiry to resolve
recovery questions without a hardware experiment. If no useful answer arrives, continue host implementation and static
analysis of lawfully supplied matching artifacts. Mainline platform work or a
generic development board can validate interfaces but cannot replace Sony boot
authorization. Bare-metal payloads face the same acceptance gate.

## Proposed characterization requirements

Purpose: identify the active Linux resources, not exercise them. First inventory
existing private evidence and supplied artifacts to avoid duplicate collection.
Before device access, review an exact command/file allowlist,
privilege level, maximum output size and local-only destination before use.

Potential data classes are selected DT identity/properties, kernel build/config
identity, bound-driver/module names, ALSA card/PCM/control *descriptions*, evdev
capabilities, DRM/panel/backlight identity, existing firmware filenames and
power/thermal/watchdog ownership. Prefer immutable supplied files and existing
diagnostics. Some generated driver reads have side effects or wake hardware,
so even “read-only” collection needs review. Do not trigger driver reprobes,
write controls/sysfs, change routes or volume, query raw buses, acquire keys,
reboot, enter another mode or access block devices as a convenience.

Stop on unexpected permission prompts, denied paths, unknown interface behavior,
device instability or any proposed state change. Keep raw results private and
redact identifiers before publication. Device access requires an explicit
operation plan and approval. Any later boot or
firmware change additionally requires demonstrated recovery and a reviewed
failure-mode plan, preferably validated on the matching spare.

## Historical service questions

M4 refined the questions around same-board restoration, exact tool/artifact IDs,
model/region matching and supported independent execution. The consolidated
[service questions](m6-recovery-engineering.md#sony-inquiry-unsent) retain those
requirements. No inquiry was sent.

## Proposed M5 split

Track A: close application error reporting and chained-stream/duration gaps;
validate resampler quality and cross-rate transition policy; isolate the ASan
runtime hang before broader memory/leak tests; test evidence-based Linux output,
input and safety interfaces. Track B: obtain an authorized written service answer
and matching board/artifact inputs, then review characterization/spare plans.
The resulting M5 work is recorded in the [Linux prototype](m5-linux-prototype.md).
