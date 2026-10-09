#!/usr/bin/env python3
"""Recompute aggregate figure data from immutable archives; no exposure estimation."""
import csv
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_reproducibility_bundle import read_paths, PROJECT
from harmonise_pilot import classify, read_mtx_mapping
from audit_pilot_semantics import finite_numeric
from figure_quality import inspect_figure

BRANCH = Path(__file__).resolve().parents[1]
OUT = BRANCH / '06_outputs/figures'
BLUE, ORANGE, GREEN, GRAY = '#0072B2', '#D55E00', '#009E73', '#999999'
STEMS = {2: 'figure2_selection_diagnostics', 3: 'figure3_result_semantics', 4: 'figure4_source_discrepancies'}

def audit(path, mapping):
    samples, selected, cereal = set(), Counter(), Counter()
    types, numeric = Counter(), Counter()
    strategy = defaultdict(set)
    total = 0
    with zipfile.ZipFile(path) as z:
        members = [n for n in z.namelist() if n.lower().endswith('.csv')]
        assert len(members) == 1 and z.testzip() is None
        with z.open(members[0]) as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
                total += 1
                sid = r['sampId_A']
                assert sid
                samples.add(sid)
                code = r['sampMatCode.base.building']
                if classify(mapping.get(code, '')) != 'animal_food_candidate':
                    continue
                selected[sid] += 1
                strategy[r['sampStrategy']].add(sid)
                types[r['resType']] += 1
                if finite_numeric(r['resVal']):
                    numeric[r['resType']] += 1
                if code == 'A03QY':
                    cereal[sid] += 1
    assert sum(map(len, strategy.values())) == len(selected), 'Sample has multiple strategies'
    return dict(all_rows=total, all_samples=len(samples), candidate_rows=sum(selected.values()),
                candidate_samples=len(selected), result_types=dict(types), numeric_types=dict(numeric),
                strategy_samples={k:len(v) for k,v in strategy.items()},
                rows_per_sample_histogram={str(k):v for k,v in sorted(Counter(selected.values()).items())},
                cereal_samples=len(cereal), cereal_rows=sum(cereal.values()))

def panel(ax, letter, title):
    ax.set_title(f'{letter}  {title}', loc='left', fontsize=10, weight='bold', pad=12)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=8.5)

def save(fig, number):
    inspect_figure(fig, OUT / f'{STEMS[number]}_layout_qa.json')
    for ext in ('svg', 'pdf', 'png'):
        fig.savefig(OUT / f'{STEMS[number]}.{ext}', dpi=300, facecolor='white')
    plt.close(fig)

def bars(ax, values, labels, colors, ylabel):
    ax.bar(labels, values, color=colors, width=.55)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(values)*1.28)
    for i,v in enumerate(values):
        ax.text(i,v, f'{v:,}', ha='center', va='bottom', fontsize=9)

