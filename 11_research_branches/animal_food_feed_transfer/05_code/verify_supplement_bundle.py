"""Portable artifact verification, not a raw-data analysis.

Only reads the explicitly selected extracted bundle. No project configuration,
third-party Python modules, original monitoring records or network are needed.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

THRESHOLDS=(2,10,20)

def require(condition,message):
    if not condition:raise ValueError(message)

def equal(a,b):
    require(math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-10),f'Endpoint mismatch: {a}, {b}')

def rows(path):
    with path.open(newline='',encoding='utf-8') as handle:return list(csv.DictReader(handle))

def file_hashes(root):
    manifest=json.loads((root/'MANIFEST.json').read_text())
    require(isinstance(manifest,dict) and bool(manifest),'Empty/invalid manifest')
    for name,digest in manifest.items():
        rel=Path(name)
        require(not rel.is_absolute() and '..' not in rel.parts,'Unsafe manifest path')
        path=(root/rel).resolve()
        require(path.is_relative_to(root.resolve()),'Manifest path leaves bundle')
        require(path.is_file(),f'Missing bundle file: {name}')
        require(hashlib.sha256(path.read_bytes()).hexdigest()==digest,f'Hash mismatch: {name}')
    return len(manifest)

def np_rows(results,statistics):
    require(len(results)==len(statistics) and bool(results),'Result/statistic row-count mismatch')
    for r,s in zip(results,statistics):
        require((r['year'],r['commodity'],r['analyte'],r['factor'])==(
            s['year'],s['commodity'],s['analyte'],s['NP_assumed_factor']),'NP row identity mismatch')
        n=int(s['n']);require(n>0 and int(r['n_all'])==n,'Invalid/mismatched denominator')
        for end in ('lower','upper'):
            equal(r[end],float(s[f'sum_{end}_ppb'])/n)
            for t in THRESHOLDS:
                k=int(s[f'count_{end}_above_{t}']);require(0<=k<=n,'Invalid threshold count')
                equal(r[f'above_{t}_{end}'],k/n)
    return len(results)

def full_denominator(cells):
    for r in cells:
        n,w,u=int(r['n_all']),int(r['n_working']),int(r['n_NP'])+int(r['n_invalid'])
        require(n>0 and w>=0 and u>=0 and w+u==n,'Full denominator partition mismatch')
        lower=float(r['R0_lower'])*w/n if w else 0
        upper=math.inf if u else float(r['R0_upper'])
        equal(r['full_lower'],lower);equal(r['full_upper'],upper)
    return len(cells)

def histograms(cells,retained):
    by={(r['commodity'],r['analyte']):r for r in cells}
    require(len(by)==len(cells),'Duplicate cell key')
    groups=defaultdict(list)
    for r in retained:groups[(r['commodity'],r['analyte'],r['level'])].append(r)
    expected={(c,a,level) for (c,a),r in by.items() if int(r['n_working'])>0
              for level in ('R0','R1','R1_coarse','R2')}
    require(set(groups)==expected,'Missing or unexpected retained histogram')
    for (c,a,level),records in groups.items():
        n=sum(int(r['count']) for r in records)
        require(n>0 and n==int(by[c,a]['n_working']),'Histogram denominator mismatch')
        for r in records:
            require(int(r['count'])>0 and 0<=float(r['lower_ppb'])<=float(r['upper_ppb']),'Invalid histogram interval/count')
        for end in ('lower','upper'):
            equal(by[c,a][f'{level}_{end}'],sum(float(r[end+'_ppb'])*int(r['count']) for r in records)/n)
            for t in THRESHOLDS:
                equal(by[c,a][f'{level}_above_{t}_{end}'],sum(int(r['count']) for r in records if float(r[end+'_ppb'])>t)/n)
    return {'source_cells':len(cells),'histogram_groups':len(groups)}

def synthetic(data):
    require(data['status']=='SYNTHETIC_CONSTRUCTIVE_EXAMPLES_NOT_EMPIRICAL_VALIDATION','Synthetic label missing')
    a,b=data['same_mean_different_threshold']['cases'];t=data['same_mean_different_threshold']['threshold_ppb']
    for case in (a,b):
        limits=case['LOD_ppb'];require(case['n']==len(limits)==2,'Toy denominator mismatch')
        equal(case['mean_lower'],0);equal(case['fraction_lower'],0)
        equal(case['mean_upper'],sum(limits)/len(limits))
        equal(case['fraction_upper'],sum(x>t for x in limits)/len(limits))
    require(a['mean_upper']==b['mean_upper']==10 and (a['fraction_upper'],b['fraction_upper'])==(.5,0),'First collision missing')
    a,b=data['same_marginals_different_joint']['cases'];t=data['same_marginals_different_joint']['threshold_ppb']
    for case in (a,b):
        pairs=case['paired_values_ppb'];require(case['n']==len(pairs)==2,'Toy pairing denominator mismatch')
        require(sorted(x for x,y in pairs)==case['marginal_A']==[1,3],'A marginal mismatch')
        require(sorted(y for x,y in pairs)==case['marginal_B']==[1,3],'B marginal mismatch')
        equal(case['A_above'],sum(x>t for x,y in pairs)/len(pairs))
        equal(case['B_above'],sum(y>t for x,y in pairs)/len(pairs))
        equal(case['joint_above'],sum(x>t and y>t for x,y in pairs)/len(pairs))
    require((a['joint_above'],b['joint_above'])==(.5,0),'Second collision missing')
    return 2

def verify(root):
    result={'status':'PASS_INTEGRITY_AND_ARITHMETIC_ONLY','file_hashes':file_hashes(root),
            'raw_records_read':False,'configuration_read':False,'scientific_validation':False}
    p=root/'aggregates'
    if (p/'all_cells.csv').is_file():
        cells=rows(p/'all_cells.csv')
        result.update(supplement='S4',**histograms(cells,rows(p/'retained_interval_histograms.csv')))
        result['full_denominator_cells']=full_denominator(cells)
        require(result['source_cells']==490,'Unexpected frozen S4 cell count')
    elif (p/'NP_scenarios_all_cells.csv').is_file():
        result['supplement']='S5'
        result['NP_rows']=np_rows(rows(p/'NP_scenarios_all_cells.csv'),rows(p/'filled_reporting_template.csv'))
        require(result['NP_rows']==3425,'Unexpected frozen S5 row count')
        result.update(histograms(rows(p/'catfish_2010_cells.csv'),rows(p/'catfish_2010_histograms.csv')))
        require(result['source_cells']==195,'Unexpected frozen 2010 cell count')
        result['synthetic_examples']=synthetic(json.loads((p/'counterexamples.json').read_text()))
    else:raise ValueError('Not a supported S4/S5 aggregate bundle')
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent,
                        help='Explicit extracted S4/S5 bundle root; defaults to this script directory')
    args=parser.parse_args()
    try:result=verify(args.bundle.resolve())
    except (ValueError,OSError,KeyError,TypeError) as exc:
        parser.exit(1,f'FAIL: {exc}\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
