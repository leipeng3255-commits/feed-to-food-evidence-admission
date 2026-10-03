"""Plot archived developmental rule disagreements, never accuracy."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from figure_quality import inspect_figure

BRANCH = Path(__file__).resolve().parent


def main():
    source = BRANCH / 'classification_summary.json'
    data = json.loads(source.read_text())
    counts = data['counts']
    print(json.dumps(counts, indent=2))
    modules = list(counts)
    pesticide = next(key for key in modules if 'pesticide' in key.lower())
    veterinary = next(key for key in modules if key != pesticide)
    out = BRANCH / 'rendered'
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'svg.fonttype': 'none', 'pdf.fonttype': 42,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.4))
    fig.subplots_adjust(left=.25, right=.86, top=.90, bottom=.13, hspace=.65)
    groups = ['BOTH_SELECTED', 'KEYWORD_ONLY', 'HIERARCHY_ONLY']
    expected = ([50, 6, 14], [8270, 0, 330])
    for ax, module, title, check in zip(axes, [pesticide, veterinary],
                                      ['A  Pesticide monitoring', 'B  Veterinary-drug monitoring'], expected):
        values = [counts[module].get(key + '_sample_ids', 0) for key in groups]
        assert values == check, (module, values)
        ax.barh(range(3), values, color=['#0072B2', '#D55E00', '#009E73'], height=.48)
        ax.set_yticks(range(3), ['Both rules', 'Keywords only', 'Hierarchy only'])
        ax.invert_yaxis()
        ax.set_xlim(0, max(values) * 1.21)
        for index, value in enumerate(values):
            ax.text(value + max(values)*.025, index, f'{value:,}', va='center', fontsize=9)
        ax.set_title(title, loc='left', fontsize=11, weight='bold', pad=12)
        ax.set_xlabel('Sample identifiers (within-module count)', fontsize=9)
        ax.xaxis.grid(True, alpha=.15)
        ax.set_axisbelow(True)
    fig.text(.25, .035, 'Post-hoc rule disagreement; no independent reference labels.', fontsize=8)
    stem = out / 'figure5_classification_disagreement'
    inspect_figure(fig, stem.with_suffix('.qa.json'))
    for extension in ['svg', 'pdf', 'png']:
        fig.savefig(stem.with_suffix('.' + extension), dpi=450)
    stem.with_suffix('.source.json').write_text(json.dumps({
        'source_config_key': 'public_extension_directory',
        'source_relative_path': source.name,
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'counts': counts, 'status': data['status']}, indent=2) + '\n')
    plt.close(fig)


if __name__ == '__main__':
    main()
