"""Editable Figure 8 from aggregate reporting results; no exposure inference."""
from pathlib import Path
import csv
import hashlib
import json
import math
import subprocess
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Text
from information_loss_20261008 import B, ROOT, paths


def read_csv(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    subprocess.run(['python3', str(ROOT/'05_code/utilities/check_paths.py')], check=True,
                   stdout=subprocess.DEVNULL)
    source = paths()['animal_food_outputs_root']/'dairy_egg_reporting_rechecked_20261013'
    strata = read_csv(source/'stratum_summary.csv')
    availability = read_csv(source/'availability.csv')
    cells = read_csv(source/'all_cells.csv')
    summary = json.loads((source/'summary.json').read_text())
    assert len(strata) == 5 and len(availability) == 28 and len(cells) == 1303
    keys = ['samples', 'analytical_rows', 'source_cells', 'working_cells',
            'mean_unchanged', 'mean_widened', 'full_unbounded', 'invalid_rows',
            'held_duplicate_cells', 'R0_nonpoint_above_10',
            'R1_nonpoint_above_10', 'R2_nonpoint_above_10']
    for r in strata:
        for k in keys:
            r[k] = int(r[k])
        assert r['mean_unchanged'] + r['mean_widened'] == r['working_cells']
        assert r['R0_nonpoint_above_10'] <= r['R1_nonpoint_above_10'] <= r['R2_nonpoint_above_10'] == r['working_cells']
        assert r['invalid_rows'] == r['held_duplicate_cells'] == 0
        group = [cell for cell in cells if cell['year']==r['year'] and cell['commodity']==r['commodity']]
        working = [cell for cell in group if int(cell['n_working']) > 0]
        assert len(group)==r['source_cells'] and len(working)==r['working_cells']
        assert sum(int(cell['n_all']) for cell in group)==r['analytical_rows']
        assert sum(math.isinf(float(cell['full_upper'])) for cell in group)==r['full_unbounded']
        assert sum(int(cell['n_NP']) > 0 for cell in group)==r['full_unbounded']
        assert sum(float(cell['R1_width']) > float(cell['R0_width'])+1e-10 for cell in working)==r['mean_widened']
        for level in ('R0','R1','R2'):
            assert sum(float(cell[f'{level}_above_10_upper']) > float(cell[f'{level}_above_10_lower'])+1e-12
                       for cell in working)==r[f'{level}_nonpoint_above_10']
    totals = {k: sum(r[k] for r in strata) for k in keys}
    assert (totals['source_cells'], totals['working_cells'], totals['mean_widened'],
            totals['mean_unchanged'], totals['full_unbounded']) == (1303,1257,16,1241,50)
    assert sum(int(r['sample_identifiers']) > 0 for r in availability) == 5
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':9,
        'axes.labelsize':9, 'xtick.labelsize':8.5, 'ytick.labelsize':8.5,
        'legend.fontsize':8.5, 'svg.fonttype':'none', 'pdf.fonttype':42,
        'axes.spines.top':False, 'axes.spines.right':False,
        'axes.linewidth':.6, 'savefig.facecolor':'white'})
    blue, orange, gray = '#0072B2', '#D55E00', '#666666'
    fig = plt.figure(figsize=(7.5,7.7), facecolor='white')
    a = fig.add_axes([.125,.66,.335,.21])
    b = fig.add_axes([.645,.66,.325,.21])
    c = fig.add_axes([.125,.22,.335,.25])
    d = fig.add_axes([.645,.22,.325,.25])
    labels = [f"{r['name']} {r['year']}" for r in strata]
    for ax in (a,b,c,d):
        ax.set_yticks(range(5), labels)
        ax.set_ylim(4.65,-.65)
        ax.tick_params(axis='y', length=0, pad=6)
        ax.grid(axis='x', color='#E6E6E6', linewidth=.5)
        ax.set_axisbelow(True)
        ax.spines['left'].set_visible(False)
    def heading(x,y,letter,title,subtitle):
        fig.text(x,y,f'{letter}  {title}',fontweight='bold',fontsize=10,va='top')
        fig.text(x,y-.027,subtitle,fontsize=8.5,color='#444444',va='top')
    heading(.045,.957,'A','Sparse archive coverage',
            '5 of 28 audited year–code strata; 2011–2024')
    heading(.565,.957,'B','Most mean bounds are unchanged',
            'R0 → R1: 16 / 1,257 working cells widen')
    heading(.045,.553,'C','Status alone loses threshold detail',
            'Non-point fraction bounds at >10 ppb')
    heading(.565,.553,'D','NP assumptions set a different limit',
            '50 / 1,303 source cells have no finite upper mean')
    for i,r in enumerate(strata):
        a.barh(i,r['analytical_rows'],height=.52,color=blue)
        a.text(r['analytical_rows']+6500,i,
               f"{r['analytical_rows']:,}\n({r['samples']:,})",va='center',fontsize=8.5)
    a.set_xlim(0,435000)
    a.set_xticks([0,100000,200000,300000],['0','100k','200k','300k'])
    a.set_xlabel('Analytical rows\n(sample IDs in parentheses)',labelpad=7)
    for i,r in enumerate(strata):
        same=100*r['mean_unchanged']/r['working_cells']
        wider=100*r['mean_widened']/r['working_cells']
        b.barh(i,same,height=.52,color=blue)
        b.barh(i,wider,left=same,height=.52,color=orange)
        b.text(105,i,f"{r['mean_unchanged']} | {r['mean_widened']}",va='center',fontsize=8.5)
    b.set_xlim(0,149)
    b.set_xticks([0,50,100],['0','50','100'])
    b.set_xlabel('Working cells (%)',labelpad=7)
    b.text(105,-.8,'Same | wider',fontsize=8.5,va='bottom')
    b.text(.0,-.35,'Blue: unchanged; orange: widened',transform=b.transAxes,
           fontsize=8.5,va='top')
    for level,offset,color,marker in [('R0',-.17,blue,'o'),('R1',0,orange,'D'),('R2',.17,gray,'s')]:
        values=[100*r[f'{level}_nonpoint_above_10']/r['working_cells'] for r in strata]
        c.scatter(values,[i+offset for i in range(5)],color=color,marker=marker,
                  s=23,label=level,zorder=3)
    c.set_xlim(-3,106)
    c.set_xticks([0,25,50,75,100])
    c.set_yticklabels([f"{label}\nn = {r['working_cells']}" for label,r in zip(labels,strata)])
    c.set_xlabel('Working cells with non-point bounds (%)',labelpad=7)
    c.legend(loc='lower left',bbox_to_anchor=(-.02,-.40),ncol=3,frameon=False,
             handletextpad=.35,columnspacing=1.0,borderaxespad=0)
    for i,r in enumerate(strata):
        share=100*r['full_unbounded']/r['source_cells']
        d.barh(i,share,height=.52,color=orange)
        d.text(share+.45,i,f"{r['full_unbounded']} / {r['source_cells']}",va='center',fontsize=8.5)
    d.set_xlim(0,16.2)
    d.set_xticks([0,4,8,12])
    d.set_xlabel('Observed source cells (%)',labelpad=7)
    d.text(0,-.25,'NP is restored as [0, ∞); no cap is assumed.',
           transform=d.transAxes,fontsize=8.5,va='top')
    fig.text(.045,.109,'Cells are year–commodity–analyte groups; records and sample IDs are not interchangeable.',fontsize=8.5)
    fig.text(.045,.086,'R0: reported magnitudes / limits.  R1: fixed bins + ND limits.  R2: status counts only.',fontsize=8.5)
    fig.text(.045,.063,'Denominators are observed cells, not potential untested combinations. Missing codes are not non-detections.',fontsize=8.5)
    fig.text(.045,.040,'Conditional reporting calculations; >10 ppb is a reporting probe, not a safety threshold or predictive validation.',fontsize=8.5)
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    texts=[t for t in fig.findobj(Text) if t.get_visible() and t.get_text() and t.get_window_extent(renderer).width>0]
    outside=[]
    for t in texts:
        bb=t.get_window_extent(renderer)
        if bb.x0 < -.5 or bb.y0 < -.5 or bb.x1 > fig.bbox.x1+.5 or bb.y1 > fig.bbox.y1+.5:
            outside.append(t.get_text())
    assert not outside, outside
    # Meaningful text-box collisions: tick text, annotations, headings and labels.
    collisions=[]
    for i,t in enumerate(texts):
        p=t.get_window_extent(renderer)
        for u in texts[i+1:]:
            q=u.get_window_extent(renderer)
            if min(p.x1,q.x1)-max(p.x0,q.x0)>1 and min(p.y1,q.y1)-max(p.y0,q.y0)>1:
                collisions.append([t.get_text(),u.get_text()])
    out=B/'06_outputs/figures';out.mkdir(parents=True,exist_ok=True)
    target=out/'figure8_dairy_egg_reporting'
    for ext in ('svg','pdf','png'):
        fig.savefig(target.with_suffix('.'+ext),dpi=350)
    svg=ET.parse(target.with_suffix('.svg')).getroot()
    assert not svg.findall('.//{http://www.w3.org/2000/svg}image')
    assert len(svg.findall('.//{http://www.w3.org/2000/svg}text'))>50
    qa={'figure_inches':[7.5,7.7], 'minimum_font_pt':min(t.get_fontsize() for t in texts),
        'minimum_font_at_6_5in_width_pt':min(t.get_fontsize() for t in texts)*6.5/7.5,
        'outside_text':outside, 'text_bbox_collisions':collisions,
        'native_svg_text':True,'raster_images_in_svg':0,
        'visual_review':'REQUIRED_AFTER_RENDER','scope':'Aggregate reporting diagnostics, not validation'}
    (out/'figure8_dairy_egg_layout_qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    assert not collisions, collisions
    metrics={'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [source/'stratum_summary.csv',source/'availability.csv',source/'all_cells.csv',source/'summary.json']},
        'input_directory_relative_to_animal_food_outputs':'dairy_egg_reporting_rechecked_20261013',
        'strata':strata,'totals':totals,'audited_year_code_strata':len(availability),
        'widened_working_percent':100*totals['mean_widened']/totals['working_cells'],
        'full_unbounded_source_percent':100*totals['full_unbounded']/totals['source_cells'],
        'threshold_ppb':10,'threshold_interpretation':'non-regulatory reporting probe',
        'source_status':summary['status']}
    (out/'figure8_dairy_egg_plot_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps(qa,indent=2))
    plt.close(fig)


if __name__=='__main__':
    main()
