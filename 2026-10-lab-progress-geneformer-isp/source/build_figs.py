"""Figures for the lab progress talk 'Reading the Current' (2026-10-01).

Data figures read only the committed or reviewed result files in source/data/ (hashes in
source/SHA256SUMS). Schematic figures use synthetic points and are labelled as schematics.
"""
import json, os, statistics
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "..", "figures")
os.makedirs(OUT, exist_ok=True)

INK, PAPER, TEAL, BRASS, CORAL, FOAM, MIST = "#13233a", "#f4efe4", "#2a7f7a", "#b8862b", "#c4553a", "#4f9d8a", "#8a96a6"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 13, "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "text.color": INK, "figure.facecolor": PAPER,
    "axes.facecolor": PAPER, "savefig.facecolor": PAPER, "axes.spines.top": False, "axes.spines.right": False,
})


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def contour_art(path, seed, w=16, h=9, levels=22, alpha=0.22):
    """Decorative chart contours: a smooth random field, no data."""
    rng = np.random.default_rng(seed)
    x, y = np.meshgrid(np.linspace(0, w, 400), np.linspace(0, h, 225))
    z = np.zeros_like(x)
    for _ in range(9):
        cx, cy, s, a = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(1.2, 3.5), rng.uniform(-1, 1)
        z += a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s ** 2))
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.contour(x, y, z, levels=levels, colors=TEAL, linewidths=0.8, alpha=alpha)
    fig.savefig(path, dpi=100, transparent=True); plt.close(fig)


def fig_isp_schematic():
    """Schematic: tumour cloud, the donor's normal 'harbour', and a perturbed cell's shift."""
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(8, 5.4))
    t = rng.normal([2.2, 2.0], 0.55, size=(70, 2)); n = rng.normal([6.6, 4.1], 0.5, size=(70, 2))
    ax.scatter(*t.T, s=22, color=CORAL, alpha=0.55, lw=0, label="tumour T cells")
    ax.scatter(*n.T, s=22, color=FOAM, alpha=0.55, lw=0, label="same donor, normal-tissue T cells")
    goal = n.mean(0)
    ax.add_patch(Circle(goal, 0.22, fill=False, ec=INK, lw=2))
    ax.text(goal[0] - 0.2, goal[1] + 1.15, "goal: this donor's\nnormal centroid", fontsize=12, ha="center")
    ax.annotate("", xy=goal + np.array([0, 0.25]), xytext=goal + np.array([0, 0.95]), arrowprops=dict(arrowstyle="-", color=INK, lw=1))
    c = np.array([2.5, 2.3])
    ax.scatter(*c, s=110, color=INK, zorder=5)
    ax.text(c[0] + 0.15, c[1] - 0.75, "one tumour\nT cell", fontsize=12, ha="left", bbox=dict(fc=PAPER, ec="none", alpha=0.85, pad=1.5))
    for d, col, lab in [((1.25, 0.62), TEAL, "delete gene X:\nmoves toward goal"), ((-0.85, -0.45), BRASS, "overexpress gene X:\nmoves away")]:
        ax.add_patch(FancyArrowPatch(c, c + d, arrowstyle="-|>", mutation_scale=22, lw=2.4, color=col, zorder=6))
        ax.text(*(c + np.array(d) + np.array([0.15, -0.75] if d[0] > 0 else [-0.15, -0.6])), lab,
                fontsize=11.5, color=col, ha="left" if d[0] > 0 else "right", bbox=dict(fc=PAPER, ec="none", alpha=0.85, pad=1.5))
    ax.annotate("", xy=goal, xytext=c, arrowprops=dict(arrowstyle="-", ls=(0, (3, 3)), color=MIST, lw=1.3))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel("embedding space (a 2-D sketch of a high-dimensional space)")
    ax.legend(loc="upper left", frameon=False, fontsize=11)
    ax.set_title("Schematic, not data", fontsize=12, color=INK, loc="right")
    ax.set_xlim(-0.2, 8.6); ax.set_ylim(0.0, 5.6)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "isp_schematic.png"), dpi=200); plt.close(fig)


