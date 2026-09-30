"""Material ADDED on 2026-09-28 for a geneticist audience (human's request via
the project lead): research background, our earlier 24JSDP poster (P25) and what changed,
plain-language methods, one "in plain words" line per headline number, a
glossary, the S100 ISP result (new since 25 Sep), and an appendix.

The 18 original slides are untouched; this module only adds. Each added
factual statement carries its source (file + commit, or a verified paper)
in `notes` / `refs`; both generators (make_pptx.py, make_docx.py) read from
here so the deck and the report cannot drift apart. S100 numbers are loaded
from data/ at build time and asserted, never typed.

Markup in strings: **bold** only.
"""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
S100_DIR = os.path.join(DATA, "git", "53adee2", "sclc_validation", "perturbation_workflow", "s100_isp")
S100_RESULT_MD = os.path.join(S100_DIR, "results_s100_luad_20260928", "RESULT.md")
S100_JSON = os.path.join(S100_DIR, "results_s100_luad_20260928", "primary_results.json")
S100_DRIVER = os.path.join(S100_DIR, "analyse_s100_luad_20260928.py")

# ---------------------------------------------------------------------------
# Verified literature (each DOI resolved on Crossref, 2026-09-28).
# ---------------------------------------------------------------------------
LIT = {
    "theodoris2023": "Theodoris CV, Xiao L, Chopra A, et al. Transfer learning enables predictions in network "
                     "biology. Nature 2023. doi:10.1038/s41586-023-06139-9",
    "horn2018": "Horn L, Mansfield AS, Szczęsna A, et al. First-line atezolizumab plus chemotherapy in "
                "extensive-stage small-cell lung cancer. N Engl J Med 2018. doi:10.1056/NEJMoa1809064",
    "wherry2015": "Wherry EJ, Kurachi M. Molecular and cellular insights into T cell exhaustion. Nat Rev "
                  "Immunol 2015. doi:10.1038/nri3862",
    "rudin2019": "Rudin CM, Poirier JT, Byers LA, et al. Molecular subtypes of small cell lung cancer: a synthesis "
                 "of human and mouse model data. Nat Rev Cancer 2019. doi:10.1038/s41568-019-0133-9",
    "gay2021": "Gay CM, Stewart CA, Park EM, et al. Patterns of transcription factor programs and immune pathway "
               "activation define four major subtypes of SCLC with distinct therapeutic vulnerabilities. Cancer "
               "Cell 2021. doi:10.1016/j.ccell.2020.12.014",
    "young2020": "Young MD, Behjati S. SoupX removes ambient RNA contamination from droplet-based single-cell RNA "
                 "sequencing data. GigaScience 2020. doi:10.1093/gigascience/giaa151",
    "bh1995": "Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach "
              "to multiple testing. J R Stat Soc B 1995. doi:10.1111/j.2517-6161.1995.tb02031.x",
    "string2023": "Szklarczyk D, Kirsch R, Koutrouli M, et al. The STRING database in 2023: protein-protein "
                  "association networks and functional enrichment analyses for any sequenced genome of interest. "
                  "Nucleic Acids Res 2023. doi:10.1093/nar/gkac1000",
    "mw1947": "Mann HB, Whitney DR. On a test of whether one of two random variables is stochastically larger "
              "than the other. Ann Math Stat 1947. doi:10.1214/aoms/1177730491",
}

# Package-internal sources, cited by key.
SRC = {
    "poster": "data/sources/poster_final.pdf (our 24JSDP poster, P25; geneformer-lung-tcell "
              "poster/poster_final.pdf, untracked; sha256 94638dba...)",
    "jsdp_talk": "data/sources/JSDP_P25_talk.pdf (the talk that accompanied the poster; geneformer-lung-tcell "
                 "talk/JSDP_P25_talk.pdf, untracked; sha256 3f013a5d...)",
    "methods": "data/git/dd7366c/sclc_validation/perturbation_workflow/METHODS.md (geneformer-lung-tcell @ dd7366c)",
    "s100_result": "data/git/53adee2/.../results_s100_luad_20260928/RESULT.md (geneformer-lung-tcell @ 53adee2; "
                   "merged to main in PR #37, 4455914)",
    "s100_json": "data/git/53adee2/.../results_s100_luad_20260928/primary_results.json (@ 53adee2)",
    "s100_driver": "data/git/53adee2/.../s100_isp/analyse_s100_luad_20260928.py (@ 53adee2): gene groups, "
                   "Ensembl IDs, ambient-risk values",
    "isp_std": "the lab's ISP outcome standard (ISP-STD-1 v1.1, the floor's wording rules; not in this package)",
}


