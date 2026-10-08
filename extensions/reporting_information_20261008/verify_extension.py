"""Portable, raw-data-free integrity/arithmetic checks for the public extension.

This is a release-verification utility, not a raw-data analysis. It intentionally
uses only release-relative paths; no scientific data location is inferred.
"""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
THRESHOLDS = (2, 10, 20)

def rows(path):
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))

def equal(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-10), (a, b)

def histograms(data, cell_name, hist_name):
    cells = {(r['commodity'], r['analyte']): r for r in rows(data/cell_name)}
    hs = defaultdict(list)
    for r in rows(data/hist_name):
        hs[(r['commodity'], r['analyte'], r['level'])].append(r)
    for (commodity, analyte, level), records in hs.items():
        cell = cells[(commodity, analyte)]
        n = sum(int(r['count']) for r in records)
        assert n == int(cell['n_working'])
        for end in ('lower', 'upper'):
            equal(sum(float(r[end+'_ppb'])*int(r['count']) for r in records)/n,
                  cell[level+'_'+end])
            for t in THRESHOLDS:
                equal(sum(int(r['count']) for r in records if float(r[end+'_ppb']) > t)/n,
                      cell[f'{level}_above_{t}_{end}'])
    return len(cells), len(hs)

def main():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    p = ROOT/'aggregates/np_temporal_20261008'
    results = rows(p/'NP_scenarios_all_cells.csv')
    statistics = rows(p/'filled_reporting_template.csv')
    assert len(results) == len(statistics) == 3425
    by = defaultdict(list)
    for r, s in zip(results, statistics):
        assert (r['year'], r['commodity'], r['analyte'], r['factor']) == (
            s['year'], s['commodity'], s['analyte'], s['NP_assumed_factor'])
        assert int(r['n_all']) == int(s['n'])
        for end in ('lower', 'upper'):
            equal(r[end], float(s[f'sum_{end}_ppb'])/int(s['n']))
            for t in THRESHOLDS:
                equal(r[f'above_{t}_{end}'], int(s[f'count_{end}_above_{t}'])/int(s['n']))
        by[(r['year'], r['commodity'], r['analyte'])].append(r)
    assert len(by) == 685
    for group in by.values():
        assert len(group) == 5
        assert len({r['n_all'] for r in group}) == len({r['lower'] for r in group}) == 1
        for a, b in zip(group, group[1:]):
            assert float(a['upper']) <= float(b['upper']) + 1e-10
    a = histograms(ROOT/'aggregates/information_loss_20261008', 'all_cells.csv',
                   'retained_interval_histograms.csv')
    b = histograms(p, 'catfish_2010_cells.csv', 'catfish_2010_histograms.csv')
    assert a[0] == 490 and b[0] == 195
    print(json.dumps({'file_hashes': len(manifest), 'NP_rows_reconstructed': 3425,
                      'S4_source_cells': a[0], 'S5_source_cells': b[0],
                      'raw_records_read': False, 'status': 'PASS_ARITHMETIC_NOT_VALIDATION'}))

if __name__ == '__main__':
    main()
