# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only local evidence hashes; size agreement and hash agreement are separate.

This does not parse PDFs or authenticate a publisher. The catalog supplies
reference metadata, not trusted executable instructions. No network access.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys


MAX_DOCUMENT_BYTES = 32 * 1024 * 1024


def hash_document(path):
    """Hash a bounded regular file, rejecting replacement or concurrent edits."""
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or not 1 <= before.st_size <= MAX_DOCUMENT_BYTES:
        raise ValueError('evidence must be a regular file within size bounds')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0)
    flags |= getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or
                (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)):
            raise ValueError('evidence changed before opening')
        digest = hashlib.sha256()
        remaining = opened.st_size
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError('evidence truncated while hashing')
            digest.update(chunk)
            remaining -= len(chunk)
        if stream.read(1):
            raise ValueError('evidence grew while hashing')
        after = os.fstat(stream.fileno())
        if (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('evidence changed while hashing')
    return opened.st_size, digest.hexdigest()


def inventory(root, catalog, acquisition):
    root = root.resolve(strict=True)
    documents = catalog['documents']
    if not isinstance(documents, list) or not 1 <= len(documents) <= 256:
        raise ValueError('invalid document count')
    logs = {}
    for entry in acquisition['files']:
        name = entry['relative_path']
        if name in logs:
            raise ValueError('duplicate acquisition path')
        logs[name] = entry
    seen, results = set(), []
    for entry in documents:
        name = entry['relative_path']
        relative = PurePosixPath(name)
        if '\\' in name or ':' in name or relative.is_absolute() or '..' in relative.parts or \
                not relative.parts or relative.parts[0] != 'pdfs' or relative.suffix != '.pdf':
            raise ValueError('unsafe evidence path')
        if name in seen or name not in logs:
            raise ValueError('duplicate catalog path or missing acquisition record')
        seen.add(name)
        path = (root / name).resolve(strict=True)
        if root not in path.parents or not path.is_file():
            raise ValueError('evidence path escapes root or is not a file')
        size, digest = hash_document(path)
        expected_hash, expected_size = entry.get('sha256'), entry.get('size_bytes')
        if expected_hash is not None and not re.fullmatch('[0-9a-fA-F]{64}', expected_hash):
            raise ValueError('invalid reference digest')
        if expected_size is not None and (type(expected_size) is not int or expected_size <= 0):
            raise ValueError('invalid reference size')
        prior = logs[name]
        results.append({'file': name, 'bytes': size, 'sha256': digest,
            'published_sha256': expected_hash, 'published_bytes': expected_size,
            'hash_matches_reference': digest == expected_hash.lower() if expected_hash else None,
            'size_matches_reference': size == expected_size if expected_size is not None else None,
            'size_delta': size-expected_size if expected_size is not None else None,
            'matches_acquisition_hash': digest == prior.get('sha256'),
            'matches_acquisition_size': size == prior.get('bytes'),
            'acquisition_classification': prior.get('verification'),
            'source_url': entry.get('url')})
    if seen != set(logs):
        raise ValueError('uncatalogued acquisition records')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args()
    try:
        results = inventory(args.root,
            json.loads((args.root/'reference_catalog.json').read_text(encoding='utf-8')),
            json.loads((args.root/'download_results.json').read_text(encoding='utf-8')))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'inventory failed: {exc}', file=sys.stderr)
        sys.exit(2)
    print(json.dumps(results, indent=2))