# ---------------------------------------------------------------------------
# S100 numbers, read from the committed result files.
# ---------------------------------------------------------------------------
def s100() -> dict:
    res = json.load(open(S100_JSON))
    drv = open(S100_DRIVER).read()
    groups = {}
    for name in ("HIGH", "LOW"):
        m = re.search(rf"^{name} = (\{{.*?\}})$", drv, re.M)
        groups[name] = eval(m.group(1), {})  # a literal dict of symbol -> Ensembl ID
    risk = eval(re.search(r"^RISK = (\{.*?\})$", drv, re.M | re.S).group(1), {})
    out = {"high": groups["HIGH"], "low": groups["LOW"], "risk": risk, "contrasts": {}}
    for c, v in res.items():
        t = v["primary_test"]
        out["contrasts"][c] = {"status": v["status"], "U": t["statistic"], "p": t["p_exact"],
                               "p70": round(t["p_exact"] * 70), "direction": t["direction"],
                               "Q": v["Q"], "loo": v["loo_n_positive"], "n_loo": v["stability_gate"]["n_loo"],
                               "gate": v["stability_gate"]["outcome"], "controls": v["n_valid_controls"]}
    n, s = out["contrasts"]["luad_to_normal"], out["contrasts"]["luad_to_sclc"]
    assert (n["status"], n["U"], n["p70"]) == ("negative", 1.5, 6), n
    assert (s["status"], s["U"], s["p70"]) == ("negative", 5.5, 34), s
    assert n["gate"] == s["gate"] == "not_positive" and n["loo"] == s["loo"] == 0 and n["n_loo"] == 160
    assert all(v == 20 for c in out["contrasts"].values() for v in c["controls"].values())
    md = open(S100_RESULT_MD).read()
    for needle in ("No-op: PASS", "S100P (40 cells)", "S100A16 (48 cells)", "S100A8 and S100A9 are anchors",
                   "only complete\nseparation (p = 2/70) can pass"):
        assert needle in md, needle
    return out


S = s100()
N_, S_ = S["contrasts"]["luad_to_normal"], S["contrasts"]["luad_to_sclc"]

# ---------------------------------------------------------------------------
# "In plain words" lines for headline numbers on the ORIGINAL slides
# (keyed by original slide number). Each restates a number already on the slide.
# ---------------------------------------------------------------------------
PLAIN = {
    16: "In plain words: the links between these genes come from STRING, a public database of known and "
        "predicted protein interactions (Szklarczyk 2023), i.e. from prior literature, not from these cells.",
    5: "In plain words: shown T cells from 8 people it had never seen, the model named the right disease state "
       "for about 92 of every 100 cells; the normal-tissue part of that score rests on one person.",
    7: "In plain words: a gene counts only if removing it and boosting it push the cell in opposite directions, "
       "each beyond chance; FDR < 0.05 means at most about 5% of such calls are expected to be false.",
    9: "In plain words: in real tumour slices, spots with more antigen-presentation activity also held more "
       "T cells (rho 0.361, where 0 is no relation and 1 is perfect), far beyond chance (7.95 sigma).",
    10: "In plain words: the rarer a gene is in the data, the bigger its apparent effect tends to be (rho -0.60), "
        "so the size of an effect alone is not evidence.",
    11: "In plain words: counting each person once instead of each cell, SCLC and LUAD T cells do not differ "
        "significantly on this axis (p = 0.216); one donor had supplied most of the test-only SCLC cells.",
    12: "In plain words: an FDR of 1.45e-224 says the shift is almost certainly not chance, not that it is large "
        "or meaningful; S100A8/S100A9 still fail the both-directions test in all 6 comparisons.",
    13: "In plain words: half of the 120 strongest hits carry a flag for possible contamination by RNA from other "
        "cells, or are known contaminant marker genes, so they need caution before being called T-cell biology.",
    14: "In plain words: NBEAL1 passed the both-directions test in all 5 comparisons it appears in and is seen in "
        "3 of every 4 cells, so it is not a rare-gene artefact; it is a candidate, not a proven driver.",
    15: "In plain words: rerunning the model at lower numerical precision gave essentially the same answers "
        "(rho 0.9998), so rounding does not explain any result in this talk.",
}

