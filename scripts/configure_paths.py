#!/usr/bin/env python3
"""Create ignored local path configuration from an explicitly selected data root."""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-root', required=True, type=Path)
    args = parser.parse_args()
    data = args.data_root
    if not data.is_absolute() or not data.is_dir() or not os.access(data, os.W_OK):
        raise SystemExit('Choose an existing, writable absolute data directory; no fallback is permitted.')
    data = data.resolve()
    if data == ROOT or ROOT in data.parents:
        raise SystemExit('Raw/large data must be outside the code checkout.')
    branch = 'branches/animal_food_feed_transfer'
    config = {'project_root': str(ROOT), 'data_root': str(data),
              'raw_data_root': str(data/'02_raw_data'),
              'animal_food_raw_root': str(data/'02_raw_data'/branch),
              'animal_food_intermediate_root': str(data/'03_intermediate/public_reproduction'/branch),
              'animal_food_processed_root': str(data/'04_processed/public_reproduction'/branch),
              'animal_food_outputs_root': str(data/'06_outputs/public_reproduction'/branch)}
    for key, value in config.items():
        if key not in {'project_root','data_root'}:
            Path(value).mkdir(parents=True, exist_ok=True)
    target = ROOT/'00_admin/paths.yaml'
    target.parent.mkdir(parents=True, exist_ok=True)
    text = ''.join(f'{key}: {json.dumps(value, ensure_ascii=False)}\n' for key,value in config.items())
    if target.exists() and target.read_text() != text:
        raise SystemExit('Existing paths.yaml differs; inspect and edit it explicitly rather than overwrite it.')
    target.write_text(text)
    print('Local paths configured. No source files downloaded or changed.')


if __name__ == '__main__':
    main()