def figures(data):
    from publication_figures import figures as narrative_figures
    return narrative_figures(data)
    # Historical rendering retained below for comparison; execution uses v2.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none',
                        'svg.hashsalt':'afft-multipanel-v1','pdf.fonttype':42, 'axes.labelsize':9})
    p, v = data['pesticide'], data['veterinary_drug']
    fig, aa = plt.subplots(2,2,figsize=(7.5,6.5),layout='constrained')
    for ax, d, letter, title in zip(aa[0],[p,v],'AB',['Pesticide archive screen','Veterinary archive screen']):
        panel(ax,letter,title)
        bars(ax,[d['all_samples'],d['candidate_samples']],['Archive','Keyword\ncandidates'],[GRAY,BLUE],'Unique sample identifiers')
        ax.text(.98,.95,f"Retained: {d['candidate_samples']/d['all_samples']:.1%}",transform=ax.transAxes,ha='right',va='top')
    ax=aa[1,0]; panel(ax,'C','Cereal false-positive contribution')
    vals=[100*p['cereal_samples']/p['candidate_samples'],100*p['cereal_rows']/p['candidate_rows']]
    ax.bar(['Samples','Result rows'],vals,color=ORANGE,width=.55); ax.set_ylim(0,45); ax.set_ylabel('Share of keyword candidates (%)')
    for i,(x,n,d) in enumerate(zip(vals,[p['cereal_samples'],p['cereal_rows']],[p['candidate_samples'],p['candidate_rows']])):
        ax.text(i,x,f'{n:,}/{d:,}\n{x:.1f}%',ha='center',va='bottom')
    ax=aa[1,1]; panel(ax,'D','Candidate sampling strategies')
    for y,(d,label) in enumerate([(p,'Pesticide'),(v,'Veterinary')]):
        start=0
        for code,color in [('ST20A',BLUE),('ST10A',ORANGE)]:
            n=d['strategy_samples'].get(code,0); w=n/d['candidate_samples']*100
            ax.barh(y,w,left=start,color=color,height=.5,label=code if y==0 else None); start+=w
        ax.text(0,y+.32,f"Selective {d['strategy_samples'].get('ST20A',0):,}; objective {d['strategy_samples'].get('ST10A',0):,}",fontsize=8.5)
    ax.set_yticks([0,1],['Pesticide','Veterinary']); ax.set_xlim(0,100); ax.set_ylim(-.6,1.65)
    ax.set_xlabel('Share of candidate samples (%)'); ax.legend(loc='upper center',bbox_to_anchor=(.5,-.2),ncol=2,fontsize=8.5,frameon=False)
    save(fig,2)

    fig, aa = plt.subplots(2,2,figsize=(7.5,6.5),layout='constrained')
    for ax,d,letter,title in zip(aa[0],[p,v],'AB',['Pesticide result coding','Veterinary result coding']):
        panel(ax,letter,title)
        codes=sorted(d['result_types']); counts=[d['result_types'][c] for c in codes]
        ax.bar(codes,counts,color=BLUE,width=.55); ax.set_yscale('log'); ax.set_ylim(.8,max(counts)*8)
        ax.set_ylabel('Candidate result rows (log scale)')
        for i,n in enumerate(counts): ax.text(i,n,f'{n:,}',ha='center',va='bottom',fontsize=8.5)
    ax=aa[1,0]; panel(ax,'C','Numeric-bearing result rows')
    for i,d in enumerate([p,v]):
        start=0
        for code,color in [('VAL',GREEN),('LOQ',ORANGE)]:
            n=d['numeric_types'].get(code,0); ax.bar(i,n,bottom=start,color=color,label=code if i==0 else None,width=.55)
            if n < 3:
                ax.annotate(str(n),(i+.27,start+n/2),xytext=(8,0),textcoords='offset points',ha='left',va='center',fontsize=9)
            else:
                ax.text(i,start+n/2,str(n),ha='center',va='center',fontsize=9,color='white')
            start+=n
        assert set(d['numeric_types']) <= {'VAL','LOQ'}
    ax.set_xticks([0,1],['Pesticide','Veterinary']); ax.set_ylabel('Rows with finite numeric resVal'); ax.set_ylim(0,48); ax.legend(frameon=False,fontsize=8.5)
    ax=aa[1,1]; panel(ax,'D','Rows per candidate sample')
    for d,label,color in [(p,'Pesticide',BLUE),(v,'Veterinary',ORANGE)]:
        h=d['rows_per_sample_histogram']; x=np.array([int(k) for k in h]); n=np.array(list(h.values()))
        ax.step(x,np.cumsum(n)/sum(n),where='post',label=f'{label} (n={sum(n):,})',color=color)
    ax.set_xscale('log'); ax.set_ylim(0,1.05); ax.set_xlabel('Result rows per sample (log scale)'); ax.set_ylabel('Cumulative fraction of samples'); ax.legend(fontsize=8.5,frameon=False,loc='lower right')
    save(fig,3)

    fig,aa=plt.subplots(1,3,figsize=(7.5,3.3),layout='constrained')
    s=data['source_discrepancies']; nominal=s['nominal_middle_ppm']; tissue=s['day7_high_dose_kidney_mg_kg']
    panel(aa[0],'A','Nominal middle dose'); bars(aa[0],[nominal['summary'],nominal['evaluation']],['Summary','Full\nevaluation'],[GRAY,BLUE],'Reported feed dose (ppm)')
    panel(aa[1],'B','Week-2 deviation'); bars(aa[1],[nominal['evaluation'],s['middle_week2_ppm']],['Nominal','Week 2\nrecorded'],[BLUE,ORANGE],'Reported feed dose (ppm)')
    panel(aa[2],'C','Day-7 kidney conflict')
    for i,label in enumerate(['glyphosate','AMPA']):
        vals=[tissue[k][label] for k in ['table124','prose']]
        aa[2].plot([0,1],vals,'o--',color=[BLUE,ORANGE][i],label=label)
        for x,y in enumerate(vals): aa[2].annotate(f'{y:.2f}',(x,y),xytext=(0,6),textcoords='offset points',ha='center',fontsize=8.5)
    aa[2].set_xticks([0,1],['Table 124','Adjacent\nprose']); aa[2].set_xlim(-.3,1.3); aa[2].set_ylim(0,.18); aa[2].set_ylabel('Reported concentration (mg/kg)'); aa[2].legend(fontsize=8.5,frameon=False,loc='upper left')
    save(fig,4)

