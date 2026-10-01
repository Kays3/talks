# Changelog

Versions are dated. Each talk folder's `source/README.md` has the full provenance.

This repository was published on 2026-09-30 as a single commit, tagged `v2026-09-30`. The
entries below also describe the earlier versions, which were not published separately.

## Unreleased: lab progress report, version 2 (proposed 2026-10-01)

Added `2026-10-lab-progress-geneformer-isp-v2`: "Reading the Current, version 2", a 26-slide
rewrite of the lab progress report for students and professors together. One point per slide, a
figure on most slides, a progress bar, one colour per verdict and one icon per evaluation check;
plain language with a short glossary. New summary slides list the evaluation criteria found so
far (each with the evidence behind it), what still needs testing, and the outline of a possible
paper, with established results and hypotheses marked apart. No new measurement; the colon run
is shown as running, with no result. Version 1 is unchanged. The root README index lists it.

## Unreleased: citizen-science poster (proposed 2026-10-01)

Added `2026-08-te-citizen-science-poster`, the plain-language companion to the ocean-acidification
poster (4 August 2026). Local file paths in the speaker notes are reduced to file names, camera and
editing metadata is removed from the embedded photographs, and a PDF is exported. The root README
index lists it.

## Unreleased: lab progress report (proposed 2026-10-01)

Added `2026-10-lab-progress-geneformer-isp`: "Reading the Current", a 28-slide lab progress report
on Geneformer, in-silico perturbation and the criteria used to judge it, with speaker notes, a
one-page handout, `SOURCES.md` (a source for every number) and `source/` (figure and deck
generators with their input data and checksums). Prepared from an internal draft: reviewer names,
host names and internal folder paths were removed. Slide 23 is a dated status of the colorectal
run at 12:45 JST on 1 October and shows no result; it will be updated when the run has finished
and been reviewed. The root README index lists it.

## Unreleased: four more talks and posters (proposed 2026-09-30)

Added, one folder each, with a README recording provenance and pre-publication edits:
`2026-09-balanced-donor-luad` (copied unchanged), `2026-08-jsdp-sclc-tcell-talk` and
`2026-08-jsdp-sclc-tcell-poster` (co-author e-mail and local paths removed), and
`2026-08-te-ocean-acidification-poster` (local paths and the private-repository link removed, PDF
exported). The root README index lists them.

## Unreleased: report page numbers (proposed 2026-09-30)

Lung T-cell talk: the written report (`report.pdf`, `report.docx`) now has "Page N of M" at the
bottom centre of every page. No text changed; still 22 pages.

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
