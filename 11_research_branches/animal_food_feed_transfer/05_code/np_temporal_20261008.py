"""NP assumption sensitivity and fixed-rule temporal application; aggregate outputs."""
from collections import Counter, defaultdict
import csv
import io
import json
import math
import re
import subprocess
import zipfile
from information_loss_20261008 import (B, ROOT, paths, sha, finite, envelope, EDGES,
    COARSE, THRESHOLDS, metrics, assert_contains, write_csv, json_safe)

FACTORS = (1.,2.,5.,10.,math.inf)
DETECTIONS = {'O','A','R'}
UNITS = {'B':1.,'M':1000.,'T':.001}

def norm(s):return ' '.join(s.casefold().split())

def in_ppb(value,unit):
    assert unit in UNITS
    return None if value is None else value*UNITS[unit]

def archive(year, commodities):
    c=paths();p=c['raw_data_root']/f'usda_pdp/{year}PDPDatabase.zip'
    with (ROOT/'00_admin/download_manifest.csv').open(encoding='utf-8-sig') as f:receipts=list(csv.DictReader(f))
    digest=sha(p)
    matched=[r for r in receipts if r['local_file_path']==str(p) and r['sha256']==digest]
    assert matched,p
    sample_info={};groups=defaultdict(list);flags=Counter();units=Counter();total=0;keys=set()
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        ref=subprocess.check_output(['pdftotext','-layout','-','-'],input=z.read(f'PDP ReferenceTables {year}.pdf')).decode()
        dictionary=subprocess.check_output(['pdftotext','-layout','-','-'],input=z.read(f'PDP DataDictionary {year}.pdf')).decode()
        for phrase in ['Non-Detect: Marginal Performing Analyte','Non-Detect: Validated, well-recovered','Detect: Original Extraction Value']:
            assert phrase in ref
        assert 'SAMPLE_PK' in dictionary and 'CONCEN' in dictionary and 'LOD' in dictionary
        assert 'M=ppm,B=ppb,T=ppt' in re.sub(r'\s+','',dictionary)
        names={}
        for line in ref.splitlines():
            m=re.match(r'^\s*([A-Z0-9]{3})\s{2,}(.+?)\s{2,}([A-Z])\s+([\d,]+)\s*$',line)
            if m:names[m[1]]=m[2]
        sn=next(n for n in z.namelist() if n.lower().endswith(f'{str(year)[2:]}samples.txt'))
        rn=next(n for n in z.namelist() if n.lower().endswith(f'{str(year)[2:]}results.txt'))
        with z.open(sn) as f:
            for a in csv.reader(io.TextIOWrapper(f,encoding='latin1'),delimiter='|'):
                assert a[0] not in sample_info
                sample_info[a[0]]=a[6]
        with z.open(rn) as f:
            for a in csv.reader(io.TextIOWrapper(f,encoding='latin1'),delimiter='|'):
                total+=1
                assert a[0] in sample_info
                if sample_info[a[0]] not in commodities:continue
                assert a[1]==sample_info[a[0]]
                key=(a[0],a[4]);assert key not in keys;keys.add(key)
                unit=a[8].strip();assert unit in UNITS
                flag=a[13].strip();assert flag in DETECTIONS|{'ND','NP'}
                flags[flag]+=1;units[unit]+=1
                val=finite(a[6].strip());lod=finite(a[7].strip(),True)
                groups[(a[1],a[4])].append({'state':flag,'value':in_ppb(val,unit),
                    'lod':in_ppb(lod,unit),'raw_value_blank':a[6].strip()==''})
        if flags['R']:assert 'Detect - Re-extraction Analysis Value' in ref
        if flags['A']:assert 'Detect: Avg of Original & Re-extract' in ref
    assert sha(p)==digest
    meta={'year':year,'source_sha256':digest,'official_url':matched[-1]['official_url'],
          'relative_raw_path':str(p.relative_to(c['raw_data_root'])),'all_archive_rows':total,
          'all_archive_samples':len(sample_info),'selected_samples':dict(Counter(x for x in sample_info.values() if x in commodities)),
          'selected_flags':dict(flags),'original_units':dict(units),'source_cells':len(groups)}
    assert all(a in names for co,a in groups)
    return groups,names,meta