def main():
    subprocess.run([sys.executable,str(PROJECT/'05_code/utilities/check_paths.py')],check=True,stdout=subprocess.DEVNULL)
    paths=read_paths(); raw=paths['animal_food_raw_root']; OUT.mkdir(parents=True,exist_ok=True)
    mapping,_=read_mtx_mapping(raw/'efsa_catalogues_2026/DCF_catalogues.zip')
    files={'pesticide':'efsa_pesticides_luxembourg/MOPER_ALL_DATA_SSD2_2024_LU.ZIP', 'veterinary_drug':'efsa_vmpr_belgium/VMPR_2024_BE.ZIP'}
    data={key:audit(raw/rel,mapping) for key,rel in files.items()}
    assert (data['pesticide']['candidate_samples'], data['pesticide']['candidate_rows'])==(56,12824)
    assert (data['veterinary_drug']['candidate_samples'], data['veterinary_drug']['candidate_rows'])==(8270,239803)
    data['provenance']={rel:hashlib.sha256((raw/rel).read_bytes()).hexdigest() for rel in [*files.values(),'efsa_catalogues_2026/DCF_catalogues.zip','validation_sources/JMPR_2005_Glyphosate_evaluation.pdf']}
    data['source_discrepancies']={'study':'MSL6729','locator':'FAO/WHO 2005 glyphosate evaluation, printed pp. 466–467, Tables 123–124 and adjacent prose; summary glyphosate section', 'nominal_middle_ppm':{'summary':100,'evaluation':120},'middle_week2_ppm':160,'day7_high_dose_kidney_mg_kg':{'table124':{'glyphosate':.05,'AMPA':.07},'prose':{'glyphosate':.13,'AMPA':.08}}}
    data['boundary']='Aggregate post-pilot diagnostic audit. Keywords are not validated eligibility; numeric-bearing LOQ rows are not uncensored detections. No population prevalence, exposure, model accuracy or biological independence is inferred. Source discrepancies are not independent experiments.'
    (OUT/'multipanel_calculation_data.json').write_text(json.dumps(data,indent=2)+'\n')
    figures(data)
    print(json.dumps(data,indent=2))

def bundle():
    names=['build_multipanel_figures.py','build_gate_figure.py','figure_quality.py','publication_figures.py',
           'test_multipanel_figures.py','build_reproducibility_bundle.py','harmonise_pilot.py','audit_pilot_semantics.py']
    files=[BRANCH/'05_code'/n for n in names]
    files += [OUT/'multipanel_calculation_data.json',OUT/'MULTIPANEL_README.md',BRANCH/'08_review/figure_evidence_adequacy_20260930.md']
    files += [BRANCH/'08_review/reference_count_and_citation_audit_20260930.json']
    for stem in ['figure1_noncompensatory_evidence_gate',*STEMS.values()]:
        files += [OUT/f'{stem}.{ext}' for ext in ['svg','pdf','png']]
        files.append(OUT/f'{stem}_layout_qa.json')
    target=BRANCH/'09_submission/Food_Control_editable_figures_and_calculations_20260930.zip'
    manifest={}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:
            name=str(p.relative_to(PROJECT)); payload=p.read_bytes()
            z.writestr(name,payload); manifest[name]=hashlib.sha256(payload).hexdigest()
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest.items())
    print(target)

if __name__=='__main__':
    if '--bundle' in sys.argv:
        bundle()
    elif '--plot-only' in sys.argv:
        figures(json.loads((OUT/'multipanel_calculation_data.json').read_text()))
    else:
        main()
