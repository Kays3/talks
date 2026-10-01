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

**Pending.** The colon perturbation run (369 genes, 19 donors) started at 02:42 JST on 1 October; results are expected on 2 October and will be reported only after independent review.

**Bulk RNA-seq (open question, no result).** A bulk profile averages many cell types, so ISP on it mixes cell-type composition with within-cell regulation, and its input lies outside the single-cell pretraining distribution. Options: (A) a pseudo-bulk benchmark built from our own single-cell data and compared with single-cell ISP, with T-cell-only and all-cell versions to separate composition; (B) deconvolution before perturbation; (C) treating a sample as one "cell", with a sample-level reading at most. A is the proposed first test.

**Still to test.** Goal swap; subset re-analysis; an interpretable baseline from T-cell programs (TCAT, Kotliar et al. 2025); model size (104M vs 316M); positive controls and experimental screens; bulk transfer. Possible methods paper, working title "Opposite by default". Every number is sourced in `SOURCES.md`.
