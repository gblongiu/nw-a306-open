# SPDX-License-Identifier: GPL-2.0-or-later
"""KC1 synthetic transport only; real sockets and process constructors blocked."""
import copy
import gzip
import io
import struct
import unittest
from unittest import mock

import test_adb_readonly as af
import acquire_kernel_config as kc

cp = af.cp
HEADER = b"#\n# Automatically generated file; DO NOT EDIT.\n# Linux/arm64 4.19.157-perf+ Kernel Configuration\n#\n"
CONFIG = HEADER + b"# CONFIG_KEXEC is not set\nCONFIG_IKCONFIG=y\nCONFIG_IKCONFIG_PROC=y\n"


def packed(text=CONFIG): return gzip.compress(text, mtime=0)


def padded_gzip(size):
    data = packed()
    header = bytearray(data[:10]); header[3] |= 16  # Legal gzip FCOMMENT.
    return bytes(header) + b"p" * (size-len(data)-1) + b"\0" + data[10:]


class KernelConfigTests(unittest.TestCase):
    setUp = af.AdapterTests.setUp
    check_hashes = af.AdapterTests.check_hashes

    def approval(self, output):
        return dict(approved=True, stage="KC1", plan_sha256=cp.sha(cp.canonical(kc.plan())),
                    profile_sha256=cp.sha(cp.canonical(self.profile)), output=str(output.absolute()))

    def capture(self, data=None):
        self.counter += 1
        out = self.root / f"kc1-{self.counter}"
        self.server.fragment = 4096
        self.server.values[kc.READ.remote] = packed() if data is None else data
        result = kc.run(self.approval(out), out, self.profile, connector=self.server)
        return result, out

    def respond_read(self, frames):
        def override(service, sock):
            if service == "shell,v2,raw:" + kc.READ.remote:
                sock.shell = True; self.server.commands.append(service)
                return b"OKAY" + frames
            return None
        self.server.override = override

    def test_fixed_single_read_identity_bookends_and_integrity(self):
        self.assertEqual(len(kc.OPERATIONS), 23)
        self.assertEqual(kc.OPERATIONS[:11], cp.IDENTITY)
        self.assertEqual(kc.OPERATIONS[-11:], cp.OPERATIONS[-11:])
        self.assertEqual(kc.READ.remote, "/system/bin/toybox head -c 262145 /proc/config.gz")
        self.assertEqual((kc.READ.cap, kc.READ.timeout_ms), (262144, 5000))
        result, out = self.capture()
        self.assertTrue(result["complete"], result["stop"])
        self.assertTrue(result["session_binding_identity_verified"])
        self.assertFalse(result["physical_evidence"])
        self.assertEqual(self.server.commands.count("shell,v2,raw:" + kc.READ.remote), 1)
        self.assertEqual(self.server.stdin_closes, 23)
        self.assertEqual((out / "11-stdout.bin").read_bytes(), packed())
        self.assertEqual(result["artifact"]["symbols"], {"CONFIG_KEXEC":"n", "CONFIG_KEXEC_FILE":"not_present",
                         "CONFIG_IKCONFIG":"y", "CONFIG_IKCONFIG_PROC":"y"})
        self.assertTrue(result["artifact"]["next_action"].startswith("stop_ordinary"))
        self.check_hashes(result, out)

    def test_enabled_missing_and_file_loader_are_distinct(self):
        result = kc.inspect_config(packed(CONFIG.replace(b"# CONFIG_KEXEC is not set", b"CONFIG_KEXEC=y")))
        self.assertTrue(result["next_action"].startswith("assess_legitimate"))
        result = kc.inspect_config(packed(HEADER+b"CONFIG_KEXEC_FILE=y\nCONFIG_IKCONFIG=m\n"))
        self.assertEqual(result["symbols"]["CONFIG_KEXEC"], "not_present")
        self.assertTrue(result["next_action"].startswith("unresolved"))
        self.assertFalse(result["privilege_or_execution_proved"])

    def test_missing_and_permission_denial_stop_without_bookends_or_retry(self):
        for message, reason in ((b"No such file or directory\n", "command_failed"),
                                (b"Permission denied\n", "inaccessible")):
            with self.subTest(reason=reason):
                self.respond_read(af.frame(2,message)+af.frame(3,b"\1"))
                before=len(self.server.commands)
                result,out=self.capture()
                self.assertEqual(result["stop"], reason)
                self.assertEqual(len(self.server.commands)-before,12)
                self.assertNotIn("artifact",result)
                self.assertEqual((out/'11-stderr.bin').read_bytes(),message)
                self.check_hashes(result,out)

    def test_truncated_corrupt_trailing_and_multiple_gzip_members(self):
        badcrc=bytearray(packed()); badcrc[-8]^=1
        badsize=bytearray(packed()); badsize[-4]^=1
        cases=[(packed()[:-1],"truncated_gzip"),(bytes(badcrc),"invalid_gzip_or_crc"),
               (bytes(badsize),"invalid_gzip_or_crc"),(b"garbage","invalid_gzip_or_crc"),
               (packed()+b"\0","trailing_gzip_data_or_members"),
               (packed()+packed(),"trailing_gzip_data_or_members")]
        for data,reason in cases:
            with self.subTest(reason=reason):
                result,out=self.capture(data)
                self.assertEqual(result["stop"],reason)
                self.assertEqual(len(result["observations"]),12)
                self.assertEqual((out/'11-stdout.bin').read_bytes(),data)
                self.assertNotIn('artifact',result)

    def test_malformed_configuration_and_target_values_rejected(self):
        for raw in (b'',b'hello\n',CONFIG[:-1],CONFIG+b'garbage\n',CONFIG+b'CONFIG_BAD=?\n',
                    CONFIG+b'# CONFIG_FOO is maybe set\n',CONFIG+b'CONFIG_X="unterminated\n',
                    CONFIG+b'CONFIG_KEXEC=y\n',CONFIG.replace(b'CONFIG_IKCONFIG=y',b'CONFIG_IKCONFIG="yes"'),
                    CONFIG.replace(b'is not set',b'is not set\0'),
                    HEADER+b'CONFIG_KEXEC=m\n',HEADER+b'CONFIG_X="\xff"\n'):
            with self.subTest(raw=raw[-40:]), self.assertRaises(cp.Refusal): kc.inspect_config(packed(raw))

    def test_exact_compressed_cap_and_one_byte_overflow(self):
        result,_=self.capture(padded_gzip(kc.MAX_COMPRESSED))
        self.assertTrue(result['complete'],result['stop'])
        for size in (kc.MAX_COMPRESSED+1,kc.MAX_COMPRESSED+2):
            result,out=self.capture(padded_gzip(size))
            self.assertEqual(result['stop'],'stream_byte_limit')
            self.assertLessEqual((out/'11-stdout.bin').stat().st_size,kc.MAX_COMPRESSED+1)
            self.assertNotIn('artifact',result)
        self.respond_read(af.frame(1,b'x'*kc.MAX_COMPRESSED)+af.frame(1,b'x')+af.frame(3,b'\0'))
        result,out=self.capture()
        self.assertEqual(result['stop'],'stream_byte_limit')
        self.assertEqual((out/'11-stdout.bin').stat().st_size,kc.MAX_COMPRESSED+1)
        self.check_hashes(result,out)

    def test_expansion_bound_before_full_allocation(self):
        base=CONFIG+b'# '
        raw=base+b'x'*(kc.MAX_EXPANDED-len(base)-1)+b'\n'
        self.assertEqual(kc.inspect_config(packed(raw))['expanded_bytes'],kc.MAX_EXPANDED)
        result,_=self.capture(packed(raw+b'# x\n'))
        self.assertEqual(result['stop'],'expanded_config_byte_limit')
        self.assertNotIn('artifact',result)

    def test_initial_identity_failure_prevents_read(self):
        self.server.values[cp.IDENTITY[0].remote]=b'0\n'
        result,_=self.capture()
        self.assertEqual(result['stop'],'identity mismatch: uid')
        self.assertEqual(len(result['observations']),1)
        self.assertNotIn('shell,v2,raw:'+kc.READ.remote,self.server.commands)

    def test_ending_identity_failure_keeps_raw_but_no_promoted_result(self):
        calls=0
        def change(service,sock):
            nonlocal calls
            if service=='shell,v2,raw:'+cp.IDENTITY[0].remote:
                calls+=1
                if calls==2:
                    sock.shell=True;self.server.commands.append(service)
                    return b'OKAY'+af.frame(1,b'0\n')+af.frame(3,b'\0')
            return None
        self.server.override=change
        result,out=self.capture()
        self.assertEqual(result['stop'],'identity mismatch: uid')
        self.assertEqual((out/'11-stdout.bin').read_bytes(),packed())
        self.assertNotIn('artifact',result)

    def test_current_id_once_original_profile_immutable(self):
        original=copy.deepcopy(self.profile)
        self.server.tid=8
        self.server.listing=self.server.listing.replace(b'transport_id:7',b'transport_id:8')
        result,_=self.capture()
        self.assertTrue(result['complete'],result['stop'])
        self.assertEqual(result['session_profile']['binding']['transport_id'],'8')
        self.assertEqual(self.profile,original)
        self.assertEqual(result['expected_profile'],original)

    def test_wrong_serial_usb_and_mid_session_binding_stop(self):
        self.server.listing=self.server.listing.replace(self.profile['binding']['serial'].encode(),b'OTHER')
        result,_=self.capture()
        self.assertFalse(result['complete']);self.assertFalse(self.server.commands)
        self.server=af.FakeServer(self.profile);self.server.tid=8
        result,_=self.capture()
        self.assertEqual(result['stop'],'usb_transport_mismatch');self.assertFalse(self.server.commands)
        self.server=af.FakeServer(self.profile)
        def change(service,sock):
            if service=='shell,v2,raw:'+kc.READ.remote:
                self.server.tid=8
                self.server.listing=self.server.listing.replace(b'transport_id:7',b'transport_id:8')
            return None
        self.server.override=change
        result,_=self.capture()
        self.assertEqual(result['stop'],'binding_mismatch')
        self.assertNotIn('artifact',result)
        self.assertEqual(len(self.server.commands),12)

    def test_tracker_disconnect_and_partial_binary_preservation(self):
        original=af.FakeSocket.recv
        def disconnect(sock,count):
            if sock.watch and sock.watch_initial_done:return b''
            return original(sock,count)
        with mock.patch.object(af.FakeSocket,'recv',disconnect): result,_=self.capture()
        self.assertFalse(result['complete']);self.assertNotIn('artifact',result)
        self.assertNotIn('shell,v2,raw:'+kc.READ.remote,self.server.commands)
        self.server=af.FakeServer(self.profile)
        self.respond_read(af.frame(1,packed()[:25]))
        result,out=self.capture()
        self.assertEqual(result['stop'],'truncated_protocol')
        self.assertEqual((out/'11-stdout.bin').read_bytes(),packed()[:25])

    def test_read_timeout_and_total_wire_limit(self):
        original=af.ar.Session.wire
        def short(session,label,timeout_ms=5000):
            return original(session,label,1 if label=='shell-11' else timeout_ms)
        self.respond_read(b'');self.server.hang=True
        with mock.patch.object(af.ar.Session,'wire',short): result,_=self.capture()
        self.assertEqual(result['stop'],'timeout');self.assertNotIn('artifact',result)
        self.server=af.FakeServer(self.profile)
        original_plan=kc.plan
        def limited():
            p=original_plan();p['wire_cap']=128;return p
        with mock.patch.object(kc,'plan',limited): result,_=self.capture()
        self.assertEqual(result['stop'],'session_byte_limit')

    def test_final_tracker_race_prevents_artifact_promotion(self):
        original=kc.Acquisition.check
        def late_change(session):
            original(session)
            records=session.manifest['observations']
            if len(records)==23 and records[-1]['complete']:
                session.changed.set()
        with mock.patch.object(kc.Acquisition,'check',late_change): result,out=self.capture()
        self.assertEqual(result['stop'],'transport_watch_changed_or_lost')
        self.assertFalse(result['complete']);self.assertNotIn('artifact',result)
        self.assertEqual((out/'11-stdout.bin').read_bytes(),packed())

    def test_unknown_service_and_overlarge_frame_header(self):
        session=kc.Acquisition(self.root,self.server,af.threading.Event());session.profile=self.profile
        for service in ('host:kill','shell,v2,raw:/system/bin/toybox cat /proc/config.gz',
                        'shell,v2,raw:'+kc.READ.remote+'; reboot'):
            with self.assertRaises(cp.Refusal):session.allow(service)
        self.respond_read(struct.pack('<BI',1,2**32-1))
        result,out=self.capture()
        self.assertEqual(result['stop'],'stream_byte_limit')
        self.assertEqual((out/'11-stdout.bin').stat().st_size,0)

    def test_false_stale_mismatched_approvals_and_reuse_never_connect(self):
        for key,value in (('approved',False),('stage','P1'),('plan_sha256','bad'),
                          ('profile_sha256','bad'),('output','elsewhere')):
            out=self.root/key;approval=self.approval(out);approval[key]=value
            with self.assertRaises(cp.Refusal):kc.run(approval,out,self.profile,connector=self.server)
        self.assertFalse(self.server.requests)
        result,out=self.capture();before=len(self.server.requests)
        with self.assertRaises(FileExistsError):kc.run(self.approval(out),out,self.profile,connector=self.server)
        self.assertEqual(len(self.server.requests),before)

    def test_default_cli_and_unapproved_arguments_are_inert(self):
        with mock.patch.object(af.ar,'connect_existing',side_effect=AssertionError('forbidden')):
            with mock.patch('sys.stdout',io.StringIO()):
                self.assertEqual(kc.main([]),0)
                self.assertEqual(kc.main(['--profile','anything']),2)
                self.assertEqual(kc.main(['--run-approved']),2)
        self.assertFalse(self.server.requests)


if __name__ == '__main__': unittest.main()
