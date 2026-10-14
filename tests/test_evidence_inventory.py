# SPDX-License-Identifier: GPL-2.0-or-later
"""Deterministic metadata conflicts and safe local inventory paths."""
import hashlib
import io
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from evidence_inventory import hash_document, inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root/'pdfs/a.pdf'
        self.path.parent.mkdir()
        self.data = b'synthetic hash fixture; no PDF structure claim\n'
        self.path.write_bytes(self.data)
        digest = hashlib.sha256(self.data).hexdigest()
        self.doc = {'relative_path':'pdfs/a.pdf','sha256':digest,'size_bytes':len(self.data)}
        self.log = {'relative_path':'pdfs/a.pdf','sha256':digest,'bytes':len(self.data)}

    def run_inventory(self):
        return inventory(self.root, {'documents':[self.doc]}, {'files':[self.log]})[0]

    def test_exact(self):
        r = self.run_inventory()
        self.assertTrue(r['hash_matches_reference'] and r['size_matches_reference'])

    def test_hash_agreement_with_size_discrepancy(self):
        self.doc['size_bytes'] += 2
        self.log['verification'] = 'parsed_pdf_published_hash_mismatch'
        r = self.run_inventory()
        self.assertTrue(r['hash_matches_reference'])
        self.assertFalse(r['size_matches_reference'])
        self.assertEqual(r['size_delta'], -2)

    def test_genuine_hash_mismatch(self):
        self.doc['sha256'] = '0'*64
        self.assertFalse(self.run_inventory()['hash_matches_reference'])

    def test_missing_reference_hash(self):
        self.doc.pop('sha256')
        self.assertIsNone(self.run_inventory()['hash_matches_reference'])

    def test_changed_acquisition(self):
        self.path.write_bytes(b'changed')
        r = self.run_inventory()
        self.assertFalse(r['matches_acquisition_hash'] or r['matches_acquisition_size'])

    def test_unsafe_paths(self):
        for name in ['../a.pdf','/pdfs/a.pdf','pdfs/../a.pdf','pdfs\\a.pdf','other/a.pdf', 'pdfs/a.pdf:stream.pdf']:
            self.doc['relative_path'] = name
            with self.assertRaises(ValueError):
                self.run_inventory()

    def test_duplicates_and_missing_records(self):
        with self.assertRaises(ValueError):
            inventory(self.root,{'documents':[self.doc,self.doc]},{'files':[self.log]})
        with self.assertRaises(ValueError):
            inventory(self.root,{'documents':[self.doc]},{'files':[]})

    def test_missing_file_and_invalid_metadata(self):
        self.doc['sha256']='not a digest'
        with self.assertRaises(ValueError):
            self.run_inventory()
        self.doc['sha256']='0'*64
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            self.run_inventory()
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[1] / 'tools/evidence_inventory.py'),
             '--root', str(self.root)], capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')
        self.assertIn(b'inventory failed:', result.stderr)
        self.assertNotIn(b'Traceback', result.stderr)

    def test_nonregular_file_rejected_before_open(self):
        for mode in (stat.S_IFCHR, stat.S_IFBLK, stat.S_IFIFO):
            with self.subTest(mode=mode), patch.object(Path, 'stat', return_value=SimpleNamespace(st_mode=mode)), patch('evidence_inventory.os.open') as opener:
                with self.assertRaises(ValueError):
                    hash_document(self.path)
                opener.assert_not_called()

    def test_growth_and_truncation_rejected(self):
        original = self.path.stat()
        for data in (self.data[:-1], self.data + b'growth'):
            stream = io.BytesIO(data)
            stream.fileno = lambda: 123
            with self.subTest(length=len(data)), patch('evidence_inventory.os.open', return_value=123), patch('evidence_inventory.os.fdopen', return_value=stream), patch('evidence_inventory.os.fstat', return_value=original):
                with self.assertRaisesRegex(ValueError, 'truncated|grew'):
                    hash_document(self.path)

    def test_mutation_during_hash_rejected(self):
        original = self.path.stat()
        changed = SimpleNamespace(st_size=original.st_size, st_mtime_ns=original.st_mtime_ns + 1)
        with patch('evidence_inventory.os.fstat', side_effect=[original, changed]):
            with self.assertRaisesRegex(ValueError, 'changed while hashing'):
                hash_document(self.path)


if __name__ == '__main__':
    unittest.main()