def fig_null_scatter():
    a5, n200 = load("a5_primary_result_v2.json"), load("n200_combined_result_v2.json")
    d1, o1 = np.array(a5["null_delete_medians"]), np.array(a5["null_overexpress_medians"])
    d2, o2 = np.array(n200["null_delete_medians"]), np.array(n200["null_overexpress_medians"])
    r1, r2 = a5["primary"]["rho"], n200["extension_n200"]["rho"]
    fig, ax = plt.subplots(figsize=(8.4, 6.0))
    extra = np.ones(len(d2), bool); extra[:len(d1)] = False  # nested: first 100 of the 200 are the N=100 set
    assert np.allclose(d2[:len(d1)], d1) and np.allclose(o2[:len(o1)], o1)
    from scipy.stats import rankdata, spearmanr
    assert abs(spearmanr(d1, o1)[0] - r1) < 1e-9 and abs(spearmanr(d2, o2)[0] - r2) < 1e-9
    rd, ro = rankdata(d2) / len(d2), rankdata(o2) / len(o2)  # ranks within the 200, scaled to 0-1
    ax.scatter(rd[extra], ro[extra], s=26, color=MIST, alpha=0.8, lw=0, label="genes 101-200 (N=200 extension)")
    ax.scatter(rd[~extra], ro[~extra], s=34, color=TEAL, alpha=0.9, lw=0, label="genes 1-100 (registered primary)")
    ax.plot([0, 1], [1, 0], color=BRASS, lw=1, ls="--")
    ax.set_xlabel("deletion shift toward normal: rank among the 200 genes (0 = lowest, 1 = highest)")
    ax.set_ylabel("overexpression shift: rank among the 200")
    ax.text(0.98, 0.97, f"N=100: Spearman rho = {r1:.3f}\nN=200: rho = {r2:.3f}\none-sided p at the floor of\n100,000 permutations (<= 1e-5)",
            transform=ax.transAxes, ha="right", va="top", fontsize=12, bbox=dict(fc=PAPER, ec=BRASS, lw=1.2, boxstyle="round,pad=0.4"))
    ax.legend(loc="lower left", frameon=False, fontsize=11, bbox_to_anchor=(0, -0.02))
    ax.set_title("Random genes, no relation to tumour vs normal: still anti-correlated", fontsize=13)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "null_scatter.png"), dpi=200); plt.close(fig)
    return r1, r2, len(d1), len(d2)


def fig_gate_strip():
    e2, lu = load("e2_classifier_gate.json"), load("luad_classifier_gate.json")
    ev, lv = sorted(e2["per_donor_balanced_accuracy"].values()), sorted(lu["per_donor_balanced_accuracy"].values())
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    rng = np.random.default_rng(3)
    for i, (v, col, lab, pooled) in enumerate([(lv, MIST, f"Lung (LUAD), 43 donors", lu["pooled_balanced_accuracy"]),
                                                (ev, TEAL, f"Colorectal (E2), 19 donors", e2["pooled_balanced_accuracy"])]):
        x = i + rng.uniform(-0.16, 0.16, len(v))
        ax.scatter(x, v, s=34, color=col, alpha=0.9, lw=0)
        ax.plot([i - 0.3, i + 0.3], [pooled] * 2, color=BRASS, lw=2.6)
        ax.text(i + 0.33, pooled, f"pooled {pooled:.3f}", va="center", fontsize=12, color=BRASS)
    ax.axhline(0.60, color=INK, ls="--", lw=1.1); ax.text(1.55, 0.605, "gate 0.60", fontsize=11, ha="right")
    ax.axhline(0.50, color=MIST, ls=":", lw=1.1); ax.text(1.55, 0.505, "chance 0.50", fontsize=11, ha="right", color=MIST)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Lung (LUAD)\n43 donors, 5 studies", "Colorectal (E2)\n19 donors, 1 study"])
    ax.set_ylabel("held-out balanced accuracy per donor"); ax.set_ylim(0.45, 1.01); ax.set_xlim(-0.6, 1.65)
    ax.set_title("Each dot is one donor scored by a model that never saw that donor", fontsize=12.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "gate_strip.png"), dpi=200); plt.close(fig)
    return (e2["pooled_balanced_accuracy"], min(ev), statistics.median(ev), e2["donors_above_0.5"],
            lu["pooled_balanced_accuracy"], min(lv), max(lv), statistics.median(lv), lu["donors_above_0.5"])


if __name__ == "__main__":
    contour_art(os.path.join(OUT, "contours_a.png"), 11)
    contour_art(os.path.join(OUT, "contours_b.png"), 29, alpha=0.16)
    fig_isp_schematic()
    print("null", fig_null_scatter())
    print("gate", fig_gate_strip())