def base_interval(r):
    if r['state'] in DETECTIONS and r['value'] is not None:return (r['value'],r['value'])
    if r['state']=='ND' and r['lod'] is not None and r['raw_value_blank']:return (0.,r['lod'])
    return None

def np_hist(records,k):
    h=Counter()
    for r in records:
        if r['state']=='NP':
            upper=math.inf if math.isinf(k) or r['lod'] is None else k*r['lod']
            pair=(0.,upper)
        else:pair=base_interval(r) or (0.,math.inf)
        h[pair]+=1
    return h

def sufficient(h):
    n=sum(h.values());out={'n':n,'sum_lower_ppb':sum(l*k for (l,u),k in h.items()),
        'sum_upper_ppb':sum(u*k for (l,u),k in h.items()),
        'n_unbounded':sum(k for (l,u),k in h.items() if math.isinf(u))}
    for t in THRESHOLDS:
        out[f'count_lower_above_{t:g}']=sum(k for (l,u),k in h.items() if l>t)
        out[f'count_upper_above_{t:g}']=sum(k for (l,u),k in h.items() if u>t)
    return out

def sensitivity(groups,names,meta):
    rows=[];report=[]
    for (co,a),rs in sorted(groups.items()):
        counts=Counter(r['state'] for r in rs);previous=None
        detected_sum=sum(r['value'] for r in rs if r['state'] in DETECTIONS and r['value'] is not None)
        nd_limit_sum=sum(r['lod'] for r in rs if r['state']=='ND' and base_interval(r) is not None)
        np_limit_sum=sum(r['lod'] for r in rs if r['state']=='NP' and r['lod'] is not None)
        common={'year':meta['year'],'commodity':co,'analyte':a,'analyte_name':names[a],
            'n_all':len(rs),'n_NP':counts['NP'],'n_ND':counts['ND'],
            'n_detected':sum(counts[k] for k in DETECTIONS),
            'invalid_NP_limits':sum(r['state']=='NP' and r['lod'] is None for r in rs),
            'invalid_nonNP':sum(r['state']!='NP' and base_interval(r) is None for r in rs)}
        for k in FACTORS:
            h=np_hist(rs,k);m=metrics(h);s=sufficient(h)
            assert m['n']==len(rs)==s['n']
            assert m['lower']==s['sum_lower_ppb']/s['n']
            assert m['upper']==s['sum_upper_ppb']/s['n']
            if not common['invalid_NP_limits'] and not common['invalid_nonNP'] and math.isfinite(k):
                direct_upper=(detected_sum+nd_limit_sum+k*np_limit_sum)/len(rs)
                assert math.isclose(m['upper'],direct_upper,rel_tol=1e-12,abs_tol=1e-10)
                assert math.isclose(m['lower'],detected_sum/len(rs),rel_tol=1e-12,abs_tol=1e-10)
            for t in THRESHOLDS:
                for end in ['lower','upper']:
                    assert m[f'above_{t:g}_{end}']==s[f'count_{end}_above_{t:g}']/s['n']
            if previous:
                assert_contains(previous,m)
                assert m['lower']==previous['lower']
                if not counts['NP']:assert m==previous
            previous=m
            rows.append({**common,'factor':k,**m})
            report.append({'source_schema':'PDP annual ASCII+reference tables','source_sha256':meta['source_sha256'],
                'year':meta['year'],'commodity':co,'analyte':a,'analyte_name':names[a],
                'residue_definition_locator':'Annual reference-table analyte label; toxicology crosswalk not established',
                'unit':'ppb','target_frame':'Selected archive records, unweighted','NP_assumed_factor':k,
                'limit_type':'Recorded LOD; ND interval conditional on reporting semantics',
                'n_eligible':len(rs)-counts['NP']-common['invalid_nonNP'],
                'n_ND':counts['ND'],'n_detected':common['n_detected'],
                'n_NP':counts['NP'],'invalid_NP_limits':common['invalid_NP_limits'],
                'invalid_nonNP':common['invalid_nonNP'],'status':'CONDITIONAL_REPORTING_BOUND',**s})
    return rows,report

