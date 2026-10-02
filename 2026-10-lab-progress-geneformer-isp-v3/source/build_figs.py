"""Figures for 'Evaluating in-silico perturbation with Geneformer' (lab progress report, version 3, 2026-10-01).

Three kinds of figure, each labelled on the figure:
  data figures read only the files in data/ (hashes in SHA256SUMS);
  diagrams show the analysis steps as they are implemented ("Diagram");
  schematics use invented values to explain an idea ("Schematic, not data").
Colour code used throughout the talk: teal = passed, coral = failed, amber = not yet known.
Cell groups use purple (tumour) and blue (normal) so they never look like a verdict.
PNG files are written without metadata (no Software or date chunks).
"""
import csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from scipy.stats import rankdata, spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "..", "figures")
os.makedirs(OUT, exist_ok=True)

INK, PAPER, GREY, LIGHT = "#1d2b3a", "#fbf8f2", "#8a96a6", "#e9e3d6"
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


def stamp(ax, text="Schematic, not data", y=0.99):
    ax.text(0.99, y, text, transform=ax.transAxes, ha="right", va="top" if y > 0.5 else "bottom", fontsize=13, color=GREY, style="italic")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=170, metadata={"Software": None}); plt.close(fig)


def box(ax, x, y, w, h, text, fc="#ffffff", ec=INK, color=INK, fs=15, lw=1.4, ls="-", weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=ec, lw=lw, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, weight=weight, linespacing=1.3)


def arrow(ax, a, b, color=INK, lw=2.0, ms=18):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color))


def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax); ax.set_ylim(0, ymax); ax.axis("off")
    return fig, ax


# ---------- diagrams ----------
def fig_pipeline():
    """The analysis as implemented, from cohort to a patient-level call."""
    fig, ax = canvas(12.6, 5.0, 12.6, 5.0)
    top = [("1  Cohort", "paired donors:\ntumour and normal\nT cells, ≥100 each"),
           ("2  Tokenise", "each cell as a\nrank-ordered\ngene list"),
           ("3  Fine-tune", "tumour vs normal\nclassifier, donors\nheld out by fold"),
           ("4  Gates", "held-out accuracy\n≥ 0.60; an empty\nedit moves 0.0")]
    bot = [("5  Edit (ISP)", "delete or\noverexpress one\ngene per cell"),
           ("6  Score", "cosine shift toward\nthe donor's own\nnormal centroid"),
           ("7  Compare", "against matched\ncontrol genes and\nrandom genes"),
           ("8  Call", "per donor, stability\nchecked, fixed\noutcome names")]
    w, h, gap = 2.75, 1.85, 0.42
    for row, (items, y) in enumerate([(top, 2.85), (bot, 0.35)]):
        for i, (head, body) in enumerate(items):
            x = 0.25 + i * (w + gap)
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                        fc="#ffffff", ec=INK if row == 0 else PASS, lw=1.6))
            ax.text(x + 0.16, y + h - 0.2, head, ha="left", va="top", fontsize=16, weight="bold")
            ax.text(x + 0.16, y + h - 0.62, body, ha="left", va="top", fontsize=13.5, color="#33445a", linespacing=1.3)
            if i < 3:
                arrow(ax, (x + w + 0.03, y + h / 2), (x + w + gap - 0.03, y + h / 2))
    x4, x5, ym = 0.25 + 3 * (w + gap) + w / 2, 0.25 + w / 2, 2.52
    ax.plot([x4, x4, x5], [2.83, ym, ym], color=GREY, lw=2)
    arrow(ax, (x5, ym), (x5, 2.24), color=GREY)
    ax.text(12.5, 4.98, "Diagram", ha="right", va="top", fontsize=12, color=GREY, style="italic")
    fig.tight_layout(); save(fig, "pipeline.png")


