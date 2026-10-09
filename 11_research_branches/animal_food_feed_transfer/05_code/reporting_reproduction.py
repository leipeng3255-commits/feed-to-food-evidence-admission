"""Explicit source-reproduction mode; never silently substitutes a receipt store."""
import csv
import hashlib
import json
from pathlib import Path

BRANCH = Path(__file__).resolve().parents[1]
ROOT = BRANCH.parents[1]

def source_receipt(path, config, public_reproduction=False):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    relative = str(path.relative_to(config['raw_data_root']))
    if public_reproduction:
        receipts = json.loads((BRANCH/'01_protocol/pdp_source_receipts_20261009.json').read_text())
        matches = [r for r in receipts if r['relative_raw_path'] == relative and r['sha256'] == digest]
    else:
        with (ROOT/'00_admin/download_manifest.csv').open(encoding='utf-8-sig') as handle:
            receipts = list(csv.DictReader(handle))
        matches = [r for r in receipts if r['local_file_path'] == str(path) and r['sha256'] == digest]
    assert len(matches) >= 1, f'No matching frozen receipt: {relative}'
    return {'relative_raw_path':relative,'sha256':digest,'bytes':path.stat().st_size,
            'official_url':matches[-1]['official_url']}

def output_root(config, public_reproduction=False):
    root = config['animal_food_outputs_root']
    return root/'public_reporting_reproduction_20261009' if public_reproduction else root
