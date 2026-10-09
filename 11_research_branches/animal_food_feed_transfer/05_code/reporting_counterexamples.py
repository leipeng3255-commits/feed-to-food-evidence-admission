"""Constructive synthetic examples; not empirical datasets or new theory."""
import json
import subprocess
from information_loss_20261008 import ROOT, paths

def interval_summary(intervals, threshold):
    assert intervals and all(0 <= lo <= hi for lo, hi in intervals)
    n = len(intervals)
    return {'n':n, 'mean_lower':sum(lo for lo, hi in intervals)/n,
            'mean_upper':sum(hi for lo, hi in intervals)/n,
            'fraction_lower':sum(lo > threshold for lo, hi in intervals)/n,
            'fraction_upper':sum(hi > threshold for lo, hi in intervals)/n}

def paired_summary(a, b, threshold):
    assert a and len(a) == len(b), 'Complete matched panels required in this toy example'
    n = len(a)
    return {'n':n,'marginal_A':sorted(a),'marginal_B':sorted(b),
            'A_above':sum(x > threshold for x in a)/n,
            'B_above':sum(x > threshold for x in b)/n,
            'joint_above':sum(x > threshold and y > threshold for x, y in zip(a,b))/n}

def examples():
    limits = [[1,19],[10,10]]
    mean = [{'LOD_ppb':ls,**interval_summary([(0.,x) for x in ls],10)} for ls in limits]
    pairs = [[(3,3),(1,1)],[(3,1),(1,3)]]
    joint = [{'paired_values_ppb':xs,**paired_summary([a for a,b in xs],[b for a,b in xs],2)} for xs in pairs]
    assert mean[0]['mean_upper'] == mean[1]['mean_upper'] == 10
    assert [r['fraction_upper'] for r in mean] == [.5,0]
    assert joint[0]['marginal_A'] == joint[1]['marginal_A']
    assert joint[0]['marginal_B'] == joint[1]['marginal_B']
    assert [r['joint_above'] for r in joint] == [.5,0]
    return {'status':'SYNTHETIC_CONSTRUCTIVE_EXAMPLES_NOT_EMPIRICAL_VALIDATION',
        'threshold_convention':'Strictly greater than; ppb; illustrative, not safety limits',
        'same_mean_different_threshold':{'threshold_ppb':10,'cases':mean},
        'same_marginals_different_joint':{'threshold_ppb':2,'cases':joint},
        'scope':'Demonstrates losses under two specific summary maps. Not unique minimal statistics, statistical sufficiency, population identification or validation.'}

def main():
    subprocess.run(['python3',str(ROOT/'05_code/utilities/check_paths.py')],check=True,stdout=subprocess.DEVNULL)
    out=paths()['animal_food_outputs_root']/'reporting_counterexamples_20261009'
    out.mkdir(parents=True,exist_ok=True)
    target=out/'counterexamples.json'
    target.write_text(json.dumps(examples(),indent=2)+'\n')
    print(target)

if __name__ == '__main__':
    main()
