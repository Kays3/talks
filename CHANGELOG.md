# Changelog

Versions are dated. Each talk folder's `source/README.md` has the full provenance.

This repository was published on 2026-09-30 as a single commit, tagged `v2026-09-30`. The
entries below also describe the earlier versions, which were not published separately.

## Unreleased: four more talks and posters (proposed 2026-09-30)

Added, one folder each, with a README recording provenance and pre-publication edits:
`2026-09-balanced-donor-luad` (copied unchanged), `2026-08-jsdp-sclc-tcell-talk` and
`2026-08-jsdp-sclc-tcell-poster` (co-author e-mail and local paths removed), and
`2026-08-te-ocean-acidification-poster` (local paths and the private-repository link removed, PDF
exported). The root README index lists them.

## v2026-09-30: public release

Lung T-cell talk, prepared for making the repository public. Slide numbers, results and the
abstract are unchanged.

- Slide 1: the co-author's e-mail address, the "DRAFT -- outline stage" footer and the line naming
  the source poster, talk and build time are removed. A line pointing to this repository is added.
- The QR codes on slides 1 and 20 now open `https://github.com/Kays3/talks` (they pointed at the
  private project repository).
- The report and the READMEs no longer print the co-author's e-mail address.
- The unpublished result tables (`source/data/git/`, `source/data/git_facts.json`) are no longer
  tracked. Without them `./build.sh` checks `SHA256SUMS` and exits instead of rebuilding; see
  `source/README.md`, "What is not in this repository".
- The 25 Sep original outline PDF in `source/verify/`, which prints the co-author's e-mail
  address, is no longer tracked. It is used only by `./build.sh verify`.
- `slides.pptx`, `slides.pdf`, `report.docx`, `report.pdf` and `SHA256SUMS` rebuilt.

## 2026-09-30: abstract and docs rewrite (not published separately)

Lung T-cell talk (`2026-09-lung-tcell-imrad/`).

- Abstract: the four IMRaD sections rewritten in plainer prose. Every number, gene, test and
  caveat is kept, and the title is unchanged. The text is 380 words (375 before). The closing
  build note moved to `source/README.md`.
- `report.docx` and `report.pdf` rebuilt, because the report's Abstract section uses the same
  text. The slides did not change.
- READMEs and `source/env/TOOLS.md` rewritten and stale statements corrected.
- `SHA256SUMS` regenerated. `CITATION.cff` gains a version field.

Afterwards the local working copy was moved on disk. No tracked file depends on the location.
`env/.venv` does, so it was recreated and the talk rebuilt, and every file in `SHA256SUMS` still
matched. The Build section of `source/README.md` records the step.

## 2026-09-29 (not published separately)

First complete version of the lung T-cell IMRaD talk, with slides, report, abstract, figures and
the self-contained build package.
