"""Verify S5 aggregate arithmetic without reading source monitoring records."""
import argparse
import csv
import json
import math
from pathlib import Path
from information_loss_20261008 import paths,THRESHOLDS

def main():
    c=paths()
    parser=argparse.ArgumentParser()
    parser.add_argument('--aggregates',type=Path,help='Explicit alternative aggregate directory')
    args=parser.parse_args()
    p=args.aggregates or c['animal_food_outputs_root']/'np_temporal_20261008'
    with (p/'NP_scenarios_all_cells.csv').open() as f:rs=list(csv.DictReader(f))
    with (p/'filled_reporting_template.csv').open() as f:ss=list(csv.DictReader(f))
    assert len(rs)==len(ss)==3425
    for r,s in zip(rs,ss):
        assert (r['year'],r['commodity'],r['analyte'],r['factor'])==(s['year'],s['commodity'],s['analyte'],s['NP_assumed_factor'])
        assert int(r['n_all'])==int(s['n'])
        for end in ['lower','upper']:
            a=float(r[end]);b=float(s[f'sum_{end}_ppb'])/int(s['n'])
            assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10)
            for t in THRESHOLDS:
                a=float(r[f'above_{t:g}_{end}']);b=int(s[f'count_{end}_above_{t:g}'])/int(s['n'])
                assert math.isclose(a,b,abs_tol=1e-12)
    print(json.dumps({'rows_verified':len(rs),'raw_data_read':False,'mean_and_threshold_reconstruction':'PASS'}))

if __name__=='__main__':main()