def fig_tokenise():
    """Rank-value encoding as implemented in the Geneformer tokenizer (invented values)."""
    genes = ["ACTB", "RPL13", "GAPDH", "CD3E", "LTB", "IL7R", "CCR7", "TCF7", "MKI67"]
    raw = np.array([60, 52, 40, 9, 8, 6, 5, 3, 0.0])
    med = np.array([30, 40, 25, 2.0, 3.5, 1.5, 1.6, 0.6, 1.0])
    norm = raw / raw.sum() * 10_000
    rel = norm / (med / med.sum() * 10_000)
    fig, axs = plt.subplots(1, 3, figsize=(13.4, 5.6), gridspec_kw={"width_ratios": [1, 1, 0.95]})
    ax = axs[0]
    ax.barh(range(len(genes)), raw, color=GREY); ax.set_yticks(range(len(genes))); ax.set_yticklabels(genes); ax.invert_yaxis()
    ax.set_xticks([]); ax.set_title("1. Counts in one cell", loc="left", fontsize=17)
    ax.set_xlabel("UMI counts")
    ax = axs[1]
    ax.barh(range(len(genes)), rel, color=[NOR if v > 2 else GREY for v in rel]); ax.set_yticks(range(len(genes)))
    ax.set_yticklabels(genes); ax.invert_yaxis(); ax.set_xticks([])
    ax.set_title("2. Scale by usual level", loc="left", fontsize=17)
    ax.set_xlabel("÷ cell total, ÷ gene's corpus median")
    ax = axs[2]; ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title("3. Sort; zeros dropped", loc="left", fontsize=17)
    order = [i for i in np.argsort(-rel) if raw[i] > 0]
    for k, i in enumerate(order):
        y = 0.93 - k * 0.105
        ax.add_patch(FancyBboxPatch((0.05, y - 0.04), 0.62, 0.075, boxstyle="round,pad=0.005,rounding_size=0.02",
                                    fc=NOR if rel[i] > 2 else GREY, ec="none"))
        ax.text(0.08, y, f"{k + 1}", va="center", fontsize=13, color="white")
        ax.text(0.36, y, genes[i], va="center", ha="center", fontsize=15, color="white", family="monospace")
    ax.text(0.72, 0.93, "first", fontsize=13, color=GREY, va="center")
    ax.text(0.72, 0.93 - (len(order) - 1) * 0.105, "last", fontsize=13, color=GREY, va="center")
    ax.text(0.05, 0.02, "MKI67: zero counts, not in the list.\nV2 models read at most 4,096 tokens.", fontsize=12.5, color="#33445a")
    stamp(axs[1], "Schematic, invented values", y=0.02)
    fig.tight_layout(); save(fig, "tokenise.png")


def fig_isp_mech():
    """What one in-silico edit does to one cell's token list, and how it is scored."""
    fig, ax = canvas(12.6, 5.4, 12.6, 5.4)
    rows = [("original", ["CD3E", "IL7R", "X", "LTB", "TCF7", "…"], None),
            ("delete X", ["CD3E", "IL7R", "LTB", "TCF7", "…"], None),
            ("overexpress X", ["X", "CD3E", "IL7R", "LTB", "TCF7", "…"], 0)]
    for r, (lab, toks, hi) in enumerate(rows):
        y = 4.35 - r * 1.35
        ax.text(0.15, y + 0.3, lab, fontsize=16, weight="bold", va="center")
        for k, t in enumerate(toks):
            x = 2.35 + k * 0.92
            fc = OPEN if t == "X" else (GREY if t == "…" else NOR)
            ax.add_patch(FancyBboxPatch((x, y), 0.8, 0.6, boxstyle="round,pad=0.01,rounding_size=0.08", fc=fc, ec="none"))
            ax.text(x + 0.4, y + 0.3, t, ha="center", va="center", fontsize=13, color="white", family="monospace")
        arrow(ax, (8.0, y + 0.3), (8.75, y + 0.3), color=GREY)
        box(ax, 8.85, y - 0.02, 1.5, 0.64, "model", fc=INK, ec=INK, color="white", fs=14)
        arrow(ax, (10.4, y + 0.3), (11.05, y + 0.3), color=GREY)
        ax.text(11.15, y + 0.3, r"$e$" if r == 0 else r"$e'$", fontsize=21, va="center")
    ax.text(0.15, 0.55, "Score per cell:  cos(e', g) − cos(e, g),   g = centroid of the same donor's normal T cells.\n"
                        "Mean over the donor's cells that carry X, then median over donors (≥ 10 donors with ≥ 10 such cells).",
            fontsize=14.5, va="center", color="#33445a", linespacing=1.5)
    ax.text(12.5, 5.38, "Diagram", ha="right", va="top", fontsize=12, color=GREY, style="italic")
    fig.tight_layout(); save(fig, "isp_mech.png")


