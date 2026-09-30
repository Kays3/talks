"""Figure generator for the lung T-cell oral presentation, 2026-09-24.

Every number plotted here is pulled at build time from the exact repo
commit it belongs to via `git show <ref>:<path>` -- nothing is typed from
memory or cached from a prior read. Run this before
make_lung_tcell_talk_slides_20260924.py; it writes PNGs the slide script
embeds.

Sources (all verified independently before this script was written; see
lung_tcell_talk_sources_20260924.md for the full citation table):
  - S100A8/S100A9 rows + top-120 screen breakdown:
    sclc_validation/primary_test_perturbation/tables/isp_plausibility_top_candidates.csv
    @ b99365b, plus ambient_risk_manifest.json @ b99365b
  - Donor robustness T6: sclc_validation/immune_axis_test/results/
    {t6_weighting_reconciliation,t6_donor_level_scores}.csv @ 9ec518c
  - bf16 canary: sclc_validation/bf16_bench/committed_run_stats/
    316m_canary_{fp32,bf16}/targeted_panel/stats/overexpress/*.csv @ origin/main
    (added by PR #22, content unchanged since; values cited at afa0564 in prose)
"""
from __future__ import annotations

import csv
import io
import json
import os
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = "<path to a geneformer-lung-tcell checkout>"
OUT_DIR = "<output directory>/lung_tcell_talk_assets_20260924"
os.makedirs(OUT_DIR, exist_ok=True)

INK = "#12211E"
ACC = "#0E6E5C"
WARM = "#B4552F"
MUT = "#5C6B66"
LINE = "#DCE3DF"
PAPER = "#F6F8F6"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": LINE,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUT,
    "ytick.color": MUT,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def git_show(ref: str, path: str) -> str:
    out = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True, check=True, text=True,
    )
    return out.stdout


def read_csv(ref: str, path: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(git_show(ref, path))))


# --------------------------------------------------------------------------
# Figure 1: S100A8/S100A9 concordance failure -- delete vs overexpress shift
# --------------------------------------------------------------------------

def fig_concordance():
    rows = read_csv("b99365b", "sclc_validation/primary_test_perturbation/tables/isp_plausibility_top_candidates.csv")
    s100 = [r for r in rows if r["Gene_name"] in ("S100A8", "S100A9")]
    assert len(s100) == 12, f"expected 12 S100A8/A9 rows, got {len(s100)}"

    fig, ax = plt.subplots(figsize=(7.2, 5.4), dpi=200)
    ax.axhline(0, color=LINE, lw=1, zorder=1)
    ax.axvline(0, color=LINE, lw=1, zorder=1)

    markers = {"S100A8": "o", "S100A9": "^"}
    colors = {"S100A8": WARM, "S100A9": ACC}
    n_same_sign = 0
    n_concordant = 0
    for r in s100:
        dx = float(r["delete_shift"])
        oy = float(r["overexpress_shift"])
        same_sign = (dx * oy) > 0
        n_same_sign += same_sign
        concordant = r["concordant"] == "True"
        n_concordant += concordant
        ax.scatter(
            dx, oy, s=95, marker=markers[r["Gene_name"]],
            facecolor=colors[r["Gene_name"]] if same_sign else "white",
            edgecolor=colors[r["Gene_name"]], linewidth=1.6, zorder=3,
        )

    lim = max(abs(float(r["delete_shift"])) for r in s100 + s100) * 1.25
    lim = max(lim, max(abs(float(r["overexpress_shift"])) for r in s100) * 1.25)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)

    # shade the two quadrants a genuine dose-responsive driver must land in
    ax.fill_between([-lim, 0], 0, lim, color=ACC, alpha=0.05, zorder=0)
    ax.fill_between([0, lim], -lim, 0, color=ACC, alpha=0.05, zorder=0)
    ax.text(-lim * 0.96, lim * 0.90, "concordant region\n(opposite sign)",
            fontsize=8.5, color=ACC, ha="left", va="top", style="italic")

    ax.set_xlabel("delete_shift  (deletion)")
    ax.set_ylabel("overexpress_shift  (overexpression)")
    ax.set_title(f"S100A8 / S100A9: {n_same_sign} of 12 rows same-sign, "
                 f"{n_concordant} of 12 concordant", fontsize=12, fontweight="bold", color=INK)

    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", color=WARM, linestyle="", markersize=9, label="S100A8"),
        Line2D([0], [0], marker="^", color=ACC, linestyle="", markersize=9, label="S100A9"),
        Line2D([0], [0], marker="o", color=INK, linestyle="", markersize=9,
               markerfacecolor="white", label="opposite sign (concordant candidate)"),
        Line2D([0], [0], marker="o", color=INK, linestyle="", markersize=9,
               markerfacecolor=INK, label="same sign (not concordant)"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=8, frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "fig_concordance.png")
    fig.savefig(path)
    plt.close(fig)
    return path, n_same_sign, n_concordant


# --------------------------------------------------------------------------
# Figure 2: screen-level ambient breakdown, top-120 by effect
# --------------------------------------------------------------------------

