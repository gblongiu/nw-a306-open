# SPDX-License-Identifier: GPL-2.0-or-later
"""Synthetic dimensionless limits only; these are not NW-A306 settings."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from linux_safety import REQUIRED, readiness


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.policy = {'battery_temperature': (0, 10, 2), 'battery_voltage': (2, 4, 2),
                       'soc_temperature': (0, 10, 2)}
        self.samples = {'battery_temperature': (5, 9), 'battery_voltage': (3, 9),
                        'soc_temperature': (5, 9)}
        self.verified = dict.fromkeys(REQUIRED, True)

    def test_ready_requires_all_inputs(self):
        self.assertEqual(readiness(self.policy, self.samples, self.verified, 10), (True, []))

    def test_every_missing_condition_keeps_muted(self):
        for key in REQUIRED:
            with self.subTest(key=key):
                flags = self.verified | {key: False}
                self.assertFalse(readiness(self.policy, self.samples, flags, 10)[0])

    def test_missing_or_stale_readings(self):
        for samples in [{}, None, self.samples | {'battery_temperature': (5, 7)},
                        self.samples | {'battery_voltage': (3, 11)}]:
            with self.subTest(samples=samples):
                self.assertFalse(readiness(self.policy, samples, self.verified, 10)[0])

    def test_no_default_hardware_policy(self):
        for policy in [{}, None, {'bad': (10, 0, 1)}, {'bad': (0, 10, 0)}]:
            with self.subTest(policy=policy):
                self.assertFalse(readiness(policy, self.samples, self.verified, 10)[0])

    def test_fault_and_nonfinite_values(self):
        for value in [-1, 11, float('nan'), float('inf'), True, '5', 10**1000]:
            with self.subTest(value=value):
                samples = self.samples | {'battery_temperature': (value, 9)}
                self.assertFalse(readiness(self.policy, samples, self.verified, 10)[0])

    def test_invalid_clock_and_unverified_owner(self):
        for now in [-1, float('nan'), None, True]:
            self.assertFalse(readiness(self.policy, self.samples, self.verified, now)[0])
        self.assertFalse(readiness(self.policy, self.samples, None, 10)[0])

    def test_policy_cannot_omit_critical_readings(self):
        for key in self.policy:
            policy = {k: v for k, v in self.policy.items() if k != key}
            self.assertFalse(readiness(policy, self.samples, self.verified, 10)[0])


if __name__ == '__main__':
    unittest.main()
