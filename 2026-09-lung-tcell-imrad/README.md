# A Foundation-Model T-cell Dysfunction Screen: Translational Candidates, Then a Full Audit

Kaisar Dauyey · Shinji Nakaoka, Laboratory of Mathematical Biology, Hokkaido University,
Japan. Contact: k.dauyey.bio.nu@gmail.com

## Files

| What | File |
|---|---|
| Slides (26: talk 1-21, backup 22-26) | [slides.pdf](slides.pdf) · [slides.pptx](slides.pptx) (the speaker notes give per-slide timing and sources) |
| Written report (22 pages) | [report.pdf](report.pdf) · [report.docx](report.docx) |
| Abstract (structured, 380 words) | [abstract.md](abstract.md) |
| Figures (PNG, named by slide) | [figures/](figures/) |

The talk fits in 30 minutes: slides 1-21 take about 24, and the rest is questions. Slides 22-26
are backup and are shown only if someone asks.

## Figures

| File | Slide |
|---|---|
| `slide06_four-replicated-hits.png` | Four replicated checkpoint/persistence hits |
| `slide08_classifier-confusion-matrix.png` | Held-out test performance of the SCLC/LUAD/normal classifier |
| `slide12_spatial-tissue-validation.png` | Independent spatial (Visium) validation |
| `slide13_sparse-genes-fake-big-effects.png` | Detection vs deletion effect size |
| `slide14_sclc-vs-luad-donor-level.png` | Donor-level vs cell-level SCLC-vs-LUAD comparison |
| `slide15_s100a8-s100a9-concordance.png` | S100A8/S100A9 delete vs overexpress |
| `slide16_ambient-breakdown-top120.png` | Ambient-RNA flags in the top 120 candidates |
| `slide23_bf16-vs-fp32-precision.png` | Precision control (bf16 vs fp32) |
| `slide24_interaction-neighbourhood.png` | Interaction neighbourhood of the four original hits |
| `slide26_immune-genes-ranked-by-deletion.png` | All 31 immune/lineage genes ranked by deletion effect |

## Rebuilding

You do not need anything in [`source/`](source/) to read the talk. It holds the generators
(`src/`), the input images and data manifest (`data/`), the Python requirements
(`env/requirements.txt`), the 25 Sep outline build the deck started from (`build/`, `verify/`) and
`SHA256SUMS`. [source/README.md](source/README.md) has the full provenance.

The unpublished result tables the generators read (`source/data/git/`, `source/data/git_facts.json`)
are not in this repository, so a clone cannot regenerate the talk. It can check that every
published file is intact:

```sh
cd source
./build.sh                                    # no unpublished data: checks SHA256SUMS and exits 0
cd .. && shasum -a 256 -c source/SHA256SUMS   # the same check by hand; paths are relative to the talk folder
```

With those files in place, `./build.sh publish` rebuilds slides, report and abstract (Python 3.13
and LibreOffice needed); see "What is not in this repository" in
[source/README.md](source/README.md).

The `.pptx`, `.docx` and abstract rebuild byte for byte. The two PDFs are LibreOffice exports of
the Office files, and LibreOffice changes the embedded font bytes on every export. A rebuilt PDF
therefore looks the same but hashes differently; `SHA256SUMS` pins the published PDFs.