def temporal(groups,names):
    cells=[];histograms=[]
    for (co,a),rs in sorted(groups.items()):
        counts=Counter(r['state'] for r in rs)
        working=[r for r in rs if r['state']!='NP' and base_interval(r) is not None]
        h={l:Counter() for l in ('R0','R1','R1_coarse','R2')}
        for r in working:
            pair=base_interval(r);h['R0'][pair]+=1
            h['R1'][envelope(r['value']) if r['state'] in DETECTIONS else pair]+=1
            h['R1_coarse'][envelope(r['value'],COARSE) if r['state'] in DETECTIONS else pair]+=1
            h['R2'][(0.,math.inf)]+=1
        m={level:metrics(hh) for level,hh in h.items()} if working else None
        common={'commodity':co,'analyte':a,'analyte_name':names[a],'n_all':len(rs),
            'n_working':len(working),'n_NP':counts['NP'],'n_ND':counts['ND'],
            'n_O':counts['O'],'n_A':counts['A'],'n_R':counts['R'],
            'n_invalid':len(rs)-len(working)-counts['NP']}
        if m:
            assert_contains(m['R0'],m['R1']);assert_contains(m['R1'],m['R2']);assert_contains(m['R1'],m['R1_coarse'])
            for level,hh in h.items():
                for (lo,hi),n in sorted(hh.items()):histograms.append({'commodity':co,'analyte':a,'level':level,'lower_ppb':lo,'upper_ppb':hi,'count':n})
                common.update({f'{level}_{k}':v for k,v in m[level].items() if k!='n'})
        else:
            for level in h:
                common.update({f'{level}_{k}':'' for k in ['lower','upper','width',*(f'above_{t:g}_{end}' for t in THRESHOLDS for end in ['lower','upper'])]})
        cells.append(common)
    return cells,histograms

def year_summary(cells):
    valid=[r for r in cells if int(r['n_working'])]
    out={'all_cells':len(cells),'working_cells':len(valid),
        'working_rows':sum(int(r['n_working']) for r in cells),'all_rows':sum(int(r['n_all']) for r in cells),
        'NP_rows':sum(int(r['n_NP']) for r in cells),
        'R1_wider':sum(float(r['R1_width'])>float(r['R0_width'])+1e-10 for r in valid),
        'R1_unchanged':sum(math.isclose(float(r['R1_width']),float(r['R0_width']),rel_tol=0,abs_tol=1e-10) for r in valid),
        'finite_means':{l:sum(math.isfinite(float(r[l+'_upper'])) for r in valid) for l in ['R0','R1','R2']},
        'nonpoint_exceedance':{l:{f'{t:g}':sum(float(r[f'{l}_above_{t:g}_upper'])>float(r[f'{l}_above_{t:g}_lower'])+1e-12 for r in valid) for t in THRESHOLDS} for l in ['R0','R1','R2']}}
    assert out['R1_wider']+out['R1_unchanged']==len(valid)
    return out

