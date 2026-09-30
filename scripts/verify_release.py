#!/usr/bin/env python3
"""Check manifest bytes and file set; this is not scientific validation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/'RELEASE_MANIFEST.json').read_text())
for entry in manifest['files']:
    path = ROOT/entry['path']
    assert path.is_file(), entry['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], entry['path']
print(f"PASS {len(manifest['files'])} published file hashes. Technical integrity only.")
