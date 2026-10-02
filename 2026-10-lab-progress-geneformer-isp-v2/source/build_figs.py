"""Figures for 'Reading the Current, version 2' (lab progress talk, 2026-10-01).

Two kinds of figure, always labelled:
  data figures read only the result files in data/ (hashes in SHA256SUMS);
  schematics use invented points or bars and say "Schematic, not data" on the figure.
Colour code used throughout the talk: teal = passed, coral = failed, amber = not yet known.
Cell groups use purple (tumour) and blue (normal) so they never look like a verdict.
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch
from scipy.stats import rankdata, spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "..", "figures")
os.makedirs(OUT, exist_ok=True)

INK, PAPER, GREY = "#1d2b3a", "#fbf8f2", "#8a96a6"
PASS, FAIL, OPEN = "#2a7f7a", "#c4553a", "#c99a2e"
TUM, NOR = "#7a5ea8", "#3f7cbf"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 17, "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "text.color": INK, "figure.facecolor": PAPER,
    "axes.facecolor": PAPER, "savefig.facecolor": PAPER, "axes.spines.top": False, "axes.spines.right": False,
})


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def stamp(ax, text="Schematic, not data"):
    ax.text(0.99, 0.99, text, transform=ax.transAxes, ha="right", va="top", fontsize=13, color=GREY, style="italic")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=170, metadata={"Software": None}); plt.close(fig)


def fig_cell_ranking():
    """A cell's genes, scaled by their usual level, then sorted into a ranked list."""
    genes = ["ACTB", "CD3E", "IL7R", "CCR7", "GAPDH", "TCF7", "LTB", "RPL13"]
    raw = np.array([95, 40, 30, 22, 88, 12, 26, 90.0])
    usual = np.array([100, 12, 10, 8, 95, 5, 14, 96.0])
    rel = raw / usual
    fig, axs = plt.subplots(1, 2, figsize=(11.0, 6.0), gridspec_kw={"width_ratios": [1, 1]})
    ax = axs[0]
    ax.barh(range(len(genes)), raw, color=GREY)
    ax.set_yticks(range(len(genes))); ax.set_yticklabels(genes); ax.invert_yaxis()
    ax.set_xlabel("how much of each gene the cell has"); ax.set_title("1. Count the genes", loc="left", fontsize=18)
    ax.set_xticks([])
    ax = axs[1]
    order = np.argsort(-rel)
    cols = [NOR if rel[i] > 1.5 else GREY for i in order]
    ax.barh(range(len(genes)), rel[order], color=cols)
    ax.set_yticks(range(len(genes))); ax.set_yticklabels([genes[i] for i in order]); ax.invert_yaxis()
    ax.set_xlabel("compared with the gene's usual level"); ax.set_title("2. Rank by what is unusual", loc="left", fontsize=18)
    ax.set_xticks([])
    stamp(ax)
    fig.tight_layout(); save(fig, "cell_ranking.png")


def fig_finetune():
    """Two clouds of cells from one patient, and the line the fine-tuned model learns."""
    rng = np.random.default_rng(5)
    t = rng.normal([2.4, 2.2], 0.6, size=(80, 2)); n = rng.normal([6.0, 4.4], 0.6, size=(80, 2))
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.scatter(*t.T, s=40, color=TUM, alpha=0.7, lw=0, label="T cells from the tumour")
    ax.scatter(*n.T, s=40, color=NOR, alpha=0.7, lw=0, label="T cells from normal tissue")
    xs = np.linspace(0.5, 8.0, 10); ax.plot(xs, -0.95 * xs + 7.6, color=INK, lw=2, ls="--")
    ax.text(4.6, 0.5, "the line the model learns to draw", fontsize=15, ha="left", bbox=dict(fc=PAPER, ec="none", pad=2))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel("the model's map of cells (a 2-D sketch)")
    ax.legend(loc="upper left", frameon=False, fontsize=15); ax.set_xlim(0, 8.4); ax.set_ylim(0, 7.2)
    stamp(ax, "Schematic, one patient, not data")
    fig.tight_layout(); save(fig, "finetune.png")


