# Sources for every number in "Evaluating in-silico perturbation with Geneformer" (version 3)

Version 3 reuses the numbers of versions 1 and 2 (`../2026-10-lab-progress-geneformer-isp/` and `../2026-10-lab-progress-geneformer-isp-v2/`) and adds figures drawn from existing results: the external-cohort feasibility count (E0), the colon classifier gate (E2) and the bulk perturbation test against measured knockouts (slides 27-28). It adds no new measurement of its own. Files under `source/data/` are ten inputs: the five result files of version 2 (three byte-identical to the result files named below; in the two null-study files the free-text `about` notes were shortened for publication and every value is unchanged) the E0 per-donor count table (byte-identical, sha256 `3e47f81b0cd2f44d73d47e88650fd4ade809775bcd4f073a3b5dfb5b4086f2e9`) and four bulk-test tables (see slides 26 to 28). `source/SHA256SUMS` lists the copies' hashes.

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
| 23 | Perturbation run: 369 genes (100 random, 28 panel, 241 controls), 19 donors, both edits; started 02:42 JST 1 Oct (2026-09-30 17:42:37 UTC); finished 10:20 JST 2 Oct; 32.6 of 52 GPU-hours (see E2 results below) | `E2_REGISTRATION.md` sections 5.4 and 7; deviation D1 at ab66d3a (per-gene cost above the prediction, within the ceiling); `isp_started_utc.txt` |
| 24 | "Not shown" list | R `balanced-donor-null-imrad-report-20260930.md`, section 5; R `geneformer-next-cycle-proposal-20261001.md`, Summary; R `geneformer-alt-dataset-experiment-design-20261001.md`, section 1 |
| 25 | Pre-specified readings of the colon outcomes | `E2_REGISTRATION.md` sections 7 and 10 |

## Slides 26 to 28: bulk RNA-seq

