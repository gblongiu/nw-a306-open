# SPDX-License-Identifier: GPL-2.0-or-later
"""Pure readiness policy; performs no device I/O and cannot unmute hardware.

No Sony limits are supplied. A future collector must use authenticated board
policy and a single monotonic clock; missing policy always keeps audio muted.
"""
import math

REQUIRED = ('board_identity', 'firmware', 'calibration', 'route', 'gain_limits',
            'kernel_charging', 'thermal_protection', 'watchdog_owner')
REQUIRED_READINGS = ('battery_voltage', 'battery_temperature', 'soc_temperature')


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def readiness(policy, samples, verified, now):
    """Return (ready, reasons). Caller must remain muted unless ready is True.

    policy maps each required sample name to (minimum, maximum, max_age_seconds).
    samples maps that name to (value, monotonic_timestamp). Limits and units
    must come from an independently reviewed board contract, never guesses.
    """
    reasons = []
    if not isinstance(verified, dict):
        verified = {}
    reasons += ['unverified:' + key for key in REQUIRED if verified.get(key) is not True]
    if not number(now) or now < 0:
        reasons.append('invalid_clock')
        return False, reasons
    if not isinstance(policy, dict) or not policy:
        return False, reasons + ['missing_policy']
    reasons += ['missing_policy:' + key for key in REQUIRED_READINGS if key not in policy]
    if not isinstance(samples, dict):
        samples = {}
    for key, bounds in policy.items():
        if not isinstance(key, str):
            reasons.append('invalid_policy_key')
            continue
        if (not isinstance(bounds, (tuple, list)) or len(bounds) != 3 or
                not all(number(x) for x in bounds) or bounds[0] >= bounds[1] or bounds[2] <= 0):
            reasons.append('invalid_policy:' + key)
            continue
        sample = samples.get(key)
        if (not isinstance(sample, (tuple, list)) or len(sample) != 2 or
                not all(number(x) for x in sample)):
            reasons.append('missing_or_invalid:' + key)
            continue
        value, stamp = sample
        if stamp < 0 or stamp > now or now - stamp > bounds[2]:
            reasons.append('stale_or_future:' + key)
        if not bounds[0] <= value <= bounds[1]:
            reasons.append('outside_policy:' + key)
    return not reasons, reasons