def fig_criteria():
    """The six checks in the order a result meets them, and the outcome names."""
    fig, ax = canvas(12.6, 4.3, 12.6, 4.3)
    steps = ["1\nRegistered\nfirst", "2\nInstrument\nworks", "3\nSame cells,\nboth edits", "4\nBeats\nlook-alikes",
             "5\nBeats random\ngenes", "6\nDonor-level,\nstable"]
    w, gap, y = 1.62, 0.2, 2.1
    for i, s in enumerate(steps):
        x = 0.15 + i * (w + gap)
        box(ax, x, y - 0.15, w, 1.65, s, fc="#ffffff", ec=PASS, fs=12.5, lw=1.8)
        if i < 5:
            arrow(ax, (x + w + 0.01, y + 0.67), (x + w + gap - 0.01, y + 0.67), color=PASS)
    xe = 0.15 + 6 * (w + gap)
    arrow(ax, (xe - gap + 0.01, y + 0.67), (xe + 0.12, y + 0.67), color=PASS)
    ax.text(xe + 0.15, y + 0.67, "a call", fontsize=16, va="center", weight="bold")
    outs = [("positive", PASS), ("negative", INK), ("opposite_direction", INK), ("control_draw_sensitive_open", OPEN),
            ("not_estimable", GREY), ("no_op_failed", FAIL)]
    x = 0.15
    ax.text(0.15, 1.35, "Fixed outcome names (never \"no effect\"):", fontsize=14, color="#33445a")
    for name, c in outs:
        wd = 0.108 * len(name) + 0.3
        ax.add_patch(FancyBboxPatch((x, 0.35), wd, 0.6, boxstyle="round,pad=0.01,rounding_size=0.06", fc="#ffffff", ec=c, lw=1.6))
        ax.text(x + wd / 2, 0.65, name, ha="center", va="center", fontsize=11.5, color=c, family="monospace")
        x += wd + 0.14
    ax.text(12.5, 4.28, "Diagram (ISP-STD-1)", ha="right", va="top", fontsize=12, color=GREY, style="italic")
    fig.tight_layout(); save(fig, "criteria.png")


def fig_finetune():
    """Two clouds of cells from one patient, and the boundary the fine-tuned model learns."""
    rng = np.random.default_rng(5)
    t = rng.normal([2.4, 2.2], 0.6, size=(80, 2)); n = rng.normal([6.0, 4.4], 0.6, size=(80, 2))
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.scatter(*t.T, s=40, color=TUM, alpha=0.7, lw=0, label="tumour-infiltrating T cells")
    ax.scatter(*n.T, s=40, color=NOR, alpha=0.7, lw=0, label="normal-tissue T cells")
    xs = np.linspace(2.0, 8.0, 10); ax.plot(xs, -0.95 * xs + 7.6, color=INK, lw=2, ls="--")
    ax.text(4.6, 0.5, "learned decision boundary", fontsize=15, ha="left", bbox=dict(fc=PAPER, ec="none", pad=2))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel("embedding space (2-D sketch)")
    ax.legend(loc="upper left", frameon=False, fontsize=15); ax.set_xlim(0, 8.4); ax.set_ylim(0, 7.2)
    stamp(ax, "Schematic, one donor, not data")
    fig.tight_layout(); save(fig, "finetune.png")


