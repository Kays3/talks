# Sources for every number in "Evaluating in-silico perturbation with Geneformer" (version 3)

Version 3 reuses the numbers of versions 1 and 2 (`../2026-10-lab-progress-geneformer-isp/` and `../2026-10-lab-progress-geneformer-isp-v2/`) and adds figures drawn from two existing results: the external-cohort feasibility count (E0) and the colon classifier gate (E2). It adds no new measurement. Files under `source/data/` are six inputs: the five result files of version 2 (three byte-identical to the result files named below; in the two null-study files the free-text `about` notes were shortened for publication and every value is unchanged) and the E0 per-donor count table (byte-identical, sha256 `3e47f81b0cd2f44d73d47e88650fd4ade809775bcd4f073a3b5dfb5b4086f2e9`). `source/SHA256SUMS` lists the copies' hashes.

Paths: G = Kays3/geneformer-lung-tcell at `origin/main` unless a commit or branch is named; T = this talks repository; R = the lab's internal reports folder; STD = the lab's internal standard `isp-outcome-criteria.md` (ISP-STD-1 v1.1, adopted 2026-09-28); GF = the Geneformer package source, `geneformer/tokenizer.py`. Every row was re-read at source on 2026-10-01.

## Slides 1 to 10: question and method

| Slide | Number or statement | Source |
|---|---|---|
| 4 | The eight steps: cohort rule (at least 100 T cells per tissue), tokenisation, donor-held-out fine-tuning, classifier gate (held-out balanced accuracy >= 0.60) and no-op gate (shift exactly 0), deletion and overexpression, cosine shift toward the donor's own normal centroid, comparison with matched controls and random genes, donor-level call with fixed outcome names | G branch `analysis/e2-pelka-crc-20261001`, `pelka_crc_e2/registration/E2_REGISTRATION.md` (8b11d5d), sections 5.4, 6.1 and 6.2; STD sections A and B |
| 5 | Counts divided by the cell's total (scaled to 10,000) and by each gene's median across the pretraining corpus, then sorted; zero-count genes absent; V2 models read at most 4,096 tokens | GF `tokenize_anndata` (`X_view / n_counts * target_sum`, then `/ norm_factor_vector`), `rank_genes` (sort on non-zero values), `model_input_size` (4,096 for V2); Theodoris et al., Nature 618, 616-624 (2023). Genes and bars in the figure are invented and labelled so |
| 6, 30 | Masked-gene pretraining; about 104 million cells; model sizes 104M and 316M parameters (slide 30) | Theodoris et al. 2023; Geneformer model card on Hugging Face (ctheodoris/Geneformer) |
| 7, 24 | Lung classifier: pooled held-out balanced accuracy 0.8249 (shown 0.825); 43 of 43 donors above 0.5 | G `balanced_donor_luad/phase4_results/classifier_gate.json`; copy `source/data/luad_classifier_gate.json` |
| 8 | Score per cell = change in cosine similarity of the CLS embedding to the goal (exact-mean CLS embedding of the donor's own normal pool cells); donor mean over token-positive cells; gene value = median over donors with >= 10 token-positive cells, at least 10 donors | `E2_REGISTRATION.md` (8b11d5d) section 5.4 step 3 and section 6.2 |
| 7, 9 | Two cell clouds, the boundary and the edit arrows | Schematics labelled "Schematic, not data" (`source/build_figs.py`) |
| 10 | July screen: 21,000 T cells, 104M model, 2,937,776 held-out cell-gene deletions | G `README.md` lines 34-36 and 50-53 |
| 10 | 28 July audit: the LUAD/LUSC work could not by itself support the abstract's SCLC claims (paraphrased) | G `sclc_validation/audit/SCLC_DATA_FEASIBILITY_AUDIT.md` lines 3-10 |
| 10 | 50 genes; four passed in both directions in 3 of 3 SCLC test donors (TIM-3/HAVCR2, TIGIT, CTLA-4, IL7R) | T `2026-08-jsdp-sclc-tcell-talk/slides.pdf` |

## Slides 11 to 14: lessons

| Slide | Number or statement | Source |
|---|---|---|
| 11, 29 | S100A8 and S100A9 among the most significant genes (S100A8 12th and S100A9 16th of 784 gated rows in luad_to_sclc); same direction under both edits in 9 of 12 rows; 55 of the top 120 rows ambient-flagged | R `s100a8-s100a9-crossref-20260922.md` lines 92 and 105-150 |
| 11, 29 | 0 of 18 studies supplied both normal and tumour T cells (July classifier) | G `current_workflow/METHODS.md` lines 231-256 |
| 11 | 13 of the 15 July genes not testable in T cells | R `balanced-donor-null-imrad-report-20260930.md`, section 3.2 |
| 12, 29 | One SCLC donor held 74.9% of the SCLC test cells; donor-level p 0.216 (19 vs 22 donors) | G `sclc_validation/immune_axis_test/RESULTS_T6.md` lines 58-70 and 79-81 |
| 13, 18, 29 | Overexpress arm 2,424 SCLC test cells for every gene; delete arm 202 to 1,131; "a qualifier, not a retraction"; runner fixed 22 Sep (66d235b); panel not rerun | R `lung_tcell_talk_imrad_sources_20260925.md` lines 128-157 |
| 13, 29 | Gene-list overexpression inserts into every cell: 14,738 of 15,179 calls | G `balanced_donor_luad/registration/PHASE5_ISP_REGISTRATION.md`, Amendment 3h (b2473ef) |
| 14, 20, 29, 31, 32 | Random genes: Spearman rho -0.5927 (N = 100) and -0.6078 (N = 200), shown -0.593 and -0.608 (-0.59 and -0.61 on slides 31 and 32); one-sided p 9.9999e-06 = 1/100,001, the floor of 100,000 permutations | `phase8_null/a5_primary_result_v2.json` (upstream sha256 a00ccb2f62a7a888386208eb63a2f349d1c2ee8717208f742a563bc508588267) and `phase8_null/n200_combined_result_v2.json` (upstream c9e56026fac99d30a89da91ab557b09e7889717163712242a961d33295a3b847); copies in `source/data/`; the figure asserts that the first 100 genes equal the N = 100 set and that the recomputed rho equals the stored value |

## Slides 15 to 21: criteria

| Slide | Number or statement | Source |
|---|---|---|
| 15 | Six checks in order; outcome names positive, negative, opposite_direction, control_draw_sensitive_open, not_estimable, no_op_failed; adopted 2026-09-28 | STD A6 and sections A and B; `E2_REGISTRATION.md` section 6.2 (status list) |
| 16, 25 | Colon: expected n = 10 testable reference genes; repeated if at least 9 of 10 (8 of 9 if n = 9); one-sided exact binomial | `E2_REGISTRATION.md` (8b11d5d), section 6.3 |
| 16 | First review of that plan not passed: environment stated as unchanged, but pandas went 3.0.5 -> 2.3.3 | internal review of the registration, 2026-09-30; corrected in 8b11d5d |
| 17, 23, 24 | Colon classifier: pooled 0.9042 (shown 0.904); 19 of 19 donors above 0.5; lowest 0.655; no-op largest shift 0.0 | G `pelka_crc_e2/phase4_results/classifier_gate.json` and `noop_gate.json` at 2c104ab; copies `source/data/e2_classifier_gate.json`, `source/data/e2_noop_gate.json` |
| 18 | Constant-count warning sign; replay count checks in every analysis since 25 Sep, including the colon study | STD B2; Amendment 3h (b2473ef); `E2_REGISTRATION.md` section 6.2 |
| 19 | At least 20 matched controls within 0.5 log2 detection and 5 rank-percentile points; fewer than 20: not_estimable; ambient and classifier-anchor genes flagged | STD B1, B4 |
| 19, 20, 24 | 13 of 34 testable panel genes stable against matched controls | R `balanced-donor-null-imrad-report-20260930.md`, section 3.3 and the Abstract |
| 20 | Control genes: rho -0.658 on 308 of 318 | `phase8_null/a5_primary_result_v2.json`, key `validity_check_318_control_genes` |
| 21 | Stable = holds in every leave-one-control-out and in >= 95% of 10,000 bootstrap draws; never "no effect" | STD A6, B5, B8 |
| 21 (notes) | S100 ambient test negative, p = 6/70 and 34/70 | G at 53adee2 `.../results_s100_luad_20260928/RESULT.md` lines 1-8 |
| 11-21 | "Addressed by" and "From" links between lessons and checks | the author's reading of the history above; STD cites the same episodes (B2, B4, B7) |

## Slides 22 to 25: status

| Slide | Number or statement | Source |
|---|---|---|
| 22 | Pelka et al. 2021 (GSE178341): 62 patients, 36 with a normal specimen, 25 with >= 100 CD4/CD8 T cells (author annotation TCD4/TCD8) in both tissues; sorting mix differs within 11 of the 25; 19 when both tissues are restricted to unsorted cells | R `geneformer-e0-feasibility-20261001.md`, Summary and section 2; per-donor table copy `source/data/pelka_e0_counts.csv` (the figure asserts 36 and 25 and that the 19 E2 donors are among the 25) |
| 22 | Figure: counts over all processing types; the 19 E2 donors are the keys of `per_donor_balanced_accuracy` in the E2 gate file; open circles are the other 6 qualifying donors | `source/data/pelka_e0_counts.csv`, `source/data/e2_classifier_gate.json` |
| 22, 30 | Bischoff et al. 2021: data only as a Code Ocean capsule, which refused automated access (HTTP 403); E1 blocked | R `geneformer-e0-feasibility-20261001.md`, section 3 |
| 23 | Registration reviewed and passed before any GPU step | review of `E2_REGISTRATION.md` at 8b11d5d (sha256 of the file adc7548b...), 2026-09-30 |
| 23 | Five new fold classifiers from the base V2-316M weights, LUAD recipe unchanged; sign test p = 1/262,144 = 3.8e-06; per-donor values and MMR markers (MMR from the E0 table: 9 MMRd, 10 MMRp among the 19); C134 lowest at 0.655 with the fewest tumour T cells (137 unsorted); lowest three donors MMRp; no MMR test registered | `e2_classifier_gate.json` (keys `sign_test_p_float`, `per_donor_balanced_accuracy`); `pelka_e0_counts.csv` (column `MMR`); R `geneformer-e2-classifier-gate-20261001.md`, Methods and Results |
| 23 | Perturbation run: 369 genes (100 random, 28 panel, 241 controls), 19 donors, both edits; started 02:42 JST 1 Oct (2026-09-30 17:42:37 UTC); finish expected the morning of 2 Oct; 52 GPU-hour ceiling; no result shown | `E2_REGISTRATION.md` sections 5.4 and 7; deviation D1 at ab66d3a (per-gene cost above the prediction, within the ceiling); `isp_started_utc.txt` |
| 24 | "Not shown" list | R `balanced-donor-null-imrad-report-20260930.md`, section 5; R `geneformer-next-cycle-proposal-20261001.md`, Summary; R `geneformer-alt-dataset-experiment-design-20261001.md`, section 1 |
| 25 | Pre-specified readings of the colon outcomes | `E2_REGISTRATION.md` sections 7 and 10 |

## Slides 26 to 28: bulk RNA-seq (proposal)

| Slide | Number or statement | Source |
|---|---|---|
| 26 | Geneformer pretrained on single-cell rank encodings; zero-count genes absent from the list; V2 input limit 4,096 tokens | Theodoris et al. 2023; GF `tokenizer.py` (as slide 5) |
| 26 | "No bulk ISP result in our work" | search of the lab's internal reports and shared notes on 2026-10-01 for bulk RNA-seq and in-silico perturbation: the only bulk-related items are per-donor pseudo-bulk tables used for differential expression (T6), not ISP |
| 26 | Composition figure | Schematic with invented values, labelled so |
| 27, 28 | Options A to C and the test design | the author's proposal; no study registered, no compute spent |
| 28 | Sample counts: lung 43 donors x 2 tissues = 86, colon 19 x 2 = 38 | donor counts from the two classifier gate files |

## Slides 29 to 33: summary and next

| Slide | Number or statement | Source |
|---|---|---|
| 29 | Criteria table | rows above (slides 11-21) |
| 30 | Goal swap, subset re-analysis, interpretable baseline from T-cell programs (TCAT; Kotliar et al., Nature Methods 22, 1964-1980, 2025); model size; positive controls and experimental screens | R `geneformer-next-cycle-proposal-20261001.md`, sections 4 and 5; STD C2, C4 and D1 |
| 30 | Bulk row | slides 26-28 |
| 31 | Working title, result (rho -0.59 and -0.61; lung, V2-316M, goal = the donor's own normal centroid), argument, hypotheses, figure list | proposal by the author; each figure marked drawable now (teal) or needing an open study (amber) |
| 32 | Summary statements | rows above |