# ---------------------------------------------------------------------------
# Added slides.
# ---------------------------------------------------------------------------
NEW = {}

NEW["background"] = {
    "eyebrow": "Research background · for geneticists",
    "title": "T cells in lung cancer: why they matter, and what was already known",
    "cards": [
        ("The disease",
         ["Lung cancer comes in distinct types. **Small cell lung cancer (SCLC)** is the most aggressive thoracic "
          "malignancy; **lung adenocarcinoma (LUAD)** is a non-small-cell type.",
          "SCLC itself splits into subtypes defined by master transcription factors (ASCL1, NEUROD1, POU2F3) "
          "(Rudin 2019)."]),
        ("The immune angle",
         ["**T cells** can kill tumour cells. Under chronic stimulation they can become dysfunctional "
          "(\"exhausted\"), marked by inhibitory receptors such as PD-1, TIM-3 and CTLA-4 (Wherry 2015).",
          "Immune checkpoint inhibitors release these brakes, but add only a modest survival benefit in "
          "extensive-stage SCLC (Horn 2018), despite its high tumour mutational burden."]),
        ("The open question",
         ["Whether SCLC T cells are dysfunctional, and through which genes, was poorly characterised at "
          "single-cell resolution when this work began.",
          "SCLC subtypes differ in immune activation; an inflamed subtype benefits most from immunotherapy "
          "(Gay 2021). This talk asks what a model trained on T cells themselves can say."]),
    ],
    "plain": "In plain words: we study the immune cells inside lung tumours, because drugs that re-activate them "
             "help SCLC patients less than hoped, and nobody knows exactly why.",
    "footer": "Rudin 2019; Wherry 2015; Horn 2018; Gay 2021; poster_final (Why this matters)",
    "notes": ["SCLC 'most aggressive thoracic malignancy', 'responds poorly to immune checkpoint blockade despite a "
              "high tumour mutational burden', 'transcriptional basis poorly characterised at single-cell resolution': "
              "JSDP poster, section A 'Why this matters' - " + SRC["poster"],
              "SCLC transcription-factor subtypes: " + LIT["rudin2019"],
              "T-cell exhaustion and inhibitory receptors: " + LIT["wherry2015"],
              "Modest benefit of adding atezolizumab to chemotherapy in extensive-stage SCLC: " + LIT["horn2018"],
              "Inflamed SCLC subtype and immunotherapy benefit: " + LIT["gay2021"]],
}

NEW["methods_plain"] = {
    "eyebrow": "Methods in plain words · read this first",
    "title": "Three tools, one analogy each",
    "cards": [
        ("Single-cell RNA sequencing",
         ["Reads which genes are switched on in **each individual cell**, not in a ground-up tissue sample.",
          "Analogy: a list of every fruit in the bowl, instead of the smoothie.",
          "Here: 46,140 T cells from 42 people (HTAN MSK collection, CELLxGENE)."]),
        ("Geneformer, a foundation model",
         ["A neural network pre-trained on a large corpus of single-cell profiles (Theodoris 2023). It reads a "
          "cell as its genes **ranked by expression**, most-expressed first, and turns it into a list of numbers "
          "(an **embedding**) that puts similar cells near each other.",
          "Analogy: a map coordinate for every cell. We fine-tuned it to tell SCLC, LUAD and normal-tissue "
          "T cells apart."]),
        ("In silico perturbation",
         ["Delete one gene from a cell's ranked list, or move it to the top (\"overexpress\"), re-read the cell, "
          "and measure how far the model's picture of it moves toward another disease state.",
          "Analogy: a Perturb-seq screen run on the computer. **Nothing is edited in a lab**: it generates "
          "hypotheses, it is not a knockout."]),
    ],
    "plain": "In plain words: we taught a model what SCLC, LUAD and normal T cells look like, then asked it "
             "\"what if this gene were missing, or boosted?\" for thousands of real cells.",
    "footer": "METHODS.md @ dd7366c; Theodoris 2023; poster_final Fig. 1, Fig. 5",
    "notes": ["46,140 cells, 42 individuals, HTAN MSK / CELLxGENE dataset 6fde3ad9: " + SRC["methods"] +
              " (lines 5-10) and the poster's cohort panel.",
              "Geneformer: " + LIT["theodoris2023"],
              "'Reads a cell as an ordered list of its genes, most-expressed first'; 'nothing is edited in a "
              "laboratory'; 'a hypothesis generator, not a knockout experiment'; 'a Perturb-seq screen run in "
              "silico': JSDP poster Fig. 1 and Fig. 5 captions - " + SRC["poster"],
              "Delete = token removed from the rank-value encoding; overexpress = moved to the front: " +
              SRC["methods"] + " (lines 180-187)."],
}

