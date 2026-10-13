"""Metadata-gated, fixed-rule milk/egg reporting experiment; no exposure model."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,hashlib,io,json,math,re,subprocess,zipfile
from information_loss_20261008 import paths,metrics,envelope,finite,write_csv,json_safe,THRESHOLDS,B,ROOT

UNIT={'B':1.,'M':1000.,'T':.001}
FOODS={'MK':'Milk','EG':'Eggs'}

def require(condition,message):
    if not condition:raise ValueError(message)

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def pdf_text(z,name):
    return subprocess.check_output(['pdftotext','-layout','-','-'],input=z.read(name)).decode()

def interval(flag,value,lod,unit):
    if unit not in UNIT:return None
    if flag=='ND':
        x=finite(lod,True)
        return (0.,x*UNIT[unit]) if x is not None and value=='' else None
    if flag in ('O','R'):
        x=finite(value)
        return (x*UNIT[unit],x*UNIT[unit]) if x is not None else None
    return None

def names_from_reference(text):
    names={}
    for line in text.splitlines():
        m=re.match(r'^\s*([A-Z0-9]{3})\s{2,}(.+?)\s{2,}([A-Z])\s+([\d,]+)\s*$',line)
        if m:names[m[1]]=m[2]
    return names

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-name',default='dairy_egg_reporting_20261013')
    args=parser.parse_args()
    require(re.fullmatch(r'[A-Za-z0-9_-]+',args.output_name) is not None,'Unsafe output directory name')
    subprocess.run(['python3',str(ROOT/'05_code/utilities/check_paths.py')],check=True,stdout=subprocess.DEVNULL)
    c=paths();out=c['animal_food_outputs_root']/args.output_name
    out.mkdir(parents=True,exist_ok=False)
    protocol=B/'01_protocol/dairy_egg_reporting_extension_20261013.md'
    (out/'protocol_sha256.txt').write_text(digest(protocol)+'\n')
    with (ROOT/'00_admin/download_manifest.csv').open(encoding='utf-8-sig',newline='') as f:manifest=list(csv.DictReader(f))
    receipts=[];availability=[];cells=[];retained=[];statistics=[];summaries=[];coverage=[];unit_evidence=[]
    for year in range(2011,2025):
        source=c['raw_data_root']/('other/2024PDPDatabase.zip' if year==2024 else f'usda_pdp/{year}PDPDatabase.zip')
        match=[r for r in manifest if r['local_file_path']==str(source)]
        hash_before=digest(source)
        require(any(r['sha256']==hash_before for r in match),f'Source manifest mismatch: {source.name}')
        with zipfile.ZipFile(source) as z:
            require(z.testzip() is None,'ZIP integrity failure')
            reference_name=next(n for n in z.namelist() if 'reference' in n.lower() and n.lower().endswith('.pdf'))
            reference=pdf_text(z,reference_name)
            dictionary_name=next(n for n in z.namelist() if 'dictionary' in n.lower() and n.lower().endswith('.pdf'))
            dictionary=pdf_text(z,dictionary_name)
            sample_name=next(n for n in z.namelist() if n.lower().endswith('samples.txt'))
            sample_codes={};sample_types=Counter();counts=Counter()
            with z.open(sample_name) as f:
                for row in csv.reader(io.TextIOWrapper(f,encoding='latin1'),delimiter='|'):
                    require(len(row)>=8 and row[0] not in sample_codes,'Invalid/repeated sample key')
                    sample_codes[row[0]]=row[6];counts[row[6]]+=1
            decoded={}
            for line in reference.splitlines():
                m=re.match(r'^\s*([A-Z]{2})\s{2,}([A-Za-z][A-Za-z ,()-]*?)\s{2,}([\d,]+)\s*$',line)
                if m:decoded[m[1]]=(m[2].strip(),int(m[3].replace(',','')))
            selected=[]
            for food,label in FOODS.items():
                n=counts[food]
                if n:
                    require(food in decoded and decoded[food]==(label,n),'Commodity label/provider-count mismatch')
                    selected.append(food)
                availability.append({'year':year,'commodity':food,'name':label,'sample_identifiers':n,
                                     'status':'ADMITTED_REPORTING_EXPERIMENT' if n else 'NO_SAMPLES_OF_THIS_CODE_IN_ARCHIVE'})
            receipts.append({'year':year,'file':source.name,'relative_raw_path':str(source.relative_to(c['raw_data_root'])),
                             'sha256':hash_before,'manifest_match':True,'zip_crc':'PASS','sample_rows':len(sample_codes),
                             'reference_member':reference_name,'dictionary_member':dictionary_name,
                             'official_url':next(r['official_url'] for r in match if r['sha256']==hash_before)})
            if not selected:
                require(digest(source)==hash_before,'Raw source changed while reading')
                continue
            unit_line=next((line.strip() for line in dictionary.splitlines() if line.strip().startswith('CONUNIT')), '')
            require('Concentration/LOD unit of measure (M=ppm, B=ppb, T=ppt)' in unit_line,'Unit semantics not verified')
            unit_evidence.append({'year':year,'dictionary_member':dictionary_name,
                'dictionary_page_1_based':dictionary.splitlines() and dictionary[:dictionary.index(unit_line.split()[0])].count('\f')+1,
                'unit_field_excerpt':unit_line,'converted_basis':'ppb','M_factor':1000,'B_factor':1,'T_factor':0.001})
            for token in ('SAMPLE_PK','COMMOD','PESTCODE','CONCEN','LOD','CONUNIT','MEAN'):
                require(token in dictionary,'Required dictionary field missing')
            for token in ('Non-Detect: Validated, well-recovered','Non-Detect: Marginal Performing Analyte','Detect: Original Extraction Value','Detect: Re-extraction Analysis Value'):
                require(token in reference,'Unknown status semantics')
            analytes=names_from_reference(reference)
            group=defaultdict(list);keys=Counter();all_rows=0;units=Counter();flags=Counter()
            result_name=next(n for n in z.namelist() if n.lower().endswith('results.txt'))
            with z.open(result_name) as f:
                for row in csv.reader(io.TextIOWrapper(f,encoding='latin1'),delimiter='|'):
                    all_rows+=1
                    require(len(row)>=16 and row[0] in sample_codes,'Result schema/unmatched key')
                    if sample_codes[row[0]] not in selected:continue
                    require(row[1]==sample_codes[row[0]],'Result/sample food mismatch')
                    food,analyte=row[1],row[4]
                    keys[(row[0],analyte)]+=1
                    group[food,analyte].append((row[0],row[13].strip(),row[6].strip(),row[7].strip(),row[8].strip()))
                    units[row[8].strip()]+=1;flags[row[13].strip()]+=1;sample_types[food,row[2].strip()]+=1
            receipts[-1].update(result_member=result_name,programme_result_rows=all_rows,selected_unit_counts=dict(units),selected_state_counts=dict(flags))
            instruction_name=next(n for n in z.namelist() if 'instruction' in n.lower() and n.lower().endswith('.pdf'))
            instruction=pdf_text(z,instruction_name)
            expected_samples=re.search(r'holds\s+([\d,]+)\s+Sample Information',instruction)
            expected_results=re.search(r'holds\s+([\d,]+)\s+Analytical Results',instruction)
            require(expected_samples and expected_results,'Programme total evidence missing')
            require(int(expected_samples[1].replace(',',''))==len(sample_codes),'Provider sample total mismatch')
            require(int(expected_results[1].replace(',',''))==all_rows,'Provider result total mismatch')
            receipts[-1].update(instruction_member=instruction_name,provider_programme_totals='PASS',
                               source_hash_after=digest(source),unit_semantics_checked=True)
            for (food,analyte),records in sorted(group.items()):
                require(analyte in analytes,f'Unresolved analyte label: {year}/{analyte}')
                duplicate=sum(keys[s,analyte]>1 for s,_,_,_,_ in records)
                coverage.append({'year':year,'commodity':food,'analyte':analyte,'commodity_sample_identifiers':counts[food],
                    'observed_unique_sample_identifiers':len({r[0] for r in records}),'observed_result_rows':len(records),
                    'coverage_fraction':len({r[0] for r in records})/counts[food],
                    'unobserved_sample_analyte_combinations':counts[food]-len({r[0] for r in records}),
                    'unobserved_combinations_imputed':False})
                base={'year':year,'commodity':food,'commodity_name':FOODS[food],'analyte':analyte,'analyte_name':analytes[analyte],
                      'n_all':len(records),'n_NP':sum(f=='NP' for _,f,_,_,_ in records),'duplicate_record_rows':duplicate}
                if duplicate:
                    base.update(status='HELD_REPEATED_SAMPLE_ANALYTE_KEY',n_working=0,n_invalid=len(records)-base['n_NP'])
                    cells.append(base);continue
                h={level:Counter() for level in ('R0','R1','R2')};invalid=0;direct=[]
                for sample,flag,value,lod,unit in records:
                    if flag=='NP':continue
                    pair=interval(flag,value,lod,unit)
                    if pair is None:invalid+=1;continue
                    direct.append(pair);h['R0'][pair]+=1
                    h['R1'][envelope(pair[0]) if flag in ('O','R') else pair]+=1
                    h['R2'][0.,math.inf]+=1
                base.update(status='WORKING_INTERVALS' if direct else 'NO_WORKING_SUBSET',n_working=len(direct),n_invalid=invalid)
                full=h['R0'].copy()
                if base['n_NP']+invalid:full[0.,math.inf]+=base['n_NP']+invalid
                if direct:
                    ms={level:metrics(hist) for level,hist in h.items()}
                    require(math.isclose(ms['R0']['lower'],sum(a for a,b in direct)/len(direct),abs_tol=1e-12),'Direct lower mismatch')
                    require(math.isclose(ms['R0']['upper'],sum(b for a,b in direct)/len(direct),abs_tol=1e-12),'Direct upper mismatch')
                    for level,hist in h.items():
                        base.update({f'{level}_{k}':v for k,v in ms[level].items() if k!='n'})
                        for (lo,hi),n in sorted(hist.items()):retained.append({'year':year,'commodity':food,'analyte':analyte,'level':level,'lower_ppb':lo,'upper_ppb':hi,'count':n})
                        st={'year':year,'commodity':food,'analyte':analyte,'level':level,'n':len(direct),
                            'sum_lower_ppb':sum(a*k for (a,b),k in hist.items()),'sum_upper_ppb':sum(b*k for (a,b),k in hist.items())}
                        for t in THRESHOLDS:
                            for side,idx in [('lower',0),('upper',1)]:st[f'count_{side}_above_{t:g}']=sum(k for pair,k in hist.items() if pair[idx]>t)
                        statistics.append(st)
                    for a,b in [('R0','R1'),('R1','R2')]:
                        for prefix in ['',*(f'above_{t:g}_' for t in THRESHOLDS)]:
                            require(ms[b][prefix+'lower']<=ms[a][prefix+'lower']+1e-10 and ms[b][prefix+'upper']+1e-10>=ms[a][prefix+'upper'],'Enclosure violation')
                fm=metrics(full);require(fm['n']==len(records),'Full denominator changed')
                base.update(full_lower=fm['lower'],full_upper=fm['upper'])
                cells.append(base)
            for food in selected:
                cs=[r for r in cells if r['year']==year and r['commodity']==food];ws=[r for r in cs if r['n_working']]
                summary={'year':year,'commodity':food,'name':FOODS[food],'samples':counts[food],'analytical_rows':sum(r['n_all'] for r in cs),
                         'source_cells':len(cs),'working_cells':len(ws),'held_duplicate_cells':sum(bool(r['duplicate_record_rows']) for r in cs),
                         'NP_rows':sum(r['n_NP'] for r in cs),'invalid_rows':sum(r['n_invalid'] for r in cs),
                         'working_rows':sum(r['n_working'] for r in cs),
                         'mean_unchanged':sum(math.isclose(r['R0_lower'],r['R1_lower'],abs_tol=1e-10) and math.isclose(r['R0_upper'],r['R1_upper'],abs_tol=1e-10) for r in ws),
                         'mean_widened':sum(not(math.isclose(r['R0_lower'],r['R1_lower'],abs_tol=1e-10) and math.isclose(r['R0_upper'],r['R1_upper'],abs_tol=1e-10)) for r in ws),
                         'R1_unbounded':sum(math.isinf(r['R1_upper']) for r in ws),
                         'full_unbounded':sum('full_upper' in r and math.isinf(r['full_upper']) for r in cs)}
                for t in THRESHOLDS:
                    for level in ('R0','R1','R2'):summary[f'{level}_nonpoint_above_{t:g}']=sum(r[f'{level}_above_{t:g}_upper']-r[f'{level}_above_{t:g}_lower']>1e-12 for r in ws)
                summaries.append(summary)
            receipts[-1]['commodity_type_result_counts']={f'{f}/{t}':n for (f,t),n in sample_types.items()}
        require(digest(source)==hash_before,'Raw source changed while reading')
        print(json.dumps({'year':year,'selected':selected,'state':'READ_ONLY_COMPLETE'},ensure_ascii=False),flush=True)
    # Union schema preserves unavailable values as blank, never zero.
    fields=list(dict.fromkeys(k for r in cells for k in r))
    with (out/'all_cells.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cells)
    for name,data in [('availability.csv',availability),('retained_histograms.csv',retained),('filled_reporting_statistics.csv',statistics),('stratum_summary.csv',summaries),('coverage.csv',coverage)]:write_csv(out/name,data)
    (out/'source_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
    (out/'coverage_and_units.json').write_text(json.dumps({'status':'PROVIDER_TOTALS_AND_UNIT_DEFINITIONS_CHECKED',
        'unit_evidence':unit_evidence,'denominator':'Observed analytical result records; never all possible sample-analyte pairs',
        'coverage_cells':len(coverage),'commodity_type_counts_unit':'Analytical result rows, not samples',
        'analysis_code_sha256':digest(Path(__file__)),'unobserved_combinations_imputed':False},indent=2)+'\n')
    result={'status':'POST_PILOT_REPORTING_EXTENSION_NOT_SCIENTIFIC_VALIDATION','protocol_sha256':digest(protocol),
            'source_years_metadata_audited':14,'admitted_source_years':sorted({r['year'] for r in summaries}),
            'strata':summaries,'source_cells':len(cells),'reporting_statistic_rows':len(statistics),'raw_records_exported':False,
            'new_source_downloads':0,'exposure_model':False,'parent_and_original_2009_2010_results_changed':False}
    (out/'summary.json').write_text(json.dumps(json_safe(result),indent=2)+'\n')
    print(json.dumps({'output':str(out),'cells':len(cells),'strata':summaries},indent=2),flush=True)

if __name__=='__main__':main()