BI = Kays3/Geneformer_TE `main` at merge commit `6b637d8a409f5fffc4cf5998406b5851251acaf1` (pull request #1; results committed in `e36f9fc`), folder `docs/runs/2026-10-02_human_tcell_bulk_isp/` (pre-registration committed at `0714626` before the run; amendments A1 `08010fe`, A2 `56bc282`). The two tables were checked byte-for-byte against `6b637d8`. Two of its tables are copied byte-identical into `source/data/`: `tables/09_per_ko.tsv` as `bulk_isp_per_ko.tsv` (sha256 `81bc3c18...`) and `tables/09_tests.json` as `bulk_isp_tests.json` (sha256 `5d2882f4...`).

BW = the Weinstock replication, Kays3/Geneformer_TE `main` at merge commit `460da8a` (pull request #2, head `32bf745`; pre-registration `1ff9c5c`, amendment R1 `188a46b`, results `6d704db`), folder `docs/runs/2026-10-02_human_tcell_weinstock_bulk_isp/`. Its `tables/09_per_ko.tsv` and `tables/09_tests.json` are copied byte-identical as `bulk_isp_weinstock_per_ko.tsv` (sha256 `86eca492...`) and `bulk_isp_weinstock_tests.json` (sha256 `1b716648...`), checked against `460da8a` and `32bf745`; the Freimer tables are unchanged at `460da8a`. Lab reports: `geneformer-te-bulk-isp-weinstock-20261002.md` and `geneformer-te-bulk-isp-combined-reading-20261002.md`.

| Slide | Number or statement | Source |
|---|---|---|
| 26 | Geneformer's input is a single-cell rank encoding with at most 4,096 tokens (V2), so it cannot take a bulk profile | Theodoris et al. 2023; GF `tokenizer.py` (as slide 5) |
| 26 | Composition figure | Schematic with invented values, labelled so |
| 27 | Model: CellOracle-style linear network, ridge regression on TF-to-target edges of the CellOracle hg38 promoter base GRN, restricted to promoters overlapping a Freimer ATAC peak; leave-one-knockout-out; knockout clamped low and propagated | BI `PREREGISTRATION.md`; lab report `geneformer-te-bulk-isp-celloracle-tcell-20261002.md`, Methods; Kamimoto et al., Nature 614, 742-751 (2023) |
| 27 | Ground truth (first set): Freimer et al. 2022, 24 Cas9 knockouts in CD4+ T cells, 3 donors, AAVS1 controls; 17 are TFs in the base network (PTEN, MBD2 and CBFB only through motif annotation, not classical sequence-specific TFs), 7 not representable | GEO GSE171677 and GSE171736; `bulk_isp_tests.json` keys `n_scored` (17), `n_not_representable` (7) |
| 27 | P1 median rho 0.083, p = 0.012; P2 median sign agreement 0.545, p = 0.013; P3 median difference from shuffled GRN +0.039, p = 0.19 (fail); P4 4 of 17 beat random TFs, p = 0.009; reading `RECOVERED_NONSPECIFIC` | `bulk_isp_tests.json` keys `P1_*` to `P4_*`, `pass`, `reading` |
| 27 | Second set: Weinstock et al. 2024 (GEO GSE271788), 60 Cas9 knockouts in CD4+ T cells, 3 donors, 35 AAVS1 controls, none among the Freimer genes; 38 in the base network and scored, 22 not representable. P1 0.033, p = 0.21; P2 0.517, p = 0.38; P3 +0.035, p = 0.14; P4 3 of 38, p = 0.30; all fail; reading `NOT_RECOVERED`; by the rule in its pre-registration (section 5), the Freimer reading does not replicate | `bulk_isp_weinstock_tests.json` keys `n_scored`, `n_not_representable`, `P1_*` to `P4_*`, `reading`; BW `PREREGISTRATION.md` section 5; Weinstock report, Summary |
| 27 | Figure: per-knockout rho of the model, median of 50 shuffled GRNs, median of random TFs of the same out-degree quintile, and the co-expression baseline; asterisks mark knockouts with random-TF p <= 0.05 (ETS1, HIVEP2, IRF1, IRF4) | `bulk_isp_per_ko.tsv` columns `rho_resp`, `rho_shuf_median`, `rho_random_median`, `rho_baseline`, `p_random_tf`; the script asserts 17 scored knockouts and that the median of `rho_resp` equals `P1_rho_resp_median` |
| 28 | As a group, no gain over shuffled networks (P3 failed in both sets); individually 0 of 17 (Freimer) and 3 of 38 (Weinstock: NFAT5, NFE2L2, ZNF329) beat their 50 shuffles at empirical p <= 0.05, about the 1.9 expected by chance in 38 | `bulk_isp_tests.json` and `bulk_isp_weinstock_tests.json` keys `P3_*`; column `p_shuf` of both per-knockout tables; combined-reading report (corrected wording) |
| 28 | Co-expression baseline: median rho 0.21 in Freimer (model vs baseline paired median difference 0.002, two-sided p = 0.85); 0.015 in Weinstock | `bulk_isp_tests.json` and `bulk_isp_weinstock_tests.json`, keys `baseline_rho_resp_median`, `model_minus_baseline_median`, `model_vs_baseline_wilcoxon_two_sided_p` |
| 28 | Controls-only network: median rho -0.013 (Freimer, one-sided p = 0.76) and 0.008 (Weinstock); no agreement above chance in either | column `S2_controls_only_rho` of `bulk_isp_per_ko.tsv` (median -0.0126) and `bulk_isp_weinstock_per_ko.tsv` (median 0.0084); lab reports, Results |
| 28 | Predicted shifts 55 to 85 times too small: median ratio of predicted to measured shift 0.018 (Freimer) and 0.012 (Weinstock) | combined-reading report, "What the pair shows"; Freimer report, "Magnitude and robustness" |
| 28 | TE arm `NOT_TESTABLE`: no deposited multi-mapping-aware TE count table from human T cells or blood with perturbations was found in a bounded search (GEO metadata and the web; ArrayExpress, Zenodo, figshare and paper supplements not searched); re-alignment ruled out | BI amendment A2 (`56bc282`) and `te/SEARCH.md`; lab report, "TE arm" |
| 28 | Why the sets may differ (untested): median responsive genes per knockout 394 (Freimer) and 70.5 (Weinstock). Uncontrolled differences: harvest 5 days after electroporation (Freimer) versus 8 days after isolation and activation (Weinstock); UMI deduplication named by Freimer, not in Weinstock's GEO record; counting pipeline; unknown donor overlap | column `n_resp` of both per-knockout tables (medians 394 and 70.5); Weinstock report, Methods ("Data"); combined-reading report, "Why the two sets may differ" |
| 28 | A revisit would need a composition covariate registered in advance, or single-cell or sorted data | combined-reading report, "Consequence" |

## Slides 29 to 33: summary and next

| Slide | Number or statement | Source |
|---|---|---|
| 29 | Criteria table | rows above (slides 11-21) |
| 30 | Goal swap, subset re-analysis, interpretable baseline from T-cell programs (TCAT; Kotliar et al., Nature Methods 22, 1964-1980, 2025); model size; positive controls and experimental screens | R `geneformer-next-cycle-proposal-20261001.md`, sections 4 and 5; STD C2, C4 and D1 |
| 30 | Bulk row: not supported; two registered tests, 55 knockouts (17 + 38) | slides 27-28 |
| 31 | Working title, result (rho -0.59 and -0.61; lung, V2-316M, goal = the donor's own normal centroid), argument, hypotheses, bulk line (two tests, 55 knockouts, not supported), figure list | proposal by the author; bulk line from slides 27-28; each figure marked drawable now (teal) or needing an open study (amber) |
| 32 | Summary statements | rows above |

## E2 results (added 2 October 2026)

E2R = Kays3/geneformer-lung-tcell `main`, merge `4cce44a` of PR #45 (branch `analysis/e2-pelka-crc-20261001`; results commit `b7369cb`, files unchanged at the merge, checked by sha256), folder `pelka_crc_e2/results/`, and the internal E2 results report `geneformer-e2-pelka-20261002.md` (passed review 2 October 2026, 12:39 JST [03:39 UTC]). Upstream sha256: `h2b_null_result.json` 48d036a8db55b1f9921f4f1250b4b57188c6c036e6f7a681db6d7faf6ad3461e; `h2c_result.json` 6e687f91059f52e1635ab27378af23e291bba0e21986cbff04f3dfa5ad4a35ab; `panel_b/outcome_rows.json` 79a8cb08979fbef8a501665ba54b109e8110bf190614e4f46da13c7605d2caa8.

| Slide | Number or statement | Source |
|---|---|---|
| 24 | Random genes (H2b, primary): Spearman ρ −0.24522, shown −0.245 (−0.25 on the lay slide); one-sided permutation p 0.006740 (100,000 permutations), shown 0.0067; 100 of 100 estimable; leave-one-out 100 of 100 pass; bootstrap stable fraction 0.7791 of 10,000, shown 78%, against the registered 0.95; status `control_draw_sensitive_open` | E2R `h2b_null_result.json` key `primary`; registration (`E2_REGISTRATION.md`, 8b11d5d) sections 6.2 and 7 |
| 24 | Control genes also negative (ρ −0.531, 231 of 241 estimable), sign-only check; populations differ, magnitudes not compared | E2R `h2b_null_result.json` key `validity_check_318_control_genes` (the key name and its note carry LUAD labels; E2 has 241 unique controls, `design.json` strata) |
| 24 | Lung reference genes (H2c): 10 testable of 13; 3 keep their lung deletion sign (GZMA, LCK, CD247); exact one-sided binomial p 121/128 = 0.95; bar 9 of 10; reading `pattern_not_replicated`; 7 or more of 10 opposite by chance: 176/1024 = 0.17 | E2R `h2c_result.json` keys `n_tested`, `del_agree`, `p_exact`, `reading`, `per_gene`; report, Discussion |
| 24 | Panel genes in colon: 1 of 28 dose-concordant (PRF1 `T_CELL_SIGNAL_TOWARD`, `COHERENT`); PRF1 `OPEN` in lung | E2R `panel_b/outcome_rows.json` (status counts: 1 TOWARD, 1 DELETION_ONLY, 26 OPEN, 4 NOT_ESTIMABLE_CONTROLS, 7 NOT_RUN); `h2c_result.json` key `descriptive.status_table` |
| 24 | Run: 369 genes × 19 donors × 2 operations = 14,022 calls; finished 2026-10-02 01:20:55 UTC = 10:20 JST; 110,083 GPU-s ISP + 7,180 s preparation = 32.6 GPU-h of the 52 authorised | E2R `isp_compute.txt`, `isp_finished_utc.txt` |
| 24 | Lung against colon deletion medians over 27 shared panel genes: Spearman ρ −0.288, shown −0.29, descriptive | E2R `h2c_result.json` key `descriptive.del_median_spearman_luad_vs_e2` |
| 24 | Effects a few thousandths of cosine similarity; the lung caution and the closing sentence of the notes | report, Discussion; coordinator wording file `e2-slide-wording-v4-20261002.md` |
| 24 | A colon–lung difference is not attributable to tissue alone (study, dissociation, chemistry, annotation, null-gene population, fold models; 19 against 43 donors); new fold models, so the lung models were not tested | registration section 10; report, Discussion |
| 25, 30, 31, 32 | Summary, open-question and closing statements on the colon study | rows above |
| 24 | Figure `e2_results.png`: top, deletion against overexpression medians of the 100 null genes (×10⁻³); bottom, control-adjusted colon deletion median with exact 95% CI for the 10 testable lung reference genes, filled where the lung sign is kept | `source/data/e2_h2b_null_result.json` (`about` notes replaced for publication, values unchanged), `e2_h2c_result.json` and `e2_panel_b_outcome_rows.json` (byte-identical); `build_figs.py` `fig_e2_results()` |