NEW["poster"] = {
    "eyebrow": "Where this started · our earlier poster",
    "title": "Our 24JSDP poster (P25) and what the audit changed",
    "intro": ["**Our 24JSDP poster (P25)** reported a donor-held-out classifier (91.9% accuracy), four replicated edits "
              "(TIM-3, TIGIT, CTLA-4, IL7R) and tissue validation in 5 Visium SCLC sections (15,632 spots)."],
    "table": {
        "header": ["Poster statement", "Status after the audit (this talk)"],
        "rows": [
            ["Four edits concordant, FDR < 0.05 in both arms, same sign in all 3 SCLC donors",
             "Deletion replication stands. The concordance half was scored on different cell sets per arm "
             "(overexpress 2,424 cells, delete 202-1,131) and has not been rerun."],
            ["\"The model implies Normal < SCLC < LUAD on the checkpoint axis ... an open question\"",
             "Closed as null: donor-level SCLC vs LUAD, p = 0.216."],
            ["Detection vs effect size, rho = -0.60: sparse genes fake big effects",
             "Unchanged; the original talk's own QC slide, shown here as Results R2."],
            ["Tissue: dysfunction tracks T-cell abundance (rho 0.161); talk: antigen presentation rho 0.361",
             "Unchanged; not re-analysed here."],
        ],
        "widths_mm": [128, 170],
    },
    "plain": "In plain words: the poster's main hits survive; one of its claims (an ordering of the three "
             "disease states) did not hold up once each person was counted once.",
    "footer": "poster_final; JSDP_P25_talk; this deck, slides R1 and R3",
    "notes": ["Poster title, number, authors, sections and all poster quotes: " + SRC["poster"],
              "rho 0.361 / 7.95 sigma: " + SRC["jsdp_talk"] + " (slide 9).",
              "Status column restates this deck's own slides: Results R1 (cell-set caveat; "
              "targeted_panel_delete_overexpress_merged.csv @ 6882627, runner fix 66d235b) and R3 "
              "(t6_permutation_tests.csv @ 9ec518c).",
              "Held-out cell count: poster 9,377 vs confusion matrix 9,376 is a known one-cell truncation with "
              "no effect at any reported precision (METHODS.md lines 125-166) - not an audit change.",
              "Per the human's ruling (2026-09-28), the poster is named only as 'our 24JSDP poster (P25)': no "
              "venue, date or meeting details."],
}

NEW["s100"] = {
    "eyebrow": "Results · new since 25 Sep · pre-registered, run 2026-09-28",
    "title": "S100 genes did not beat their matched control genes",
    "cards": [
        ("Question and design",
         ["Do simulated deletion and overexpression of S100 genes push LUAD T cells toward normal or SCLC "
          "**more than matched control genes** do, and more so for the 4 S100 genes at high ambient-RNA risk "
          "(S100A2, S100B, S100A13, S100PBP) than for 4 at low risk (S100A4, S100A6, S100A10, S100A11)?",
          "Each gene vs its own 20 detection-matched controls; the two groups of 4 compared with an exact "
          "Mann-Whitney test; all registered in advance."]),
        ("Result: negative in both comparisons",
         [f"LUAD → normal: U = {N_['U']}, p = {N_['p70']}/70 ({N_['p']:.3f}).",
          f"LUAD → SCLC: U = {S_['U']}, p = {S_['p70']}/70 ({S_['p']:.2f}).",
          f"Stability gate not positive ({N_['loo']}/{N_['n_loo']} leave-one-control-out). No-op check passed. "
          "S100P and S100A16 not estimable (40 and 48 cells, below the 50-cell gate). S100A8/S100A9 excluded "
          "by design (classifier anchors)."]),
        ("How to read it",
         ["**The test was small**: with 4 v 4 the smallest possible p is 2/70 (0.029), reached only by "
          "complete separation.",
          "The ambient-high genes did not beat matched controls more than the ambient-low genes. No claim is "
          "made from the ambient-low genes' high scores.",
          "This **neither confirms nor contradicts** the S100A8/S100A9 slides."]),
    ],
    "plain": "In plain words: in a small, pre-registered test, S100 genes flagged for possible contamination "
             "did not stand out against look-alike control genes.",
    "footer": "RESULT.md, primary_results.json @ 53adee2 (main via PR #37, 4455914)",
    "notes": ["NEW since the 25 Sep deck; pre-registered; run 2026-09-28.",
              "Status, U, p, stability gate, no-op PASS, S100P/S100A16 not_estimable, anchors S100A8/A9: " +
              SRC["s100_result"] + "; numbers read at build time from " + SRC["s100_json"],
              "Gene groups and ambient risk: " + SRC["s100_driver"],
              "Wording rules (never 'no effect'; state the 2/70 floor; no claim from clean genes' high Q): " +
              SRC["isp_std"],
              "Mann-Whitney test: " + LIT["mw1947"]],
}

