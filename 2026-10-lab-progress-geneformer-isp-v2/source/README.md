# Reading the Current, version 2: build package

Talk: "Reading the Current, version 2: what Geneformer's virtual gene edits can tell us",
Kaisar Dauyey · Shinji Nakaoka.

Everything needed to rebuild the figures and the deck is in this folder; no input data is left out.

- `build_figs.py` draws the PNG figures in `../figures/` from the files in `data/`.
- `build_deck.py` writes `../slides.html` and `../speaker-notes.md`. The `.html` and `.pdf` versions of
  the speaker notes and the handout are rendered from their Markdown with pandoc and WeasyPrint.
- `data/` holds the same five result files as version 1 (two classifier gates, the colorectal no-op gate and
  the two null-study results). `SHA256SUMS` lists their hashes; check them from inside `data/`
  with `shasum -a 256 -c ../SHA256SUMS`. In the two null-study files the free-text `about` notes
  were shortened for publication; every value is unchanged. `../SOURCES.md` gives the original
  file and its hash for each.

Rebuild from the talk folder:

```
python3 source/build_figs.py && python3 source/build_deck.py
weasyprint slides.html slides.pdf   # on macOS: DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```
