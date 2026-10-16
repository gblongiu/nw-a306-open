# SPDX-License-Identifier: GPL-2.0-or-later
"""SK1 synthetic smart-socket/sync tests; real sockets/processes forbidden."""
import copy
import io
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import socket
import struct
import types
import unittest
from unittest import mock

import test_adb_readonly as af
import acquire_sony_ota_material as sk

cp = af.cp
MATERIAL = b'SK1\0' + struct.pack('<III', 0, 32, 16) + bytes(range(1, 33)) + bytes(range(101, 117))


class SyncSocket(af.FakeSocket):
    def __init__(self, server):
        super().__init__(server)
        self.sync = False
        self.sync_data = bytearray()
        self.cut = False

    def send(self, data):
        if not self.sync: return super().send(data)
        if self.cut: raise socket.timeout()
        size = min(len(data), self.server.fragment)
        if self.server.partial and data.startswith(b'DATA'):
            size = min(size, 17); self.cut = True
        self.pending.extend(data[:size])
        while len(self.pending) >= 8:
            kind, count = struct.unpack_from('<4sI', self.pending)
            length = 0 if kind in (b'DONE', b'QUIT') else count
            if len(self.pending) < 8 + length: break
            payload = bytes(self.pending[8:8+length]); del self.pending[:8+length]
            self.server.sync_packets.append((kind, count, payload))
            if kind == b'SEND':
                assert payload == (sk.REMOTE_DEX+',384').encode()
            elif kind == b'DATA': self.sync_data.extend(payload)
            elif kind == b'DONE':
                assert count == 0
                self.incoming.extend(self.server.sync_response)
            elif kind == b'QUIT': assert count == 0
            else: raise AssertionError('unreviewed sync request')
        return size


class SyncServer(af.FakeServer):
    def __init__(self, profile):
        super().__init__(profile)
        self.fragment = 4096
        self.partial = False
        self.sync_packets = []
        self.sync_response = b'OKAY'+struct.pack('<I',0)
        self.values.update({
            sk.PARENT.remote:b'drwxrwx--x 4 shell shell u:object_r:shell_data_file:s0 4096 2026-10-15 12:00 /data/local/tmp\n',
            sk.APP.remote:b'-rwxr-xr-x 1 root shell u:object_r:zygote_exec:s0 32768 2026-10-15 12:00 /system/bin/app_process64\n',
            sk.MKDIR.remote:b'',sk.HASH.remote:(sk.DEX_SHA256+'  '+sk.REMOTE_DEX+'\n').encode(),
            sk.HELPER.remote:MATERIAL,sk.REMOVE.remote:b'',sk.RMDIR.remote:b''})

    def __call__(self, deadline):
        sock = SyncSocket(self); self.sockets.append(sock); return sock

    def respond(self, service, sock):
        if service == 'sync:':
            sock.sync = True; return b'OKAY'
        return super().respond(service, sock)


