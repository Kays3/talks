#!/usr/bin/env python3
"""Generate the IMRaD abstract for the lung T-cell oral presentation.

The word count is computed from the section text on every build. It was typed
by hand three times before this and was wrong each time (197, 300, 323).
"""
from __future__ import annotations

from pathlib import Path

# PACKAGED 2026-09-28: writes into the package's build/ directory.
OUT_PATH = Path(__file__).resolve().parent.parent / "build" / "lung_tcell_talk_imrad_abstract_20260925.md"

TITLE = (
    "A Foundation-Model T-cell Dysfunction Screen: Translational Candidates, Then a "
    "Full Audit"
)

AUTHORS = "Kaisar Dauyey, Shinji Nakaoka"

BACKGROUND = (
    "Foundation models fine-tuned on single-cell transcriptomes can be probed for "
    "candidate disease-state drivers by in-silico perturbation. A classifier trained "
    "on real tissue, however, also learns whatever else correlates with its labels "
    "(ambient RNA, detection artifacts, cohort composition), and a screen alone "
    "cannot say which of these it found."
)

METHODS = (
    "A donor-disjoint SCLC/LUAD/normal T-cell classifier (46,140 cells, 42 donors; "
    "91.9% accuracy, macro F1 0.903, a third of which comes from one held-out "
    "normal-class donor with 566 cells) supported an in-silico deletion and "
    "overexpression screen, scored by significance and by bidirectional concordance "
    "between the two operations. A screen-level ambient-risk audit and a "
    "donor-weighted reanalysis followed the screen."
)

RESULTS = (
    "Four checkpoint and persistence candidates from the original work (TIGIT, "
    "TIM-3, CTLA-4, IL7R) replicate by deletion (FDR<0.05, same deletion sign in all "
    "three SCLC donors) and validate in independent spatial tissue data "
    "(antigen-presentation programme, rho=0.361, 7.95 sigma above the null). The "
    "concordance half of their original call came from a panel runner that "
    "overexpressed into all 2,424 SCLC cells but deleted only in detected cells; it "
    "has not been rerun on paired cell sets. The original work left a "
    "checkpoint-axis ordering open. At donor level, SCLC and LUAD do not differ significantly on "
    "that axis (p=.216, two-sided Monte Carlo, 100,000 replicates, 19 v 22 donors) "
    "once one donor's 74.9% cell share is accounted for. In a later, expanded screen "
    "the two most significant hits by FDR (S100A8, S100A9; FDR~1e-224) fail "
    "bidirectional concordance in all six comparisons tested; screen-wide, half of "
    "the top 120 candidates by effect are ambient-flagged, a curated ambient anchor, "
    "or both. One candidate, NBEAL1, survives every check applied. Model precision "
    "(bf16 vs fp32) replicates cleanly (rho>0.998) and explains none of these "
    "results. The pre-registered 104M sign-agreement gate still reads FAIL, final, "
    "because a bitwise-deterministic fp32-vs-fp32 rerun set its noise floor to zero, "
    "which is not a usable sign threshold. That FAIL is a property of the floor, not "
    "evidence that bf16 disagrees with fp32, and the domain reviewer ruled to leave "
    "the frozen gate unamended."
)

DISCUSSION = (
    "A perturbation screen can support real translational candidates and still "
    "require gene-by-gene auditing for confounds. Significance and effect size alone "
    "are not sufficient evidence of a cell-intrinsic driver, and an ordering claim "
    "built on a cell-weighted cross-cohort comparison needs a donor-level check "
    "before it is reported either way."
)

SECTIONS = [
    ("Background", BACKGROUND),
    ("Methods", METHODS),
    ("Results", RESULTS),
    ("Discussion", DISCUSSION),
]


def word_count(text: str) -> int:
    """Whitespace-token count, the same as `wc -w` on the rendered prose."""
    return len(text.split())


def build() -> str:
    n_no_labels = word_count(" ".join(text for _, text in SECTIONS))
    n_with_labels = word_count(" ".join(f"{label}: {text}" for label, text in SECTIONS))
    lines = [f"# {TITLE}", "", AUTHORS, ""]
    for label, text in SECTIONS:
        lines.append(f"**{label}:** {text}")
        lines.append("")
    lines.append(f"({n_no_labels} words; {n_with_labels} counting the section labels.)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    content = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(content, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
