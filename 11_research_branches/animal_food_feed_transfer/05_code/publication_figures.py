"""Narrative redesign of the frozen audit; no new observations or estimates.

All dimensions are the manuscript's actual 6.5-inch display width. Native SVG
text, directly labelled values, redundant marker encodings and zero-baseline
percentage plots keep the audit editable and interpretable in print.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from figure_quality import inspect_figure

OUT = Path(__file__).resolve().parents[1] / '06_outputs/figures'
BLUE, AMBER, INK, MUTED, LIGHT = '#17658A', '#AD571C', '#182C38', '#566773', '#E6EDF0'
STEMS = {1:'figure1_noncompensatory_evidence_gate',2:'figure2_selection_diagnostics',
         3:'figure3_result_semantics',4:'figure4_source_discrepancies'}

def style():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
        'text.color':INK,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,
        'axes.edgecolor':'#AAB7BD','axes.linewidth':.6,'axes.labelsize':9,
        'xtick.labelsize':8,'ytick.labelsize':8,'svg.fonttype':'none',
        'svg.hashsalt':'afft-narrative-v2','pdf.fonttype':42})

def canvas(title, subtitle, height):
    fig = plt.figure(figsize=(6.5,height))
    fig.text(.065,.975,title,fontsize=13,weight='bold',va='top')
    fig.text(.065,.925,subtitle,fontsize=9,color=MUTED,va='top',linespacing=1.45)
    return fig

def panel(ax,letter,title):
    ax.set_title(f'{letter}   {title}',loc='left',fontsize=10,weight='bold',pad=13)
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(length=3,width=.6)
    ax.set_axisbelow(True)

def footer(fig,text):
    fig.text(.065,.025,text,fontsize=8,color=MUTED,va='bottom',linespacing=1.4)

def save(fig,n):
    inspect_figure(fig,OUT/f'{STEMS[n]}_layout_qa.json')
    for ext in ['svg','pdf','png']:
        fig.savefig(OUT/f'{STEMS[n]}.{ext}',dpi=450,facecolor='white')
    plt.close(fig)

def gate():
    style()
    fig=canvas('Evidence volume cannot repair a missing link',
        'Frozen full-chain pilot • grouped readiness layers, not a universal scoring system',7.4)
    ax=fig.add_axes([.04,.13,.92,.71]);ax.set_xlim(0,2);ax.set_ylim(0,7);ax.axis('off')
    ax.text(.04,6.8,'A   Feed-derived pesticides',fontsize=11,weight='bold')
    ax.text(1.09,6.8,'B   Veterinary medicines',fontsize=11,weight='bold')
    left=[('Feed use','PARTIAL PASS','National totals; no species allocation'),
        ('Feed occurrence','FAIL','No complete matched denominator'),
        ('Species-stage ration','FAIL','Dose linkage not established'),
        ('Chemical transfer','FAIL','Compatible transfer not admitted'),
        ('Animal-food monitoring','PARTIAL','Bounded descriptive evidence'),
        ('Diet + reserved validation','FAIL','Compatible data not established')]
    right=[('Monitoring design','PARTIAL','Programme-specific observations'),
        ('Drug–marker–tissue','FAIL','Compatibility not established'),
        ('Numeric / censored results','PARTIAL','Codes are not concentrations'),
        ('HBGV + consumption','FAIL','Intake assessment not admitted'),
        ('Descriptive monitoring','ONLY','Permitted output for this dossier')]
    for x,rows in [(.04,left),(1.09,right)]:
        for i,(label,state,detail) in enumerate(rows):
            y=5.76-i*.91; color=AMBER if state=='FAIL' else BLUE
            rect=Rectangle((x,y),.91,.76,facecolor='#F5F8FA',edgecolor='none')
            rect.set_gid(f'box-{x}-{i}');ax.add_patch(rect)
            ax.plot([x,x],[y,y+.76],lw=2.5,color=color)
            t=ax.text(x+.035,y+.57,label,fontsize=9,weight='bold');t.set_gid(f'box-{x}-{i}-label')
            ax.text(x+.035,y+.34,state,fontsize=8,weight='bold',color=color)
            ax.text(x+.035,y+.12,detail,fontsize=8,color=MUTED)
    ax.text(1.11,.96,'Separate mechanisms.\nNo pooled residue definition,\ntransfer function or risk index.',fontsize=9,linespacing=1.65)
    footer(fig,'Decision: stop this full-chain analysis; retain bounded description.\nFAIL means unmet in this dossier, not unavailable worldwide. See Table 1 for all nine gates.')
    save(fig,1)

def selection(data):
    p,v=data['pesticide'],data['veterinary_drug']
    fig=canvas('Selection changes the apparent evidence base',
        'Keyword candidates are screening outputs—not validated animal-food samples.',7.0)
    gs=fig.add_gridspec(2,2,left=.13,right=.96,bottom=.14,top=.80,wspace=.50,hspace=.85)
    for j,(d,title) in enumerate([(p,'Pesticide archive'),(v,'Veterinary archive')]):
        ax=fig.add_subplot(gs[0,j]);panel(ax,'AB'[j],title)
        vals=[d['all_samples'],d['candidate_samples']]
        ax.bar([0,1],vals,width=.5,color=[LIGHT,BLUE])
        for i,n in enumerate(vals):ax.text(i,n+max(vals)*.055,f'{n:,}',ha='center',fontsize=10,weight='bold')
        ax.set_xticks([0,1],['Archive','Candidates']);ax.set_ylabel('Unique sample IDs')
        ax.set_ylim(0,max(vals)*1.4);ax.set_xlim(-.6,1.6);ax.yaxis.grid(True,color=LIGHT,lw=.6)
        ax.text(.97,.92,f"{vals[1]/vals[0]:.1%} retained",transform=ax.transAxes,ha='right',fontsize=9,color=BLUE)
    ax=fig.add_subplot(gs[1,0]);panel(ax,'C','One label, unequal impact')
    vals=[100*p['cereal_samples']/p['candidate_samples'],100*p['cereal_rows']/p['candidate_rows']]
    ax.bar([0,1],vals,width=.5,color=AMBER);ax.set_ylim(0,45)
    ax.set_xticks([0,1],['Samples','Result rows']);ax.set_ylabel('Cereal share of candidates (%)')
    for i,(n,den,y) in enumerate(zip([p['cereal_samples'],p['cereal_rows']],[p['candidate_samples'],p['candidate_rows']],vals)):
        ax.text(i,y+1.2,f'{y:.1f}%\n{n:,}/{den:,}',ha='center',fontsize=9,linespacing=1.5)
    ax.yaxis.grid(True,color=LIGHT,lw=.6)
    ax=fig.add_subplot(gs[1,1]);panel(ax,'D','Sampling is selective')
    for i,d in enumerate([p,v]):
        a=d['strategy_samples']['ST20A'];b=d['strategy_samples']['ST10A'];share=100*a/(a+b)
        ax.barh(i,100,color=LIGHT,height=.34);ax.barh(i,share,color=BLUE,height=.34)
        ax.text(0,i+.28,f'{share:.1f}% selective ({a:,}/{a+b:,})',fontsize=8)
    ax.set_yticks([0,1],['Pesticide','Veterinary']);ax.set_xlim(0,100);ax.set_ylim(-.45,1.7)
    ax.set_xlabel('Candidate samples (%)');ax.set_xticks([0,50,100])
    footer(fig,'Luxembourg pesticides and Belgium veterinary drugs, 2024 archives.\nC: six milk-containing cereal samples are false positives. D: pale remainder = objective sampling.')
    save(fig,2)

def semantics(data):
    p,v=data['pesticide'],data['veterinary_drug']
    fig=canvas('A result row is not a measured concentration',
        'Decode result type first; retain the sample identifier throughout the audit.',7.0)
    gs=fig.add_gridspec(2,2,left=.13,right=.96,bottom=.14,top=.80,wspace=.55,hspace=.9)
    for j,(d,title) in enumerate([(p,'Pesticide result types'),(v,'Veterinary result types')]):
        ax=fig.add_subplot(gs[0,j]);panel(ax,'AB'[j],title)
        codes=sorted(d['result_types'],key=d['result_types'].get,reverse=True)
        vals=[d['result_types'][c] for c in codes]
        ax.set_xscale('log');ax.set_xlim(.7,max(vals)*30)
        for i,(code,n) in enumerate(zip(codes,vals)):
            ax.plot(n,i,'o' if code=='VAL' else 's',ms=6,color=BLUE if code=='VAL' else MUTED)
            ax.annotate(f'{n:,}',(n,i),xytext=(7,0),textcoords='offset points',va='center',fontsize=8)
        ax.set_yticks(range(len(codes)),codes);ax.set_ylim(len(codes)-.5,-.65)
        ax.set_xlabel('Candidate result rows (log scale)');ax.xaxis.grid(True,color=LIGHT,lw=.6)
    ax=fig.add_subplot(gs[1,0]);panel(ax,'C','Finite does not mean detected')
    for j,d in enumerate([p,v]):
        for k,(code,color,marker) in enumerate([('VAL',BLUE,'o'),('LOQ',AMBER,'s')]):
            y=j*2+k*.55;n=d['numeric_types'].get(code,0)
            ax.plot([0,n],[y,y],lw=2,color=LIGHT);ax.plot(n,y,marker,color=color,ms=6)
            ax.text(n+1.7,y,str(n),va='center',fontsize=9,color=color)
    ax.set_yticks([0,.55,2,2.55],['Pest. VAL','Pest. LOQ','Vet. VAL','Vet. LOQ']);ax.set_ylim(3,-.6)
    ax.set_xlim(0,45);ax.set_xlabel('Rows with finite resVal');ax.set_xticks([0,20,40]);ax.xaxis.grid(True,color=LIGHT,lw=.6)
    ax=fig.add_subplot(gs[1,1]);panel(ax,'D','Rows ≠ replicates')
    for d,label,color,line in [(p,'Pesticide',BLUE,'-'),(v,'Veterinary',AMBER,'--')]:
        h=d['rows_per_sample_histogram'];x=np.array([int(k) for k in h]);n=np.array(list(h.values()))
        ax.step(x,np.cumsum(n)/sum(n),where='post',color=color,ls=line,lw=1.8,label=label)
    ax.set_xscale('log');ax.set_ylim(0,1.05);ax.set_xlabel('Rows per sample (log scale)');ax.set_ylabel('Cumulative sample fraction')
    ax.legend(frameon=False,fontsize=8,loc='lower right');ax.yaxis.grid(True,color=LIGHT,lw=.6)
    footer(fig,'Numeric LOQ-coded entries are not uncensored detections. Binary and decision-limit codes\nremain separate. All panels describe the original keyword subsets; no exposure is calculated.')
    save(fig,3)

def discrepancies(data):
    s=data['source_discrepancies'];t=s['day7_high_dose_kidney_mg_kg'];nom=s['nominal_middle_ppm']
    fig=canvas('Source reconciliation precedes transfer modelling',
        'JMPR glyphosate case • MSL6729 • discrepancies within one study record',6.8)
    gs=fig.add_gridspec(3,1,left=.22,right=.91,bottom=.17,top=.80,hspace=1.05)
    for j,(title,labels,vals) in enumerate([
        ('Nominal middle dose',['Summary','Full evaluation'],[nom['summary'],nom['evaluation']]),
        ('Recorded week-2 dose',['Nominal','Week 2'],[nom['evaluation'],s['middle_week2_ppm']])]):
        ax=fig.add_subplot(gs[j]);panel(ax,'AB'[j],title)
        ax.plot(vals,[0,1],color=LIGHT,lw=2)
        for i,(value,color,marker) in enumerate(zip(vals,[BLUE,AMBER],['o','s'])):
            ax.plot(value,i,marker,color=color,ms=7);ax.text(value+5,i,f'{value} ppm',va='center',fontsize=9,weight='bold')
        ax.set_yticks([0,1],labels);ax.set_ylim(1.55,-.55);ax.set_xlim(0,205);ax.set_xticks([0,50,100,150,200])
        ax.set_xlabel('Reported feed dose (ppm)');ax.xaxis.grid(True,color=LIGHT,lw=.6)
    ax=fig.add_subplot(gs[2]);panel(ax,'C','Day-7 kidney conflicts')
    for i,chemical in enumerate(['glyphosate','AMPA']):
        a,b=t['table124'][chemical],t['prose'][chemical]
        ax.plot([a,b],[i,i],color=LIGHT,lw=3)
        for value,marker,color,delta,ha in [(a,'o',BLUE,-6,'right'),(b,'s',AMBER,6,'left')]:
            ax.plot(value,i,marker,color=color,ms=7,label=('Table 124' if marker=='o' else 'Prose') if i==0 else None)
            ax.annotate(f'{value:.2f}',(value,i),xytext=(delta,0),textcoords='offset points',va='center',ha=ha,fontsize=9)
    ax.set_yticks([0,1],['Glyphosate','AMPA']);ax.set_xlim(0,.17);ax.set_ylim(1.6,-.6)
    ax.set_xlabel('High-dose day-7 kidney residue (mg/kg)');ax.set_xticks([0,.05,.10,.15]);ax.xaxis.grid(True,color=LIGHT,lw=.6)
    ax.legend(frameon=False,fontsize=8,ncol=2,loc='upper right',bbox_to_anchor=(1,1.43))
    footer(fig,'Dots and squares identify source records, not biological replicates; connectors are not trends.\nUnresolved conflicts are not averaged. Source: FAO/WHO (2005), pp. 466–467, Tables 123–124.')
    save(fig,4)

def figures(data):
    style();selection(data);semantics(data);discrepancies(data)

if __name__=='__main__':
    gate();figures(json.loads((OUT/'multipanel_calculation_data.json').read_text()))