def fig_isp():
    """A tumour T cell, the donor's normal centroid, and the two edits."""
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    t = rng.normal([2.2, 2.0], 0.55, size=(60, 2)); n = rng.normal([6.6, 4.1], 0.5, size=(60, 2))
    ax.scatter(*t.T, s=30, color=TUM, alpha=0.45, lw=0, label="tumour T cells")
    ax.scatter(*n.T, s=30, color=NOR, alpha=0.45, lw=0, label="same donor, normal T cells")
    goal = n.mean(0)
    ax.scatter(*goal, s=420, marker="*", color=NOR, edgecolor=INK, lw=1.4, zorder=6)
    ax.text(goal[0], goal[1] + 0.85, "goal g: centroid of this\ndonor's normal T cells", fontsize=14, ha="center")
    c = np.array([2.5, 2.3]); ax.scatter(*c, s=150, color=INK, zorder=7)
    ax.text(c[0] - 0.15, c[1] + 0.45, "one tumour T cell", fontsize=14, ha="right")
    for d, col, lab, off in [((1.35, 0.68), NOR, "delete X", (0.2, -0.6)),
                             ((-0.9, -0.5), TUM, "overexpress X", (-0.1, -0.7))]:
        ax.add_patch(FancyArrowPatch(c, c + d, arrowstyle="-|>", mutation_scale=26, lw=3, color=col, zorder=8))
        ax.text(*(c + np.array(d) + np.array(off)), lab, fontsize=14, color=col, ha="left" if d[0] > 0 else "right")
    ax.annotate("", xy=goal, xytext=c, arrowprops=dict(arrowstyle="-", ls=(0, (3, 3)), color=GREY, lw=1.4))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel("embedding space (2-D sketch)")
    ax.legend(loc="upper left", frameon=False, fontsize=14); ax.set_xlim(-0.4, 8.6); ax.set_ylim(-0.2, 6.0)
    stamp(ax)
    fig.tight_layout(); save(fig, "isp.png")


def fig_baseline():
    """How a candidate is judged: against the spread of matched control genes."""
    rng = np.random.default_rng(11)
    ctrl = rng.normal(0.0, 1.0, 400)
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.hist(ctrl, bins=30, color=GREY, alpha=0.75)
    ax.axvline(3.4, color=PASS, lw=3); ax.text(3.45, 34, "outside the\ncontrol spread", color=PASS, fontsize=15, va="top")
    ax.axvline(1.1, color=FAIL, lw=3); ax.text(1.15, 44, "large raw shift,\ninside the\ncontrol spread", color=FAIL, fontsize=15, va="top")
    ax.set_yticks([]); ax.set_xticks([]); ax.spines["left"].set_visible(False)
    ax.set_xlabel("shift toward the normal centroid")
    ax.text(-3.2, 40, "matched control\ngenes", color=INK, fontsize=15, va="top")
    stamp(ax)
    fig.tight_layout(); save(fig, "baseline.png")


# ---------- data figures ----------
def fig_one_patient():
    """T6: one SCLC donor held 74.9% of the SCLC test cells."""
    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    ax.barh([0], [74.9], color=FAIL); ax.barh([0], [25.1], left=[74.9], color=GREY)
    ax.text(37.4, 0, "one donor: 74.9%", ha="center", va="center", color="white", fontsize=18, weight="bold")
    ax.text(87.4, 0, "other two\ndonors: 25.1%", ha="center", va="center", color="white", fontsize=14)
    ax.set_xlim(0, 100); ax.set_yticks([]); ax.set_xlabel("share of the SCLC test cells, %")
    ax.spines["left"].set_visible(False)
    fig.tight_layout(); save(fig, "one_patient.png")


