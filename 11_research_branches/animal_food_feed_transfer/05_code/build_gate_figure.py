#!/usr/bin/env python3
"""Create the publication figure for the non-compensatory gate framework."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


BRANCH = Path(__file__).resolve().parents[1]
OUT = BRANCH / "06_outputs" / "figures"


def box(ax, x, y, width, height, label, color):
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.2, edgecolor="#263238", facecolor=color,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=8.5)


def arrow(ax, x1, x2, y):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>", mutation_scale=11, linewidth=1.1, color="#455A64"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    green, amber, red, blue = "#B7E4C7", "#FFE8A3", "#FFB4A2", "#BDE0FE"
    fig, ax = plt.subplots(figsize=(12, 5.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.4)
    ax.axis("off")

    ax.text(0.15, 4.95, "Module A: pesticide transfer from feed", fontsize=12, fontweight="bold", color="#1B4332")
    labels = [
        ("Feed use\nPARTIAL PASS", green),
        ("Feed occurrence\nFAIL", red),
        ("Species-stage ration\nFAIL", red),
        ("Chemical transfer\nFAIL", red),
        ("Animal-food monitoring\nPARTIAL", amber),
        ("Diet + reserved\nvalidation data\nFAIL", red),
    ]
    x_positions = [0.2, 2.15, 4.1, 6.05, 8.0, 9.95]
    for index, ((label, color), x) in enumerate(zip(labels, x_positions)):
        box(ax, x, 3.65, 1.55, 0.72, label, color)
        if index < len(labels) - 1:
            arrow(ax, x + 1.56, x_positions[index + 1] - 0.04, 4.01)
    ax.text(6, 3.15, "Any failed readiness layer → STOP; successful prediction validation is checked after fitting", ha="center", fontsize=9.5, fontweight="bold", color="#9D0208")

    ax.text(0.15, 2.55, "Module B: veterinary medicinal products (separate chain)", fontsize=12, fontweight="bold", color="#023E8A")
    b_labels = [
        ("Monitoring design\nPARTIAL", amber),
        ("Drug-marker-tissue\nFAIL", red),
        ("Numerical/censored result\nPARTIAL", amber),
        ("HBGV + consumption\nFAIL", red),
        ("Descriptive monitoring\nONLY", blue),
    ]
    b_positions = [0.7, 3.0, 5.3, 7.6, 9.9]
    for index, ((label, color), x) in enumerate(zip(b_labels, b_positions)):
        box(ax, x, 1.3, 1.65, 0.72, label, color)
        if index < len(b_labels) - 1:
            arrow(ax, x + 1.66, b_positions[index + 1] - 0.04, 1.66)

    ax.text(6, 0.65, "No shared residue definition, transfer function, HBGV, or combined risk index", ha="center", fontsize=9.5, color="#37474F")
    ax.text(0.2, 0.15, "Green: limited pass   Amber: descriptive-only/partial   Red: failed mandatory layer", fontsize=8.5, color="#455A64")
    fig.tight_layout()
    for suffix in ("svg", "pdf", "png"):
        fig.savefig(OUT / f"figure1_noncompensatory_evidence_gate.{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
