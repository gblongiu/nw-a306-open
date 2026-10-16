# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed B2 scope after the physical Stage B tree-property denial.

Only previously reviewed metadata commands; no execution or configurable subset.
Boot/update leads precede inventories. Device-node link metadata comes last
because its access is uncertain and it must not prevent earlier proc inventories.
"""

import characterization_plan as cp
import characterization_transport as ct

EVIDENCE_IDS = (
    "bootloader-report",
    "unlock-report",
    "android-release",
    "updater-candidates",
    "partitions",
    "sound-cards",
    "sound-pcm",
    "input-devices",
    "graphics-names",
    "power-names",
    "block-names",
)
EVIDENCE = tuple(ct.REGISTRY[key] for key in EVIDENCE_IDS)
OPERATIONS = cp.IDENTITY + EVIDENCE + cp.OPERATIONS[-len(cp.IDENTITY):]