def fig_unpaired():
    """Unpaired arms: overexpression scored on 2,424 cells for every gene, deletion on 202 to 1,131."""
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.bar([0], [2424], color=FAIL, width=0.55)
    ax.bar([1], [1131], color=GREY, width=0.55); ax.bar([1], [202], color=INK, width=0.55, alpha=0.35)
    ax.text(0, 2424 + 60, "2,424 for every gene", ha="center", fontsize=15)
    ax.text(1, 1131 + 60, "202 to 1,131,\ndepending on the gene", ha="center", fontsize=15)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["overexpress\n(all test cells)", "delete\n(cells carrying the gene)"])
    ax.set_ylabel("cells scored"); ax.set_ylim(0, 2900)
    ax.set_title("August panel: the two arms used different cells", fontsize=16, loc="left")
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
    ax.set_xlabel("deletion shift toward normal\n(rank among 200 random genes)")
    ax.set_ylabel("overexpression shift toward normal\n(rank among the same genes)")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["lowest", "highest"]); ax.set_yticks([0, 1]); ax.set_yticklabels(["lowest", "highest"])
    ax.text(0.98, 0.97, f"Spearman ρ\n{r1:.3f} (first 100 genes)\n{r2:.3f} (all 200)", transform=ax.transAxes,
            ha="right", va="top", fontsize=15, bbox=dict(fc=PAPER, ec=FAIL, lw=1.4, boxstyle="round,pad=0.4"))
    ax.set_title("Each point: one random gene; lung, 43 donors", fontsize=15, loc="left")
    fig.tight_layout(); save(fig, "null_scatter.png")
    return r1, r2


def fig_gate_strip():
    e2, lu = load("e2_classifier_gate.json"), load("luad_classifier_gate.json")
    ev, lv = sorted(e2["per_donor_balanced_accuracy"].values()), sorted(lu["per_donor_balanced_accuracy"].values())
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    rng = np.random.default_rng(3)
    for i, (v, pooled) in enumerate([(lv, lu["pooled_balanced_accuracy"]), (ev, e2["pooled_balanced_accuracy"])]):
        ax.scatter(i + rng.uniform(-0.15, 0.15, len(v)), v, s=46, color=PASS, alpha=0.85, lw=0)
        ax.plot([i - 0.28, i + 0.28], [pooled] * 2, color=INK, lw=3)
        ax.text(i + 0.31, pooled, f"{pooled:.3f}", va="center", fontsize=16)
    ax.axhline(0.50, color=FAIL, ls=":", lw=1.6); ax.text(1.62, 0.508, "chance (0.5)", fontsize=14, ha="right", color=FAIL)
    ax.axhline(0.60, color=GREY, ls="--", lw=1.2); ax.text(1.62, 0.608, "gate (0.60)", fontsize=14, ha="right", color=GREY)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Lung (LUAD)\n43 donors", "Colon (E2)\n19 donors"])
    ax.set_ylabel("held-out balanced accuracy"); ax.set_ylim(0.45, 1.01); ax.set_xlim(-0.55, 1.68)
    ax.set_title("Each point: one held-out donor", fontsize=15, loc="left")
    fig.tight_layout(); save(fig, "gate_strip.png")
    return (lu["pooled_balanced_accuracy"], lu["donors_above_0.5"], e2["pooled_balanced_accuracy"], e2["donors_above_0.5"], min(ev))


def read_e0():
    with open(os.path.join(DATA, "pelka_e0_counts.csv")) as f:
        return list(csv.DictReader(f))


