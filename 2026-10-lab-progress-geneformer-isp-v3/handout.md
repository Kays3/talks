<style>body{font-size:9.3pt;line-height:1.33;max-width:none} h1{font-size:15.5pt;margin:0 0 4pt} p{margin:4.5pt 0} table{font-size:8.4pt}</style>

# Evaluating in-silico perturbation with Geneformer

**Lab progress report, version 3, 1 October 2026 · Kaisar Dauyey**

**Method.** Geneformer encodes each cell as a list of its genes ranked by expression relative to each gene's median across the pretraining corpus (zero-count genes omitted; at most 4,096 tokens for V2 models). We fine-tune it to separate a donor's tumour-infiltrating T cells from that donor's normal-tissue T cells, with donors held out. In-silico perturbation (ISP) deletes a gene from a tumour cell's list or moves it to the top, and scores the change in cosine similarity of the cell's embedding to the centroid of the same donor's normal T cells. No cell is modified, and the model returns a score for every gene.

**Six criteria, each traced to a documented error** (lab standard ISP-STD-1, 28 September 2026)

| Criterion | Rule | Evidence behind it |
|---|---|---|
| 1. Register first | Test, direction, threshold, reachable p and outcome wording fixed and reviewed before any result | An August ordering was interpreted without a plan |
| 2. Instrument works | Held-out balanced accuracy >= 0.60 with a donor sign test; a no-op edit gives exactly 0 | July tumour and normal groups came from different studies (0 of 18 supplied both) |
| 3. Same cells | Deletion and overexpression analysed on identical cells (since 25 September) | Overexpression on 2,424 cells for every gene, deletion on 202 to 1,131 |
| 4. Matched controls | Each gene against at least 20 genes of similar detection and rank; ambient-RNA genes flagged | S100A8/S100A9 shifted cells the same way under both edits in 9 of 12 comparisons |
| 5. Random genes | Opposed effects of the two edits are not, on their own, evidence | Random genes: Spearman rho -0.593 (100 genes), -0.608 (200) |
| 6. Donors, stability, fixed names | Donor as unit; stable in 95% of 10,000 bootstrap draws; never "no effect" | One donor held 74.9% of the SCLC test cells |

**Supported.** Lung (43 donors): held-out balanced accuracy 0.825, all donors above chance; 13 of 34 testable T-cell genes exceed matched controls, stably; opposed effects are generic. Colon (E2; Pelka et al. 2021, 19 donors with unsorted cells in both tissues, from 25 eligible of 62): registration passed, classifier gate passed (0.904; 19 of 19 donors; lowest 0.655), no-op shift 0.0. **Not shown:** that any gene regulates T-cell state; what the classifier reads (T-cell state, ambient RNA or subset composition); transfer of the lung models to new lung donors (E1 blocked: data not accessible).

**Colon results (after review).** Random genes: ρ = −0.245 (p = 0.0067), same direction as lung but stable in only 78% of resamples (bar 95%): `control_draw_sensitive_open`, open. Lung reference genes: 3 of 10 kept their direction (bar 9): `pattern_not_replicated`. Not attributable to tissue alone.

**Bulk RNA-seq (two tests).** Geneformer cannot take a bulk profile, so we tested a CellOracle-style linear network (transcription-factor-to-target edges from a promoter base network, filtered by matched ATAC-seq) against measured CRISPR knockouts in CD4+ T cells, twice, with the same registered rules. Freimer et al. 2022 (17 knockouts): median rho 0.083 (p = 0.012), 4 of 17 beat random transcription factors, but not a shuffled network: `RECOVERED_NONSPECIFIC`, matched by co-expression alone. Weinstock et al. 2024 (38 new knockouts, same laboratory): no test passed (median rho 0.033, p = 0.21): `NOT_RECOVERED`, so the first reading does not replicate. In both sets, networks fitted on unperturbed controls showed no agreement above chance and predicted shifts were 55 to 85 times too small. The sets differ in harvest timing, deduplication, counting pipeline and possibly donors, uncontrolled; bulk data cannot separate composition from regulation. The transposable-element arm was `NOT_TESTABLE`: a search found no deposited TE count table, and re-alignment was ruled out.

**Still to test.** Goal swap; subset re-analysis; an interpretable baseline from T-cell programs (TCAT, Kotliar et al. 2025); model size (104M vs 316M); positive controls and experimental screens; bulk prediction with a composition covariate or single-cell data. Possible methods paper, working title "Opposite by default". Every number is sourced in `SOURCES.md`.
