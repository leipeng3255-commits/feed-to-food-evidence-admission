"""Figure7 from saved summaries: assumptions, denominator accounting and replication."""
import csv
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from information_loss_20261008 import B,paths

def main():
    p=paths()['animal_food_outputs_root']/'np_temporal_20261008'
    s=json.loads((p/'summary.json').read_text())
    with (p/'NP_scenarios_all_cells.csv').open() as f:rs=list(csv.DictReader(f))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,
        'axes.labelsize':9,'xtick.labelsize':8.2,'ytick.labelsize':8.2,'legend.fontsize':8.2,
        'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(7.5,6.5),layout='constrained')
    a,b,c,d=axes.ravel();blue='#0072B2';orange='#E69F00';gray='#A0A0A0'
    x=np.arange(5);w=.34
    for j,year in enumerate(['2009','2010']):
        ns=s['NP_sensitivity'][year];total=ns['all_cells']
        vals=[total-ns['finite_upper_by_factor'][k] for k in ['1','2','5','10','inf']]
        bars=a.bar(x+(j-.5)*w,vals,width=w,color=[blue,orange][j],label=f'{year}: {total} cells')
        a.bar_label(bars,padding=2,fontsize=8.2)
    a.set_xticks(x,['1','2','5','10','No cap']);a.set_ylim(0,48)
    a.set_xlabel('Assumed NP upper bound / recorded LOD');a.set_ylabel('Cells with unbounded means')
    a.set_title('A  Calculability depends on the cap',loc='left',fontweight='bold')
    a.legend(loc='upper left',frameon=False)
    ratios={}
    for year,color in [('2009',blue),('2010',orange)]:
        groups={}
        for r in rs:
            if r['year']==year and int(r['n_NP']):groups.setdefault((r['commodity'],r['analyte']),{})[r['factor']]=r
        vals=[]
        for group in groups.values():
            lo=float(group['1.0']['upper']);hi=float(group['10.0']['upper'])
            if lo>0 and math.isfinite(hi):vals.append(hi/lo)
        v=np.sort(vals);ratios[year]=v.tolist()
        b.step(v,np.arange(1,len(v)+1)/len(v),where='post',color=color,linestyle='-' if year=='2009' else '--',linewidth=1.5,label=f'{year}: {len(v)} NP cells')
        b.plot(v[-1],1,'o' if year=='2009' else 's',color=color,markersize=4)
    b.set_ylim(0,1.06);b.set_xlim(1,10.5);b.set_ylabel('Cumulative fraction of NP cells')
    b.set_xlabel('Upper mean at cap 10 / upper mean at cap 1')
    b.set_title('B  Numerical upper bounds are sensitive',loc='left',fontweight='bold')
    b.legend(loc='upper left',frameon=False)
    b.text(.03,.37,'24 / 31 (2009) and 20 / 20 (2010)\nare pure-NP cells: ratio = 10\nby construction, not validation',transform=b.transAxes,fontsize=8.2)
    x2=np.arange(2);bottom=np.zeros(2)
    categories=[('R1_unchanged','Unchanged',blue),('R1_wider','Widened',orange),('excluded','No ND/detection subset',gray)]
    for key,label,color in categories:
        vals=np.array([s['temporal'][y]['all_cells']-s['temporal'][y]['working_cells'] if key=='excluded' else s['temporal'][y][key] for y in ['2009','2010']])
        bars=c.bar(x2,vals,bottom=bottom,color=color,width=.55,label=label)
        for i,(bar,v) in enumerate(zip(bars,vals)):
            if v:c.text(i,bottom[i]+v/2,str(v),ha='center',va='center',color='white' if color==blue else 'black',fontsize=8.2)
        bottom+=vals
    c.set_xticks(x2,['2009 catfish','2010 catfish']);c.set_ylim(0,300)
    c.set_ylabel('All source commodity–analyte cells');c.set_title('C  Fixed bins applied across years',loc='left',fontweight='bold')
    c.legend(loc='upper left',frameon=False,fontsize=8.2)
    for year,color in [('2009',blue),('2010',orange)]:
        for level,style,marker in [('R0','-','o'),('R1','--','s')]:
            vals=[s['shared_temporal'][year]['nonpoint_exceedance'][level][str(t)] for t in [2,10,20]]
            d.plot([2,10,20],np.array(vals)/175,linestyle=style,marker=marker,color=color,linewidth=1.3,markersize=4,label=f'{year} {level}')
    d.set_xticks([2,10,20]);d.set_ylim(0,1)
    d.set_xlabel('Illustrative threshold (ppb)');d.set_ylabel('Fraction of cells with non-point bounds')
    d.set_title('D  Same 175 working analyte labels',loc='left',fontweight='bold')
    d.legend(loc='upper right',frameon=False,ncol=2,fontsize=8.2)
    for ax in axes.ravel():ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    out=B/'06_outputs/figures'
    for ext in ['svg','pdf','png']:fig.savefig(out/f'figure7_np_temporal.{ext}',dpi=350)
    (p/'figure7_plot_metrics.json').write_text(json.dumps({'NP_upper_ratio_by_year':ratios,'shared_working_cells_per_year':175},indent=2)+'\n')
    plt.close(fig)

if __name__=='__main__':main()
