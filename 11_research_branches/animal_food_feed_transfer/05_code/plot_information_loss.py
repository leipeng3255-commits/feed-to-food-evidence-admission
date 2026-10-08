"""Editable, quantitative Figure 6 from aggregate tables; no individual records."""
import csv
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from information_loss_20261008 import paths, B, COMMODITIES

def main():
    data=paths()['animal_food_outputs_root']/'information_loss_20261008'
    with (data/'all_cells.csv').open() as f: allrows=list(csv.DictReader(f))
    rows=[r for r in allrows if int(r['n_working'])]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,
        'axes.labelsize':9,'xtick.labelsize':8.2,'ytick.labelsize':8.2,'legend.fontsize':8.2,
        'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(7.5,6.4),layout='constrained')
    a,b,c,d=axes.ravel(); codes=list(COMMODITIES); x=np.arange(3)
    colors=['#0072B2','#E69F00','#009E73']
    bottom=np.zeros(3)
    for col,label,color in zip(['n_ND','n_NP','n_O'],['ND','NP: marginal method','O: detected'],colors):
        values=np.array([sum(int(r[col]) for r in allrows if r['commodity']==k) for k in codes])
        a.bar(x,values/1000,bottom=bottom/1000,color=color,label=label,width=.65)
        bottom+=values
    for i,v in enumerate(bottom):a.text(i,v/1000+2,f'{int(v):,}',ha='center',fontsize=8.2)
    a.set_xticks(x,['Beef fat','Beef muscle','Catfish']);a.set_ylim(0,125)
    a.set_ylabel('Analytical records (thousands)');a.set_title('A  Preserve analytical status',loc='left',fontweight='bold')
    a.legend(loc='upper left',fontsize=8.2)
    levels=['R0','R1','R2']
    bounded=[sum(math.isfinite(float(r[l+'_upper'])) for r in rows) for l in levels]
    b.bar(x,bounded,color='#0072B2',width=.65,label='Finite upper bound')
    b.bar(x,466-np.array(bounded),bottom=bounded,color='#E69F00',width=.65,label='Unbounded')
    for i,v in enumerate(bounded):b.text(i,480,f'{v} / {466-v}',ha='center',fontsize=8.2)
    b.set_xticks(x,['R0\nExact reports','R1\nFixed bins','R2\nFlags only']);b.set_ylim(0,620)
    b.set_ylabel('Commodity–analyte cells');b.set_title('B  Mean bounds: 466 working cells',loc='left',fontweight='bold')
    b.legend(loc='upper right',bbox_to_anchor=(1,1.0),fontsize=8.2)
    positive=[]
    for r in rows:
        w0=float(r['R0_width']);w1=float(r['R1_width'])
        if math.isfinite(w1) and w0>0:positive.append(w1/w0)
    v=np.sort(positive)
    c.step(v,np.arange(1,len(v)+1)/len(v),where='post',color='#0072B2',linewidth=1.6)
    c.set_xscale('log');c.set_ylim(0,1.04);c.set_ylabel('Cumulative fraction of finite ratios')
    c.set_xlabel('R1 / R0 mean-interval width (log scale)')
    c.set_title('C  Rounding loss is not uniform',loc='left',fontweight='bold')
    c.text(.12,.12,f'{len(v)} finite ratios; 406 unchanged\n4 zero-width baselines: ratio undefined\n1 R1 upper bound is infinite',transform=c.transAxes,fontsize=8.2)
    thresholds=[2,10,20];w=.34
    for j,l in enumerate(['R0','R1']):
        counts=[sum(float(r[f'{l}_above_{t}_upper'])>float(r[f'{l}_above_{t}_lower'])+1e-12 for r in rows) for t in thresholds]
        bars=d.bar(x+(j-.5)*w,counts,width=w,label=l,color=['#0072B2','#E69F00'][j])
        d.bar_label(bars,padding=3,fontsize=8.2)
    d.set_xticks(x,['2 ppb','10 ppb','20 ppb']);d.set_ylim(0,600)
    d.set_ylabel('Cells with non-point exceedance bounds');d.set_xlabel('Illustrative thresholds, not safety limits')
    d.set_title('D  Threshold information retained',loc='left',fontweight='bold')
    d.legend(loc='upper right');d.text(.98,.78,'R2: all 466 cells span [0, 1]',transform=d.transAxes,ha='right',fontsize=8.2)
    for ax in axes.ravel():ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    out=B/'06_outputs/figures';out.mkdir(exist_ok=True,parents=True)
    for suffix in ['svg','pdf','png']:fig.savefig(out/f'figure6_information_loss.{suffix}',dpi=350)
    (data/'figure6_plot_metrics.json').write_text(json.dumps({'finite_ratio_cells':len(v),'zero_reference_width_cells':sum(float(r['R0_width'])==0 for r in rows),'finite_mean_cells':bounded},indent=2))
    plt.close(fig)

if __name__=='__main__':main()
