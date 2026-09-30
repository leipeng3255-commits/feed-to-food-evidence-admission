#!/usr/bin/env python3
"""Read-only public-checkout path readiness check; no drive assumptions."""
import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
config = yaml.safe_load((ROOT/'00_admin/paths.yaml').read_text())
assert Path(config['project_root']).resolve() == ROOT
data = Path(config['data_root']).resolve()
assert data.is_dir() and os.access(data, os.W_OK)
assert data != ROOT and ROOT not in data.parents
for key in ['animal_food_raw_root','animal_food_intermediate_root','animal_food_processed_root','animal_food_outputs_root']:
    path = Path(config[key]).resolve()
    assert path.is_dir() and data in path.parents, key
    if key != 'animal_food_raw_root':
        assert os.access(path, os.W_OK), key
print('PASS explicit external data paths; no raw files modified.')
