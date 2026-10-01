# Evaluating in-silico perturbation with Geneformer (lab progress report, version 4)

Lab progress report, 2 October 2026. Kaisar Dauyey (Laboratory of Mathematical Biology, Hokkaido University, Japan). About 41 minutes on 39 slides, then discussion.

Version 4 is version 3 (`../2026-10-lab-progress-geneformer-isp-v3/`, unchanged) plus six slides on transposable elements (slides 29 to 34): the Geneformer_TE design, a diagram of its three tracks, two completed fish analyses with data figures (fish TE regulators against random genes; CO2 and the gill TE share), the two tests against measured TE responses that are still running, and what the work does and does not show. Summary 2, the closing summary, the outline, the glossary and the bulk slide's TE-arm line are updated. Slides 35 to 39 are version 3 slides 29 to 33. The colon perturbation run is still shown as gate passed, results pending.

Version 3 was built from `../2026-10-lab-progress-geneformer-isp-v2/` (versions 1 and 2 are unchanged). It keeps the structure of version 2 and changes three things. The language is more formal. Diagrams of the pipeline, the rank-value tokenisation, the perturbation and the evaluation criteria are added, with data figures from the external-cohort feasibility count (E0) and the colon classifier gate (E2). Three slides discuss in-silico perturbation on bulk RNA-seq and report two registered tests of a bulk network model against measured CRISPR knockouts: a weak, non-specific signal in the first that did not replicate in the second. The colon perturbation run is shown as gate passed, results pending.

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

Data figures (slides 13, 14, 17, 22, 23, 27, 31 and 32) read only the files in `source/data/`. Diagrams (slides 4, 8, 15 and 29) show the analysis as implemented or proposed. The remaining figures are schematics with invented values and say so on the figure.
