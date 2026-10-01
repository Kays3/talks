<style>body{font-size:9.8pt;line-height:1.36;max-width:none} h1{font-size:16.5pt;margin:0 0 4pt} p{margin:5pt 0} table{font-size:8.8pt}</style>

# Reading the Current, version 2: judging Geneformer's virtual gene edits

**Lab progress report, 1 October 2026 · Kaisar Dauyey · Shinji Nakaoka**

**The idea.** Geneformer reads each cell as a list of its genes, most unusual first, and places the cell on an internal map. We teach it to tell a patient's tumour T cells from their normal T cells, then edit a tumour cell's list in the computer (delete a gene, or move it to the top) and measure whether the cell moves toward that patient's normal T cells. This is called in-silico perturbation (ISP). No real cell is touched, and the model always gives an answer.

**Six checks we now apply, each learned from a real mistake** (lab standard ISP-STD-1, 28 September 2026)

| Check | Rule | What taught us |
|---|---|---|
| 1. Write the test down first | Test, direction, threshold, reachable p and the outcome words, fixed and reviewed before any result | In August we read meaning into an ordering we had not planned to test |
| 2. Check the instrument | The model must work on unseen patients; an edit that changes nothing must give zero | The July normal and tumour groups came from different studies (0 of 18 supplied both) |
| 3. Same cells for both edits | Delete and overexpress analysed on identical cells (since 25 September) | Overexpress used 2,424 cells for every gene, delete 202 to 1,131 |
| 4. Beat look-alike genes | Each gene against at least 20 genes detected about as often; ambient-RNA genes flagged | S100A8 and S100A9 moved cells the same way under both edits in 9 of 12 comparisons |
| 5. Beat random genes | Opposite effects of the two edits are not, on their own, evidence | Random genes do it too: rank correlation -0.593 (100 genes), -0.608 (200) |
| 6. Count patients, use fixed words | Patients are the unit; stable in 95% of 10,000 resamplings; never "no effect" | One patient held 74.9% of the SCLC test cells |

**What we can say.** In lung (43 patients) the model separates tumour from normal T cells in unseen patients (balanced accuracy 0.825, all 43 above chance); 13 of 34 testable T-cell genes move cells more than their look-alikes, stably; and the opposed effects of the two edits are generic. In colon (19 patients, new models) the split is learnable too (0.904, 19 of 19). **What we cannot say:** that any gene controls T-cell state; what the classifier reads (T-cell state, ambient RNA or T-cell subset mix); whether the lung models work on new lung patients.

**Running now.** The colon perturbation test (369 genes, 19 patients) started at 02:42 JST on 1 October and should finish on the morning of 2 October. No result is reported here.

**Still to test.** Whether the opposed effects belong to the model or to lung (colon run); transfer to new lung patients (blocked: data not accessible); the same effects under an unrelated goal; cell state versus T-cell subset mix; a readable baseline from published T-cell programs (TCAT, Kotliar et al. 2025); model size (104M vs 316M parameters); positive controls and real gene-editing screens. Together these could become one methods paper, working title "Opposite by default".

*Terms.* **Token:** one gene in a cell's list. **Embedding:** a cell's position on the model's map. **Balanced accuracy:** how often the model is right, counting both groups equally; 0.5 is a coin toss. **Ambient RNA:** genetic material from other cells picked up during sample preparation. **Rank correlation:** from -1 (opposed) through 0 to 1. Every number is sourced in `SOURCES.md`.