def fig_e0_cohort():
    """E0: donors of Pelka et al. 2021 with a normal-colon specimen; CD4+CD8 T cells per tissue."""
    rows = [r for r in read_e0() if r["has_N"] == "True"]
    e2 = set(load("e2_classifier_gate.json")["per_donor_balanced_accuracy"])
    q = [r for r in rows if r["qual_100"] == "True"]
    assert len(rows) == 36 and len(q) == 25 and e2 <= {r["PID"] for r in q} and len(e2) == 19
    fig, ax = plt.subplots(figsize=(7.8, 5.8))
    groups = [([r for r in rows if r["PID"] in e2], dict(color=PASS, s=70), "E2 cohort (19)"),
              ([r for r in q if r["PID"] not in e2], dict(facecolor="none", edgecolor=PASS, lw=1.8, s=70),
               "≥100 in both, dropped:\nsorting differs (6)"),
              ([r for r in rows if r["qual_100"] != "True"], dict(color=GREY, s=50, marker="x"), "<100 in a tissue (11)")]
    for g, kw, lab in groups:
        ax.scatter([int(r["N_T"]) for r in g], [int(r["T_T"]) for r in g], label=lab, **kw)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.axvline(100, color=INK, ls=":", lw=1.3); ax.axhline(100, color=INK, ls=":", lw=1.3)
    ax.set_xlim(5, 3000); ax.set_ylim(25, 5000)
    ax.set_xlabel("normal-colon T cells per donor"); ax.set_ylabel("tumour T cells per donor")
    ax.legend(loc="upper left", frameon=False, fontsize=13.5, scatterpoints=1)
    ax.set_title("36 donors with a normal specimen (all processing)", fontsize=14.5, loc="left")
    fig.tight_layout(); save(fig, "e0_cohort.png")
    mmr = {}
    for r in q:
        mmr[r["MMR"]] = mmr.get(r["MMR"], 0) + 1
    return len(read_e0()), len(rows), len(q), mmr


