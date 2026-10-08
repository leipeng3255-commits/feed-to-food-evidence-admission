"""Post-pilot, same-source reporting-information experiment; no exposure model."""
from pathlib import Path
from collections import Counter, defaultdict
import bisect
import csv
import hashlib
import io
import json
import math
import re
import subprocess
import zipfile
import yaml

B = Path(__file__).resolve().parents[1]
ROOT = B.parents[1]
EDGES = (0., 1., 10., 100., 1000., math.inf)
COARSE = (0., 10., 1000., math.inf)
THRESHOLDS = (2., 10., 20.)
COMMODITIES = {'BA': 'Beef adipose', 'BM': 'Beef muscle', 'FC': 'Catfish'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def paths():
    c = yaml.safe_load((ROOT / '00_admin/paths.yaml').read_text())
    return {k: Path(v) for k, v in c.items()}

def finite(value, positive=False):
    try:
        x = float(value)
        return x if math.isfinite(x) and (x > 0 if positive else x >= 0) else None
    except (ValueError, TypeError):
        return None

def envelope(x, edges=EDGES):
    i = bisect.bisect_right(edges, x) - 1
    return edges[i], edges[i + 1]

def metrics(hist):
    """Only consumes the retained interval histogram, never the deleted rows."""
    n = sum(hist.values())
    assert n > 0
    result = {'n': n, 'lower': sum(l * k for (l, u), k in hist.items()) / n,
              'upper': sum(u * k for (l, u), k in hist.items()) / n}
    result['width'] = result['upper'] - result['lower']
    for t in THRESHOLDS:
        result[f'above_{t:g}_lower'] = sum(k for (l, u), k in hist.items() if l > t) / n
        result[f'above_{t:g}_upper'] = sum(k for (l, u), k in hist.items() if u > t) / n
    return result

def assert_contains(a, b):
    assert a['n'] == b['n']
    for prefix in ('', *(f'above_{t:g}_' for t in THRESHOLDS)):
        assert b[prefix + 'lower'] <= a[prefix + 'lower'] + 1e-10
        assert b[prefix + 'upper'] + 1e-10 >= a[prefix + 'upper']

def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def json_safe(x):
    if isinstance(x, float) and not math.isfinite(x):
        return 'Infinity' if x > 0 else '-Infinity'
    if isinstance(x, dict):
        return {k: json_safe(v) for k, v in x.items()}
    if isinstance(x, list):
        return [json_safe(v) for v in x]
    return x

def main():
    subprocess.run(['python3', str(ROOT/'05_code/utilities/check_paths.py')], check=True, stdout=subprocess.DEVNULL)
    c = paths()
    out = c['animal_food_outputs_root'] / 'information_loss_20261008'
    out.mkdir(parents=True, exist_ok=True)
    source = c['raw_data_root'] / 'usda_pdp/2009PDPDatabase.zip'
    other = [c['animal_food_raw_root']/'australia_daff_nrs/animal_products/FY2023-24/hen-egg-2023-24.pdf',
             c['animal_food_raw_root']/'finland_ruokavirasto/FEED_ANALYTICAL/2012/eviran_julkaisuja_8_2013_paivitetty_210813.pdf']
    with (ROOT/'00_admin/download_manifest.csv').open(encoding='utf-8-sig') as f:
        receipts = list(csv.DictReader(f))
    source_receipts = []
    for p in [source, *other]:
        digest = sha(p)
        matches = [r for r in receipts if r['local_file_path'] == str(p) and r['sha256'] == digest]
        assert matches, f'Unverified source {p}'
        source_receipts.append({'relative_raw_path': str(p.relative_to(c['raw_data_root'])),
                                'sha256': digest, 'bytes': p.stat().st_size,
                                'official_url': matches[-1]['official_url']})
    samples = {}
    groups = defaultdict(list)
    all_flags = Counter()
    total_rows = 0
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        dictionary = subprocess.check_output(['pdftotext','-layout','-','-'], input=z.read('PDP ReferenceTables 2009.pdf')).decode()
        names = {}
        for line in dictionary.splitlines():
            m = re.match(r'^\s*([A-Z0-9]{3})\s{2,}(.+?)\s{2,}([A-Z])\s+([\d,]+)\s*$', line)
            if m:
                names[m[1]] = m[2]
        assert 'Non-Detect: Marginal Performing Analyte' in dictionary
        assert 'Non-Detect: Validated, well-recovered' in dictionary
        assert 'Detect: Original Extraction Value' in dictionary
        with z.open('Pdp09Samples.txt') as f:
            for a in csv.reader(io.TextIOWrapper(f, encoding='latin1'), delimiter='|'):
                assert a[0] not in samples
                samples[a[0]] = a[6]
        seen = set()
        with z.open('Pdp09Results.txt') as f:
            for a in csv.reader(io.TextIOWrapper(f, encoding='latin1'), delimiter='|'):
                total_rows += 1
                assert a[0] in samples
                if samples[a[0]] not in COMMODITIES:
                    continue
                assert a[1] == samples[a[0]] and a[8] == 'B'
                key = (a[0], a[4])
                assert key not in seen
                seen.add(key)
                flag = a[13].strip()
                all_flags[flag] += 1
                groups[(a[1], a[4])].append((flag, a[6].strip(), a[7].strip()))
    assert set(all_flags) <= {'ND','NP','O'}
    cells, retained, excludes = [], [], Counter()
    for (commodity, analyte), rows in sorted(groups.items()):
        states = Counter(flag for flag, _, _ in rows)
        h = {level: Counter() for level in ('R0','R1','R1_coarse','R2')}
        direct_lo, direct_hi = [], []
        invalid = 0
        for flag, value, lod in rows:
            if flag == 'NP':
                continue
            x = finite(value) if flag == 'O' else finite(lod, True)
            if x is None or (flag == 'ND' and value != ''):
                invalid += 1
                excludes[flag] += 1
                continue
            pair = (x, x) if flag == 'O' else (0., x)
            direct_lo.append(pair[0]); direct_hi.append(pair[1])
            h['R0'][pair] += 1
            h['R1'][envelope(x) if flag == 'O' else pair] += 1
            h['R1_coarse'][envelope(x, COARSE) if flag == 'O' else pair] += 1
            h['R2'][(0., math.inf)] += 1
        row = {'commodity':commodity, 'commodity_name':COMMODITIES[commodity],
               'analyte':analyte, 'analyte_name': names.get(analyte,'UNRESOLVED'),
               'n_all':len(rows), 'n_ND':states['ND'], 'n_NP':states['NP'],
               'n_O':states['O'], 'n_invalid':invalid, 'n_working':len(direct_lo)}
        assert row['analyte_name'] != 'UNRESOLVED', analyte
        assert row['n_all'] == row['n_working'] + row['n_NP'] + row['n_invalid']
        if direct_lo:
            ms = {level: metrics(hist) for level,hist in h.items()}
            assert math.isclose(sum(direct_lo)/len(direct_lo), ms['R0']['lower'], abs_tol=1e-10)
            assert math.isclose(sum(direct_hi)/len(direct_hi), ms['R0']['upper'], abs_tol=1e-10)
            assert all(m['n'] == len(direct_lo) for m in ms.values())
            for t in THRESHOLDS:
                for values,end in [(direct_lo,'lower'),(direct_hi,'upper')]:
                    assert math.isclose(sum(v>t for v in values)/len(values),ms['R0'][f'above_{t:g}_{end}'],abs_tol=1e-12)
            assert_contains(ms['R0'],ms['R1']); assert_contains(ms['R1'],ms['R2'])
            assert_contains(ms['R1'],ms['R1_coarse'])
            for level,hist in h.items():
                for (lo,hi),n in sorted(hist.items()):
                    retained.append({'commodity':commodity,'analyte':analyte,'level':level,'lower_ppb':lo,'upper_ppb':hi,'count':n})
                row.update({f'{level}_{k}':v for k,v in ms[level].items() if k!='n'})
            full = h['R0'].copy()
            if states['NP'] + invalid:
                full[(0.,math.inf)] += states['NP'] + invalid
            fm = metrics(full)
            assert fm['n'] == len(rows)
            row.update({'full_lower':fm['lower'],'full_upper':fm['upper']})
        else:
            for level in h:
                row.update({f'{level}_{k}':'' for k in ['lower','upper','width',*(f'above_{t:g}_{s}' for t in THRESHOLDS for s in ['lower','upper'])]})
            row.update({'full_lower':0.,'full_upper':math.inf})
        cells.append(row)
    # All-cell tables include cells with zero eligible rows; no favorable-case selection.
    assert sum(r['n_all'] for r in cells) == sum(all_flags.values())
    write_csv(out/'all_cells.csv', cells)
    write_csv(out/'retained_interval_histograms.csv', retained)
    valid = [r for r in cells if r['n_working']]
    def summarize(rs):
        return {'cells':len(rs), 'rows':sum(r['n_all'] for r in rs),
                'working_rows':sum(r['n_working'] for r in rs),
                'NP_rows':sum(r['n_NP'] for r in rs),
                'cells_with_NP':sum(r['n_NP']>0 for r in rs),
                'all_ND_working_cells':sum(r['n_O']==0 for r in rs),
                'R1_wider_cells':sum(r['R1_width'] > r['R0_width']+1e-10 for r in rs),
                'R1_unchanged_cells':sum(math.isclose(r['R1_width'],r['R0_width'],rel_tol=0,abs_tol=1e-10) for r in rs),
                'R1_unbounded_cells':sum(math.isinf(r['R1_upper']) for r in rs),
                'full_unbounded_cells':sum(math.isinf(r['full_upper']) for r in rs)}
    summary = {'design':'post-pilot; previously inspected source counts; not preregistered',
               'source_archive_rows':total_rows,'source_archive_samples':len(samples),
               'selected_samples':dict(Counter(v for v in samples.values() if v in COMMODITIES)),
               'selected_flags':dict(all_flags), 'excluded_invalid':dict(excludes),
               'bins_ppb':list(EDGES), 'coarse_bins_ppb':list(COARSE), 'thresholds_ppb':list(THRESHOLDS),
               'all_cells':len(cells), 'zero_working_cells':len(cells)-len(valid),
               'all_cells_with_NP':sum(r['n_NP']>0 for r in cells),
               'all_cells_full_unbounded':sum(math.isinf(r['full_upper']) for r in cells),
               'summary':summarize(valid),
               'by_commodity':{k:summarize([r for r in valid if r['commodity']==k]) for k in COMMODITIES},
               'assertions':'PASS: fixed denominators; nesting; nested coarse bins; exact histogram negative control; joins; uniqueness; raw hashes',
               'limitations':'Conditional reporting intervals, not biological truth, confidence intervals, national prevalence, exposure or external validation.'}
    assert summary['summary']['R1_wider_cells']+summary['summary']['R1_unchanged_cells'] == len(valid)
    for receipt,p in zip(source_receipts,[source,*other]):
        assert sha(p) == receipt['sha256']
    (out/'summary.json').write_text(json.dumps(json_safe(summary),indent=2,allow_nan=False)+'\n')
    (out/'source_receipts.json').write_text(json.dumps(source_receipts,indent=2)+'\n')
    fi_text = subprocess.check_output(['pdftotext','-f','44','-l','46','-layout',str(other[1]),'-']).decode()
    fi_csv = c['intermediate_data_root']/'branches/animal_food_feed_transfer/finland_feed_body_audits/feed2012_pesticide_qualitative_literal_20261005.csv'
    with fi_csv.open(encoding='utf-8-sig') as f:
        fi_rows = list(csv.DictReader(f))
    assert len(fi_rows) == fi_text.count('ei todettu') == 270
    assert all(r['analyte_label_original'] in fi_text and r['sample_id_original'] in fi_text for r in fi_rows)
    assert all(r['result_original']=='ei todettu' and r['source_sha256']==source_receipts[2]['sha256'] for r in fi_rows)
    au_text = subprocess.check_output(['pdftotext','-layout',str(other[0]),'-']).decode()
    au_rows = []
    for label in ['aldrin and dieldrin (HHDN+HEOD)','DDT','chlorpyrifos']:
        line = next(l for l in au_text.splitlines() if l.strip().startswith(label+' '))
        m = re.search(r'Whole\s+(0\.01)\s+([\d.]+)\s+(60)\s+(0)\s+(0)\s+(0)\s*$',line)
        assert m, line
        au_rows.append({'label':label,'LOR_mg_kg':float(m[1]),'MRL_mg_kg':float(m[2]),'tests':60,'above_LOR_band_counts':[0,0,0]})
    contexts = {'Finland':{'source_block_pages':[44,45,46],'qualitative_ND_entries':270,
                'sample_identifiers':len({r['sample_id_original'] for r in fi_rows}),
                'analyte_labels':len({r['analyte_label_original'] for r in fi_rows}),
                'PCB_entries':sum(r['analyte_label_original'].startswith('PCB ') for r in fi_rows),
                'transcription_sha256':sha(fi_csv),'numerical_limits_verified':False},
                'Australia':{'illustrative_rows':au_rows,'independent_samples_not_summed':True},
                'scope':'Reporting-format examples only; not a matched chain or validation dataset.'}
    (out/'context_source_checks.json').write_text(json.dumps(contexts,indent=2)+'\n')
    (out/'protocol_sha256.txt').write_text(sha(B/'01_protocol/information_loss_20261008.md')+'\n')
    print(json.dumps(json_safe(summary),indent=2))

if __name__ == '__main__':
    main()
