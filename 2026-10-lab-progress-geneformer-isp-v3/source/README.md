# Evaluating in-silico perturbation with Geneformer, version 3: build package

Talk: "Evaluating in-silico perturbation with Geneformer" (lab progress report, version 3), Kaisar Dauyey.

Everything needed to rebuild the figures and the deck is in this folder; no input data is left out.

- `build_figs.py` draws the PNG figures in `../figures/` from the files in `data/`, without PNG metadata.
- `build_deck.py` writes `../slides.html` and `../speaker-notes.md`. The `.html` and `.pdf` versions of
  the speaker notes and the handout are rendered from their Markdown with pandoc and WeasyPrint.
- `data/` holds ten files: the five result files of version 2 (two classifier gates, the colorectal no-op gate
  and the two null-study results) and `pelka_e0_counts.csv`, the per-donor T-cell counts of the E0 feasibility
  check, computed from the public GSE178341 per-cell metadata; and `bulk_isp_per_ko.tsv` and `bulk_isp_tests.json`,
  the per-knockout and test tables of the bulk perturbation study (Kays3/Geneformer_TE `main`, merge commit `6b637d8`; results commit `e36f9fc`); and `bulk_isp_weinstock_per_ko.tsv` and `bulk_isp_weinstock_tests.json`, the same tables for the Weinstock replication (merge commit `460da8a`). and three `e2_*` result files of the colon study (Kays3/geneformer-lung-tcell `main`, merge `4cce44a`, results `b7369cb`: the random-gene result, with its `about` notes replaced for publication and values unchanged, the lung-reference-gene result and the Panel B outcome rows). `SHA256SUMS` lists their hashes; check them
  from inside `data/` with `shasum -a 256 -c ../SHA256SUMS`. In the two null-study files the free-text
  `about` notes were shortened for publication; every value is unchanged. `../SOURCES.md` gives the original
  file and its hash for each.

Rebuild from the talk folder:

```
python3 source/build_figs.py && python3 source/build_deck.py
weasyprint slides.html slides.pdf   # on macOS: DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```

Requires numpy, scipy and matplotlib; no pandas.