def fig_ambient_breakdown():
    rows = read_csv("b99365b", "sclc_validation/primary_test_perturbation/tables/isp_plausibility_top_candidates.csv")
    top = [r for r in rows if r["selected_by"] == "top_n_by_effect"]
    assert len(top) == 120, f"expected 120 top_n_by_effect rows, got {len(top)}"
    manifest = json.loads(git_show("b99365b", "sclc_validation/primary_test_perturbation/tables/ambient_risk_manifest.json"))
    n_tcell_anchors = len(manifest["anchors_tcell"])
    assert n_tcell_anchors == 36

    n_ambient_flag = sum(1 for r in top if r["ambient_flag"] == "True")
    n_ambient_anchor = sum(1 for r in top if r["is_ambient_anchor"] == "True")
    n_both = sum(1 for r in top if r["ambient_flag"] == "True" and r["is_ambient_anchor"] == "True")
    n_flag_only = n_ambient_flag - n_both
    n_anchor_only = n_ambient_anchor - n_both
    n_neither = 120 - n_flag_only - n_anchor_only - n_both
    assert n_neither + n_flag_only + n_anchor_only + n_both == 120
    n_tcell_anchor_present = sum(1 for r in top if r["is_tcell_anchor"] == "True")

    # Mutually-exclusive segments of the SAME 120 rows -- flagged and anchor overlap
    # (24 of 29 anchor rows are also flagged; 5 are not), so this is a real partition,
    # not the additive stack the first draft of this figure used (which summed to >120).
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=200)
    cats = ["Top-120 rows\nby effect size", f"36 curated\nT-cell anchors"]
    neither = [n_neither, 0]
    flag_only = [n_flag_only, 0]
    anchor_only = [n_anchor_only, 0]
    both = [n_both, 0]
    tcell_present = [0, n_tcell_anchor_present]
    tcell_absent = [0, n_tcell_anchors - n_tcell_anchor_present]

    x = np.arange(2)
    width = 0.55
    ax.bar(x, neither, width, label="neither flagged nor anchor", color=LINE, zorder=3)
    ax.bar(x, flag_only, width, bottom=neither, label=f"ambient-flagged only ({n_flag_only}/120)", color=WARM, zorder=3)
    ax.bar(x, anchor_only, width, bottom=[n + f for n, f in zip(neither, flag_only)],
           label=f"ambient anchor only, below flag threshold ({n_anchor_only}/120)", color="#C9A227", zorder=3)
    ax.bar(x, both, width, bottom=[n + f + a for n, f, a in zip(neither, flag_only, anchor_only)],
           label=f"both flagged and anchor ({n_both}/120)", color="#7A2E12", zorder=4)
    ax.bar(x, tcell_present, width, bottom=0, label=f"T-cell anchors present ({n_tcell_anchor_present}/36)", color=ACC, zorder=3)
    ax.bar(x, tcell_absent, width, bottom=tcell_present, label=f"T-cell anchors absent ({n_tcell_anchors - n_tcell_anchor_present}/36)",
           color="#CFE3DE", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=10)
    ax.set_ylabel("gene-comparison rows (left) / curated genes (right) -- different denominators")
    ax.set_title(f"{n_flag_only + n_anchor_only + n_both}/120 rows are ambient-flagged or a curated anchor",
                 fontsize=12, fontweight="bold", color=INK)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), fontsize=8, frameon=False, ncol=1)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "fig_ambient_breakdown.png")
    fig.savefig(path)
    plt.close(fig)
    return path, n_ambient_flag, n_ambient_anchor, n_tcell_anchor_present, n_tcell_anchors


# --------------------------------------------------------------------------
# Figure 3: donor-level vs cell-weighted reversal (T6)
# --------------------------------------------------------------------------