def main():
    subprocess.run(['python3',str(ROOT/'05_code/utilities/check_paths.py')],check=True,stdout=subprocess.DEVNULL)
    out=paths()['animal_food_outputs_root']/'np_temporal_20261008';out.mkdir(parents=True,exist_ok=True)
    g09,n09,m09=archive(2009,{'BA','BM','FC'});g10,n10,m10=archive(2010,{'FC'})
    r09,report09=sensitivity(g09,n09,m09);r10,report10=sensitivity(g10,n10,m10)
    write_csv(out/'NP_scenarios_all_cells.csv',r09+r10)
    write_csv(out/'filled_reporting_template.csv',report09+report10)
    cells10,h10=temporal(g10,n10)
    write_csv(out/'catfish_2010_cells.csv',cells10);write_csv(out/'catfish_2010_histograms.csv',h10)
    baseline=paths()['animal_food_outputs_root']/'information_loss_20261008/all_cells.csv'
    with baseline.open() as f:prior09={r['analyte']:r for r in csv.DictReader(f) if r['commodity']=='FC'}
    cells09,_=temporal({k:rs for k,rs in g09.items() if k[0]=='FC'},n09)
    assert set(prior09)=={r['analyte'] for r in cells09}
    for r in cells09:
        prior=prior09[r['analyte']]
        for k,v in r.items():
            if k in prior:
                if k in ['commodity','analyte','analyte_name'] or v=='':assert str(v)==prior[k]
                else:assert math.isclose(float(v),float(prior[k]),rel_tol=1e-12,abs_tol=1e-10)
    c09={r['analyte']:r for r in cells09};c10={r['analyte']:r for r in cells10};paired=[];labels=[]
    for a in sorted(set(c09)|set(c10)):
        x,y=c09.get(a),c10.get(a)
        status='SHARED_LABEL' if x and y and norm(x['analyte_name'])==norm(y['analyte_name']) else ('LABEL_CHANGED' if x and y else '2009_ONLY' if x else '2010_ONLY')
        labels.append({'analyte':a,'name_2009':x['analyte_name'] if x else '', 'name_2010':y['analyte_name'] if y else '', 'status':status})
        if status=='SHARED_LABEL' and int(x['n_working']) and int(y['n_working']):
            paired.append({'analyte':a,'analyte_name':x['analyte_name'],
                **{f'{year}_{key}':r[key] for year,r in [(2009,x),(2010,y)] for key in ['n_all','n_working','n_NP','R0_width','R1_width','R0_upper','R1_upper']}})
    write_csv(out/'temporal_label_audit.csv',labels)
    assert paired
    write_csv(out/'shared_label_cells.csv',paired)
    name09=defaultdict(set);name10=defaultdict(set)
    for a,r in c09.items():name09[norm(r['analyte_name'])].add(a)
    for a,r in c10.items():name10[norm(r['analyte_name'])].add(a)
    name_code_conflicts=[{'name':name,'codes_2009':sorted(name09[name]),'codes_2010':sorted(name10[name])}
                        for name in set(name09)&set(name10) if name09[name]!=name10[name]]
    shared_codes={r['analyte'] for r in paired}
    summary={'protocol_sha256':sha(B/'01_protocol/np_temporal_20261008.md'),
        'baseline_2009_aggregate_sha256':sha(baseline),
        'baseline_recalculation':'PASS: fresh2009 source FC results agree with prior aggregate table',
        'source_receipts':[m09,m10],'factors':list(FACTORS),'bins_ppb':list(EDGES),'thresholds_ppb':list(THRESHOLDS),
        'temporal':{'2009':year_summary(cells09),'2010':year_summary(cells10)},
        'shared_temporal':{'2009':year_summary([r for r in cells09 if r['analyte'] in shared_codes]),
                           '2010':year_summary([r for r in cells10 if r['analyte'] in shared_codes])},
        'label_match_status':dict(Counter(r['status'] for r in labels)), 'shared_working_cells':len(paired),
        'same_name_code_conflicts':name_code_conflicts,
        'NP_sensitivity':{str(year):{'all_cells':len(groups),'NP_cells':sum(any(r['state']=='NP' for r in rs) for rs in groups.values()),
            'finite_upper_by_factor':{f'{k:g}':sum(math.isfinite(r['upper']) for r in rows if r['factor']==k) for k in FACTORS},
            'invalid_NP_limits':sum(r['state']=='NP' and r['lod'] is None for rs in groups.values() for r in rs)} for year,groups,rows in [(2009,g09,r09),(2010,g10,r10)]},
        'reporting_template_rows':len(report09)+len(report10),'assertions':'PASS: fixed denominators, NP nesting, invariant non-NP cells, sufficient-statistic reconstruction, temporal interval nesting, source hashes/joins/keys',
        'boundary':'Finite NP caps are assumptions; temporal application is exploratory, not biological validation or a population time trend.'}
    (out/'summary.json').write_text(json.dumps(json_safe(summary),indent=2,allow_nan=False)+'\n')
    print(json.dumps(json_safe(summary),indent=2))

if __name__=='__main__':main()