NEW["glossary"] = {
    "eyebrow": "Glossary",
    "title": "Terms used in this talk",
    "table": {
        "header": ["Term", "Meaning here"],
        "rows": [
            ["Single-cell RNA-seq", "Measures which genes are active in each individual cell."],
            ["T-cell dysfunction / exhaustion", "A worn-out T-cell state after chronic stimulation, with "
                                                "inhibitory receptors (PD-1, TIM-3, CTLA-4) (Wherry 2015)."],
            ["Immune checkpoint", "An inhibitory receptor that brakes T cells; checkpoint-inhibitor drugs block it."],
            ["Foundation model (Geneformer)", "A model pre-trained on many cells, then fine-tuned for one task "
                                              "(Theodoris 2023)."],
            ["Embedding", "The list of numbers the model uses to place a cell; similar cells sit close together."],
            ["In silico perturbation", "Deleting or boosting a gene in the model's input and measuring the shift."],
            ["Concordant", "Deletion and overexpression move the cell in opposite directions, both significant."],
            ["FDR", "False discovery rate: the expected share of false calls among all calls (Benjamini 1995)."],
            ["Donor-level analysis", "Each person counted once, so one person's many cells cannot dominate."],
            ["Ambient RNA", "Free-floating RNA from other cells that contaminates a cell's reads (Young 2020)."],
            ["Matched controls", "Non-S100 genes chosen to be detected about as often as the gene tested."],
            ["Mann-Whitney U", "A rank test of whether one group tends to score higher than another (Mann 1947)."],
            ["Pre-registration", "Fixing the test and its pass/fail rule in writing before seeing the result."],
            ["bf16", "A lower-precision number format; used to check that rounding does not drive results."],
        ],
        "widths_mm": [70, 228],
    },
    "footer": "definitions: this talk; Wherry 2015; Theodoris 2023; Benjamini 1995; Young 2020; Mann 1947",
    "notes": ["Glossary definitions are this talk's working definitions. Literature: " + "; ".join(
        LIT[k] for k in ("wherry2015", "theodoris2023", "bh1995", "young2020", "mw1947"))],
}

NEW["appendix"] = {
    "eyebrow": "Appendix",
    "title": "Backup slides",
    "intro": ["Deep-dive technical slides, kept for questions:",
              "A1 · Precision control: is any of this a bf16 artefact? (was slide 15 of the 25 Sep deck)",
              "A2 · Mechanism: the four hits in one interaction neighbourhood (was slide 16; the designated cut "
              "for a shorter slot)",
              "A3 · S100 ISP per-gene scores (new, 2026-09-28)",
              "A4 · All 31 immune / lineage genes ranked by deletion shift (panel b of the detection figure, "
              "moved here so it can be read at 14 pt)"],
    "footer": "",
    "notes": ["Appendix divider. Slides moved here, not deleted, per the 2026-09-28 request to keep the main talk "
              "length sane."],
}


def s100_table():
    rows = []
    for grp, genes in (("ambient-high", S["high"]), ("ambient-low", S["low"])):
        for g, eid in genes.items():
            rows.append([g, eid, grp, f"{S['risk'][g]:.3g}", f"{N_['Q'][g]:.1f}", f"{S_['Q'][g]:.1f}"])
    return rows


