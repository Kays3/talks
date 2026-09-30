# Lung T-cell IMRaD talk: self-contained build package

Talk: "A Foundation-Model T-cell Dysfunction Screen: Translational Candidates, Then a Full Audit",
Kaisar Dauyey · Shinji Nakaoka.

The talk started as an 18-slide IMRaD deck (Background / Introduction / Methods / Results /
Discussion), restructured on 2026-09-25 from poster_final (2026-08-15) and JSDP_P25_talk
(2026-08-17), with an abstract in IMRaD form. Its generators were merged to `geneformer-lung-tcell`
main in PR #33 (`316bbc0`, `talk/imrad_20260925/`). On 2026-09-28 it grew into the published
26-slide deck and written report (see "Editable Office versions" below). This folder packages the
generators so that everything rebuilds without access to that repository or to the internal
analysis workspace, provided the unpublished input files are present. They are not in the public
repository; see "What is not in this repository" below.

The packaging itself changed no slide or abstract content. Later content changes are dated below:
the 2026-09-28 additions, the 2026-09-29 decisions and publication edits, and the 2026-09-30
rewrite of the abstract text.

## Build

```
./build.sh           # builds build/lung_tcell_talk_imrad_20260925.pdf and build/lung_tcell_talk_imrad_abstract_20260925.md
./build.sh verify    # also compares them page by page with verify/ (needs poppler)
```

On the first run, `build.sh` creates `env/.venv` from the pinned wheels in `env/wheels/` and goes
to PyPI only if those wheels do not fit the platform. To use an interpreter you already have, run
`PYTHON=/path/to/python3 ./build.sh`; it needs the packages in `env/requirements.txt`.

`env/.venv` stores the absolute path it was created at. After moving or copying the repository,
delete `env/.venv` and run `./build.sh` again to recreate it. No tracked file depends on where the
repository sits; on 2026-09-30 the working copy was moved (from `workspace/talks` to
`workspace/github/talks`), the venv recreated offline from `env/wheels/`, and the rebuild left
every tracked file unchanged.

The build is byte-reproducible. ReportLab writes the PDF with `invariant=1`, which fixes the
creation date and document ID. Until 2026-09-30 the title slide also printed the original build
time; that line is gone, so `TALK_BUILD_TIME_NOW=1` no longer changes the output.

Slide 1 changed twice after 25 Sep. On 2026-09-29 it gained a contact line (PDF sha256 `a90d7367…`
to `72a65b95…`). On 2026-09-30 it lost the co-author's e-mail address, the "DRAFT" footer and the
provenance/build-time line, and both QR codes (slide 1 and page 18) were regenerated to point at
this repository (`72a65b95…` to `253add74…`). `./build.sh verify` now reports 16 of 18 pages
identical to `verify/`: page 1 differs in text and QR code, page 18 in its QR code only (its text
is identical). It also reports the abstract as DIFFERS (see "Abstract" below).

Expected `build/BUILD_SHA256SUMS`:
```
253add742a8882dc2f032b0678178bfc0c5d625d14610edcd0dc1824b1396d0e  lung_tcell_talk_imrad_20260925.pdf
3328801ad0b753c1da45a100c158c5836b7a1e2d79be633e91baa8d1eb133ef7  lung_tcell_talk_imrad_abstract_20260925.md
```

## What is not in this repository