class SonyMaterialTests(unittest.TestCase):
    def setUp(self):
        af.AdapterTests.setUp(self)
        self.synthetic_dex()
        self.server = SyncServer(self.profile)

    def synthetic_dex(self):
        dex=self.root/'synthetic.dex';data=b'dex\n035\0synthetic helper bytes';dex.write_bytes(data)
        for key,value in (('DEX',dex),('DEX_SIZE',len(data)),('DEX_SHA256',cp.sha(data))):
            patch=mock.patch.object(sk,key,value);patch.start();self.addCleanup(patch.stop)

    check_hashes = af.AdapterTests.check_hashes

    def approval(self, output):
        return dict(approved=True,stage='SK1',plan_sha256=cp.sha(cp.canonical(sk.plan())),
                    bundle_sha256='e'*64,
                    profile_sha256=cp.sha(cp.canonical(self.profile)),output=str(output.absolute()))

    def capture(self):
        self.counter += 1
        out = self.root/f'sk1-{self.counter}'
        result = sk.run(self.approval(out),out,self.profile,connector=self.server)
        self.check_hashes(result,out)
        return result,out

    def response(self, op, frames):
        def override(service,sock):
            if service == 'shell,v2,raw:'+op.remote:
                sock.shell=True; self.server.commands.append(service)
                return b'OKAY'+frames
            return None
        self.server.override=override

    def assert_stopped(self,result,last):
        self.assertFalse(result['complete']); self.assertFalse(result['material_promoted'])
        self.assertNotIn('artifact',result); self.assertNotIn('candidate_artifact',result)
        self.assertEqual(result['observations'][-1]['id'],last.id)
        self.assertEqual(self.server.commands.count('shell,v2,raw:'+sk.HELPER.remote),int(last in sk.OPERATIONS[15:]))

    def test_success_exact_upload_one_business_attempt_bookends_private_record(self):
        result,out=self.capture()
        self.assertTrue(result['complete'],result['stop'])
        self.assertFalse(result['physical_evidence']); self.assertFalse(result['material_promoted'])
        self.assertTrue(result['host_guard_pending'])
        self.assertEqual(len(result['observations']),29)
        self.assertEqual(self.server.stdin_closes,29)
        self.assertEqual([p[0] for p in self.server.sync_packets],[b'SEND',b'DATA',b'DONE',b'QUIT'])
        self.assertEqual(self.server.sync_packets[1][2],sk.DEX.read_bytes())
        self.assertEqual(self.server.requests.count('sync:'),1)
        self.assertEqual(self.server.commands.count('shell,v2,raw:'+sk.HELPER.remote),1)
        upload=next(r for r in result['connections'] if r['label']=='helper-upload')
        self.assertEqual(upload['requests'],['host:tport:serial:'+self.profile['binding']['serial'],'sync:'])
        self.assertFalse(result['temporary_paths_may_remain'])
        self.assertEqual((out/'15-stdout.bin').read_bytes(),MATERIAL)
        public=json.dumps(result)
        self.assertNotIn(MATERIAL[16:].hex(),public)
        self.assertNotIn(list(MATERIAL[16:48]).__repr__(),public)
        self.assertEqual(result['candidate_artifact']['key_bytes'],32)

    def test_denied_HAL_and_cleanup_errors_stop_without_later_requests(self):
        for op in (sk.HELPER,sk.REMOVE,sk.RMDIR):
            with self.subTest(op=op.id):
                self.server=SyncServer(self.profile)
                self.response(op,af.frame(2,b'Permission denied\n')+af.frame(3,b'\1'))
                result,out=self.capture()
                self.assertEqual(result['stop'],'inaccessible');self.assert_stopped(result,op)
                self.assertEqual(self.server.commands[-1],'shell,v2,raw:'+op.remote)
                if op!=sk.HELPER:self.assertEqual((out/'15-stdout.bin').read_bytes(),MATERIAL)

    def test_existing_temporary_path_stops_before_upload_and_never_removes_it(self):
        self.response(sk.MKDIR,af.frame(2,b'File exists\n')+af.frame(3,b'\1'))
        result,_=self.capture()
        self.assert_stopped(result,sk.MKDIR)
        self.assertEqual(result['stop'],'command_failed')
        self.assertNotIn('sync:',self.server.requests)
        self.assertEqual(len(self.server.commands),14)

    def test_malformed_material_exact_caps_truncation_exit_and_stderr(self):
        cases=[b'',MATERIAL[:-1],b'BAD!'+MATERIAL[4:],MATERIAL[:4]+struct.pack('<III',1,32,16)+MATERIAL[16:],
               MATERIAL[:8]+struct.pack('<II',16,32)+MATERIAL[16:],MATERIAL[:16]+bytes(32)+MATERIAL[48:]]
        for data in cases:
            with self.subTest(length=len(data)):
                self.server=SyncServer(self.profile);self.server.values[sk.HELPER.remote]=data
                result,out=self.capture();self.assert_stopped(result,sk.HELPER)
                self.assertEqual((out/'15-stdout.bin').read_bytes(),data)
        for frames,reason in (
            (af.frame(1,MATERIAL+b'x')+af.frame(3,b'\0'),'stream_byte_limit'),
            (struct.pack('<BI',1,2**32-1),'stream_byte_limit'),
            (af.frame(1,MATERIAL[:20]),'truncated_protocol'),
            (af.frame(1,MATERIAL)+af.frame(3,b'\1'),'command_failed'),
            (af.frame(1,MATERIAL)+af.frame(2,b'x')+af.frame(3,b'\0'),'unexpected_stderr'),
            (af.frame(1,MATERIAL)+af.frame(3,b'\0')+b'x','trailing_protocol_data')):
            self.server=SyncServer(self.profile);self.response(sk.HELPER,frames)
            result,_=self.capture();self.assertEqual(result['stop'],reason);self.assert_stopped(result,sk.HELPER)

    def test_partial_upload_is_preserved_never_resent_or_cleaned(self):
        self.server.partial=True
        result,out=self.capture()
        self.assertEqual(result['stop'],'uncertain_send')
        self.assert_stopped(result,sk.MKDIR)
        self.assertEqual(self.server.requests.count('sync:'),1)
        self.assertEqual([p[0] for p in self.server.sync_packets],[b'SEND'])
        raw=next(r['tx'] for r in result['connections'] if r['label']=='helper-upload')
        self.assertTrue((out/raw['file']).read_bytes().endswith(b'DATA'+struct.pack('<I',sk.DEX_SIZE)+sk.DEX.read_bytes()[:9]))

    def test_sync_denial_malformed_status_partial_response_and_trailing_bytes(self):
        for response,reason in ((b'FAIL'+struct.pack('<I',6)+b'secret','sync_denied'),
                                (b'FAIL'+struct.pack('<I',4097),'sync_failure_message_limit'),
                                (b'OKAY'+struct.pack('<I',1),'invalid_sync_response'),
                                (b'XXXX'+bytes(4),'invalid_sync_response'),
                                (b'OKAY','truncated_protocol'),
                                (b'OKAY'+bytes(4)+b'x','trailing_protocol_data')):
            self.server=SyncServer(self.profile);self.server.sync_response=response
            result,_=self.capture();self.assertEqual(result['stop'],reason)
            self.assert_stopped(result,sk.MKDIR)
            self.assertNotIn('secret',json.dumps(result))

    def test_upload_and_helper_timeouts_stop_without_cleanup(self):
        original=sk.Acquisition.wire
        for label in ('helper-upload','shell-15'):
            self.server=SyncServer(self.profile)
            if label=='helper-upload':self.server.sync_response=b''
            else:self.response(sk.HELPER,b'')
            original_recv=SyncSocket.recv
            def wait(sock,count):
                if not sock.incoming and ((label=='helper-upload' and sock.sync) or (label=='shell-15' and sock.shell and self.server.commands[-1]=='shell,v2,raw:'+sk.HELPER.remote)):
                    raise socket.timeout()
                return original_recv(sock,count)
            def short(session,name,timeout_ms=5000):return original(session,name,50 if name==label else timeout_ms)
            with mock.patch.object(sk.Acquisition,'wire',short),mock.patch.object(SyncSocket,'recv',wait):result,_=self.capture()
            self.assertEqual(result['stop'],'timeout')
            self.assertEqual(self.server.requests.count('sync:'),1)
            self.assertNotIn('shell,v2,raw:'+sk.REMOVE.remote,self.server.commands)

    def test_wrong_identities_before_and_after_preserve_secret_no_promotion(self):
        self.server.values[cp.IDENTITY[0].remote]=b'0\n'
        result,_=self.capture();self.assertEqual(len(result['observations']),1)
        self.assertNotIn('sync:',self.server.requests)
        self.server=SyncServer(self.profile);calls=0
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
        self.assertEqual((out/'15-stdout.bin').read_bytes(),MATERIAL)
        self.assertFalse(result['material_promoted']);self.assertNotIn('candidate_artifact',result)
        self.assertEqual(len(result['observations']),19)

    def test_one_initial_current_id_original_profile_immutable_mid_session_rebinding_forbidden(self):
        original=copy.deepcopy(self.profile)
        self.server.tid=8;self.server.listing=self.server.listing.replace(b'transport_id:7',b'transport_id:8')
        result,_=self.capture();self.assertTrue(result['complete'],result['stop'])
        self.assertEqual(self.profile,original);self.assertEqual(result['session_profile']['binding']['transport_id'],'8')
        self.server=SyncServer(self.profile)
        def change(service,sock):
            if service=='shell,v2,raw:'+sk.HELPER.remote:
                self.server.listing=self.server.listing.replace(b'transport_id:7',b'transport_id:8');self.server.tid=8
            return None
        self.server.override=change
        result,out=self.capture();self.assertEqual(result['stop'],'binding_mismatch')
        self.assertEqual((out/'15-stdout.bin').read_bytes(),MATERIAL)
        self.assertNotIn('shell,v2,raw:'+sk.REMOVE.remote,self.server.commands)

    def test_atomic_upload_selection_and_transport_watch_loss(self):
        original=SyncServer.respond
        selections=0
        def wrong(server,service,sock):
            nonlocal selections
            if service.startswith('host:tport:serial:'):
                selections+=1
                if selections==15:return b'OKAY'+struct.pack('<Q',8)
            return original(server,service,sock)
        with mock.patch.object(SyncServer,'respond',wrong):result,_=self.capture()
        self.assertEqual(result['stop'],'selected_transport_mismatch');self.assertNotIn('sync:',self.server.requests)
        self.server=SyncServer(self.profile)
        original_recv=SyncSocket.recv
        def lost(sock,count):
            if sock.watch and sock.watch_initial_done:return b''
            return original_recv(sock,count)
        with mock.patch.object(SyncSocket,'recv',lost):result,_=self.capture()
        self.assertFalse(result['complete']);self.assertNotIn('sync:',self.server.requests)

    def test_final_watch_shutdown_race_never_produces_candidate(self):
        original=sk.Acquisition.close
        def close(session):
            original(session);session.changed.set()
        with mock.patch.object(sk.Acquisition,'close',close):result,out=self.capture()
        self.assertFalse(result['complete']);self.assertNotIn('candidate_artifact',result)
        self.assertEqual((out/'15-stdout.bin').read_bytes(),MATERIAL)

    def test_metadata_aliases_and_hash_mismatch_fail_closed(self):
        for op,data in ((sk.PARENT,b'lrwxrwxrwx 1 shell shell u:object_r:shell_data_file:s0 /data/local/tmp -> /elsewhere\n'),
                        (sk.APP,b'not a listing\n'),(sk.HASH,b'wrong hash\n')):
            self.server=SyncServer(self.profile);self.server.values[op.remote]=data
            result,_=self.capture();self.assert_stopped(result,op)

    def test_admission_frozen_dex_and_reuse_never_connect(self):
        for key,value in (('approved',False),('stage','KC1'),('profile_sha256','bad'),('plan_sha256','bad'),('bundle_sha256','bad'),('output','elsewhere')):
            out=self.root/key;a=self.approval(out);a[key]=value
            with self.assertRaises(cp.Refusal):sk.run(a,out,self.profile,connector=self.server)
        self.assertFalse(self.server.requests)
        bad=self.root/'classes.dex';bad.write_bytes(b'dex\nwrong')
        with mock.patch.object(sk,'DEX',bad),self.assertRaises(cp.Refusal):
            out=self.root/'bad-dex';sk.run(self.approval(out),out,self.profile,connector=self.server)
        self.assertFalse(self.server.requests)
        result,out=self.capture();before=len(self.server.requests)
        with self.assertRaises(FileExistsError):sk.run(self.approval(out),out,self.profile,connector=self.server)
        self.assertEqual(len(self.server.requests),before)

    def test_cancellation_wire_and_session_deadlines_fail_closed(self):
        original=sk.plan
        for key,value,reason in (('wire_cap',128,'session_byte_limit'),('session_ms',0,'session_timeout')):
            def limited():
                p=original();p[key]=value;return p
            self.server=SyncServer(self.profile)
            with mock.patch.object(sk,'plan',limited):result,_=self.capture()
            self.assertEqual(result['stop'],reason);self.assertNotIn('sync:',self.server.requests)
        event=af.threading.Event();event.set();out=self.root/'cancelled'
        result=sk.run(self.approval(out),out,self.profile,connector=self.server,cancel=event)
        self.assertEqual(result['stop'],'cancelled');self.assertFalse(result['material_promoted'])

    def test_service_allowlist_duplicate_transfer_and_default_CLI(self):
        session=sk.Acquisition(self.root,self.server,af.threading.Event());session.profile=self.profile
        for service in ('sync:','host:kill','shell,v2,raw:'+sk.HELPER.remote+'; reboot'):
            with self.assertRaises(cp.Refusal):session.allow(service)
        session.upload_attempted=True
        with self.assertRaises(cp.Refusal):session.upload(self.profile,b'x')
        with mock.patch.object(af.ar,'connect_existing',side_effect=AssertionError('forbidden')):
            with mock.patch('sys.stdout',io.StringIO()):
                self.assertEqual(sk.main([]),0);self.assertEqual(sk.main(['--run-approved']),2)
        self.assertFalse(self.server.requests)