def fig_t6_reversal():
    recon = read_csv("9ec518c", "sclc_validation/immune_axis_test/results/t6_weighting_reconciliation.csv")
    donor_scores = read_csv("9ec518c", "sclc_validation/immune_axis_test/results/t6_donor_level_scores.csv")

    def get(pop, state):
        return next(r for r in recon if r["population"] == pop and r["state"] == state)

    complete_sclc = get("complete", "sclc")
    complete_luad = get("complete", "luad")
    test_sclc = get("test_only", "sclc")
    test_luad = get("test_only", "luad")

    pe = next(r for r in donor_scores if r["donor"] == "PleuralEffusion" and r["population"] == "test_only")
    pe_share = float(test_sclc["max_donor_cell_share"])
    assert abs(pe_share - 0.74917) < 1e-3, pe_share

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.6), dpi=200, sharey=True)

    # panel 1: donor-level means, both populations -- no reversal
    ax = axes[0]
    labels = ["complete", "test-only"]
    sclc_vals = [float(complete_sclc["donor_level_mean"]), float(test_sclc["donor_level_mean"])]
    luad_vals = [float(complete_luad["donor_level_mean"]), float(test_luad["donor_level_mean"])]
    x = np.arange(2)
    w = 0.32
    ax.bar(x - w / 2, sclc_vals, w, label="SCLC (donor-level mean)", color=WARM)
    ax.bar(x + w / 2, luad_vals, w, label="LUAD (donor-level mean)", color=ACC)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Donor-level: SCLC > LUAD, both populations", fontsize=10.5, fontweight="bold")
    ax.set_ylabel("mean donor score")
    ax.legend(fontsize=8, frameon=False, loc="upper right")

    # panel 2: cell-weighted means, test-only -- reversal, PleuralEffusion called out
    ax2 = axes[1]
    cw_sclc = float(test_sclc["cell_weighted_mean"])
    cw_luad = float(test_luad["cell_weighted_mean"])
    ax2.bar(["SCLC\n(cell-weighted)", "LUAD\n(cell-weighted)"], [cw_sclc, cw_luad], color=[WARM, ACC], width=0.5)
    ax2.set_title("Test-only, cell-weighted: reverses", fontsize=10.5, fontweight="bold")
    ax2.annotate(
        f"PleuralEffusion (HTA8_2001)\ncarries {pe_share*100:.1f}% of SCLC\ntest-only cells, score {float(pe['score']):.3f}",
        xy=(0, cw_sclc), xytext=(0.15, cw_sclc + 0.05),
        fontsize=8, color=INK,
        arrowprops=dict(arrowstyle="->", color=MUT, lw=1),
    )
    for a in axes:
        for spine in ("top", "right"):
            a.spines[spine].set_visible(False)
    fig.suptitle("The SCLC-vs-LUAD ordering \"disagreement\" is a weighting artifact",
                 fontsize=12, fontweight="bold", color=INK, y=1.03)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "fig_t6_reversal.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path, pe_share, float(pe["score"])


# --------------------------------------------------------------------------
# Figure 4: bf16 canary, fp32 vs bf16 scatter, 316M model, overexpress arm
# --------------------------------------------------------------------------

def fig_bf16_canary():
    comparisons = ["sclc_to_luad", "luad_to_sclc", "sclc_to_normal", "normal_to_sclc", "luad_to_normal", "normal_to_luad"]
    fp32_vals, bf16_vals = [], []
    for comp in comparisons:
        fp32_rows = read_csv(
            "origin/main",
            f"sclc_validation/bf16_bench/committed_run_stats/316m_canary_fp32/targeted_panel/stats/overexpress/targeted_overexpress_{comp}.csv",
        )
        bf16_rows = read_csv(
            "origin/main",
            f"sclc_validation/bf16_bench/committed_run_stats/316m_canary_bf16/targeted_panel/stats/overexpress/targeted_overexpress_{comp}.csv",
        )
        bf16_by_gene = {r["Gene_name"]: float(r["Shift_to_goal_end"]) for r in bf16_rows}
        for r in fp32_rows:
            g = r["Gene_name"]
            if g in bf16_by_gene:
                fp32_vals.append(float(r["Shift_to_goal_end"]))
                bf16_vals.append(bf16_by_gene[g])

    fp32_vals = np.array(fp32_vals)
    bf16_vals = np.array(bf16_vals)
    from scipy.stats import spearmanr
    rho, _ = spearmanr(fp32_vals, bf16_vals)
    max_abs_diff = float(np.max(np.abs(fp32_vals - bf16_vals)))
    sign_agree = int(np.sum(np.sign(fp32_vals) == np.sign(bf16_vals)))

    fig, ax = plt.subplots(figsize=(6.0, 5.4), dpi=200)
    lim = max(np.abs(fp32_vals).max(), np.abs(bf16_vals).max()) * 1.15
    ax.plot([-lim, lim], [-lim, lim], color=LINE, lw=1, zorder=1)
    ax.axhline(0, color=LINE, lw=0.8, zorder=1)
    ax.axvline(0, color=LINE, lw=0.8, zorder=1)
    ax.scatter(fp32_vals, bf16_vals, s=40, color=ACC, alpha=0.75, edgecolor="white", linewidth=0.4, zorder=3)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("fp32, Shift_to_goal_end")
    ax.set_ylabel("bf16, Shift_to_goal_end")
    ax.set_title(f"316M canary, overexpress arm: rho={rho:.4f}, sign agree {sign_agree}/{len(fp32_vals)}",
                 fontsize=11, fontweight="bold", color=INK)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "fig_bf16_canary.png")
    fig.savefig(path)
    plt.close(fig)
    return path, float(rho), sign_agree, len(fp32_vals), max_abs_diff


if __name__ == "__main__":
    p1, same_sign, concordant = fig_concordance()
    print("fig 1 (concordance):", p1, "same_sign=", same_sign, "concordant=", concordant)
    p2, af, aa, tp, tt = fig_ambient_breakdown()
    print("fig 2 (ambient breakdown):", p2, af, aa, tp, tt)
    p3, share, pe_score = fig_t6_reversal()
    print("fig 3 (T6 reversal):", p3, "PleuralEffusion share=", share, "score=", pe_score)
    p4, rho, sign_agree, n, maxdiff = fig_bf16_canary()
    print("fig 4 (bf16 canary):", p4, "rho=", rho, f"sign_agree={sign_agree}/{n}", "max_abs_diff=", maxdiff)
