#!/usr/bin/env python3
"""Read-only raw re-audit; writes a new aggregate report, never frozen summaries."""
import csv
import hashlib
import io
import json
import math
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from build_reproducibility_bundle import read_paths, PROJECT
from harmonise_pilot import classify, read_mtx_mapping


def finite_numeric(value):
    try:
        return math.isfinite(float(value))
    except (ValueError, TypeError):
        return False


def audit_archive(path, mapping):
    counts = Counter()
    types = Counter()
    flagged_types = Counter()
    flagged_units = Counter()
    numeric_types = Counter()
    pairs = Counter()
    records = Counter()
    samples = set()
    candidate_matrices = Counter()
    other_matrices = Counter()
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith('.csv')]
        if len(names) != 1:
            raise ValueError('Expected exactly one CSV member')
        with archive.open(names[0]) as binary:
            reader = csv.DictReader(io.TextIOWrapper(binary, encoding='utf-8-sig', newline=''))
            fields = reader.fieldnames
            required = {'sampId_A', 'sampMatCode.base.building', 'resType', 'resVal', 'resUnit', 'paramCode.base.param'}
            if not required.issubset(fields):
                raise ValueError(f'Missing audit fields: {required-set(fields)}')
            for row in reader:
                counts['all_rows'] += 1
                name = mapping.get(row['sampMatCode.base.building'], '')
                if not name:
                    counts['unresolved_matrix_rows'] += 1
                if classify(name) != 'animal_food_candidate':
                    other_matrices[name] += 1
                    continue
                counts['candidate_rows'] += 1
                candidate_matrices[name] += 1
                sample = row['sampId_A']
                samples.add(sample)
                counts['missing_sample_id_rows'] += not bool(sample)
                types[row['resType']] += 1
                numeric = finite_numeric(row['resVal'])
                flag = row['resType'] == 'VAL' or bool(row['resVal'] and row['resVal'] != 'N_A')
                counts['legacy_flag_rows'] += flag
                counts['finite_numeric_rows'] += numeric
                if numeric:
                    numeric_types[row['resType']] += 1
                if flag:
                    flagged_types[row['resType']] += 1
                    flagged_units[row['resUnit']] += 1
                    counts['legacy_flag_without_finite_number'] += not numeric
                    counts['legacy_flag_missing_unit'] += row['resUnit'] in ('', 'N_A')
                pairs[(sample, row['paramCode.base.param'])] += 1
                # Hash complete rows; no identifiers or values are exported.
                records[hashlib.sha256(json.dumps(row, sort_keys=True).encode()).digest()] += 1
    return {'counts': dict(counts), 'candidate_unique_samples': len(samples-{''}),
            'candidate_result_types': dict(types), 'legacy_flag_result_types': dict(flagged_types),
            'legacy_flag_units': dict(flagged_units), 'finite_numeric_result_types': dict(numeric_types),
            'exact_duplicate_excess_rows': sum(n-1 for n in records.values()),
            'repeated_sample_analyte_groups': sum(n > 1 for n in pairs.values()),
            'sample_analyte_excess_rows': sum(n-1 for n in pairs.values()),
            'candidate_matrix_row_counts': dict(candidate_matrices), 'noncandidate_matrix_row_counts': dict(other_matrices),
            'boundary': 'Repeated sample-analyte keys may represent legitimate multiple results, not proven erroneous duplicates. Keyword candidate labels are not a validated edible-tissue crosswalk. Numeric/type/unit checks do not establish residue-definition compatibility.'}


def main():
    subprocess.run([sys.executable, str(PROJECT/'05_code/utilities/check_paths.py')], check=True, stdout=subprocess.DEVNULL)
    paths = read_paths()
    raw = paths['animal_food_raw_root']
    mapping, _ = read_mtx_mapping(raw/'efsa_catalogues_2026/DCF_catalogues.zip')
    report = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Post-pilot computational audit; frozen classifications, counts and scientific decisions unchanged',
              'pesticide': audit_archive(raw/'efsa_pesticides_luxembourg/MOPER_ALL_DATA_SSD2_2024_LU.ZIP', mapping),
              'veterinary_drug': audit_archive(raw/'efsa_vmpr_belgium/VMPR_2024_BE.ZIP', mapping)}
    target = paths['animal_food_outputs_root']/'pilot_semantics_audit_20260930.json'
    with target.open('x', encoding='utf-8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(json.dumps({'report': str(target), 'pesticide':report['pesticide']['counts'], 'veterinary_drug':report['veterinary_drug']['counts']}))


if __name__ == '__main__':
    main()
