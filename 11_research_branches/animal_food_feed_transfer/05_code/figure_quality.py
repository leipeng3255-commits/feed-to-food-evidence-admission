"""Renderer-based text collision, canvas and minimum-size diagnostics."""
import json

def inspect_figure(fig, target, word_width_inches=6.5):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    texts=list(fig.texts)
    for ax in fig.axes:
        texts.extend([ax.title,ax._left_title,ax._right_title,*ax.texts])
        if ax.axison:
            texts.extend([ax.xaxis.label,ax.yaxis.label])
            for axis,limits in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
                lo,hi=sorted(limits)
                for tick in [*axis.get_major_ticks(),*axis.get_minor_ticks()]:
                    if lo <= tick.get_loc() <= hi:
                        texts.extend([tick.label1,tick.label2])
            legend=ax.get_legend()
            if legend: texts.extend(legend.get_texts())
    texts=[t for t in dict.fromkeys(texts) if t.get_visible() and t.get_text().strip()]
    boxes=[t.get_window_extent(renderer) for t in texts]
    outside=[]; collisions=[]
    for t,b in zip(texts,boxes):
        if b.x0 < -1 or b.y0 < -1 or b.x1 > fig.bbox.width+1 or b.y1 > fig.bbox.height+1:
            outside.append(t.get_text())
    for i,a in enumerate(boxes):
        for j in range(i):
            b=boxes[j]
            if min(a.x1,b.x1)-max(a.x0,b.x0)>1 and min(a.y1,b.y1)-max(a.y0,b.y0)>1:
                collisions.append([texts[j].get_text(),texts[i].get_text()])
    sizes=[t.get_fontsize() for t in texts]
    report={'text_objects':len(texts),'canvas_overflow':outside,'text_box_collisions':collisions,
            'minimum_source_font_pt':min(sizes),'minimum_at_6_5_inch_width_pt':min(sizes)*word_width_inches/fig.get_figwidth(),
            'scope':'Renderer geometry check, complemented by visual inspection; not a guarantee of arbitrary font substitution or downstream edits.'}
    target.write_text(json.dumps(report,indent=2)+'\n')
    if outside or collisions or report['minimum_at_6_5_inch_width_pt'] < 7:
        raise RuntimeError(f'Figure typography check failed: {target}: {report}')
    return report
