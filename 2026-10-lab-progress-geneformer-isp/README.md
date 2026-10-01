# Reading the Current: Geneformer, in-silico perturbation, and how we judge it

Lab progress report, 1 October 2026. Kaisar Dauyey · Shinji Nakaoka (Laboratory of Mathematical Biology, Hokkaido University, Japan). About 25 minutes of talk on 28 slides, including the project's history from July (the first version was about 21 minutes; the history adds about 4, so the slot needs to allow for it), followed by 5 to 10 minutes of discussion. Written for lab members who are new to Geneformer.

**Status: progress report, published 1 October 2026.** Slide 23 gives the dated status of the colorectal (E2) perturbation run at 12:45 JST on 1 October and the readings registered for each outcome; no result is shown. The results are expected on the morning of 2 October; this folder will be updated once they have been reviewed, and [CHANGELOG.md](../CHANGELOG.md) will say what changed.

| File | What it is |
|---|---|
| `slides.html` | The deck, self-contained. Use the arrow keys or click to move; N shows the speaker notes. |
| `slides.pdf` | The same deck, one slide per page, with "Page N of M" at the bottom. |
| `speaker-notes.md` / `.html` / `.pdf` | The notes for each slide, with timings. |
| `handout.md` / `.html` / `.pdf` | A one-page guide to the six evaluation rules, with the key numbers and ways to join. |
| `SOURCES.md` | The source file, commit or hash for every number. |
| `figures/` | The figures as PNG files (they are also embedded in the deck). |
| `source/` | `build_figs.py` and `build_deck.py`, the input data (`data/`, hashes in `SHA256SUMS`). |

Rebuild: `python3 source/build_figs.py && python3 source/build_deck.py`, then `weasyprint slides.html slides.pdf` (on macOS, set `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`).

Data figures read only the files in `source/data/`. The figure on slide 5 and the gene list on slide 4 are schematics and are labelled as such.
