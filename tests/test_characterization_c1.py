# SPDX-License-Identifier: GPL-2.0-or-later
"""C1 fixed-scope integration on injected sockets, with real I/O blocked."""
import copy
import io
import unittest
from unittest import mock

import test_adb_readonly as af

ar, cp = af.ar, af.cp
c1 = ar.c1
PARENT = b"drwxr-x--- 2 system cache u:object_r:cache_file:s0 4096 2026-10-15 01:00 /mnt/icx_cache\n"
TARGET = b"-rw-r--r-- 1 system cache u:object_r:cache_file:s0 1500000000 2026-10-14 12:30 /mnt/icx_cache/NW_WM_FW.zip\n"


class C1Tests(unittest.TestCase):
    check_hashes = af.AdapterTests.check_hashes

    def setUp(self):
        af.AdapterTests.setUp(self)
        self.server.fragment = 65536
        self.server.values.update({c1.EVIDENCE[0].remote:PARENT, c1.EVIDENCE[1].remote:TARGET})

    def approval(self, out):
        return {"approved":True,"stage":"C1","plan_sha256":cp.sha(cp.canonical(ar.plan("C1"))),
                "profile_sha256":cp.sha(cp.canonical(self.profile)),"output":str(out.absolute())}

    def run_c1(self):
        self.counter += 1
        out = self.root/f"c1-{self.counter}"
        return ar.run("C1",self.approval(out),out,self.profile,connector=self.server), out

    def test_fixed_scope_digest_limits_and_inert_default(self):
        policy=ar.plan("C1")
        self.assertEqual(len(policy["operations"]),24)
        self.assertEqual([o.remote for o in c1.EVIDENCE],["/system/bin/toybox ls -ldZ /mnt/icx_cache","/system/bin/toybox ls -ldZ /mnt/icx_cache/NW_WM_FW.zip"])
        self.assertTrue(all(o.cap==4096 and o.timeout_ms==5000 for o in c1.OPERATIONS))
        self.assertEqual(policy["output_cap"],sum(2*o.cap for o in c1.OPERATIONS))
        self.assertEqual(policy["wire_cap"],2097152)
        self.assertEqual(policy["session_ms"],300000)
        self.assertEqual(set(policy["code_sha256"]),{"adb_readonly.py","characterization_plan.py","characterization_transport.py","characterization_c1.py"})
        with mock.patch.object(ar,"connect_existing",side_effect=AssertionError("no live socket")), mock.patch("sys.stdout",io.StringIO()) as output:
            self.assertEqual(ar.main(["--stage","C1"]),0)
            saved=cp.json.loads(output.getvalue()); digest=saved.pop("plan_sha256")
            self.assertEqual(digest,cp.sha(cp.canonical(policy)))
            self.assertEqual(saved,policy)
        self.assertFalse(self.server.requests)

    def test_success_exact_order_atomic_transport_and_evidence_hashes(self):
        result,out=self.run_c1()
        self.assertTrue(result["complete"],result["stop"])
        self.assertEqual(self.server.commands,["shell,v2,raw:"+o.remote for o in c1.OPERATIONS])
        self.assertEqual(self.server.stdin_closes,24)
        self.assertFalse(result["physical_evidence"])
        self.assertTrue(all(o["complete"] for o in result["observations"]))
        self.assertEqual((out/"12-stdout.bin").read_bytes(),TARGET)
        self.check_hashes(result,out)
        self.assertTrue(all(s.closed for s in self.server.sockets))

    def test_parent_invalid_type_or_ambiguous_output_stops_before_target(self):
        for value in [PARENT.replace(b"drwx",b"lrwx"),PARENT.replace(b"drwx",b"-rwx"),PARENT+PARENT,PARENT.replace(b"cache_file:s0",b"?"),PARENT.replace(b"2026-10-15",b"2026-99-99"),PARENT.replace(b"/mnt/icx_cache",b"/another"),PARENT.replace(b"4096",b"bad"),PARENT.replace(b" 2 system",b" 0 system")]:
            self.server.values[c1.EVIDENCE[0].remote]=value
            before=len(self.server.commands)
            result,out=self.run_c1()
            with self.subTest(value=value):
                self.assertFalse(result["complete"])
                self.assertEqual(len(result["observations"]),12)
                self.assertEqual(len(self.server.commands)-before,12)
                self.assertEqual((out/"11-stdout.bin").read_bytes(),value)
                self.check_hashes(result,out)

    def test_target_empty_symlink_directory_or_extra_line_stops_without_end_guards(self):
        for value in [TARGET.replace(b"1500000000",b"0"),b"l"+TARGET[1:],b"d"+TARGET[1:],TARGET+b"extra\n",TARGET.replace(b"NW_WM_FW.zip",b"other.zip"),TARGET.replace(b"12:30",b"25:00")]:
            self.server.values[c1.EVIDENCE[1].remote]=value
            result,out=self.run_c1()
            self.assertFalse(result["complete"])
            self.assertEqual(len(result["observations"]),13)
            self.assertEqual(result["observations"][-1]["id"],c1.EVIDENCE[1].id)
            self.assertEqual((out/"12-stdout.bin").read_bytes(),value)

    def test_denial_absence_and_stderr_preserve_failure_no_retry(self):
        for index,remote in enumerate([o.remote for o in c1.EVIDENCE],11):
            for error,exit in [(b"Permission denied\n",1),(b"No such file or directory\n",1),(b"unexpected warning\n",0)]:
                before=len(self.server.commands)
                def reply(service,sock):
                    if service=="shell,v2,raw:"+remote:
                        sock.shell=True; self.server.commands.append(service)
                        return b"OKAY"+af.frame(2,error)+af.frame(3,bytes([exit]))
                    return None
                self.server.override=reply
                result,out=self.run_c1()
                self.assertFalse(result["complete"])
                self.assertEqual(len(result["observations"]),index+1)
                self.assertEqual(len(self.server.commands)-before,index+1)
                self.assertEqual((out/f"{index:02d}-stderr.bin").read_bytes(),error)
                self.check_hashes(result,out)

    def test_strict_caps_reject_before_capturing_oversized_stream(self):
        for channel in (1,2):
            def reply(service,sock):
                if service=="shell,v2,raw:"+c1.EVIDENCE[0].remote:
                    sock.shell=True; self.server.commands.append(service)
                    return b"OKAY"+af.frame(channel,b"x"*4097)+af.frame(3,b"\0")
                return None
            self.server.override=reply
            result,out=self.run_c1()
            self.assertEqual(result["stop"],"stream_byte_limit")
            self.assertEqual(len(result["observations"]),12)
            self.assertLessEqual((out/"11-stdout.bin").stat().st_size,4096)
            self.assertLessEqual((out/"11-stderr.bin").stat().st_size,4096)

    def test_unapproved_changed_plan_profile_and_scope_never_connect(self):
        for field,value in [("approved",False),("stage","B2"),("plan_sha256","0"*64),("profile_sha256","0"*64),("output","elsewhere")]:
            out=self.root/field; approval=self.approval(out); approval[field]=value
            with self.assertRaises(cp.Refusal):ar.run("C1",approval,out,self.profile,connector=self.server)
            self.assertFalse(out.exists())
        out=self.root/"changed"; approval=self.approval(out)
        with mock.patch.object(c1,"OPERATIONS",c1.OPERATIONS[:-1]),self.assertRaises(cp.Refusal):
            ar.run("C1",approval,out,self.profile,connector=self.server)
        self.assertFalse(self.server.requests)

    def test_binding_and_atomic_transport_changes_prevent_shell(self):
        self.server.listing=self.server.listing.replace(self.profile["binding"]["serial"].encode(),b"other")
        result,_=self.run_c1()
        self.assertEqual(result["stop"],"binding_mismatch")
        self.assertFalse(self.server.commands)
        self.server=af.FakeServer(self.profile)
        self.server.override=lambda s,sock:b"OKAY"+af.struct.pack("<Q",8) if s.startswith("host:tport:serial:") else None
        result,_=self.run_c1()
        self.assertEqual(result["stop"],"selected_transport_mismatch")
        self.assertFalse(self.server.commands)

    def test_metadata_parser_conservative_but_accepts_aligned_output(self):
        parsed=c1.metadata(c1.EVIDENCE[1],TARGET.replace(b" 1 system",b"    1  system"))
        self.assertEqual(parsed["bytes"],1500000000)
        self.assertFalse(parsed["read_access_established"])
        self.assertFalse(parsed["content_read"])
        for data in (b"",TARGET[:-1],TARGET.replace(b"system",b"\x1bsystem"),TARGET.replace(b"1500000000",b"99999999999999999999"),TARGET.replace(b"system",b"\xff")):
            with self.assertRaises(cp.Refusal):c1.metadata(c1.EVIDENCE[1],data)
        with self.assertRaises(cp.Refusal):c1.validate(cp.Operation("other","cat /other"),TARGET,self.profile)


if __name__ == "__main__": unittest.main()