The public repository leaves out the unpublished results the generators read: the 15 files under
`data/git/` (tables, result notes and scripts copied from the private project repository) and
`data/git_facts.json` (that repository's commit metadata). Every published file is complete
without them; they are needed only to regenerate the slides, report, abstract and figures.

It also leaves out `verify/original_lung_tcell_talk_imrad_20260925.pdf`, the 25 Sep outline that
`./build.sh verify` compares against, because its title slide prints the co-author's e-mail
address. Its sha256 is
`21c306a0a261d9cd35b0a345b39f2bf5a492488b6b96cc02a2657df72d0641be`. The original abstract in
`verify/` is kept.

`data/MANIFEST.tsv` still lists each omitted file with its origin and sha256, so a copy obtained
from the authors can be checked before use. In a clone without them, `./build.sh` says so, checks
every published file against `SHA256SUMS` and exits 0:

```
$ ./build.sh
data/git/ and data/git_facts.json are not in this repository (unpublished results); the talk
cannot be rebuilt from a public clone. Checking the published files against SHA256SUMS instead:
all files in source/SHA256SUMS match
```

With the files in place (same paths, matching sha256), all build modes work as described above.

## Abstract

`src/make_lung_tcell_talk_imrad_abstract_20260925.py` writes the abstract and computes its word
count from the section text on each build. The count had been typed by hand three times before
(197, then 300, then 323), and each figure was wrong or stale by the next edit; the last was cut
short by an off-by-one line range in a `sed` check that was never re-run against the file. The
current text is 380 words, or 384 with the four section labels; `abstract.md` prints both.

No word limit was stated for this talk. The 2026-09-24 abstract used a 250-300-word default, and
the current text is over it. It was not trimmed to fit, because the qualifications in the Results
section are what make it longer. If a limit is ever set, cut parenthetical precision first (for
example the exact FDR) and keep the caveat that the two concordance arms were measured on
different cell sets and the panel has not been rerun. Earlier versions of this note also listed
the 202-1,131 detection range as cuttable; that range is not in the abstract text.

The byline is "Kaisar Dauyey, Shinji Nakaoka", matching `poster_final` and `JSDP_P25_talk`
exactly, with no AI co-authorship line (decided 2026-09-29; see "Decisions" below).

History of `abstract.md`:

- 2026-09-25: first build, `26e2be16…`.
- 2026-09-29: only the closing note changed, recording the 30-minute talk length and the byline
  decision. sha256 `f138cfe6…`.
- 2026-09-30: the four sections were rewritten for plain, direct prose. Every number, gene,
  test and caveat is kept; the title is unchanged. The closing note moved here, leaving only the
  word count in `abstract.md`. sha256 `3328801a…`. The report's Abstract section is built from
  the same text, so `report.docx` (`0780849a…` to `b21bafe1…`) and `report.pdf` changed with it.
  The slides did not change.

## Editable Office versions (added 2026-09-28)

```
./build.sh office    # builds the PDF, then editable/*.pptx and *.docx, then checks them with LibreOffice
```

The editable versions are the 25 Sep talk plus material added on 2026-09-28 for an audience of
geneticists from various fields, most of whom do not work in bioinformatics. The 18 original
slides keep their findings, numbers and wording; the only changes to them are the page numbers
and an added "In plain words" line under headline numbers. All added material lives in
`src/additions.py`, with a source for every added fact, and both Office files are built from it.

### Talk running order (26 slides)

| # | Slide | |
|---|---|---|
| 1 | Title | original 1 |
| 2 | Research background: T cells in lung cancer | added |
| 3 | Methods in plain words: three tools, one analogy each | added |
| 4 | Our 24JSDP poster (P25) and what the audit changed (table) | added |
| 5-7 | Background; Introduction I1, I2 | original 2-4 |
| 8-11 | Methods M1-M4 | original 5-8 (plain-words lines on 8, 10) |
| 12-17 | Results R1-R6 | original 9-14 (plain-words lines on all six) |
| 18 | S100 ISP result: new since 25 Sep, pre-registered, run 2026-09-28 | added |
| 19-20 | Discussion; Limitations | original 17-18 |
| 21 | Glossary (14 terms) | added |
| 22 | Appendix divider | added |
| 23-24 | Precision control (bf16); Mechanism (the designated cut) | original 15-16, moved to the appendix (plain-words line on 23) |
| 25 | S100 per-gene scores (appendix table) | added |
| 26 | Detection figure, panel b (all 31 genes ranked; readable redraw) | added |

### Report

The report has a title block, Abstract, Introduction, Methods, Results, Discussion, Limitations,
Glossary, Appendix, and References and sources. Each added subsection is labelled "Added
2026-09-28" and ends with its sources. The added subsections are Research background and The
original poster (Introduction), Three tools in plain words (Methods), the S100 ISP result
(Results), the S100 result in context (Discussion), the Glossary, and the S100 per-gene table
(Appendix).

### Sources for added material

- The JSDP poster and talk are copied into `data/sources/`. They are untracked in the repository,
  so `data/MANIFEST.tsv` identifies them by sha256.
- The S100 result files are copied from `53adee2` into `data/git/53adee2/`, and the build reads
  and asserts their numbers.
- `METHODS.md` @ `dd7366c`.
- Eight papers, each DOI resolved on Crossref on 2026-09-28: Theodoris 2023, Horn 2018,
  Wherry 2015, Rudin 2019, Gay 2021, Young 2020, Benjamini 1995, Mann 1947.
- No [TODO cite] or other [TODO] marker remains in the added material. Following a ruling on
  2026-09-28, the poster is named only as "our 24JSDP poster (P25)", with no venue, date or
  meeting details.

### Poster statements the later audit changed

1. The poster called the four edits "concordant, FDR < 0.05 in both arms". The concordance half
   was scored on different cell sets per arm (overexpress 2,424 cells, delete 202-1,131) and has
   not been rerun. Source: this deck R1; `targeted_panel_delete_overexpress_merged.csv` @
   `6882627`; runner fix `66d235b`.
2. "The model implies Normal < SCLC < LUAD on the checkpoint axis." The poster already called this
   an open question. At donor level it is now null (p = 0.216). Source: this deck R3;
   `t6_permutation_tests.csv` @ `9ec518c`.
3. Not an audit change: the poster and talk give 9,377 held-out cells, while the confusion matrix
   sums to 9,376. This is a known one-cell truncation with no effect at any reported precision
   (`METHODS.md` lines 125-166).

### Readable redraws of two figures (2026-09-28)

`src/make_readable_figures.py`, run by `./build.sh office`, redraws report Figure 4 / slide 13
(`detection`) and report Figure 5 / slide 14 (`fig_t6_reversal`) from the underlying tables. The
redraws show the same data, quantities and claims. Before drawing, the generator asserts every
number the originals showed: rho -0.60, p 2.7e-05, n 42, 2,424 source cells, 31 genes, 20
detected, TIM-3 4th and TIGIT 5th, and 0.301 / 0.244 / 0.321 / 0.267 / 0.186 / 0.242, 74.9 % and
0.122.

Sources. `detection_orig.png` is pixel-identical to `figures/cart_overexpression.png` @ `eb533f8`,
which `make_detection_figure.py` @ `eb533f8` drew from two tables last changed at `37a0211`. All
three are copied into `data/git/eb533f8/`, and the redraw uses that script's selection rules. The
T6 redraw uses `t6_weighting_reconciliation.csv` and `t6_donor_level_scores.csv` @ `9ec518c`, the
same quantities as `src/reference/`; its score is the curated 7-gene exhaustion programme
(`RESULTS_T6.md` @ `9ec518c`).

Readability. All text is at least 14 pt at the size the figure appears on the slide, and each PNG
is drawn at its slot's physical size at 300 dpi. Direct labels replace crowded legends, colours
follow the Okabe-Ito colour-blind-safe palette, axis titles are in plain language, and the T6
y-axis is named (exhaustion score). The generator fails the build if any text leaves the canvas or
overlaps other text.

One layout change was needed. The 31 gene names of the original panel b do not fit at 14 pt in
the 150 x 100 mm slide slot, so panel a stays on slide 13 and panel b moves to appendix slide 26
(A4). In the report, panel b is Figure 4 (continued), with the genes listed down the page. No gene,
value or rank changes. Three leader lines (CXCL8, TIM-3, CTLA-4) still pass over a neighbouring
marker; no text overlaps anything.

The originals are kept as `data/assets/detection_orig.png` and `fig_t6_reversal_orig.png`, and the
25 Sep PDF still uses them, so its figure pages are unchanged. `docs/figure_redraw_before_after.png`
shows both versions side by side. `data/MANIFEST.tsv` lists every new PNG with the sha256 of its
generator and inputs. The redraws added four pinned dependencies (matplotlib 3.10.8, numpy 2.4.4,
pandas 2.3.3, scipy 1.17.1), whose wheels are in `env/wheels/`.

### Editability and checks

In the `.pptx`, every piece of text is a native text box or native table (three tables: poster,
glossary, S100 per-gene). Titles sit in the layout title placeholder, figures are placed pictures,
cards are native shapes, and the palette and font are set in the slide master's theme. Eight
secondary tints stay fixed RGB: `#2A201B #4A5A55 #7A8A85 #9A877C #B8A79A #CFE0DA #D6C7BE #DCE3DF`.
The speaker notes cite a source for every slide and mark added slides "ADDED 2026-09-28".

In the `.docx`, headings use Word's Heading 1 and Heading 2 styles, and the table of contents is a
field (right-click it, then Update Field). The nine figures have SEQ-numbered captions. Word
tables hold the card grids, the poster table, the glossary, the S100 table and the references. No
[TODO] marker remains; the contact line, talk length and byline were settled on 2026-09-29.

When LibreOffice is installed, `./build.sh office` runs `src/check_office.py`, which converts both
files and checks that:

- every rendered word lies inside its text box or table (no overflow);
- each original slide's words equal its 25 Sep PDF page, plus the plain-words line;
- each added slide's words equal `additions.py`;
- every original slide paragraph and every abstract section appears verbatim in the report.

On the 2026-09-30 build: 26 slides, 0 words outside their boxes, 0 slides differing from their
source, 99 of 99 paragraphs verbatim, and a 22-page report. (On 2026-09-28, before the 2026-09-29
additions, the report converted to 20 pages.) Every slide was also inspected by eye on 2026-09-28.
Rebuilds of the `.pptx` and `.docx` are byte-identical.

## Layout

| Path | What |
|---|---|
| `build.sh` | The one build command. |
| `build/` | The 25 Sep deck PDF and the abstract, rebuilt in this folder (not copied). |
| `src/make_lung_tcell_talk_imrad_20260925.py` | Deck generator (ReportLab). |
| `src/make_lung_tcell_talk_imrad_abstract_20260925.py` | Abstract generator. It computes its own word count. |
| `src/lung_tcell_talk_imrad_figures_20260925.py` | Checks every `data/` file against its `MANIFEST.tsv` sha256 and the recorded asset sizes. Runs first. |
| `src/verify_pages.py` | Page-by-page comparison (60 dpi PNG pixel diff and extracted text) plus a byte compare of the abstract. |
| `src/reference/lung_tcell_talk_figures_20260924.py` | Generator of the four audit PNGs (matplotlib). Kept for provenance and not run by the build, which uses the PNGs in `data/assets/`. It still reads the repository through `git show`. |
| `data/git/<commit>/<repo path>` | Every repository file the deck reads, byte for byte from that commit. Not in the public repository. |
| `data/assets/` | The images on the slides. |
| `data/git_facts.json` | The git metadata the generator used to read live (commit times, file history, the `origin/main` sha). Not in the public repository. |
| `data/MANIFEST.tsv` | Each data file with its origin path, commit or location, and sha256. |
| `env/` | `requirements.txt` (pinned), `wheels/`, and `TOOLS.md` (tool versions). |
| `fonts/README.md` | Why no fonts are shipped (standard-14 PDF fonts, not embedded). |
| `editable/` | The PowerPoint deck and Word report, built by `./build.sh office`. |
| `src/capture_deck.py`, `src/additions.py`, `src/make_pptx.py`, `src/make_docx.py`, `src/check_office.py` | The Office generators, the 2026-09-28 added content, and the check. |
| `src/make_readable_figures.py` | The two readable figure redraws. |
| `src/publish.py` | Copies the final files one level up and exports the PDFs (`./build.sh publish`). |
| `data/sources/` | The JSDP poster and talk PDFs (untracked; cited by the added slides). |
| `verify/` | The PDF and abstract as built on 2026-09-25 23:57 JST (14:57Z), used only by `./build.sh verify`. The PDF is not in the public repository. |
| `docs/lung_tcell_talk_imrad_sources_20260925.md` | The sources note, with the citation for every slide. |
| `SHA256SUMS` | sha256 of every tracked file in the talk folder except itself, with paths relative to that folder. Check with `cd .. && shasum -a 256 -c source/SHA256SUMS`. |

## Differences from the repository version (paths and provenance only)

- `git show <ref>:<path>` now reads `data/git/<ref>/<path>`. Where the generator read
  `origin/main`, the package pins the commit that was the tip of main at the original build,
  `dd7366c` (2026-09-25 13:33 JST, 04:33Z). The one file read that way is `METHODS.md`, last
  changed at `ba5935c` (2026-08-12), so it is the same file at either commit.
- `git log` and `git rev-parse` calls now read `data/git_facts.json`. The generator's assertions
  still run against those values, for example that `targeted_panel_delete_overexpress_merged.csv`
  has exactly one commit on main (`6882627`) and that fix `66d235b` is dated 2026-09-22.
- The title slide's "built …" stamp is the original 2026-09-25 23:57 JST (14:57Z), not the
  current time.
- The canvas is created with `invariant=1`, which changes only PDF metadata, not page content.
- Output goes to `build/` instead of the internal analysis workspace.
- The figures script checks `data/` instead of copying from `talk/assets/`.
- The six JSDP PNGs are byte-identical to the originals in `geneformer-lung-tcell/talk/assets/`
  (checked 2026-09-28). Those originals are untracked and gitignored, so they have no commit.

## Verification (2026-09-28)

The folder was copied to a temporary directory and built with `./build.sh verify` under a macOS
`sandbox-exec` profile that denied reads of the source repository, the internal analysis
workspace and network storage. A probe inside the sandbox confirmed that neither the repository
nor the workspace was readable. The build used a fresh `env/.venv` (Python 3.13.12, reportlab
5.0.1, pillow 12.2.0) installed offline from `env/wheels/`.

All 18 pages were pixel-identical at 60 dpi and text-identical, the abstract was byte-identical,
and a second build gave the same PDF sha256 (`a90d7367…`). The PDF bytes differ from the
2026-09-25 file only in metadata (creation date and document ID), because of `invariant=1`. The
contact line (2026-09-29) and the abstract changes (2026-09-29, 2026-09-30) came after this test.

On 2026-09-30 an unchanged copy of the folder was rebuilt with `./build.sh publish` before the
abstract rewrite. Every file in `SHA256SUMS` matched except the two LibreOffice PDF exports, as
expected.

## Decisions (2026-09-29)

1. Contact address: k.dauyey.bio.nu@gmail.com was requested. Slide 1 and the report printed it
   with the co-author's address; since 2026-09-30 they print "Contact: k.dauyey.bio.nu@gmail.com"
   only (see "Publication decisions" below).
2. Byline and AI co-authorship (20:49 JST, 11:49Z): "keep the byline". It stays "Kaisar Dauyey ·
   Shinji Nakaoka", matching poster_final and JSDP_P25_talk exactly, with no AI co-authorship line.
   No slide text changed, and the report's [TODO] was removed.
3. Venue limits (20:45 JST, 11:45Z): "Talk word limit within 30 minutes, time slot is not
   important."
   - This is read as about 25 minutes of speaking plus about 5 minutes of questions.
   - The main talk (slides 1-21) is budgeted at 23:45, so no slide moved to the appendix. The
     budget is `TIMING` in `src/additions.py`, which asserts that it fits. Each slide's speaker
     notes start with its budget (e.g. `[1:30]`) and the running total; see "Talk timing".
   - No abstract word limit was stated, so the abstract was not cut to a limit.
   - The report's venue [TODO] was replaced by a line recording the 30-minute length.
   - R8 (mechanism) was already appendix slide 24 and is not part of the timed talk.

## Talk timing (added 2026-09-29)

| slide | budget | cumulative |
|---:|---:|---:|
| 1 | 0:30 | 0:30 |
| 2 | 1:30 | 2:00 |
| 3 | 1:30 | 3:30 |
| 4 | 1:15 | 4:45 |
| 5 | 1:00 | 5:45 |
| 6 | 1:00 | 6:45 |
| 7 | 1:00 | 7:45 |
| 8 | 1:15 | 9:00 |
| 9 | 1:00 | 10:00 |
| 10 | 1:15 | 11:15 |
| 11 | 1:00 | 12:15 |
| 12 | 1:30 | 13:45 |
| 13 | 1:30 | 15:15 |
| 14 | 1:00 | 16:15 |
| 15 | 1:15 | 17:30 |
| 16 | 1:15 | 18:45 |
| 17 | 1:00 | 19:45 |
| 18 | 1:30 | 21:15 |
| 19 | 1:00 | 22:15 |
| 20 | 1:15 | 23:30 |
| 21 | 0:15 | 23:45 |
| 22-26 | appendix, untimed | |

## The S100 ISP result (2026-09-28)

The S100 ISP run finished on 2026-09-28 with a registered negative result (main, PR #37
`4455914`; `sclc_validation/perturbation_workflow/s100_isp/results_s100_luad_20260928/RESULT.md`).
The 26-slide deck reports it on slide 18 and gives the per-gene scores on appendix slide 25; the
report covers it in Results, Discussion and the Appendix.

No sentence in the original 18 slides or the abstract describes the S100 ISP as designed, planned,
pending or not yet run; those texts do not mention the experiment. Slides 9, 12, 14 and 17 of the
original deck and the abstract do mention S100A8/S100A9 (whole-genome screen FDR and concordance
failure). Those two genes are classifier anchors, and the S100 ISP deliberately did not test them
(no Q). Its result concerns four ambient-high versus four ambient-low S100 genes, so it neither
confirms nor contradicts those sentences, and they were left as they are.

## Repository layout (added 2026-09-29)

This folder is `source/` of the talk folder `2026-09-lung-tcell-imrad/` in the GitHub repository
`Kays3/talks` (set up on request, 2026-09-29 20:57 JST, 11:57Z). The audience-facing files
(`slides.pdf`, `slides.pptx`, `report.pdf`, `report.docx`, `abstract.md`, `figures/`) sit one level
up, and `./build.sh publish` writes them there.

`slides.pdf` and `report.pdf` are LibreOffice exports of the final `.pptx` and `.docx`. The
26-slide deck exists only in the Office emitters; the 25 Sep ReportLab generator still builds the
18-slide outline in `build/`. The exports are not byte-reproducible because LibreOffice re-subsets
fonts on each run, so `SHA256SUMS` pins the published bytes.

A clone does not contain:

- `env/.venv/`, which `./build.sh` creates;
- `env/wheels/` (recreate with `pip download -r env/requirements.txt -d env/wheels`; without it
  `./build.sh` installs from PyPI);
- `data/sources/`, the poster and earlier-talk PDFs, which by standing ruling are kept out of
  repositories. The build only cites them and never reads them.

An earlier local-only commit (`0e7181d`, 2026-09-29) was superseded by this layout, and its `.git`
was removed when the folder moved here.

## Publication edits (2026-09-29)

Before publication, internal host names, home and server paths, office workspace paths and
people's first names were replaced by neutral roles ("the project lead", "the domain reviewer",
"the independent reviewer", "analysis workspace"). This covered `README.md`, `docs/`, `src/`
comments, `data/MANIFEST.tsv` and four files under `data/git/`, whose new sha256 values are in
`MANIFEST.tsv`. No number, test or slide wording changed.

