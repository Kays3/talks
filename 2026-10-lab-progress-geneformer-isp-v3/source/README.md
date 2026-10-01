# Evaluating in-silico perturbation with Geneformer, version 3: build package

Talk: "Evaluating in-silico perturbation with Geneformer" (lab progress report, version 3), Kaisar Dauyey.

Everything needed to rebuild the figures and the deck is in this folder; no input data is left out.

- `build_figs.py` draws the PNG figures in `../figures/` from the files in `data/`, without PNG metadata.
- `build_deck.py` writes `../slides.html` and `../speaker-notes.md`. The `.html` and `.pdf` versions of
  the speaker notes and the handout are rendered from their Markdown with pandoc and WeasyPrint.
- `data/` holds six files: the five result files of version 2 (two classifier gates, the colorectal no-op gate
  and the two null-study results) and `pelka_e0_counts.csv`, the per-donor T-cell counts of the E0 feasibility
  check, computed from the public GSE178341 per-cell metadata. `SHA256SUMS` lists their hashes; check them
  from inside `data/` with `shasum -a 256 -c ../SHA256SUMS`. In the two null-study files the free-text
  `about` notes were shortened for publication; every value is unchanged. `../SOURCES.md` gives the original
  file and its hash for each.

Rebuild from the talk folder:

```
python3 source/build_figs.py && python3 source/build_deck.py
weasyprint slides.html slides.pdf   # on macOS: DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```

Requires numpy, scipy and matplotlib; no pandas.
