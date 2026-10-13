#!/usr/bin/env python3
"""Portable aggregate arithmetic verification, not raw-source/scientific validation.

R1 uses conservative closed envelopes, not necessarily sharp identified sets.
Full denominators are observed analytical records, never samples times analytes.
Only the Python standard library is required; checks remain active with -O.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path, PurePosixPath

LEVELS = ('R0', 'R1', 'R2')
THRESHOLDS = (2, 10, 20)
REQUIRED = ('all_cells.csv', 'retained_histograms.csv', 'filled_reporting_statistics.csv',
            'stratum_summary.csv', 'availability.csv', 'source_receipts.json')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def number(value):
    result = float(value)
    require(not math.isnan(result), 'NaN forbidden')
    return result


def integer(value):
    result = number(value)
    require(math.isfinite(result) and result >= 0 and result == int(result), 'Invalid count')
    return int(result)


def close(a, b):
    return a == b or math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)


def equal(a, b, label):
    require(close(number(a), number(b)), 'Arithmetic mismatch: ' + label)


def safe_file(root, name):
    path = PurePosixPath(name)
    require(bool(name) and not path.is_absolute() and '..' not in path.parts and '\\' not in name, 'Unsafe manifest path')
    resolved = (root / name).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), 'Missing file or directory escape')
    return resolved


def rows(root, name):
    with safe_file(root, name).open(encoding='utf-8-sig', newline='') as handle:
        result = list(csv.DictReader(handle))
    require(all(None not in r and None not in r.values() for r in result), 'Malformed CSV ' + name)
    return result


def key(row):
    return row['year'], row['commodity'], row['analyte']


def metrics(hist):
    n = sum(c for lo, hi, c in hist)
    require(n > 0, 'Empty histogram')
    sums = [sum(pair[i] * pair[2] for pair in hist) for i in (0, 1)]
    result = {'lower': sums[0]/n, 'upper': sums[1]/n, 'width': (sums[1]-sums[0])/n}
    counts = {}
    for t in THRESHOLDS:
        for side, i in [('lower', 0), ('upper', 1)]:
            counts[f'count_{side}_above_{t}'] = sum(pair[2] for pair in hist if pair[i] > t)
            result[f'above_{t}_{side}'] = counts[f'count_{side}_above_{t}']/n
    return n, sums, counts, result


def verify(root):
    root = Path(root)
    manifest = json.loads(safe_file(root, 'MANIFEST.json').read_text())
    entries = manifest['files']
    if isinstance(entries, dict):
        entries = [{'path': n, 'sha256': h} for n, h in entries.items()]
    names = set()
    for entry in entries:
        name = entry.get('path', entry.get('name'))
        require(name not in names, 'Duplicate manifest path')
        names.add(name)
        data = safe_file(root, name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry['sha256'], 'Hash mismatch: ' + name)
        if 'bytes' in entry:
            require(len(data) == integer(entry['bytes']), 'Byte count mismatch')
    require(set(REQUIRED) <= names, 'Required assets not covered by manifest')
    cells = rows(root, 'all_cells.csv')
    indexed = {key(r): r for r in cells}
    require(len(indexed) == len(cells) == 1303, 'Source-cell count or uniqueness')
    working = {k: r for k, r in indexed.items() if integer(r['n_working']) > 0}
    require(len(working) == 1257, 'Working-cell count')
    histograms = defaultdict(list)
    histogram_keys = set()
    for row in rows(root, 'retained_histograms.csv'):
        group = (*key(row), row['level'])
        require(key(row) in working and row['level'] in LEVELS, 'Unexpected histogram group')
        lo, hi, n = number(row['lower_ppb']), number(row['upper_ppb']), integer(row['count'])
        require(0 <= lo <= hi and math.isfinite(lo) and n > 0, 'Invalid interval/count')
        require((*group, lo, hi) not in histogram_keys, 'Duplicate interval histogram')
        histogram_keys.add((*group, lo, hi))
        histograms[group].append((lo, hi, n))
    expected = {(*k, level) for k in working for level in LEVELS}
    require(set(histograms) == expected, 'Missing histogram group')
    stats = {}
    for row in rows(root, 'filled_reporting_statistics.csv'):
        group = (*key(row), row['level'])
        require(group not in stats, 'Duplicate statistic group')
        stats[group] = row
    require(set(stats) == expected, 'Statistic group coverage')
    for k, row in indexed.items():
        all_n, work_n, np_n, invalid = (integer(row[n]) for n in ('n_all','n_working','n_NP','n_invalid'))
        require(all_n > 0 and all_n == work_n+np_n+invalid, 'Observed-record partition')
        require(integer(row['duplicate_record_rows']) == invalid == 0, 'Duplicate/invalid records unexpected')
        require(row['status'] == ('WORKING_INTERVALS' if work_n else 'NO_WORKING_SUBSET'), 'Cell status')
        for level in LEVELS if work_n else ():
            n, sums, counts, result = metrics(histograms[(*k, level)])
            require(n == work_n == integer(stats[(*k, level)]['n']), 'Working denominator')
            for side, value in zip(('lower','upper'), sums):
                equal(value, stats[(*k, level)]['sum_'+side+'_ppb'], 'retained endpoint sum')
            for field, value in counts.items():
                require(value == integer(stats[(*k, level)][field]), 'Strict-threshold count')
            for field, value in result.items():
                equal(value, row[level+'_'+field], 'cell '+level+'_'+field)
        if work_n:
            require(histograms[(*k, 'R2')] == [(0.0, math.inf, work_n)], 'R2 unknown envelope')
            for a, b in [('R0','R1'), ('R1','R2')]:
                for prefix in ('', *(f'above_{t}_' for t in THRESHOLDS)):
                    require(number(row[b+'_'+prefix+'lower']) <= number(row[a+'_'+prefix+'lower'])+1e-10 and
                            number(row[b+'_'+prefix+'upper'])+1e-10 >= number(row[a+'_'+prefix+'upper']), 'Nesting failure')
        else:
            require(all(row.get(level+'_'+field, '') == '' for level in LEVELS for field in ('lower','upper','width')), 'Missing subset silently filled')
        full_lo = number(stats[(*k,'R0')]['sum_lower_ppb'])/all_n if work_n else 0.0
        full_hi = math.inf if np_n+invalid else number(stats[(*k,'R0')]['sum_upper_ppb'])/all_n
        equal(row['full_lower'], full_lo, 'full observed-record lower')
        equal(row['full_upper'], full_hi, 'NP-inclusive upper')
    availability = rows(root, 'availability.csv')
    avail = {(r['year'],r['commodity']): r for r in availability}
    require(len(avail) == len(availability) == 28, 'Availability year-food coverage')
    positive = {k:r for k,r in avail.items() if integer(r['sample_identifiers']) > 0}
    require(len(positive) == 5, 'Availability positive strata')
    for k,r in avail.items():
        require((r['status'] == 'ADMITTED_REPORTING_EXPERIMENT') == (k in positive), 'Availability status')
    strata = rows(root, 'stratum_summary.csv')
    require(len(strata) == 5 and len({(r['year'],r['commodity']) for r in strata}) == 5, 'Stratum uniqueness')
    require({k[:2] for k in indexed} == set(positive) == {(r['year'],r['commodity']) for r in strata}, 'Stratum coverage')
    for s in strata:
        sk = s['year'], s['commodity']
        cs = [r for k,r in indexed.items() if k[:2] == sk]
        ws = [r for r in cs if integer(r['n_working'])]
        unchanged = sum(close(number(r['R0_lower']),number(r['R1_lower'])) and close(number(r['R0_upper']),number(r['R1_upper'])) for r in ws)
        rebuilt = {'samples':integer(positive[sk]['sample_identifiers']), 'source_cells':len(cs), 'working_cells':len(ws),
                   'held_duplicate_cells':0,'invalid_rows':0,'mean_unchanged':unchanged,'mean_widened':len(ws)-unchanged,
                   'R1_unbounded':sum(math.isinf(number(r['R1_upper'])) for r in ws),
                   'full_unbounded':sum(math.isinf(number(r['full_upper'])) for r in cs)}
        for field, cell_field in [('analytical_rows','n_all'),('NP_rows','n_NP'),('working_rows','n_working')]:
            rebuilt[field] = sum(integer(r[cell_field]) for r in cs)
        for level in LEVELS:
            for t in THRESHOLDS:
                rebuilt[f'{level}_nonpoint_above_{t}'] = sum(number(r[f'{level}_above_{t}_upper'])-number(r[f'{level}_above_{t}_lower']) > 1e-12 for r in ws)
        for field,value in rebuilt.items():
            require(integer(s[field]) == value, 'Stratum mismatch: '+field)
    receipts = json.loads(safe_file(root, 'source_receipts.json').read_text())
    require(len(receipts) == 14 and {integer(r['year']) for r in receipts} == set(range(2011,2025)), 'Receipt years')
    for r in receipts:
        require(r['manifest_match'] is True and r['zip_crc']=='PASS', 'Source receipt check status')
        require(len(r['sha256'])==64 and all(c in '0123456789abcdef' for c in r['sha256']), 'Source receipt SHA256')
        require(r['official_url'].startswith('https://www.ams.usda.gov/') and r['file'] and r['relative_raw_path'] and r['reference_member'] and r['dictionary_member'], 'Source receipt fields')
        require(integer(r['sample_rows']) > 0, 'Source sample metadata')
    optional = {'coverage.csv', 'coverage_and_units.json'}
    require(not any((root/n).exists() for n in optional) or optional <= names, 'Unmanifested coverage/unit asset')
    require(not (optional & names) or optional <= names, 'Incomplete coverage/unit supplement')
    if optional <= names:
        coverage = rows(root, 'coverage.csv')
        ck = {key(r): r for r in coverage}
        require(len(coverage) == len(ck) == len(indexed) and set(ck) == set(indexed), 'Coverage cell keys')
        for k,r in ck.items():
            total = integer(r['commodity_sample_identifiers'])
            observed = integer(r['observed_unique_sample_identifiers'])
            require(total == integer(positive[k[:2]]['sample_identifiers']) and 0 < observed <= total, 'Coverage sample denominator')
            require(integer(r['observed_result_rows']) == observed == integer(indexed[k]['n_all']), 'Observed coverage record count')
            equal(r['coverage_fraction'], observed/total, 'coverage fraction')
            require(integer(r['unobserved_sample_analyte_combinations']) == total-observed, 'Unobserved combination count')
            require(r['unobserved_combinations_imputed'].lower() == 'false', 'Unobserved combinations imputed')
        unit_document = json.loads(safe_file(root, 'coverage_and_units.json').read_text())
        require(integer(unit_document['coverage_cells']) == len(indexed) and unit_document['unobserved_combinations_imputed'] is False, 'Coverage metadata')
        require(unit_document['status'] == 'PROVIDER_TOTALS_AND_UNIT_DEFINITIONS_CHECKED', 'Unit audit status')
        evidence = unit_document['unit_evidence']
        selected_years = {integer(k[0]) for k in positive}
        require(len(evidence) == len(selected_years) and {integer(e['year']) for e in evidence} == selected_years, 'Unit evidence years')
        for e in evidence:
            require('M=ppm, B=ppb, T=ppt' in e['unit_field_excerpt'] and e['converted_basis']=='ppb'
                    and e['dictionary_member'] and integer(e['dictionary_page_1_based']) > 0, 'Unit definition evidence')
            for field, factor in [('M_factor',1000),('B_factor',1),('T_factor',.001)]:
                equal(e[field],factor,'unit conversion factor')
        for r in receipts:
            if integer(r['year']) in selected_years:
                require(r['provider_programme_totals'] == 'PASS' and r['unit_semantics_checked'] is True
                        and r['sha256'] == r['source_hash_after'] and r['instruction_member'], 'Provider totals/source preservation receipt')
    return {'status':'PASS','source_cells':len(cells),'working_cells':len(working),'strata':len(strata),
            'histogram_rows':len(histogram_keys),'statistic_rows':len(stats),'source_receipts':len(receipts),
            'scope':'Aggregate arithmetic and packaged-file integrity only; no raw-source, sharpness, exposure or scientific validation'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle), indent=2))