The report now cites STRING formally (Szklarczyk et al., Nucleic Acids Res 2023,
doi:10.1093/nar/gkac1000), and slide 24 has an added "In plain words" line naming STRING as the
source of the network edges. The STRING version behind the original JSDP figure is not recorded,
so the reference is to the current STRING paper.

## Publication decisions (2026-09-30)

Decided before the repository was made public:

1. The unpublished results under `data/git/` and `data/git_facts.json` are left out (see "What is
   not in this repository"). The numbers on the slides and in the report are unchanged.
2. The QR codes on slide 1 and slide 20 (page 18 of the 25 Sep outline) pointed at the private
   project repository. They now encode `https://github.com/Kays3/talks`. The new `data/assets/qr.png`
   was generated with macOS CoreImage (error correction M, 8 px per module, same colours and size,
   296 x 296 px); its sha256 is in `MANIFEST.tsv`.
3. The co-author's e-mail address is removed from slide 1, the report and the READMEs. The byline
   still reads "Kaisar Dauyey · Shinji Nakaoka".
4. Slide 1 no longer carries the "DRAFT -- outline stage, not camera-ready" footer or the line
   naming the source poster, talk and build time. It now points readers to this repository.

After these changes `./build.sh publish` reported 0 words outside their text boxes, 0 slides whose
words differ from their source, 99 of 99 report paragraphs verbatim and a 22-page report. The
abstract and the figures did not change.

## Page numbers in the report (2026-09-30)

`src/make_docx.py` now puts "Page N of M" in the report footer, bottom centre (Word PAGE and
NUMPAGES fields), following the office rule that every report PDF carries page numbers. The report
text, figures and page count (22) are unchanged; `report.docx`, `report.pdf` and
`editable/lung_tcell_report_imrad_20260925.docx` were rebuilt, and `SHA256SUMS` regenerated. The
slides did not change, so the published `slides.pdf` was kept.

