"""Portable public-file and synthetic-arithmetic checks; no source data access."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text())
    for name,digest in manifest.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    data=json.loads((ROOT/'counterexamples.json').read_text())
    assert data['status']=='SYNTHETIC_CONSTRUCTIVE_EXAMPLES_NOT_EMPIRICAL_VALIDATION'
    a,b=data['same_mean_different_threshold']['cases'];t=data['same_mean_different_threshold']['threshold_ppb']
    for case in [a,b]:
        limits=case['LOD_ppb'];n=len(limits)
        assert case['n']==n==2
        assert case['mean_lower']==case['fraction_lower']==0
        assert case['mean_upper']==sum(limits)/n==10
        assert case['fraction_upper']==sum(x>t for x in limits)/n
    assert (a['fraction_upper'],b['fraction_upper'])==(.5,0)
    a,b=data['same_marginals_different_joint']['cases'];t=data['same_marginals_different_joint']['threshold_ppb']
    for case in [a,b]:
        pairs=case['paired_values_ppb'];n=len(pairs)
        assert case['n']==n==2
        assert sorted(x for x,y in pairs)==case['marginal_A']==[1,3]
        assert sorted(y for x,y in pairs)==case['marginal_B']==[1,3]
        assert case['joint_above']==sum(x>t and y>t for x,y in pairs)/n
    assert (a['joint_above'],b['joint_above'])==(.5,0)
    print(json.dumps({'extension_hashes':len(manifest),'synthetic_counterexamples':2,
        'arithmetic':'PASS','raw_records_read':False,'scientific_validation':False}))

if __name__=='__main__':main()
