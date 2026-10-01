# Sources for every number in "Reading the Current, version 2"

Version 2 uses the numbers of version 1 (`../2026-10-lab-progress-geneformer-isp/`, whose `SOURCES.md` holds the same rows in more detail) and adds no new measurement. Files under `source/data/` are the same five copies used in version 1: three are byte-identical to the result files named below; in the two null-study files the free-text `about` notes were shortened for publication and every value is unchanged. `source/SHA256SUMS` lists the copies' hashes.

Paths: G = Kays3/geneformer-lung-tcell at `origin/main` unless a commit is named; T = this talks repository; R = the lab's internal reports folder; STD = the lab's internal standard `isp-outcome-criteria.md` (ISP-STD-1 v1.1, adopted 2026-09-28). Every row was re-read at source on 2026-10-01.

## Slides 1 to 8: question, model, editing a cell, first results

| Slide | Number or statement | Source |
|---|---|---|
| 4, 5, 23 | Rank-value encoding (each gene scaled by its usual level, then sorted); masked-gene pretraining; V2 corpus about 104 million cells; model sizes 104M and 316M parameters (slide 23) | Theodoris et al., Nature 618, 616-624 (2023); Geneformer model card on Hugging Face (ctheodoris/Geneformer); token dictionary `token_dictionary_gc104M.pkl` |
| 4, 5, 6, 7 | Gene bars, the token row, the two cell clouds and the edit arrows | Schematics, labelled "Schematic, not data" or "Illustration, not data" (`source/build_figs.py`) |
| 6, 15, 20, 22, 23 | Lung classifier: pooled balanced accuracy 0.8249 (shown 82.5%); 43 of 43 donors above 0.5 | G `balanced_donor_luad/phase4_results/classifier_gate.json`; copy `source/data/luad_classifier_gate.json` |
| 8 | July screen: 21,000 T cells, 104M model, 2,937,776 held-out cell-gene deletions | G `README.md` lines 34-36 and 50-53 |
| 8 | "The present LUAD/LUSC exploratory work cannot by itself substantiate the abstract's SCLC claims" (28 July) | G `sclc_validation/audit/SCLC_DATA_FEASIBILITY_AUDIT.md` lines 3-10 |
| 8 | 50 genes; four passed in both directions in 3 of 3 SCLC test donors (TIM-3/HAVCR2, TIGIT, CTLA-4, IL7R), linked to exhaustion or persistence (the talk labels IL7R "persistence") | T `2026-08-jsdp-sclc-tcell-talk/slides.pdf` |

## Slides 9 to 12: how it fooled us

| Slide | Number or statement | Source |
|---|---|---|
| 9, 22 | S100A8 and S100A9 "among our most significant genes" (in luad_to_sclc, S100A8 FDR 1.45e-224, 12th of 784 gated rows; S100A9 16th; crossref section 2b); over 6 comparisons = 12 rows: same direction under delete and overexpress in 9 of 12; top 120 rows: 55 ambient-flagged | R `s100a8-s100a9-crossref-20260922.md` lines 92 and 105-150 |
| 9, 22 | 0 of 18 studies with both normal and tumour T cells (July classifier) | G `current_workflow/METHODS.md` lines 231-256 |
| 9 | 13 of the 15 July genes not testable in T cells (epithelial and blood genes, e.g. keratins) | R `balanced-donor-null-imrad-report-20260930.md`, section 3.2 |
| 10, 22 | One SCLC donor held 74.9% of the SCLC test cells (test-only population; shown with the remaining 25.1%); donor-level p 0.216 (19 vs 22 donors) | G `sclc_validation/immune_axis_test/RESULTS_T6.md` lines 58-70 and 79-81 |
| 11, 16, 22 | Overexpress arm 2,424 SCLC test cells for every gene; delete arm 202 to 1,131; "a qualifier, not a retraction"; runner fixed 22 Sep (66d235b); panel not rerun | R `lung_tcell_talk_imrad_sources_20260925.md` lines 128-157 |
| 11, 22 | Gene-list overexpression inserts into every cell: 14,738 of 15,179 calls | G `balanced_donor_luad/registration/PHASE5_ISP_REGISTRATION.md`, Amendment 3h (b2473ef) |
| 12, 18, 22, 24 | Random genes: Spearman rho -0.5927 (N = 100) and -0.6078 (N = 200), shown -0.593 and -0.608; one-sided p 9.9999e-06 = 1/100,001, the floor of 100,000 permutations ("at most about once in 100,000") | `phase8_null/a5_primary_result_v2.json` (upstream sha256 a00ccb2f62a7a888386208eb63a2f349d1c2ee8717208f742a563bc508588267) and `phase8_null/n200_combined_result_v2.json` (upstream c9e56026fac99d30a89da91ab557b09e7889717163712242a961d33295a3b847); copies in `source/data/` |
| 12 | Scatter: ranks of the 200 genes' deletion and overexpression medians; the first 100 equal the N = 100 set and the recomputed Spearman equals the stored rho (both asserted) | `source/build_figs.py` on the two files above |

## Slides 13 to 19: the six checks

