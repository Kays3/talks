"""Readable redraws of two figures (2026-09-28, human's request via the project lead):
report Figure 4 / slide "Sparse genes fake big effects" (data/assets/detection.png)
and report Figure 5 / slide "The open question is now closed as null"
(data/assets/fig_t6_reversal.png).

Same data, same quantities, same claims as the originals; only the drawing
changes: no label, legend, annotation or point overlaps another; text is at
least 14 pt at the size the figure is shown on the slide; direct labels in
place of crowded legends; Okabe-Ito colour-blind-safe colours; plain-language
axis titles with units.

Sources, read from data/ (sha256 in data/MANIFEST.tsv):
  detection  sclc_validation/checkpoint_cart_perturbation/tables/
             cart_overexpression_vs_deletion.csv, cart_engineering_perturbation.csv
             @ eb533f8 (last changed 37a0211). The original detection.png is
             pixel-identical to figures/cart_overexpression.png @ eb533f8, drawn by
             scripts/make_detection_figure.py @ eb533f8 (copied to data/git/eb533f8/);
             every selection rule below is that script's.
  T6         sclc_validation/immune_axis_test/results/t6_weighting_reconciliation.csv,
             t6_donor_level_scores.csv @ 9ec518c; selection as in
             src/reference/lung_tcell_talk_figures_20260924.py fig_t6_reversal().

Outputs, 300 dpi, sized in inches to the slot each is shown in:
  data/assets/detection.png           panel a (slide 13 slot, 150 x 100 mm)
  data/assets/detection_rank.png      panel b, genes across (appendix slide, 298 x 100 mm)
  data/assets/detection_rank_report.png  panel b, genes down (report, 160 x 190 mm)
  data/assets/fig_t6_reversal.png     T6 (slide 14 slot, 195 x 80 mm)
The originals are kept as data/assets/*_orig.png; the 25 Sep PDF uses those.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.transforms import Bbox
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ASSETS = os.path.join(DATA, "assets")
DET = os.path.join(DATA, "git", "eb533f8", "sclc_validation", "checkpoint_cart_perturbation", "tables")
T6 = os.path.join(DATA, "git", "9ec518c", "sclc_validation", "immune_axis_test", "results")
MM = 1 / 25.4
DPI = 300

# Okabe-Ito
BLUE, SKY, ORANGE, VERMILION, GREY, INK = "#0072B2", "#56B4E9", "#E69F00", "#D55E00", "#9AA3AD", "#16202C"
FS = 14          # minimum text size at slot size, points
LOW_DETECTION = 100

plt.rcParams.update({"svg.hashsalt": "0", "font.family": "DejaVu Sans", "font.size": FS, "axes.titlesize": FS,
                     "axes.labelsize": FS, "xtick.labelsize": FS, "ytick.labelsize": FS,
                     "savefig.facecolor": "white", "figure.facecolor": "white",
                     "axes.spines.top": False, "axes.spines.right": False})


# ---------------------------------------------------------------------------
# data, exactly as make_detection_figure.py @ eb533f8 selects it
# ---------------------------------------------------------------------------
def detection_data():
    panel = pd.read_csv(os.path.join(DET, "cart_overexpression_vs_deletion.csv"))
    cart = pd.read_csv(os.path.join(DET, "cart_engineering_perturbation.csv"))
    sclc = cart[cart.comparison == "sclc_to_normal"]
    replicated = list(sclc[sclc.concordant & sclc.tier.eq("all donors agree") & ~sclc.low_detection_lt100]
                      .sort_values("delete_shift", ascending=False).Gene_name)
    testable = panel[panel.deletion_testable]
    rho, p = spearmanr(testable.detection_n_cells, testable.delete_shift.abs())
    immune = panel[~panel.technical_or_ambient].copy()
    detected = immune[immune.detection_n_cells >= LOW_DETECTION].sort_values("delete_shift", ascending=False)
    rank = {g: i + 1 for i, g in enumerate(detected.Gene_name)}
    source_cells = int(panel.source_cells.iloc[0])
    # The claims the original figure makes; a redraw must reproduce them exactly.
    assert sorted(replicated) == ["CTLA4", "HAVCR2", "IL7R", "TIGIT"], replicated
    assert (round(rho, 2), len(testable), f"{p:.0e}") == (-0.60, 42, "3e-05"), (rho, len(testable), p)
    assert (len(immune), len(detected), rank["HAVCR2"], rank["TIGIT"], source_cells) == (31, 20, 4, 5, 2424)
    return panel, testable, immune, replicated, rho, p, rank, source_cells


def category(row, replicated):
    if row.Gene_name in replicated:
        return "hit"
    if row.low_detection_lt100:
        return "sparse"
    if row.is_cart_candidate:
        return "cart"
    return "other"


STYLE = {  # facecolor, edgecolor, size (pt^2)
    "hit": (BLUE, BLUE, 110),
    "cart": ("none", SKY, 70),
    "sparse": ("none", ORANGE, 70),
    "other": (GREY, GREY, 40),
}


def overlaps(bb, others, pad=1.5):
    bb = Bbox.from_extents(bb.x0 - pad, bb.y0 - pad, bb.x1 + pad, bb.y1 + pad)
    return any(bb.overlaps(o) for o in others)


def place_labels(fig, ax, items, obstacles, split_x=None):
    """Greedy direct labelling: try positions around each point, nearest first,
    and keep the first that overlaps no placed label, no marker and stays inside
    the axes. Returns the number of labels that needed a leader line."""
    renderer = fig.canvas.get_renderer()
    ax_bb = ax.get_window_extent(renderer)
    placed = list(obstacles)
    markers_only = [o for o in obstacles if getattr(o, "_is_marker", False)]
    leaders = 0
    for (x, y, text, kw) in items:
        kw = dict(kw)
        side = kw.pop("side", None)       # label must sit left/right of split_x (pixels)
        done = False
        for dist in (6, 10, 16, 24, 34, 46, 60, 76, 95, 115):
            for dx, dy in [(1, 0.6), (1, -1), (-1, 0.6), (-1, -1), (0, 1.3), (0, -1.8), (1.4, 0), (-1.4, 0)] + \
                          [(round(np.cos(a), 3) * 1.3, round(np.sin(a), 3) * 1.3) for a in np.linspace(0, 2 * np.pi, 17)[:-1]]:
                ha = "left" if dx > 0 else "right" if dx < 0 else "center"
                t = ax.annotate(text, (x, y), xytext=(dx * dist, dy * dist), textcoords="offset points",
                                ha=ha, va="center", **kw)
                bb = t.get_window_extent(renderer)
                inside = ax_bb.x0 <= bb.x0 and bb.x1 <= ax_bb.x1 and ax_bb.y0 <= bb.y0 and bb.y1 <= ax_bb.y1
                anchor = ax.transData.transform((x, y))
                seg_ok = True
                if dist > 10:
                    cx = bb.x0 if dx > 0 else bb.x1 if dx < 0 else (bb.x0 + bb.x1) / 2
                    cy = (bb.y0 + bb.y1) / 2
                    for f in np.linspace(0.05, 0.98, 80):
                        px, py = anchor[0] + f * (cx - anchor[0]), anchor[1] + f * (cy - anchor[1])
                        # leaders may pass markers, never text or the threshold line
                        if any(o.x0 <= px <= o.x1 and o.y0 <= py <= o.y1 for o in placed
                               if not getattr(o, "_is_marker", False)):
                            seg_ok = False
                            break
                side_ok = (side is None or split_x is None or
                           (side == "right" and bb.x0 > split_x + 3) or (side == "left" and bb.x1 < split_x - 3))
                if inside and seg_ok and side_ok and not overlaps(bb, placed):
                    placed.append(bb)
                    if dist > 10:
                        t.remove()
                        ax.annotate(text, (x, y), xytext=(dx * dist, dy * dist), textcoords="offset points",
                                    ha=ha, va="center",
                                    arrowprops=dict(arrowstyle="-", color="#6B7785", lw=0.8, shrinkA=0, shrinkB=4),
                                    **kw)
                        leaders += 1
                    done = True
                    break
                t.remove()
            if done:
                break
        if not done:
            raise RuntimeError(f"no free position for label {text!r}")
    return placed, leaders


def marker_boxes(fig, ax, xs, ys, sizes):
    fig.canvas.draw()
    boxes = []
    for x, y, s in zip(xs, ys, sizes):
        px, py = ax.transData.transform((x, y))
        r = (s ** 0.5) / 2 * fig.dpi / 72 + 1
        b = Bbox.from_extents(px - r, py - r, px + r, py + r)
        b._is_marker = True
        boxes.append(b)
    return boxes


def fig_detection_scatter(path, w_mm=150, h_mm=100):
    panel, testable, immune, replicated, rho, p, rank, source_cells = detection_data()
    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM), dpi=DPI)
    ax = fig.add_axes([0.19, 0.36, 0.78, 0.47])
    xs, ys, ss = [], [], []
    for _, r in testable.iterrows():
        c = category(r, replicated)
        fc, ec, s = STYLE[c]
        x, y = r.detection_n_cells, abs(r.delete_shift)
        ax.scatter(x, y, s=s, facecolors=fc, edgecolors=ec, linewidths=1.6, zorder=3 if c == "hit" else 2)
        xs.append(x); ys.append(y); ss.append(s)
    ax.axvline(LOW_DETECTION, color=ORANGE, linestyle="--", linewidth=1.4, zorder=1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.6, 6000)
    ax.set_ylim(1.5e-6, 1.2)
    notes = [(0.75, 3e-6, "< 100 cells:\nunreliable", dict(fontsize=FS, color="#9A6200", va="bottom"))]
    ax.set_xlabel(f"Cells detected in (of {source_cells:,} SCLC T cells)")
    ax.set_ylabel("Deletion effect size\n(|shift|, log scale)")
    ax.set_title(f"Rarely detected genes show the largest effects\n"
                 f"Spearman ρ = {rho:.2f}, p = {p:.1e}, n = {len(testable)} genes", loc="left", fontsize=FS)
    ax.grid(alpha=0.18)
    obstacles = marker_boxes(fig, ax, xs, ys, ss)
    r = fig.canvas.get_renderer()
    # the dashed threshold line is an obstacle for labels and leader lines
    lx = ax.transData.transform((LOW_DETECTION, 1))[0]
    ab = ax.get_window_extent(r)
    line_box = Bbox.from_extents(lx - 2, ab.y0, lx + 2, ab.y1)
    obstacles.append(line_box)
    # region note
    for x, y, text, kw in notes:
        kw = dict(kw); va = kw.pop("va", "center")
        t = ax.text(x, y, text, ha="left", va=va, **kw)
        fig.canvas.draw()
        obstacles.append(t.get_window_extent(r))
    items = []
    hits = testable[testable.Gene_name.isin(replicated)]
    for _, row in hits.iterrows():
        name = {"HAVCR2": "TIM-3", "CTLA4": "CTLA-4"}.get(row.Gene_name, row.Gene_name)
        items.append((row.detection_n_cells, abs(row.delete_shift), name,
                      dict(fontsize=FS, fontweight="bold", color=BLUE, side="right")))
    sparse = (testable[testable.low_detection_lt100].assign(_a=lambda d: d.delete_shift.abs()).nlargest(5, "_a"))
    for _, row in sparse.iterrows():
        items.append((row.detection_n_cells, abs(row.delete_shift), row.Gene_name,
                      dict(fontsize=FS, color="#9A6200", side="left")))
    _, leaders = place_labels(fig, ax, items, obstacles, split_x=lx)
    key = [("●", BLUE, "replicated hit"), ("○", SKY, "other CAR-T candidate"), ("●", GREY, "other immune gene")]
    rows_y, x0, row = [0.075, 0.012], 0.02, 0
    for sym, col, lab in key:
        for attempt in (0, 1):
            t = fig.text(x0, rows_y[row], sym, color=col, fontsize=FS, va="bottom")
            t2 = fig.text(0, rows_y[row], lab, color=INK, fontsize=FS, va="bottom")
            fig.canvas.draw()
            t2.set_x(t.get_window_extent().x1 / fig.bbox.width + 0.005)
            fig.canvas.draw()
            end = t2.get_window_extent().x1 / fig.bbox.width
            if end <= 0.99 or attempt == 1:
                break
            t.remove(); t2.remove()
            row, x0 = row + 1, 0.02          # wrap the key onto its second row
        assert end <= 0.99, f"key entry {lab!r} does not fit"
        x0 = end + 0.03
    assert_text_clean(fig)
    fig.savefig(path, dpi=DPI, metadata={"Software": None})
    plt.close(fig)
    return {"leaders": leaders}


def fig_detection_rank(path, w_mm=298, h_mm=95):
    """Panel b, genes across: every immune/lineage gene, deletion shift SCLC->normal."""
    panel, testable, immune, replicated, rho, p, rank, source_cells = detection_data()
    order = immune.sort_values("delete_shift", ascending=False, na_position="last").reset_index(drop=True)
    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM), dpi=DPI)
    ax = fig.add_axes([0.1, 0.44, 0.885, 0.4])
    x = np.arange(len(order))
    for i, r in order.iterrows():
        if not r.deletion_testable:
            ax.text(i, 2e-4, "n.d.", rotation=90, ha="center", va="bottom", fontsize=FS, color="#6B7785",
                    style="italic")
            continue
        c = category(r, replicated)
        fc, ec, s = STYLE[c]
        ax.plot([i, i], [0, r.delete_shift], color="#D5DCE3", lw=1.4, zorder=1)
        ax.scatter(i, r.delete_shift, s=s * 1.3, facecolors=fc, edgecolors=ec, linewidths=1.6, zorder=3)
    ax.axhline(0, color="#8B96A5", lw=1)
    ax.set_yscale("symlog", linthresh=1e-3)
    ax.set_ylabel("Deletion shift\n(up = toward normal)")
    ax.set_ylim(-0.08, 0.08)
    labels = [f"{g} ({'0' if pd.isna(n) else f'{int(n):,}'})" for g, n in zip(order.Gene_name, order.detection_n_cells)]
    ax.set_xticks(x, labels, rotation=90, fontsize=FS)
    for tick, g, lo in zip(ax.get_xticklabels(), order.Gene_name, order.low_detection_lt100):
        if g in replicated:
            tick.set_fontweight("bold"); tick.set_color(BLUE)
        elif lo:
            tick.set_color("#9A6200")
    ax.set_xlim(-0.7, len(order) - 0.3)
    ax.set_title(f"All {len(immune)} immune / lineage genes, SCLC → normal, ranked by deletion shift "
                 f"(cells detected in brackets). {sum(immune.detection_n_cells >= LOW_DETECTION)} detected in "
                 f"≥ {LOW_DETECTION} cells: TIM-3 (HAVCR2) ranks {rank['HAVCR2']}th, TIGIT {rank['TIGIT']}th. "
                 f"Orange names: < {LOW_DETECTION} cells.", loc="left", fontsize=FS, wrap=True)
    ax.grid(axis="y", alpha=0.18)
    assert_text_clean(fig)
    fig.savefig(path, dpi=DPI, metadata={"Software": None})
    plt.close(fig)


def fig_detection_rank_report(path, w_mm=160, h_mm=200):
    """Panel b, genes down, for the A4 report (text at report size, >= 10 pt)."""
    panel, testable, immune, replicated, rho, p, rank, source_cells = detection_data()
    order = immune.sort_values("delete_shift", ascending=True, na_position="first").reset_index(drop=True)
    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM), dpi=DPI)
    ax = fig.add_axes([0.3, 0.11, 0.66, 0.78])
    y = np.arange(len(order))
    for i, r in order.iterrows():
        if not r.deletion_testable:
            ax.text(0, i, "  n.d. (not detected)", va="center", fontsize=10.5, color="#6B7785", style="italic")
            continue
        c = category(r, replicated)
        fc, ec, s = STYLE[c]
        ax.plot([0, r.delete_shift], [i, i], color="#D5DCE3", lw=1.4, zorder=1)
        ax.scatter(r.delete_shift, i, s=s, facecolors=fc, edgecolors=ec, linewidths=1.5, zorder=3)
    ax.axvline(0, color="#8B96A5", lw=1)
    ax.set_xscale("symlog", linthresh=1e-3)
    labels = [f"{g} ({'0' if pd.isna(n) else f'{int(n):,}'})" for g, n in zip(order.Gene_name, order.detection_n_cells)]
    ax.set_yticks(y, labels, fontsize=10.5)
    for tick, g, lo in zip(ax.get_yticklabels(), order.Gene_name, order.low_detection_lt100):
        if g in replicated:
            tick.set_fontweight("bold"); tick.set_color(BLUE)
        elif lo:
            tick.set_color("#9A6200")
    ax.tick_params(axis="x", labelsize=10.5)
    ax.set_xlabel("Deletion shift, SCLC → normal\n(symmetric log scale; right = toward normal)", fontsize=10.5)
    ax.set_xlim(-0.05, 0.05)
    ax.set_title(f"All {len(immune)} immune / lineage genes (cells detected in brackets)\n"
                 f"{sum(immune.detection_n_cells >= LOW_DETECTION)} detected in ≥ {LOW_DETECTION} cells: "
                 f"TIM-3 (HAVCR2) {rank['HAVCR2']}th, TIGIT {rank['TIGIT']}th\n"
                 f"orange names: < {LOW_DETECTION} cells, effect unreliable",
                 loc="left", fontsize=10.5)
    ax.set_ylim(-0.8, len(order) - 0.2)
    ax.grid(axis="x", alpha=0.18)
    assert_text_clean(fig)
    fig.savefig(path, dpi=DPI, metadata={"Software": None})
    plt.close(fig)


# ---------------------------------------------------------------------------
# T6, exactly the quantities of fig_t6_reversal() in src/reference/
# ---------------------------------------------------------------------------
def fig_t6(path, w_mm=195, h_mm=80):
    recon = pd.read_csv(os.path.join(T6, "t6_weighting_reconciliation.csv"))
    donors = pd.read_csv(os.path.join(T6, "t6_donor_level_scores.csv"))
    get = lambda pop, st: recon[(recon.population == pop) & (recon.state == st)].iloc[0]
    cs, cl, ts, tl = get("complete", "sclc"), get("complete", "luad"), get("test_only", "sclc"), get("test_only", "luad")
    pe = donors[(donors.donor == "PleuralEffusion") & (donors.population == "test_only")].iloc[0]
    pe_share = float(ts.max_donor_cell_share)
    assert abs(pe_share - 0.74917) < 1e-3 and round(float(pe.score), 3) == 0.122
    vals = {"d_c_s": cs.donor_level_mean, "d_c_l": cl.donor_level_mean, "d_t_s": ts.donor_level_mean,
            "d_t_l": tl.donor_level_mean, "w_t_s": ts.cell_weighted_mean, "w_t_l": tl.cell_weighted_mean}
    assert [round(vals[k], 3) for k in ("d_c_s", "d_c_l", "d_t_s", "d_t_l")] == [0.301, 0.244, 0.321, 0.267]

    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM), dpi=DPI)
    fig.text(0.01, 0.97, "The SCLC-vs-LUAD \"disagreement\" is a weighting artifact", fontsize=FS,
             fontweight="bold", va="top", color=INK)
    a1 = fig.add_axes([0.15, 0.22, 0.42, 0.53])
    a2 = fig.add_axes([0.64, 0.22, 0.34, 0.53], sharey=a1)
    ymax = 0.72
    # panel 1: each person counted once, both populations
    xpos = [0, 0.9, 2.3, 3.2]
    bars = [(xpos[0], vals["d_c_s"], VERMILION, "SCLC"), (xpos[1], vals["d_c_l"], BLUE, "LUAD"),
            (xpos[2], vals["d_t_s"], VERMILION, "SCLC"), (xpos[3], vals["d_t_l"], BLUE, "LUAD")]
    for x, v, col, lab in bars:
        a1.bar(x, v, 0.8, color=col)
        a1.text(x, v + 0.012, f"{v:.3f}", ha="center", va="bottom", fontsize=FS)
    a1.set_xticks(xpos, [b[3] for b in bars])
    a1.text(0.45, -0.2, "all donors", ha="center", va="top", transform=a1.get_xaxis_transform(), fontsize=FS)
    a1.text(2.75, -0.2, "test split only", ha="center", va="top", transform=a1.get_xaxis_transform(), fontsize=FS)
    a1.set_title("Each person counted once:\nSCLC > LUAD in both", loc="left", fontsize=FS)
    a1.set_ylabel("Exhaustion score")
    a1.set_ylim(0, ymax)
    a1.set_yticks([0, 0.2, 0.4, 0.6])
    # panel 2: test split, each cell counted once
    for x, v, col, lab in ((0, vals["w_t_s"], VERMILION, "SCLC"), (1, vals["w_t_l"], BLUE, "LUAD")):
        a2.bar(x, v, 0.7, color=col)
        a2.text(x, v + 0.012, f"{v:.3f}", ha="center", va="bottom", fontsize=FS)
    a2.set_xticks([0, 1], ["SCLC", "LUAD"])
    a2.text(0.5, -0.2, "test split only", ha="center", va="top", transform=a2.get_xaxis_transform(), fontsize=FS)
    a2.set_title("Each cell counted once:\nthe order flips", loc="left", fontsize=FS)
    a2.tick_params(labelleft=False)
    a2.text(-0.5, 0.36, f"PleuralEffusion donor\n(HTA8_2001): {pe_share * 100:.1f}%\nof these SCLC cells,\nscore {float(pe.score):.3f}",
            ha="left", va="bottom", fontsize=FS, color=VERMILION)
    a2.set_xlim(-0.6, 1.6)
    assert_text_clean(fig)
    fig.savefig(path, dpi=DPI, metadata={"Software": None})
    plt.close(fig)
    return vals


def assert_text_clean(fig):
    """Every visible text item lies inside the canvas and overlaps no other text item."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    fb = fig.bbox
    boxes = []
    tick_all, tick_drawn = set(), []
    for ax_ in fig.axes:
        for axis in (ax_.xaxis, ax_.yaxis):
            for which in (False, True):
                tick_all.update(id(t) for t in axis.get_ticklabels(minor=which))
            for tick in axis._update_ticks():           # only the ticks matplotlib actually draws
                tick_drawn += [tick.label1, tick.label2]
    texts = [t for t in fig.findobj(matplotlib.text.Text) if id(t) not in tick_all] + tick_drawn
    for t in texts:
        if not t.get_visible() or not t.get_text().strip():
            continue
        b = matplotlib.text.Text.get_window_extent(t, r)   # the text only, not an annotation's leader line
        assert fb.x0 - 1 <= b.x0 and b.x1 <= fb.x1 + 1 and fb.y0 - 1 <= b.y0 and b.y1 <= fb.y1 + 1, \
            f"text {t.get_text()!r} runs off the canvas"
        boxes.append((t.get_text(), b))
    for i, (ta, a) in enumerate(boxes):
        for tb, b in boxes[i + 1:]:
            inter = Bbox.intersection(a, b)
            assert inter is None or inter.width * inter.height < 4, f"text overlap: {ta!r} / {tb!r}"
    return len(boxes)


if __name__ == "__main__":
    out = {}
    out["detection.png"] = fig_detection_scatter(os.path.join(ASSETS, "detection.png"))
    fig_detection_rank(os.path.join(ASSETS, "detection_rank.png"))
    fig_detection_rank_report(os.path.join(ASSETS, "detection_rank_report.png"))
    out["fig_t6_reversal.png"] = fig_t6(os.path.join(ASSETS, "fig_t6_reversal.png"))
    for k, v in out.items():
        print(k, v)