class EntryTests(unittest.TestCase):
    def setUp(self):
        af.AdapterTests.setUp(self)
        SonyMaterialTests.synthetic_dex(self)
        self.server=SyncServer(self.profile)
        spec=importlib.util.spec_from_file_location('sk1_entry_test',Path(sk.__file__).with_name('run_sony_ota_material_once.py'))
        self.entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.entry)
        self.here=self.root/'package';self.here.mkdir()
        self.entry.HERE=self.here;self.entry.REPO=self.root
        self.out=self.root/'private-evidence'
        self.write('execution-bundle.json',{'files':{'input.txt':cp.sha(b'frozen')}})
        (self.root/'input.txt').write_bytes(b'frozen')
        self.write('reviewed-plan.json',sk.plan())
        path=self.root/'build/m10/authorizations';path.mkdir(parents=True)
        (path/'expected-nwa306-20261014-01.json').write_text(json.dumps(self.profile))
        self.approval=dict(approved=False,stage='SK1',plan_sha256=cp.sha(cp.canonical(sk.plan())),
                           bundle_sha256=cp.sha((self.here/'execution-bundle.json').read_bytes()),
                           profile_sha256=cp.sha(cp.canonical(self.profile)),output=str(self.out.absolute()))
        self.write('approval-proposal.json',self.approval)
        self.write('approval.json',dict(self.approval,approved=True))
        self.owner=dict(confirmed=True,utc=datetime.now(timezone.utc).isoformat(),authorization_text='Synthetic approval only',
                        same_unit=True,normal_stock_android=True,debugging_already_authorized=True,idle_no_update_or_transfer=True)
        self.write('owner-readiness.json',self.owner)
        self.host=mock.Mock()
        patch=mock.patch.dict('sys.modules',{'host_guard':types.SimpleNamespace(check=self.host)})
        patch.start();self.addCleanup(patch.stop)

    def write(self,name,value):
        (self.here/name).write_text(json.dumps(value))

    def invoke(self):
        original=sk.run
        def run(a,o,p):return original(a,o,p,connector=self.server)
        with mock.patch.object(sk,'run',side_effect=run),mock.patch('sys.stdout',io.StringIO()) as stdout:
            code=self.entry.main(['--run-approved'])
        return code,stdout.getvalue()

    def test_default_inert_and_changed_input_false_approval_stale_owner_refuse(self):
        with mock.patch('sys.stdout',io.StringIO()):self.assertEqual(self.entry.main([]),0)
        for mode in ('changed','false','stale','unready'):
            with self.subTest(mode=mode):
                (self.root/'input.txt').write_bytes(b'changed' if mode=='changed' else b'frozen')
                self.write('approval.json',dict(self.approval,approved=mode!='false'))
                owner=dict(self.owner)
                if mode=='stale':owner['utc']=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()
                if mode=='unready':owner['same_unit']=False
                self.write('owner-readiness.json',owner)
                with self.assertRaises(cp.Refusal):self.invoke()
                self.assertFalse((self.here/'live-attempt.json').exists())
        self.assertFalse(self.host.mock_calls);self.assertFalse(self.server.requests)

    def test_preflight_failure_consumes_attempt_and_prevents_communication(self):
        self.host.side_effect=cp.Refusal('synthetic host failure')
        with self.assertRaises(cp.Refusal):self.invoke()
        self.assertTrue((self.here/'live-attempt.json').exists());self.assertFalse(self.server.requests)
        with self.assertRaises(cp.Refusal):self.invoke()
        self.assertEqual(self.host.call_count,1)

    def test_bundle_bytes_are_bound_to_approval(self):
        path=self.here/'execution-bundle.json'
        path.write_text(path.read_text()+'\n')
        with self.assertRaises(cp.Refusal):self.invoke()
        self.assertFalse(self.server.requests);self.assertFalse(self.host.mock_calls)
        self.assertFalse((self.here/'live-attempt.json').exists())

    def test_host_postflight_failure_preserves_raw_secret_and_prevents_promotion(self):
        self.host.side_effect=[None,cp.Refusal('synthetic host failure')]
        code,stdout=self.invoke();self.assertEqual(code,1)
        result=json.loads((self.out/'manifest.json').read_text())
        self.assertEqual(result['stop'],'host_postflight_failed');self.assertFalse(result['material_promoted'])
        self.assertNotIn('artifact',result)
        self.assertEqual((self.out/'15-stdout.bin').read_bytes(),MATERIAL)
        self.assertTrue((self.out/'adapter-manifest.json').exists())
        self.assertNotIn(MATERIAL[16:].hex(),stdout)
        self.assertEqual(self.host.call_args_list,[mock.call('before'),mock.call('after')])

    def test_success_promoted_only_after_host_postflight_and_entry_cannot_retry(self):
        code,stdout=self.invoke();self.assertEqual(code,0)
        result=json.loads((self.out/'manifest.json').read_text())
        self.assertTrue(result['material_promoted']);self.assertTrue(result['host_prerequisites_passed'])
        self.assertFalse(result['host_guard_pending']);self.assertIn('artifact',result)
        self.assertFalse(json.loads((self.out/'adapter-manifest.json').read_text())['material_promoted'])
        before=len(self.server.requests)
        with self.assertRaises(cp.Refusal):self.invoke()
        self.assertEqual(len(self.server.requests),before);self.assertNotIn(MATERIAL[16:].hex(),stdout)


if __name__=='__main__':unittest.main()