def fig_isp():
    """A tumour T cell, the patient's normal centre, and the two edits."""
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    t = rng.normal([2.2, 2.0], 0.55, size=(60, 2)); n = rng.normal([6.6, 4.1], 0.5, size=(60, 2))
    ax.scatter(*t.T, s=30, color=TUM, alpha=0.45, lw=0, label="tumour T cells")
    ax.scatter(*n.T, s=30, color=NOR, alpha=0.45, lw=0, label="same patient, normal T cells")
    goal = n.mean(0)
    ax.scatter(*goal, s=420, marker="*", color=NOR, edgecolor=INK, lw=1.4, zorder=6)
    ax.text(goal[0], goal[1] + 0.85, "goal: centre of this\npatient's normal cells", fontsize=14, ha="center")
    c = np.array([2.5, 2.3]); ax.scatter(*c, s=150, color=INK, zorder=7)
    ax.text(c[0] - 0.15, c[1] + 0.45, "one tumour T cell", fontsize=14, ha="right")
    for d, col, lab, off in [((1.35, 0.68), NOR, "delete gene X\n(remove it from the list)", (0.2, -0.95)),
                             ((-0.9, -0.5), TUM, "overexpress gene X\n(move it to the top)", (-0.1, -1.0))]:
        ax.add_patch(FancyArrowPatch(c, c + d, arrowstyle="-|>", mutation_scale=26, lw=3, color=col, zorder=8))
        ax.text(*(c + np.array(d) + np.array(off)), lab, fontsize=13.5, color=col, ha="left" if d[0] > 0 else "right")
    ax.annotate("", xy=goal, xytext=c, arrowprops=dict(arrowstyle="-", ls=(0, (3, 3)), color=GREY, lw=1.4))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel("the model's map of cells (a 2-D sketch)")
    ax.legend(loc="upper left", frameon=False, fontsize=14); ax.set_xlim(-0.4, 8.6); ax.set_ylim(-0.2, 6.0)
    stamp(ax)
    fig.tight_layout(); save(fig, "isp.png")


def fig_one_patient():
    """T6: one SCLC patient held 74.9% of the SCLC test cells."""
    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    ax.barh([0], [74.9], color=FAIL); ax.barh([0], [25.1], left=[74.9], color=GREY)
    ax.text(37.4, 0, "one patient: 74.9%", ha="center", va="center", color="white", fontsize=18, weight="bold")
    ax.text(87.4, 0, "the other\ntwo: 25.1%", ha="center", va="center", color="white", fontsize=14)
    ax.set_xlim(0, 100); ax.set_yticks([]); ax.set_xlabel("share of the small-cell (SCLC) test cells, %")
    ax.spines["left"].set_visible(False)
    fig.tight_layout(); save(fig, "one_patient.png")


def fig_unpaired():
    """Unpaired arms: overexpression scored on 2,424 cells for every gene, deletion on 202 to 1,131."""
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.bar([0], [2424], color=FAIL, width=0.55)
    ax.bar([1], [1131], color=GREY, width=0.55); ax.bar([1], [202], color=INK, width=0.55, alpha=0.35)
    ax.text(0, 2424 + 60, "2,424 for every gene", ha="center", fontsize=15)
    ax.text(1, 1131 + 60, "202 to 1,131,\ndepending on the gene", ha="center", fontsize=15)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["overexpress\n(all test cells)", "delete\n(only cells with the gene)"])
    ax.set_ylabel("cells scored"); ax.set_ylim(0, 2900)
    ax.set_title("The two edits were scored on different cells", fontsize=16, loc="left")
    fig.tight_layout(); save(fig, "unpaired.png")


