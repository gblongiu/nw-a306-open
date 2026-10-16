# SPDX-License-Identifier: GPL-2.0-or-later
"""P1 on injected sockets only; real network and process paths are blocked."""
import io
import copy
import unittest
from unittest import mock

import test_adb_readonly as af

ar, cp = af.ar, af.cp
p1 = ar.p1
PARENT = b'drwxr-xr-x 2 root root u:object_r:block_device:s0 4096 2026-10-15 01:00 /dev/block/by-name\n'
NODES = (b'total 0\n'
         b'brw------- 1 root root u:object_r:block_device:s0 179,  1 2026-10-15 01:00 fixture_loader_a\n'
         b'brw-rw---- 1 root disk u:object_r:block_device:s0 179,  2 2026-10-15 01:00 fixture_boot_b\n')


class P1Tests(unittest.TestCase):
    check_hashes = af.AdapterTests.check_hashes

    def setUp(self):
        af.AdapterTests.setUp(self)
        self.server.fragment = 65536
        self.server.values.update({p1.EVIDENCE[0].remote: PARENT, p1.EVIDENCE[1].remote: NODES})

    def approval(self, out):
        return dict(approved=True, stage='P1', plan_sha256=cp.sha(cp.canonical(ar.plan('P1'))),
                    profile_sha256=cp.sha(cp.canonical(self.profile)), output=str(out.absolute()))

    def run_p1(self):
        self.counter += 1
        out = self.root / ('p1-' + str(self.counter))
        return ar.run('P1', self.approval(out), out, self.profile, connector=self.server), out

    def test_fixed_scope_caps_hashes_and_inert_default(self):
        plan = ar.plan('P1')
        self.assertEqual(len(plan['operations']), 24)
        self.assertEqual([o.remote for o in p1.EVIDENCE], [
            '/system/bin/toybox ls -ldZ /dev/block/by-name',
            '/system/bin/toybox ls -lZL /dev/block/by-name'])
        self.assertEqual([o.cap for o in p1.OPERATIONS], [4096]*12 + [65536] + [4096]*11)
        self.assertTrue(all(o.timeout_ms == 5000 for o in p1.OPERATIONS))
        self.assertEqual(plan['output_cap'], sum(2*o.cap for o in p1.OPERATIONS))
        self.assertEqual(plan['output_cap'], 319488)
        self.assertEqual(plan['wire_cap'], 2097152)
        self.assertEqual(plan['session_ms'], 300000)
        self.assertTrue(plan['strict_stream_cap'])
        self.assertIn('no mid-session rebinding', plan['transport_binding'])
        self.assertEqual(set(plan['code_sha256']), {'adb_readonly.py', 'characterization_plan.py',
            'characterization_transport.py', 'characterization_c1.py', 'characterization_p1.py'})
        with mock.patch.object(ar, 'connect_existing', side_effect=AssertionError('live forbidden')):
            with mock.patch('sys.stdout', io.StringIO()) as output:
                self.assertEqual(ar.main(['--stage', 'P1']), 0)
                policy = cp.json.loads(output.getvalue())
                digest = policy.pop('plan_sha256')
                self.assertEqual(policy, plan)
                self.assertEqual(digest, cp.sha(cp.canonical(plan)))
        self.assertFalse(self.server.requests)

    def test_full_success_exact_order_capture_and_atomic_transport(self):
        result, out = self.run_p1()
        self.assertTrue(result['complete'], result['stop'])
        self.assertEqual(self.server.commands, ['shell,v2,raw:' + o.remote for o in p1.OPERATIONS])
        self.assertEqual(self.server.stdin_closes, 24)
        self.assertTrue(all(o['complete'] for o in result['observations']))
        self.assertFalse(result['physical_evidence'])
        self.assertEqual((out/'12-stdout.bin').read_bytes(), NODES)
        self.assertTrue(all(s.closed for s in self.server.sockets))
        self.assertTrue(result['session_binding_identity_verified'])
        self.assertEqual(result['session_profile'], self.profile)
        self.check_hashes(result, out)

    def test_parent_type_path_label_and_field_failures_prevent_second_command(self):
        for value in [b'l'+PARENT[1:], b'-'+PARENT[1:], PARENT+PARENT,
                PARENT.replace(b'/dev/block/by-name', b'/other'),
                PARENT.replace(b'block_device:s0', b'?'),
                PARENT.replace(b'2026-10-15', b'2026-99-99'),
                PARENT.replace(b' 2 root', b' 0 root'), PARENT.replace(b'4096', b'bad')]:
            self.server.values[p1.EVIDENCE[0].remote] = value
            before = len(self.server.commands)
            result, out = self.run_p1()
            with self.subTest(value=value):
                self.assertFalse(result['complete'])
                self.assertEqual(len(result['observations']), 12)
                self.assertEqual(self.server.commands[before:], ['shell,v2,raw:'+o.remote for o in p1.OPERATIONS[:12]])
                self.assertEqual((out/'11-stdout.bin').read_bytes(), value)
                self.check_hashes(result, out)

    def test_nonblock_ambiguous_or_incomplete_inventory_prevents_end_guards(self):
        for value in [b'total 0\n', NODES.replace(b'brw', b'lrw', 1),
                NODES.replace(b'brw', b'crw', 1), NODES.replace(b'brw', b'-rw', 1),
                NODES.replace(b'fixture_boot_b', b'fixture_loader_a'),
                NODES.replace(b'fixture_boot_b', b'../other'),
                NODES.replace(b'179,', b'179'), NODES.replace(b'179,', b'4294967296,'),
                NODES.replace(b'01:00', b'25:00'), NODES[:-1], NODES+b'extra\n',
                NODES.replace(b'root', b'\xffroot', 1), NODES.replace(b'root', b'\x1broot', 1)]:
            self.server.values[p1.EVIDENCE[1].remote] = value
            result, out = self.run_p1()
            with self.subTest(value=value):
                self.assertFalse(result['complete'])
                self.assertEqual(len(result['observations']), 13)
                self.assertEqual((out/'12-stdout.bin').read_bytes(), value)
                self.check_hashes(result, out)

    def test_denial_absence_and_warning_preserve_failure_without_retry(self):
        for index, op in enumerate(p1.EVIDENCE, 11):
            for error, code in [(b'Permission denied\n', 1), (b'No such file or directory\n', 1), (b'warning\n', 0)]:
                before = len(self.server.commands)
                def reply(service, sock):
                    if service == 'shell,v2,raw:' + op.remote:
                        sock.shell = True
                        self.server.commands.append(service)
                        return b'OKAY' + af.frame(2, error) + af.frame(3, bytes([code]))
                    return None
                self.server.override = reply
                result, out = self.run_p1()
                self.assertFalse(result['complete'])
                self.assertEqual(len(result['observations']), index+1)
                self.assertEqual(len(self.server.commands)-before, index+1)
                self.assertEqual((out/('%02d-stderr.bin'%index)).read_bytes(), error)
                self.check_hashes(result, out)

    def test_strict_stream_limits_on_both_operations(self):
        for index, op in enumerate(p1.EVIDENCE, 11):
            for channel in (1, 2):
                def reply(service, sock):
                    if service == 'shell,v2,raw:' + op.remote:
                        sock.shell = True
                        self.server.commands.append(service)
                        return b'OKAY'+af.frame(channel, b'x'*(op.cap+1))+af.frame(3, b'\0')
                    return None
                self.server.override = reply
                result, out = self.run_p1()
                self.assertEqual(result['stop'], 'stream_byte_limit')
                self.assertEqual(len(result['observations']), index+1)
                self.assertLessEqual((out/('%02d-stdout.bin'%index)).stat().st_size, op.cap)
                self.assertLessEqual((out/('%02d-stderr.bin'%index)).stat().st_size, op.cap)

    def test_unapproved_changed_plan_profile_scope_refused_before_connection(self):
        for field, value in [('approved', False), ('stage', 'C1'), ('plan_sha256', '0'*64),
                ('profile_sha256', '0'*64), ('output', 'elsewhere')]:
            out = self.root/field
            approval = self.approval(out); approval[field] = value
            with self.assertRaises(cp.Refusal):
                ar.run('P1', approval, out, self.profile, connector=self.server)
            self.assertFalse(out.exists())
        out = self.root/'changed'; approval = self.approval(out)
        with mock.patch.object(p1, 'OPERATIONS', p1.OPERATIONS[:-1]), self.assertRaises(cp.Refusal):
            ar.run('P1', approval, out, self.profile, connector=self.server)
        self.assertFalse(self.server.requests)

    def test_transport_mismatch_cannot_be_rebound(self):
        self.server.tid += 1
        result, out = self.run_p1()
        self.assertEqual(result['stop'], 'usb_transport_mismatch')
        self.assertFalse(self.server.commands)
        self.assertEqual(result['expected_profile'], self.profile)
        self.check_hashes(result, out)

    def test_serial_and_atomic_selection_changes_prevent_shell(self):
        self.server.listing = self.server.listing.replace(self.profile['binding']['serial'].encode(), b'other')
        result, _ = self.run_p1()
        self.assertEqual(result['stop'], 'P1 current target differs from original approved device')
        self.assertFalse(self.server.commands)
        self.server = af.FakeServer(self.profile)
        self.server.override = lambda s, sock: b'OKAY'+af.struct.pack('<Q', 8) if s.startswith('host:tport:serial:') else None
        result, _ = self.run_p1()
        self.assertEqual(result['stop'], 'selected_transport_mismatch')
        self.assertFalse(self.server.commands)

    def test_fresh_ids_across_sessions_preserve_original_profile(self):
        original = copy.deepcopy(self.profile)
        for tid in (9, 42):
            self.server.listing = self.server.listing.replace(
                ('transport_id:' + str(self.server.tid)).encode(), ('transport_id:' + str(tid)).encode())
            self.server.tid = tid
            result, out = self.run_p1()
            self.assertTrue(result['complete'], result['stop'])
            self.assertEqual(result['expected_profile'], original)
            self.assertEqual(result['session_profile']['binding']['transport_id'], str(tid))
            self.assertEqual(result['session_profile']['identity'], original['identity'])
            self.assertTrue(result['session_binding_identity_verified'])
            self.assertEqual(self.profile, original)
            self.check_hashes(result, out)

    def test_ambiguous_offline_nonusb_and_invalid_initial_candidates(self):
        good = self.server.listing
        for listing in [b'', good+good, good.replace(b' device ', b' offline '),
                good.replace(b' device ', b' unauthorized '),
                good.replace(b'device:icx1301', b'device:other'),
                good.replace(b'transport_id:7', b'transport_id:0'),
                good.replace(b'transport_id:7', b'transport_id:18446744073709551616')]:
            self.server.listing = listing
            result, out = self.run_p1()
            self.assertFalse(result['complete'])
            self.assertFalse(self.server.commands)
            self.assertNotIn('session_profile', result)
            self.check_hashes(result, out)
        self.server.listing = good
        self.server.override = lambda s, sock: b'FAIL0006no usb' if s == 'host:tport:usb' else None
        result, _ = self.run_p1()
        self.assertEqual(result['stop'], 'server_FAIL')
        self.assertFalse(self.server.commands)

    def test_wrong_android_identity_blocks_metadata_after_new_id_resolution(self):
        self.server.listing = self.server.listing.replace(b'transport_id:7', b'transport_id:19')
        self.server.tid = 19
        self.server.values[cp.IDENTITY[0].remote] = b'0\n'
        result, out = self.run_p1()
        self.assertEqual(result['stop'], 'identity mismatch: uid')
        self.assertFalse(result['session_binding_identity_verified'])
        self.assertEqual(len(self.server.commands), 1)
        self.assertEqual(result['session_profile']['binding']['transport_id'], '19')
        self.check_hashes(result, out)

    def test_transport_change_inside_session_never_refreshes(self):
        for count in (0, 11, 12):
            self.server = af.FakeServer(self.profile)
            self.server.fragment = 65536
            self.server.values.update({p1.EVIDENCE[0].remote: PARENT, p1.EVIDENCE[1].remote: NODES})
            inventories = 0
            def reply(service, sock):
                nonlocal inventories
                if service == 'host:devices-l':
                    inventories += 1
                    if inventories > 1 and len(self.server.commands) == count:
                        self.server.listing = self.server.listing.replace(b'transport_id:7', b'transport_id:8')
                return None
            self.server.override = reply
            result, out = self.run_p1()
            self.assertEqual(result['stop'], 'binding_mismatch')
            self.assertEqual(len(self.server.commands), count)
            self.assertEqual(result['session_profile']['binding']['transport_id'], '7')
            self.assertFalse(result['complete'])
            self.check_hashes(result, out)

    def test_watch_notification_aborts_without_metadata_or_retry(self):
        original = af.FakeSocket.recv
        triggered = False
        def changed(sock, count):
            nonlocal triggered
            if sock.shell and not triggered:
                triggered = True
                next(s for s in self.server.sockets if s.watch).incoming.extend(b'0000')
                af.time.sleep(.02)
            return original(sock, count)
        with mock.patch.object(af.FakeSocket, 'recv', changed):
            result, out = self.run_p1()
        self.assertEqual(result['stop'], 'transport_watch_changed_or_lost')
        self.assertEqual(len(self.server.commands), 1)
        self.assertFalse(result['session_binding_identity_verified'])
        self.check_hashes(result, out)

    def test_scope_rejects_content_reads_and_modes_do_not_establish_access(self):
        parent = p1.metadata(p1.EVIDENCE[0], PARENT)
        nodes = p1.metadata(p1.EVIDENCE[1], NODES)
        self.assertEqual(parent['path'], p1.PARENT)
        self.assertEqual(nodes[0]['major'], 179)
        self.assertEqual(nodes[0]['minor'], 1)
        self.assertTrue(all(not x['content_read'] and not x['read_access_established'] for x in nodes))
        with self.assertRaises(cp.Refusal):
            p1.validate(cp.Operation('other', '/system/bin/toybox cat /dev/block/by-name/x'), NODES, self.profile)
        for data in [b'', PARENT[:-1], PARENT.replace(b'4096', b'9'*20)]:
            with self.assertRaises(cp.Refusal):
                p1.metadata(p1.EVIDENCE[0], data)


if __name__ == '__main__':
    unittest.main()
