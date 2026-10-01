# Reading the Current, version 2: what Geneformer's virtual gene edits can tell us

Lab progress report, 1 October 2026. Kaisar Dauyey · Shinji Nakaoka (Laboratory of Mathematical Biology, Hokkaido University, Japan). About 26 minutes on 26 slides, then 5 to 10 minutes of discussion.

Version 2 of `../2026-10-lab-progress-geneformer-isp/` (version 1 is unchanged). It is written for students and professors together: one point per slide, stated in the title; a figure on most slides; a progress bar; one colour per verdict (teal passed, coral failed, amber not yet known); one icon for each of the six checks; plain words, with the remaining terms in a short glossary. It adds two summary slides (the evaluation criteria we found, and what we still need to test) and the outline of a possible paper. It adds no new measurement; the colon perturbation run is shown as running, with no result.

| File | What it is |
|---|---|
| `slides.html` | The deck, self-contained. Arrow keys or click to move; N shows the speaker notes. |
| `slides.pdf` | The same deck, one slide per page, with "Page N of M" at the bottom. |
| `speaker-notes.md` / `.html` / `.pdf` | The notes for each slide, with timings. |
| `handout.md` / `.html` / `.pdf` | A one-page summary: the idea, the six checks, what we can and cannot say, what is next. |
| `SOURCES.md` | The source file, commit or hash for every number. |
| `figures/` | The figures as PNG files (also embedded in the deck). |
| `source/` | `build_figs.py`, `build_deck.py` and the input data (`data/`, hashes in `SHA256SUMS`). |

Rebuild from this folder: `python3 source/build_figs.py && python3 source/build_deck.py`, then `weasyprint slides.html slides.pdf` (on macOS, set `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`). The notes and handout are rendered from Markdown with pandoc and WeasyPrint.

Data figures (slides 12 and 15) read only the files in `source/data/`. All other figures are schematics and say so on the figure.
