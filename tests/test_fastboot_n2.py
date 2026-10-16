# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed N2 on existing injected sockets/processes, never physical tools."""
import copy
from datetime import datetime, timezone, timedelta
import json
import unittest

import test_fastboot_n1 as n1fixtures
from test_characterization_transport import Process
import fastboot_n2 as n2


class N2IntegrationTests(unittest.TestCase):
    def setUp(self):
        n1fixtures.N1Tests.setUp(self)
        self.approval['stage'] = 'N2'
        self.approval['plan_sha256'] = n2.cp.sha(n2.cp.canonical(n2.plan()))

    def start(self):
        return n2.start(self.approval, self.profile, self.out, self.ready, self.guard, connector=self.server)

    def launcher(self, args):
        return n1fixtures.N1Tests.launcher(self, args)

    def diagnose(self, launcher=None):
        return n2.diagnose(self.approval, self.profile, self.out, self.supervised, self.guard,
                           launcher=launcher or self.launcher)

    def test_exact_approved_schedule_and_inert_plan(self):
        p = n2.plan()
        self.assertEqual([a[-1] for a in p['native_commands']], ['-l', 'product', 'is-userspace'])
        self.assertEqual(len(p['pre_identity']), 11)
        self.assertEqual(p['pre_identity'], p['post_identity'])
        for forbidden in ['version-bootloader', 'unlocked', 'secure', 'current-slot', 'all', 'boot', 'reboot']:
            with self.assertRaises(n2.cp.Refusal): n2.argv('fixture', forbidden)
            with self.assertRaises(n2.cp.Refusal): n2.launch([str(self.exe), '-s', 'fixture', 'getvar', forbidden])
        self.assertFalse(self.server.requests)

    def test_bound_entry_once_current_ephemeral_transport_profile_immutable(self):
        original = copy.deepcopy(self.profile)
        self.server.tid += 1
        self.server.listing = self.server.listing.replace(('transport_id:' + self.profile['binding']['transport_id']).encode(), ('transport_id:' + str(self.server.tid)).encode())
        result = self.start()
        self.assertTrue(result['complete'], result['stop'])
        self.assertEqual(len(result['observations']), 11)
        self.assertEqual(result['session_profile']['binding']['transport_id'], str(self.server.tid))
        self.assertEqual(self.profile, original)
        self.assertEqual(self.server.requests.count('reboot:bootloader'), 1)
        with self.assertRaises(FileExistsError): self.start()
        self.assertEqual(self.server.requests.count('reboot:bootloader'), 1)

    def test_changed_serial_or_identity_never_enters(self):
        self.server.listing = self.server.listing.replace(self.profile['binding']['serial'].encode(), b'other')
        result = self.start()
        self.assertFalse(result['entry_attempted'])
        self.assertNotIn('reboot:bootloader', self.server.requests)

    def test_failed_identity_does_not_enter(self):
        self.server.values[n2.cp.IDENTITY[0].remote] = b'0\n'
        result = self.start()
        self.assertFalse(result['entry_attempted'])
        self.assertNotIn('reboot:bootloader', self.server.requests)

    def test_approval_and_readiness_guard_before_any_connection(self):
        for field, value in [('approved', False), ('stage', 'N1'), ('plan_sha256', 'old'), ('profile_sha256', 'bad'), ('output', 'other')]:
            a = self.approval.copy(); a[field] = value
            with self.assertRaises(n2.cp.Refusal): n2.start(a, self.profile, self.out, self.ready, self.guard, connector=self.server)
        r = self.ready.copy(); r['power_ready'] = False
        with self.assertRaises(n2.cp.Refusal): n2.start(self.approval, self.profile, self.out, r, self.guard, connector=self.server)
        r = self.ready.copy(); r['utc'] = (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat()
        with self.assertRaises(n2.cp.Refusal): n2.start(self.approval, self.profile, self.out, r, self.guard, connector=self.server)
        self.assertFalse(self.server.requests)

    def test_explicit_no_three_commands_exact_and_no_repeat(self):
        self.start()
        r = self.diagnose()
        self.assertTrue(r['complete'], r['stop'])
        self.assertEqual(r['classification'], 'bootloader-fastboot')
        self.assertTrue(r['post_return_guards_permitted'])
        self.assertEqual([a[-1] for a in self.calls], ['-l', 'product', 'is-userspace'])
        with self.assertRaises(FileExistsError): self.diagnose()
        self.assertEqual(len(self.calls), 3)

    def test_explicit_yes_classifies_userspace(self):
        self.values['is-userspace'] = 'yes'
        self.start()
        self.assertEqual(self.diagnose()['classification'], 'fastbootd')

    def test_empty_success_inconclusive_and_post_return_allowed(self):
        self.values['is-userspace'] = ''
        self.start()
        r = self.diagnose()
        self.assertTrue(r['complete'], r['stop'])
        self.assertEqual(r['classification'], 'inconclusive')
        self.assertTrue(r['post_return_guards_permitted'])
        post = n2.verify_return(self.approval, self.profile, self.out, True, self.guard, connector=self.server)
        self.assertTrue(post['complete'], post['stop'])
        self.assertEqual(len(post['observations']), 11)

    def test_unsupported_exit_zero_is_inconclusive_no_post_return_requests(self):
        self.start()
        def unsupported(args):
            if args[-1] == 'is-userspace':
                self.calls.append(args)
                return Process(stderr=b"getvar:is-userspace FAILED (remote: 'unknown variable')\n")
            return self.launcher(args)
        r = self.diagnose(unsupported)
        self.assertEqual(r['classification'], 'inconclusive')
        self.assertEqual(r['stop'], 'optional_unsupported')
        self.assertFalse(r['post_return_guards_permitted'])
        count = len(self.server.requests)
        with self.assertRaises(n2.cp.Refusal): n2.verify_return(self.approval, self.profile, self.out, True, self.guard, connector=self.server)
        self.assertEqual(len(self.server.requests), count)
        self.assertEqual(len(self.calls), 3)

    def test_optional_io_failure_stops_and_keeps_raw(self):
        self.start()
        def failure(args):
            if args[-1] == 'is-userspace':
                self.calls.append(args)
                return Process(stderr=b'fastboot: error: Write to device failed (no link)\n', code=1)
            return self.launcher(args)
        r = self.diagnose(failure)
        self.assertFalse(r['complete'])
        self.assertFalse(r['post_return_guards_permitted'])
        self.assertIn(b'no link', (self.out/'fastboot/02-stderr.bin').read_bytes())
        self.assertEqual(len(self.calls), 3)

    def test_product_mismatch_stops_before_optional(self):
        self.values['product'] = 'wrong'
        self.start()
        self.assertFalse(self.diagnose()['complete'])
        self.assertEqual(len(self.calls), 2)

    def test_supervision_and_host_failure_block_native_dispatch(self):
        self.start()
        self.supervised['same_unit_fastboot_screen'] = False
        with self.assertRaises(n2.cp.Refusal): self.diagnose()
        self.supervised['same_unit_fastboot_screen'] = True
        self.guard.side_effect = n2.cp.Refusal('USB changed')
        self.assertFalse(self.diagnose()['complete'])
        self.assertFalse(self.calls)

    def test_post_return_rebinds_new_transport_without_modifying_original(self):
        self.start(); self.diagnose()
        old = copy.deepcopy(self.profile)
        self.server.tid += 2
        self.server.listing = self.server.listing.replace(('transport_id:' + old['binding']['transport_id']).encode(), ('transport_id:' + str(self.server.tid)).encode())
        r = n2.verify_return(self.approval, self.profile, self.out, True, self.guard, connector=self.server)
        self.assertTrue(r['complete'], r['stop'])
        self.assertEqual(r['session_profile']['binding']['transport_id'], str(self.server.tid))
        self.assertEqual(self.profile, old)

    def test_saved_optional_integrity_failure_blocks_post_return(self):
        self.start(); self.diagnose()
        (self.out/'fastboot/02-stderr.bin').write_bytes(b'is-userspace: yes\n')
        count = len(self.server.requests)
        with self.assertRaises(n2.cp.Refusal): n2.verify_return(self.approval, self.profile, self.out, True, self.guard, connector=self.server)
        self.assertEqual(len(self.server.requests), count)

    def test_entry_failure_preserved_no_native_dispatch(self):
        self.server.override = lambda req, sock: b'FAIL' + n1fixtures.af.string(b'fixture entry denied') if req == 'reboot:bootloader' else None
        r = self.start()
        self.assertTrue(r['entry_attempted'])
        self.assertFalse(r['entry_acknowledged'])
        self.assertEqual(self.server.requests.count('reboot:bootloader'), 1)
        with self.assertRaises(n2.cp.Refusal): self.diagnose()
        self.assertFalse(self.calls)

    def test_atomic_usb_mismatch_never_enters(self):
        self.server.tid += 1  # Inventory still declares the previous ID.
        r = self.start()
        self.assertFalse(r['entry_attempted'])
        self.assertNotIn('reboot:bootloader', self.server.requests)

    def test_expired_session_blocks_return_before_requests(self):
        self.start(); self.diagnose()
        path = self.out/'pre-entry/manifest.json'
        m = json.loads(path.read_text()); m['monotonic_start'] -= 451
        path.write_text(json.dumps(m))
        count = len(self.server.requests)
        with self.assertRaises(n2.cp.Refusal): n2.verify_return(self.approval, self.profile, self.out, True, self.guard, connector=self.server)
        self.assertEqual(len(self.server.requests), count)


if __name__ == '__main__': unittest.main()
