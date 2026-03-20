#!/usr/bin/env python3
"""Generate report figures from FP-18v2 experiment results.

Reads JSON outputs from outputs/experiments_v2/ and generates:
  1. Detection rate vs paraphrase passes (E1)
  2. Z-score decay curve with error bars (E1)
  3. Watermark strength (delta) vs robustness (E4)
  4. Text length vs robustness (E3)
  5. False positive rate summary (E5)

Saves to blog/images/ (for blog) and outputs/figures/ (for report).

Usage:
    python scripts/make_report_figures.py
"""
import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

INPUT_DIR = Path("outputs/experiments_v2")
OUT_DIRS = [Path("blog/images"), Path("outputs/figures")]

# Style
plt.rcParams.update({
    "figure.figsize": (8, 5),
    "font.size": 12,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"]


def ensure_dirs():
    for d in OUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def save(fig, name):
    for d in OUT_DIRS:
        fig.savefig(d / f"{name}.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {name}.png")


def load_json(name):
    path = INPUT_DIR / f"{name}_results.json"
    if not path.exists():
        print(f"  SKIP: {path} not found")
        return None
    with open(path) as f:
        return json.load(f)["results"]


def fig_e1_detection_rate():
    """Detection rate vs paraphrase passes."""
    data = load_json("e1")
    if not data:
        return

    passes = sorted(int(k) for k in data.keys())
    rates = [data[str(p)]["detection_rate"] * 100 for p in passes]

    fig, ax = plt.subplots()
    ax.plot(passes, rates, "o-", color=COLORS[0], linewidth=2, markersize=8)
    ax.fill_between(passes, rates, alpha=0.1, color=COLORS[0])
    ax.set_xlabel("Paraphrase Passes")
    ax.set_ylabel("Detection Rate (%)")
    ax.set_title("Watermark Detection Rate vs Paraphrase Passes\n(Kirchenbauer δ=2.0, GPT-2 watermark, Claude Haiku paraphrase)")
    ax.set_ylim(-5, 105)
    ax.set_xticks(passes)
    ax.axhline(y=50, color="gray", linestyle="--", alpha=0.5, label="50% threshold")
    ax.legend()
    save(fig, "e1_detection_rate")
    plt.close()


def fig_e1_zscore_decay():
    """Z-score decay with error bars."""
    data = load_json("e1")
    if not data:
        return

    passes = sorted(int(k) for k in data.keys())
    means = [data[str(p)]["z_score_mean"] for p in passes]
    stds = [data[str(p)]["z_score_std"] for p in passes]

    fig, ax = plt.subplots()
    ax.errorbar(passes, means, yerr=stds, fmt="o-", color=COLORS[0],
                linewidth=2, markersize=8, capsize=5, capthick=2)
    ax.axhline(y=2.0, color=COLORS[1], linestyle="--", linewidth=1.5,
               label="Detection threshold (z=2.0)")
    ax.set_xlabel("Paraphrase Passes")
    ax.set_ylabel("Z-Score (mean ± std)")
    ax.set_title("Watermark Z-Score Decay Under Paraphrasing\n(5 seeds, Kirchenbauer δ=2.0)")
    ax.set_xticks(passes)
    ax.legend()
    save(fig, "e1_zscore_decay")
    plt.close()


def fig_e4_delta_robustness():
    """Watermark strength vs robustness."""
    data = load_json("e4")
    if not data:
        return

    deltas = sorted(float(k) for k in data.keys())
    means = [data[str(d) if str(d) in data else f"{d:.1f}"]["z_score_mean"] for d in deltas]
    stds = [data[str(d) if str(d) in data else f"{d:.1f}"]["z_score_std"] for d in deltas]
    rates = [data[str(d) if str(d) in data else f"{d:.1f}"]["detection_rate"] * 100 for d in deltas]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    bars = ax1.bar([str(d) for d in deltas], means, yerr=stds, capsize=5,
                   color=COLORS[0], alpha=0.7, label="Mean z-score")
    ax2.plot([str(d) for d in deltas], rates, "o-", color=COLORS[1],
             linewidth=2, markersize=10, label="Detection rate")

    ax1.axhline(y=2.0, color="gray", linestyle="--", alpha=0.5)
    ax1.set_xlabel("Watermark Strength (δ)")
    ax1.set_ylabel("Z-Score (mean ± std)", color=COLORS[0])
    ax2.set_ylabel("Detection Rate (%)", color=COLORS[1])
    ax2.set_ylim(-5, 105)
    ax1.set_title("Watermark Strength vs Robustness After 3 Paraphrase Passes")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    save(fig, "e4_delta_robustness")
    plt.close()


def fig_e3_length_robustness():
    """Text length vs robustness."""
    data = load_json("e3")
    if not data:
        return

    lengths = sorted(int(k) for k in data.keys())
    means = [data[str(l)]["z_score_mean"] for l in lengths]
    stds = [data[str(l)]["z_score_std"] for l in lengths]
    rates = [data[str(l)]["detection_rate"] * 100 for l in lengths]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.bar([str(l) for l in lengths], means, yerr=stds, capsize=5,
            color=COLORS[2], alpha=0.7, label="Mean z-score")
    ax2.plot([str(l) for l in lengths], rates, "o-", color=COLORS[1],
             linewidth=2, markersize=10, label="Detection rate")

    ax1.axhline(y=2.0, color="gray", linestyle="--", alpha=0.5)
    ax1.set_xlabel("Text Length (tokens)")
    ax1.set_ylabel("Z-Score (mean ± std)", color=COLORS[2])
    ax2.set_ylabel("Detection Rate (%)", color=COLORS[1])
    ax2.set_ylim(-5, 105)
    ax1.set_title("Text Length vs Watermark Robustness After 3 Paraphrase Passes")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    save(fig, "e3_length_robustness")
    plt.close()


def fig_e5_false_positive():
    """False positive rate summary."""
    data = load_json("e5")
    if not data:
        return

    categories = []
    fpr_values = []
    for key, label in [("unwatermarked_llm", "Unwatermarked\nLLM Text"),
                        ("human_text", "Human-Written\nText")]:
        if key in data:
            categories.append(label)
            fpr_values.append(data[key]["false_positive_rate"] * 100)

    if not categories:
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(categories, fpr_values, color=[COLORS[0], COLORS[2]], alpha=0.7)
    ax.set_ylabel("False Positive Rate (%)")
    ax.set_title("False Positive Rate on Non-Watermarked Text")
    ax.set_ylim(0, max(10, max(fpr_values) * 1.5 if fpr_values else 10))
    ax.axhline(y=5, color=COLORS[1], linestyle="--", label="5% FPR threshold")
    ax.legend()

    for bar, val in zip(bars, fpr_values):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.3,
                f"{val:.1f}%", ha="center", va="bottom", fontweight="bold")

    save(fig, "e5_false_positive")
    plt.close()


def main():
    ensure_dirs()
    print("Generating FP-18v2 report figures...")

    fig_e1_detection_rate()
    fig_e1_zscore_decay()
    fig_e4_delta_robustness()
    fig_e3_length_robustness()
    fig_e5_false_positive()

    print("Done.")


if __name__ == "__main__":
    main()