| Slide | Number or statement | Source |
|---|---|---|
| 13 | Six checks; adopted 2026-09-28 | STD sections A and B (A1-A6, B1-B8) |
| 14 | Colon study: expected n = 10 testable reference genes; pattern repeated if at least 9 of 10 (8 of 9 if n = 9); one-sided exact binomial | G `pelka_crc_e2/registration/E2_REGISTRATION.md` at 8b11d5d, section 6.3 |
| 14 | First review of that plan not passed: the software environment was stated as unchanged, but pandas went 3.0.5 -> 2.3.3 | internal review of the registration, 2026-09-30; corrected in 8b11d5d |
| 15, 20 | Colon classifier: pooled 0.9042 (shown 90.4%); 19 of 19 donors above 0.5; lowest 0.655 | G `pelka_crc_e2/phase4_results/classifier_gate.json` at 2c104ab; copy `source/data/e2_classifier_gate.json` |
| 15 | Colon no-op: largest shift 0.0 | G `pelka_crc_e2/phase4_results/noop_gate.json` at 2c104ab; copy `source/data/e2_noop_gate.json` |
| 16 | Warning sign: one arm's cell count constant across genes while the other varies; panel runner fixed 22 Sep (66d235b); rebuilt study corrected 25 Sep (overexpress positions reconstructed, token-positive cells analysed); replay count checks (`build_ovx_index`) in every analysis since, including the colon study | STD B2; G `balanced_donor_luad/registration/PHASE5_ISP_REGISTRATION.md`, Amendment 3h (b2473ef); `pelka_crc_e2/registration/E2_REGISTRATION.md` section 6.2 |
| 17 | At least 20 matched controls within 0.5 log2 detection and 5 rank-percentile points; fewer than 20: not_estimable, tolerances never widened; ambient and classifier-anchor genes flagged | STD B1, B4 |
| 17, 18, 20 | 13 of 34 testable panel genes stable against matched controls | R `balanced-donor-null-imrad-report-20260930.md`, section 3.3 and the Abstract |
| 18 | Control genes: rho -0.658 on 308 of 318 | `phase8_null/a5_primary_result_v2.json`, key `validity_check_318_control_genes` (copy in `source/data/`) |
| 19 | Stable = meets the criterion in every leave-one-control-out and in >= 95% of 10,000 bootstrap draws; otherwise open (control_draw_sensitive_open); fixed outcome names; never "no effect" | STD A6, B5, B8 |
| 19 (notes) | S100 ambient test negative, p = 6/70 and 34/70 | G at 53adee2 `.../results_s100_luad_20260928/RESULT.md` lines 1-8 |
| 9-19 | "Learned from" and "Answered by" links between traps and checks | the authors' reading of the history above; STD cites the same episodes (B2 unpaired arms, B4 S100A8/S100A9, B7 the delete/overexpress table) |

## Slides 20 to 24: what we know, what is next

| Slide | Number or statement | Source |
|---|---|---|
| 20 | "Not shown" list: no causal role; classifier may read T-cell state, ambient RNA or T-cell subset mix; lung transfer untested | R `balanced-donor-null-imrad-report-20260930.md`, section 5 (ambient RNA differs between tissues within a donor); R `geneformer-next-cycle-proposal-20261001.md`, Summary (what the classifier reads; panel genes outside the control spread are subset markers); R `geneformer-alt-dataset-experiment-design-20261001.md`, section 1 (transfer untested) |
| 21 | Colon run: 369 genes (100 random, 28 panel, 241 controls), 19 donors, both edits; started 02:42 JST 1 Oct; finish expected the morning of 2 Oct; 52 GPU-hour ceiling; no result shown | G `pelka_crc_e2/registration/E2_REGISTRATION.md` at 8b11d5d (sections 5.4, 6.2, 6.3, 7) and deviation D1 at ab66d3a; run start from `isp_started_utc.txt` (2026-09-30 17:42:37 UTC) |
| 21 | What each answer would mean (opposed in colon: more likely model and design; not opposed: tissue cannot be blamed alone) | `E2_REGISTRATION.md` section 7 and section 10 |
| 23 | E1 blocked: the one independent lung candidate (Bischoff et al. 2021) is a Code Ocean capsule that refused automated access | R `geneformer-e0-feasibility-20261001.md`, Summary |
| 23 | Goal swap, subset re-analysis, readable baseline from T-cell programs (TCAT; Kotliar et al., Nature Methods 22, 1964-1980, 2025) | R `geneformer-next-cycle-proposal-20261001.md`, sections 4 (WP1, WP2, WP3) and 5 |
| 23 | Model size 104M vs 316M; positive controls; ground truth from experimental screens | STD C2, C4 and D1; R `balanced-donor-null-imrad-report-20260930.md`, section 5 (no 104M arm was run in the lung study) |
| 24 | Result (rank correlation -0.59 and -0.61, rounded from -0.5927 and -0.6078; lung, V2-316M, goal = the donor's own normal centroid), the argument drawn from it, the hypothesis, figure list | proposal by the authors; each figure marked as drawable now (teal) or needing an open study (amber) |
