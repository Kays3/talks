# Changelog

Versions are dated. Each talk folder's `source/README.md` has the full provenance.

This repository was published on 2026-09-30 as a single commit, tagged `v2026-09-30`. The
entries below also describe the earlier versions, which were not published separately.

## Unreleased: lab progress report, version 4 (proposed 2026-10-02)

Updated version 4 on 2026-10-03 with a third bulk panel (slide 29), after its report passed review: the
same registered bulk network against 34 ENCODE CRISPRi knockdowns in K562 (Geneformer_TE main, merge
`73226eb`) reads `RECOVERED_NONSPECIFIC`, and a co-expression baseline did better. A data figure is drawn
from three copied result tables. The synthesis slide (now 40) counts eight tests (synthesis revision 3),
with the panel-level P3 gain not distinguishable from zero in any of the four panels; the bulk
introduction, the TE summary, Summary 2, the paper and closing slides, the handout, `SOURCES.md` (later
slides renumbered) and the READMEs are updated. The deck has 42 slides.

Rebuilt on 2026-10-02 the outputs that still carried the old affiliation after the affiliation change:
`2026-08-jsdp-sclc-tcell-poster/poster.html` (edited in place, it has no builder) and `poster.pdf`
(WeasyPrint 69.0, as before), and `slides.html` and `slides.pdf` of lab progress versions 1 to 3, with
their manifests. The extracted text changes only in the affiliation lines.

Updated version 4 on 2026-10-02 with a cross-project synthesis slide (39) before the closing summary:
seven tests across the two projects, where predictions tracked the data the controls did too, and no
Geneformer prediction has been checked against a measured perturbation. It adds no new number. The deck
has 41 slides.

Updated versions 1 to 4 on 2026-10-02 with the reviewed results of the colon perturbation study (E2;
Kays3/geneformer-lung-tcell `main`, merge `4cce44a`). Random genes were
opposed in the same direction as in lung (rho -0.245, one-sided p 0.0067) but stayed significant in only
78% of resamples against the registered 95%, so the registered reading is `control_draw_sensitive_open`;
3 of 10 lung reference genes kept their lung direction (9 were needed), so `pattern_not_replicated`.
Versions 3 and 4 replace the slide of pre-specified readings with a results slide and a data figure drawn
from three copied result files; versions 1 and 2 replace their running-status slide. Summaries, open
questions and handouts are updated. Version 1 also adopts the wording "negative (the anti-correlation did
not appear)", and the version 2 gate-strip figure no longer clips its y-axis label.

Updated version 4 on 2026-10-02 with the TE arm of the Freimer T-cell knockout test (Geneformer_TE
`main` merge `c17d39b`, after science and numbers review). Slide 34 now shows the result with a data
figure drawn from four copied tables: the registered reading is `TE_RECOVERED_NONSPECIFIC`; a post hoc
control-only null shows that most knockouts' TE subfamily counts are reachable by chance (CBFB the one
exception); and 83% of TE counts are intronic, so TE shifts cannot be separated from host-gene
transcription. No TE test is shown as running. The bulk slide's TE-arm line, the track diagram, the TE
conclusions, Summary 2, the closing summary, the outline and the handout are updated.

Updated version 4 on 2026-10-02 with the zebrafish ground truth from Geneformer_TE (report at `main`
`246c3e4`, after science and numbers review). A new slide 33 shows 17 zebrafish perturbation contrasts
with a data figure drawn from six copied tables: no loss-of-function study shifted the global TE share
(0 of 16); the one shift, human UHRF1 overexpression, is mostly compositional; loss of DNA-methylation
regulators leaned toward derepression in 6 of 7 studies in exploratory tests that do not pass correction;
and the fish network directions agreed with the zebrafish leans at chance level (4 of 9). The running-tests
slide (now 34) keeps only the Freimer TE arm. The TE conclusions, Summary 2, the closing summary, the
outline, the track diagram and the handout are updated. The deck has 40 slides.

Added `2026-10-lab-progress-geneformer-isp-v4`: version 3 plus six slides (29 to 34) on transposable
elements, from the Geneformer_TE project, by Kaisar Dauyey. A diagram shows the project's three tracks
(single-cell Geneformer, bulk linear network, measured knockouts as ground truth) and their state. Two data
figures come from merged tables: 30 fish TE regulators against 90 expression-matched random genes in 162
bulk libraries (no regulator passed), and the TE share of reads by tissue and CO2 group (gill lower after
developmental exposure; exploratory). The zebrafish knockout panel and the TE re-alignment of the Freimer
knockouts are shown as running, with what they will test and no results. Summary 2, the closing summary,
the outline and the glossary are updated, and the bulk slide notes that the TE re-alignment was approved.
Version 3 is unchanged. The root README index lists it.

## Unreleased: lab progress report, version 3 (proposed 2026-10-01)

Added `2026-10-lab-progress-geneformer-isp-v3`: "Evaluating in-silico perturbation with Geneformer",
a 33-slide revision of version 2 by Kaisar Dauyey. The language is more formal. New diagrams show the
pipeline, rank-value tokenisation, the perturbation and its score, and the evaluation criteria; new data
figures show the external-cohort feasibility count (Pelka et al. 2021) and the per-donor colon classifier
gate. Three slides discuss whether in-silico perturbation applies to bulk RNA-seq, stated as a proposal
with no result, and the summary and paper-outline slides include that question. The colon perturbation
run is shown as gate passed, results pending. The E0 per-donor count table is added to `source/data/`.
Versions 1 and 2 are unchanged. The root README index lists it. Follow-up (2026-10-01): larger
study diagram on slide 28 (four boxes), the boundary line on slide 7 no longer crosses the legend, and
the legend on slide 22 no longer covers two data points.
Follow-up (2026-10-02): slides 26 to 28 report the first bulk RNA-seq test (a linear network
model against 17 measured CRISPR knockouts in CD4+ T cells; registered reading non-specific) in place
of the proposal, with a new data figure; the open-questions, paper-outline and summary slides are updated
accordingly.
Follow-up (2026-10-02): slides 27, 28 and 30 to 32 add the replication on 38 new knockouts (Weinstock
et al. 2024), which did not reproduce the first reading; the two tests are shown side by side with the
uncontrolled differences between them.

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