NEW["s100_table"] = {
    "eyebrow": "Appendix · S100 ISP per-gene scores (new, 2026-09-28)",
    "title": "Each S100 gene's percentile against its own 20 matched controls (Q)",
    "table": {
        "header": ["Gene", "Ensembl ID", "Group", "Ambient risk", "Q, LUAD→normal", "Q, LUAD→SCLC"],
        "rows": s100_table(),
        "widths_mm": [34, 62, 46, 42, 57, 57],
    },
    "intro_after": [f"Group test (exact two-sided Mann-Whitney, 4 v 4): LUAD→normal U = {N_['U']}, p = "
                    f"{N_['p70']}/70; LUAD→SCLC U = {S_['U']}, p = {S_['p70']}/70. Negative in both. The "
                    "ordering seen (ambient-low above) is descriptive only; the ambient-low genes' high Q was "
                    "not tested and supports no claim."],
    "footer": "primary_results.json, analyse_s100_luad_20260928.py @ 53adee2",
    "notes": ["Q values and group test read at build time from " + SRC["s100_json"],
              "Ensembl IDs, groups and ambient-risk values: " + SRC["s100_driver"],
              "Q is the gene's midrank percentile among its 20 matched controls; 8 of 8 genes have 20 valid "
              "controls in both contrasts."],
}

NEW["detection_rank"] = {
    "eyebrow": "Appendix · detection figure, panel b",
    "title": "Every immune / lineage gene, ranked by its deletion effect",
    "image": os.path.join(DATA, "assets", "detection_rank.png"),
    "plain": "In plain words: the four replicated hits sit near the top among well-detected genes; the very top "
             "is taken by genes seen in fewer than 100 cells, whose effects are unreliable.",
    "footer": "cart_overexpression_vs_deletion.csv @ eb533f8 (make_detection_figure.py rule)",
    "notes": ["Panel b of the original detection figure (poster Fig. 6 / JSDP talk slide 7), redrawn 2026-09-28 by "
              "src/make_readable_figures.py so its 31 gene names read at 14 pt; the slide-size slot of the Results "
              "slide cannot hold them. Same genes, values, ranks (TIM-3 4th, TIGIT 5th of 20 detected in >= 100 "
              "cells) and colour rules as data/git/eb533f8/.../scripts/make_detection_figure.py.",
              "Data: data/git/eb533f8/sclc_validation/checkpoint_cart_perturbation/tables/"
              "cart_overexpression_vs_deletion.csv and cart_engineering_perturbation.csv (last changed 37a0211)."],
}

# ---------------------------------------------------------------------------
# Running order. ("orig", n) = slide n of the 25 Sep deck, unchanged apart from
# its page number and an added "in plain words" line.
# ---------------------------------------------------------------------------
ORDER = [
    ("orig", 1), ("new", "background"), ("new", "methods_plain"), ("new", "poster"),
    ("orig", 2), ("orig", 3), ("orig", 4), ("orig", 5), ("orig", 6), ("orig", 7), ("orig", 8),
    ("orig", 9), ("orig", 10), ("orig", 11), ("orig", 12), ("orig", 13), ("orig", 14), ("new", "s100"),
    ("orig", 17), ("orig", 18), ("new", "glossary"),
    ("new", "appendix"), ("orig", 15), ("orig", 16), ("new", "s100_table"), ("new", "detection_rank"),
]
APPENDIX_START = ORDER.index(("new", "appendix")) + 1   # 1-based slide number of the divider

REFERENCES = [LIT[k] for k in ("theodoris2023", "horn2018", "wherry2015", "rudin2019", "gay2021", "young2020",
                               "bh1995", "mw1947", "string2023")]
TODO_CITES: list[str] = []   # every added literature claim above has a verified citation


# ---- Talk timing (human, 2026-09-29 20:45 JST: "within 30 minutes, time slot is not important") ----
# Assumption: 30 min = ~25 min speaking + ~5 min questions. Budget per main-talk slide (position in
# ORDER -> seconds), set by content: title/glossary brief, figure and dense-table slides longer.
# The glossary (21) is a reference slide, only pointed at. Appendix slides (22-26) are untimed.
SLOT_MIN = 30
QUESTIONS_MIN = 5
TIMING = {
    1: 30, 2: 90, 3: 90, 4: 75, 5: 60, 6: 60, 7: 60, 8: 75, 9: 60, 10: 75, 11: 60,
    12: 90, 13: 90, 14: 60, 15: 75, 16: 75, 17: 60, 18: 90, 19: 60, 20: 75, 21: 15,
}
assert sorted(TIMING) == list(range(1, APPENDIX_START)), "every main-talk slide needs a budget"
assert sum(TIMING.values()) <= (SLOT_MIN - QUESTIONS_MIN) * 60, "main talk over the speaking budget"


def mmss(seconds):
    return f"{seconds // 60}:{seconds % 60:02d}"