def fig_e2_gate():
    """E2 classifier gate: per-donor held-out balanced accuracy, MMR status from the E0 table."""
    g = load("e2_classifier_gate.json")
    mmr = {r["PID"]: r["MMR"] for r in read_e0()}
    items = sorted(g["per_donor_balanced_accuracy"].items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    for i, (pid, v) in enumerate(items):
        ax.scatter(i, v, s=90, color=PASS if mmr[pid] == "MMRd" else "white", edgecolor=PASS, lw=2,
                   marker="o" if mmr[pid] == "MMRd" else "s", zorder=3)
    nd = sum(mmr[k] == "MMRd" for k, _ in items)
    ax.scatter([], [], s=90, color=PASS, marker="o", label=f"MMR-deficient ({nd})")
    ax.scatter([], [], s=90, color="white", edgecolor=PASS, lw=2, marker="s", label=f"MMR-proficient ({len(items) - nd})")
    p = g["pooled_balanced_accuracy"]
    ax.axhline(p, color=INK, lw=2.2); ax.text(18.4, p + 0.012, f"pooled {p:.3f}", ha="right", fontsize=14)
    ax.axhline(g["gate_ba"], color=GREY, ls="--", lw=1.3); ax.text(18.4, g["gate_ba"] + 0.012, "gate 0.60", ha="right", fontsize=13, color=GREY)
    ax.axhline(0.5, color=FAIL, ls=":", lw=1.5); ax.text(18.4, 0.512, "chance 0.5", ha="right", fontsize=13, color=FAIL)
    ax.set_xticks(range(len(items))); ax.set_xticklabels([k for k, _ in items], rotation=90, fontsize=11.5)
    ax.set_ylim(0.45, 1.0); ax.set_ylabel("held-out balanced accuracy")
    ax.legend(loc="upper left", frameon=False, fontsize=13, scatterpoints=1)
    ax.set_title(f"{g['donors_above_0.5']} of {g['n_donors']} donors above chance; sign test p = {g['sign_test_p_float']:.1e}",
                 fontsize=14.5, loc="left")
    fig.tight_layout(); save(fig, "e2_gate.png")
    return p, g["donors_above_0.5"], min(v for _, v in items), g["sign_test_p_float"], g["PASS"]


def fig_e2_results():
    """E2 perturbation results (geneformer-lung-tcell, analysis/e2-pelka-crc-20261001 at 55b06a4; results b7369cb):
    H2b null genes, deletion vs overexpression medians; H2c colon deletion medians of the 10 testable LUAD reference genes."""
    h = load("e2_h2b_null_result.json"); c = load("e2_h2c_result.json")
    rows = {r["gene"]: r for r in load("e2_panel_b_outcome_rows.json")}
    pr = h["primary"]
    assert pr["status"] == "control_draw_sensitive_open" and pr["n_estimable"] == 100
    d = np.array(h["null_delete_medians"]) * 1e3; o = np.array(h["null_overexpress_medians"]) * 1e3
    assert abs(float(spearmanr(d, o)[0]) - pr["rho"]) < 1e-12
    ref = [g for g in c["per_gene"] if g["e2_tested"]]
    assert len(ref) == c["n_tested"] == 10 and sum(g["del_agree"] for g in ref) == c["del_agree"] == 3
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 7.6), gridspec_kw={"height_ratios": [1, 1.1]})
    a1.axhline(0, color=GREY, lw=1); a1.axvline(0, color=GREY, lw=1)
    a1.scatter(d, o, s=26, color=INK, alpha=0.75, lw=0)
    a1.set_xlabel("deletion shift, donor median (×10⁻³)", fontsize=15); a1.set_ylabel("overexpression\nshift (×10⁻³)", fontsize=15)
    a1.tick_params(labelsize=14)
    a1.set_title("100 random genes", fontsize=15, loc="left")
    ref.sort(key=lambda g: g["e2_del_median"])
    y = np.arange(len(ref))
    a2.axvline(0, color=GREY, lw=1)
    for yi, g in zip(y, ref):
        r = rows[g["gene"]]; assert abs(r["del_median"] - g["e2_del_median"]) < 1e-15
        col = INK if g["del_agree"] else "#7d93ad"
        a2.plot([r["del_ci_lo"] * 1e3, r["del_ci_hi"] * 1e3], [yi, yi], color=col, lw=2)
        a2.scatter(r["del_median"] * 1e3, yi, s=60, color=col if g["del_agree"] else PAPER, edgecolor=col, lw=2, zorder=5)
    a2.set_yticks(y)
    a2.set_yticklabels([f"{g['symbol']} ({'toward' if g['luad_del_median'] > 0 else 'away'})" for g in ref], fontsize=15)
    a2.set_xlabel("colon deletion shift, control-adjusted\n(×10⁻³, 95% CI)   ← away | toward normal →", fontsize=14.5)
    a2.tick_params(axis="x", labelsize=14)
    a2.set_title(f"Lung reference genes (lung direction);\nfilled: kept in colon ({c['del_agree']} of {c['n_tested']})",
                 fontsize=15, loc="left")
    fig.tight_layout(); save(fig, "e2_results.png")
    return pr["rho"], pr["p_lower_tail"], pr["bootstrap_fraction_stable"], c["del_agree"], c["p_exact"], c["reading"]