def fig_null_scatter():
    a5, n200 = load("a5_primary_result_v2.json"), load("n200_combined_result_v2.json")
    d1, o1 = np.array(a5["null_delete_medians"]), np.array(a5["null_overexpress_medians"])
    d2, o2 = np.array(n200["null_delete_medians"]), np.array(n200["null_overexpress_medians"])
    r1, r2 = a5["primary"]["rho"], n200["extension_n200"]["rho"]
    assert np.allclose(d2[:len(d1)], d1) and np.allclose(o2[:len(o1)], o1)
    assert abs(spearmanr(d1, o1)[0] - r1) < 1e-9 and abs(spearmanr(d2, o2)[0] - r2) < 1e-9
    rd, ro = rankdata(d2) / len(d2), rankdata(o2) / len(o2)
    fig, ax = plt.subplots(figsize=(7.8, 6.2))
    ax.scatter(rd, ro, s=40, color=INK, alpha=0.75, lw=0)
    ax.plot([0, 1], [1, 0], color=FAIL, lw=1.6, ls="--")
    ax.set_xlabel("deleting it moves cells toward normal\n(rank among 200 random genes)")
    ax.set_ylabel("overexpressing it moves cells toward normal\n(rank among the same genes)")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["least", "most"]); ax.set_yticks([0, 1]); ax.set_yticklabels(["least", "most"])
    ax.text(0.98, 0.97, f"rank correlation\n{r1:.3f} (first 100 genes)\n{r2:.3f} (all 200)", transform=ax.transAxes,
            ha="right", va="top", fontsize=15, bbox=dict(fc=PAPER, ec=FAIL, lw=1.4, boxstyle="round,pad=0.4"))
    ax.set_title("Each dot: one random gene, lung, 43 patients", fontsize=15, loc="left")
    fig.tight_layout(); save(fig, "null_scatter.png")
    return r1, r2


def fig_baseline():
    """How a claimed hit is judged: against look-alike genes and against random genes."""
    rng = np.random.default_rng(11)
    ctrl = rng.normal(0.0, 1.0, 400)
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.hist(ctrl, bins=30, color=GREY, alpha=0.75)
    ax.axvline(3.4, color=PASS, lw=3); ax.text(3.45, 34, "a gene worth\nfollowing up", color=PASS, fontsize=15, va="top")
    ax.axvline(1.1, color=FAIL, lw=3); ax.text(1.15, 44, "looked like a hit,\nbut is inside\nthe cloud", color=FAIL, fontsize=15, va="top")
    ax.set_yticks([]); ax.set_xticks([]); ax.spines["left"].set_visible(False)
    ax.set_xlabel("how far an edit moves cells toward normal")
    ax.text(-3.2, 40, "look-alike and\nrandom genes", color=INK, fontsize=15, va="top")
    stamp(ax)
    fig.tight_layout(); save(fig, "baseline.png")


def fig_gate_strip():
    e2, lu = load("e2_classifier_gate.json"), load("luad_classifier_gate.json")
    ev, lv = sorted(e2["per_donor_balanced_accuracy"].values()), sorted(lu["per_donor_balanced_accuracy"].values())
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    rng = np.random.default_rng(3)
    for i, (v, pooled) in enumerate([(lv, lu["pooled_balanced_accuracy"]), (ev, e2["pooled_balanced_accuracy"])]):
        ax.scatter(i + rng.uniform(-0.15, 0.15, len(v)), v, s=46, color=PASS, alpha=0.85, lw=0)
        ax.plot([i - 0.28, i + 0.28], [pooled] * 2, color=INK, lw=3)
        ax.text(i + 0.31, pooled, f"{pooled*100:.1f}%", va="center", fontsize=16)
    ax.axhline(0.50, color=FAIL, ls=":", lw=1.6); ax.text(1.62, 0.508, "coin toss (50%)", fontsize=14, ha="right", color=FAIL)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Lung\n43 patients", "Colon\n19 patients"])
    ax.set_ylabel("right answers,\nboth groups counted equally", fontsize=16); ax.set_ylim(0.45, 1.01); ax.set_xlim(-0.55, 1.68)
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0]); ax.set_yticklabels(["50%", "60%", "70%", "80%", "90%", "100%"])
    ax.set_title("Each dot: one patient the model never saw", fontsize=15, loc="left")
    fig.tight_layout(); save(fig, "gate_strip.png")
    return (lu["pooled_balanced_accuracy"], lu["donors_above_0.5"], e2["pooled_balanced_accuracy"], e2["donors_above_0.5"], min(ev))


if __name__ == "__main__":
    fig_cell_ranking(); fig_finetune(); fig_isp(); fig_one_patient(); fig_unpaired(); fig_baseline()
    print("null", fig_null_scatter())
    print("gate", fig_gate_strip())
