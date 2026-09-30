"""Figure staging for the IMRaD-restructured oral-presentation deck, 2026-09-25.

Two kinds of figure in this deck:

1. Four figures already built and independently verified (twice) for the
   2026-09-24 deck (fig_concordance, fig_ambient_breakdown, fig_t6_reversal,
   fig_bf16_canary). They are reused UNMODIFIED here -- referenced directly
   from lung_tcell_talk_assets_20260924/ by the slide generator, not copied
   or regenerated. Their own generator (lung_tcell_talk_figures_20260924.py)
   remains the source of truth for how they were built.

2. Six original JSDP figures (confusion, screen_b, detection, spatial,
   network_c, qr) restored as Results/Introduction figures now that the
   original results are back in as results. talk/assets/*.png is NOT
   tracked in git (talk/ is gitignored, same as talk/JSDP_P25_talk.pptx/pdf
   and poster/poster_final.*) -- these are local filesystem artifacts, not
   git-citable objects, so they are staged here by a verified filesystem
   copy (size-checked), the same treatment the sources note already gives
   JSDP_P25_talk and poster_final themselves.
"""
from __future__ import annotations

import hashlib
import os
import shutil

# PACKAGED 2026-09-28: the staging copy was already made (2026-09-25) and the
# files now live in data/assets/. This script no longer copies anything; it
# re-checks the recorded byte sizes and data/MANIFEST.tsv sha256 of every
# data file, so a build cannot silently run on a changed input.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ASSETS = os.path.join(ROOT, "data", "assets")

JSDP_ASSETS = {
    "confusion.png": 87715,
    "screen_b.png": 80663,
    "detection_orig.png": 308598,
    "spatial.png": 2520539,
    "network_c.png": 163632,
    "qr.png": 1240,  # regenerated 2026-09-30: points at github.com/Kays3/talks
}

REUSED_20260924 = REPO_ASSETS
REUSED_FIGS = ["fig_concordance.png", "fig_ambient_breakdown.png", "fig_t6_reversal_orig.png", "fig_bf16_canary.png"]


def stage_jsdp_assets() -> dict[str, str]:
    hashes = {}
    for name, expected_size in JSDP_ASSETS.items():
        src = os.path.join(REPO_ASSETS, name)
        actual_size = os.path.getsize(src)
        assert actual_size == expected_size, (
            f"{name}: expected {expected_size} bytes (recorded 2026-09-24), got {actual_size} -- "
            "the JSDP asset changed since it was last measured; do not silently reuse a different file."
        )
        hashes[name] = hashlib.sha256(open(src, "rb").read()).hexdigest()[:16]
    return hashes


def verify_reused_figures_present() -> None:
    for name in REUSED_FIGS:
        path = os.path.join(REUSED_20260924, name)
        assert os.path.exists(path), f"{name} missing from the 2026-09-24 assets dir -- was it moved or deleted?"


def verify_manifest() -> int:
    import csv
    data = os.path.join(ROOT, "data")
    n = 0
    with open(os.path.join(data, "MANIFEST.tsv"), newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            path = os.path.join(data, row["file"])
            if row["file"].startswith("sources/") and not os.path.exists(path):
                # poster / earlier-talk PDFs: cited only, never read by the build, and kept out of git
                print(f"data/{row['file']}: not present (local-only source, not in the repository); skipped")
                continue
            if row["file"].startswith(("git/", "git_facts.json")) and not os.path.exists(path):
                # unpublished results from the private project repository: kept out of git (2026-09-30)
                raise SystemExit(f"data/{row['file']} is not present: the unpublished results under data/git/ "
                                 "are not in the public repository, so the talk cannot be rebuilt from it. "
                                 "See source/README.md, section 'What is not in this repository'.")
            got = hashlib.sha256(open(path, "rb").read()).hexdigest()
            assert got == row["sha256"], f"data/{row['file']}: sha256 {got} != MANIFEST {row['sha256']}"
            n += 1
    return n


if __name__ == "__main__":
    print(f"data/MANIFEST.tsv: {verify_manifest()} files match sha256")
    h = stage_jsdp_assets()
    verify_reused_figures_present()
    for name, digest in h.items():
        print(f"checked {name}: sha256[:16]={digest}")
    print(f"confirmed present: {REUSED_FIGS}")
