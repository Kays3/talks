# Evaluating in-silico perturbation with Geneformer (lab progress report, version 3)

Lab progress report, 1 October 2026. Kaisar Dauyey (Laboratory of Mathematical Biology, Hokkaido University, Japan). About 34 minutes on 33 slides, then discussion.

Version 3 of `../2026-10-lab-progress-geneformer-isp-v2/` (versions 1 and 2 are unchanged). It keeps the structure of version 2 and changes three things. The language is more formal. Diagrams of the pipeline, the rank-value tokenisation, the perturbation and the evaluation criteria are added, with data figures from the external-cohort feasibility count (E0) and the colon classifier gate (E2). Three slides discuss in-silico perturbation on bulk RNA-seq and report two registered tests of a bulk network model against measured CRISPR knockouts: a weak, non-specific signal in the first that did not replicate in the second. The colon perturbation run is shown as gate passed, results pending.

| File | What it is |
|---|---|
| `slides.html` | The deck, self-contained. Arrow keys or click to move; N shows the speaker notes. |
| `slides.pdf` | The same deck, one slide per page, with "Page N of M" at the bottom. |
| `speaker-notes.md` / `.html` / `.pdf` | The notes for each slide, with timings. |
| `handout.md` / `.html` / `.pdf` | A one-page summary. |
| `SOURCES.md` | The source file, commit or hash for every number. |
| `figures/` | The figures as PNG files without metadata (also embedded in the deck). |
| `source/` | `build_figs.py`, `build_deck.py` and the input data (`data/`, hashes in `SHA256SUMS`). |

Rebuild from this folder: `python3 source/build_figs.py && python3 source/build_deck.py`, then `weasyprint slides.html slides.pdf` (on macOS, set `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`). The notes and handout are rendered from Markdown with pandoc and WeasyPrint.

Data figures (slides 13, 14, 17, 22, 23 and 27) read only the files in `source/data/`. Diagrams (slides 4, 8 and 15) show the analysis as implemented or proposed. The remaining figures are schematics with invented values and say so on the figure.