# ---------- bulk RNA-seq ----------
def fig_bulk_mix():
    """Why a bulk profile is not a cell: composition changes the bulk value with no change inside any cell."""
    types = ["T cells", "epithelial / tumour", "myeloid", "stromal"]
    cols = [NOR, TUM, OPEN, GREY]
    comp = {"normal tissue": [0.30, 0.40, 0.10, 0.20], "tumour": [0.10, 0.60, 0.20, 0.10]}
    expr = np.array([8.0, 0.5, 4.0, 1.0])  # gene G per cell type, identical in both samples
    fig, axs = plt.subplots(1, 2, figsize=(12.4, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axs[0]
    for j, (lab, c) in enumerate(comp.items()):
        left = 0
        for k, f in enumerate(c):
            ax.barh(j, f, left=left, color=cols[k], label=types[k] if j == 0 else None)
            left += f
    ax.set_yticks([0, 1]); ax.set_yticklabels(list(comp)); ax.set_xlim(0, 1); ax.set_xlabel("share of cells in the sample")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=2, frameon=False, fontsize=13)
    ax.set_title("1. Same cell types, different mix", loc="left", fontsize=16)
    ax = axs[1]
    bulk = [float(np.dot(c, expr)) for c in comp.values()]
    ax.bar([0, 1], [expr[0], expr[0]], width=0.35, color=NOR, label="inside a T cell")
    ax.bar([0.4, 1.4], bulk, width=0.35, color=INK, label="bulk sample")
    ax.set_xticks([0.2, 1.2]); ax.set_xticklabels(list(comp)); ax.set_yticks([]); ax.set_ylabel("level of gene G"); ax.set_ylim(0, expr[0] * 1.45)
    ax.legend(loc="upper right", frameon=False, fontsize=13)
    ax.set_title("2. Bulk level of G changes", loc="left", fontsize=16)
    fig.tight_layout()
    fig.text(0.99, 0.02, "Schematic, invented values", ha="right", va="bottom", fontsize=13, color=GREY, style="italic")
    save(fig, "bulk_mix.png")


def fig_bulk_result():
    """Bulk network ISP against 17 measured CRISPR knockouts (Freimer et al. 2022): per-knockout Spearman rho."""
    with open(os.path.join(DATA, "bulk_isp_per_ko.tsv")) as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if r["status"] == "SCORED"]
    t = load("bulk_isp_tests.json")
    assert len(rows) == t["n_scored"] == 17
    assert abs(float(np.median([float(r["rho_resp"]) for r in rows])) - t["P1_rho_resp_median"]) < 1e-9
    rows.sort(key=lambda r: float(r["rho_resp"]))
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8.4, 8.0))
    ax.axvline(0, color=GREY, lw=1)
    for k, (col, kw, lab) in enumerate([
            ("rho_random_median", dict(marker="|", s=260, color=GREY, lw=2.5), "random TFs, same connectivity (median)"),
            ("rho_shuf_median", dict(marker="D", s=46, facecolor="none", edgecolor=OPEN, lw=1.8), "shuffled network (median of 50)"),
            ("rho_baseline", dict(marker="s", s=46, color="#6d8f5e"), "co-expression only, no model"),
            ("rho_resp", dict(marker="o", s=80, color=INK, zorder=5), "network model")]):
        ax.scatter([float(r[col]) for r in rows], y, label=lab, **kw)
    beat = {r["ko"] for r in rows if float(r["p_random_tf"]) <= 0.05}
    ax.set_yticks(y); ax.set_yticklabels([r["ko"] + (" *" if r["ko"] in beat else "") for r in rows], fontsize=13.5)
    ax.set_xlabel("Spearman ρ, predicted vs measured shift\n(genes that respond to the knockout)")
    ax.set_xlim(-0.45, 0.8)
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.17), ncol=2, frameon=False, fontsize=12, scatterpoints=1)
    ax.set_title(f"Freimer set, 17 knockouts; median ρ {t['P1_rho_resp_median']:.3f};  * beats random TFs ({t['P4_n_beat_random']}/17)",
                 fontsize=13.5, loc="left")
    fig.tight_layout(); save(fig, "bulk_result.png")
    return t["reading"], t["P1_rho_resp_median"], t["P3_p"], t["P4_n_beat_random"], sorted(beat)


if __name__ == "__main__":
    fig_pipeline(); fig_tokenise(); fig_isp_mech(); fig_criteria(); fig_finetune(); fig_isp(); fig_baseline()
    fig_one_patient(); fig_unpaired(); fig_bulk_mix()
    print("null", fig_null_scatter())
    print("gate", fig_gate_strip())
    print("e0", fig_e0_cohort())
    print("e2", fig_e2_gate())
    print("e2_results", fig_e2_results())
    print("bulk", fig_bulk_result())
