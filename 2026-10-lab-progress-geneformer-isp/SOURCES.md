# Sources for every number in "Reading the Current"

Each figure in the slides, notes and handout is traced below. Files under `source/data/` are copies of the result files named here. Three of them are byte-identical; in the two null-study files the free-text `about` notes were replaced by a one-line description and every value is unchanged. The upstream sha256 is given in the table and the sha256 of each copy in `source/SHA256SUMS`.

| Number on a slide | Value | Source |
|---|---|---|
| Null study, N=100 | Spearman rho -0.5927 (shown -0.593); one-sided p 9.9999e-06 (floor of 100,000 permutations); leave-one-out 100/100; bootstrap 1.0 of 10,000 | `phase8_null/a5_primary_result_v2.json`, sha256 a00ccb2f62a7a888386208eb63a2f349d1c2ee8717208f742a563bc508588267 (lab compute server; IMRaD report row P23, commit 2fe4e31) |
| Null study, N=200 | rho -0.6078 (shown -0.608); p at the same floor; leave-one-out 200/200; bootstrap 1.0; headline "positive, confirmed at N=200" | `phase8_null/n200_combined_result_v2.json`, sha256 c9e56026fac99d30a89da91ab557b09e7889717163712242a961d33295a3b847 (row P24) |
| Validity check | rho -0.658 on 308 of 318 control genes; same sign as -0.62 (by sign only) | same file, `validity_check_318_control_genes`; -0.62 from `RESULTS.md` section 4 (row P22) |
| Null scatter (slide 17) | ranks of the 200 genes' deletion and overexpression medians; the first 100 equal the N=100 set (asserted), and Spearman recomputed from the plotted arrays equals the stored rho | `source/build_figs.py` on the two files above |
| Lung classifier gate | pooled balanced accuracy 0.8249 (0.825); 43/43 donors above chance; donors 0.55 to 0.985, median 0.85; folds 0.784 to 0.869 | `balanced_donor_luad/phase4_results/classifier_gate.json` on `origin/main` of Kays3/geneformer-lung-tcell |
| Lung panel | 13 of 34 testable genes stable; 318 matched controls | R `balanced-donor-null-imrad-report-20260930.md` (passed internal review), section 3.3 and the Abstract |
| E2 classifier gate | pooled 0.9042 (0.904); 19/19; lowest 0.655; median 0.925; sign test p 1/262,144; folds 0.866 to 0.935 | `pelka_crc_e2/phase4_results/classifier_gate.json` at commit 2c104ab, branch `analysis/e2-pelka-crc-20261001` |
| E2 no-op gate | max |shift| 0.0 in 3 x 100 cells | `pelka_crc_e2/phase4_results/noop_gate.json` at 2c104ab |
| E2 design | 19 unsorted-only donors; models fine-tuned per fold from V2-316M; 369 genes (100 null, 28 panel, 241 controls); 52 GPU-hour ceiling; H2c: exact one-sided binomial, p <= 0.05, n >= 5; at the expected n = 10 this needs >= 9 of 10 (11/1024 = 0.0107; 8 of 10 gives 56/1024 = 0.0547); n is known only after analysis (at n = 9 the bar is 8 of 9) | `pelka_crc_e2/registration/E2_REGISTRATION.md` at 8b11d5d (sha256 adc7548b...), passed internal review 2026-10-01 |
| E2 progress (slide 23, handout) | started 02:42 JST 1 Oct (2026-09-30 17:42:37 UTC); at 12:45 JST [03:45 UTC] 1 Oct: 119 of 369 genes complete in both operations for all 19 donors (100 null genes, the 100th finished 11:09 JST [02:09 UTC], plus 19 of 28 panel genes); ISP GPU time 34,955 s (9.7 h) from the per-unit log (monitor 34,919 s at 03:45:27Z); null genes 29,381.6 s, 293.8 s per gene; registered prediction 12.31 GPU-h for 369 genes (about 120 s per gene); prep 2.0 GPU-h (7,180 s); projected about 29.8 GPU-h ISP, about 31.8 with prep, against the 52 GPU-h ceiling (ISP hard stop 180,020 s); finish about 08:50 JST 2 Oct, plus or minus about an hour (operator projection at about 290 s per gene) | on the compute server, read-only at 12:46 JST: `isp/out/run_log_<host>.jsonl` (per-unit `seconds`), `isp/out/ceiling_monitor.log`, the `*.complete.json` markers, `isp_started_utc.txt`, `controls/isp_run_order.json` (`predicted_isp_gpu_h`); deviation D1 in `E2_REGISTRATION.md` section 12 at ab66d3a (file sha256 d41737f7...) |
| E2 registered readings (slide 23) | H2b statuses positive / negative / opposite_direction / control_draw_sensitive_open and what each means; H2c pattern_holds / pattern_not_replicated / not_testable (n_tested < 5) | `pelka_crc_e2/registration/E2_REGISTRATION.md` at 8b11d5d, sections 6.2, 6.3 and 7 |
| E2 registration review | first review not passed: pandas 3.0.5 -> 2.3.3 since the lung runs | internal review of the registration, 2026-09-30; fixed in 8b11d5d (`provenance/env_freeze_ts1_sorted.txt`) |
| Evaluation rules | matched controls >= 20 within 0.5 log2 and 5 rank-percentile points; stability: every leave-one-control-out and >= 95% of 10,000 bootstraps; status vocabulary; clause B7 | the lab's internal standard `isp-outcome-criteria.md` (ISP-STD-1 v1.1, adopted 2026-09-28) |
| Geneformer background | rank value encoding; masked-gene pretraining; V2 corpus about 104 million cells | Theodoris et al., Nature 618, 616-624 (2023); Geneformer model card on Hugging Face (ctheodoris/Geneformer); token dictionary `token_dictionary_gc104M.pkl` |
| Colorectal data | Pelka et al., Cell 2021, GEO GSE178341 | R `geneformer-e0-feasibility-20261001.md` (E0 feasibility report, passed internal review) |

Illustrative, not data: the gene "sentence" on slide 4 and the embedding sketch on slide 5 (labelled "Schematic, not data").

## Background slides 7-12 (project history)

Paths: G = Kays3/geneformer-lung-tcell at `origin/main` unless a commit is named; T = this talks repository at `main`; R = the lab's internal reports folder (also used in the table above). Each row was re-read at source on 2026-10-01.

| Slide | Number or quote | Source |
|---|---|---|
| 7 | July screen: 21,000 T cells (7,000 per class), 104M model, accuracy 0.7834, 2,937,776 held-out cell-gene deletions | G `README.md` lines 34-36 and 50-53 |
| 7 | "The present LUAD/LUSC exploratory work cannot by itself substantiate the abstract's SCLC claims" (28 July) | G `sclc_validation/audit/SCLC_DATA_FEASIBILITY_AUDIT.md` lines 3-10 |
| 7 | SCLC line: 46,140 T cells, 42 donors; test accuracy 0.919; normal test class 566 cells from 1 donor | G `README.md` lines 76 and 85-94 |
| 8 | 50 genes; four edits replicated in 3/3 SCLC test donors in both directions (delete toward normal, overexpress away; e.g. HAVCR2 +0.0019 / -0.0060) (TIM-3, TIGIT, CTLA-4, IL7R); spatial rho 0.161 and antigen-presentation rho 0.361, 7.95 sigma above null; closing question | T `2026-08-jsdp-sclc-tcell-talk/slides.pdf` (pdftotext) |
| 8 | The 7.95 sigma null: 100 random gene sets matched on mean expression; Antigen presentation / MHC rho_raw 0.3606, null mean -0.0600, null SD 0.0529, null z 7.954 | G at c693898 `sclc_validation/spatial_validation/METHODS_denoised_programs.md` section 3.3 and `denoised_programs_pooled.csv` |
| 8 | "The model pointed to" antigen presentation: the talk's title, "A foundation model points to antigen presentation in SCLC T-cell dysfunction" | T `2026-08-jsdp-sclc-tcell-talk/README.md` line 1 |
| 8 | "The model implies Normal < SCLC < LUAD on the checkpoint axis" | T `2026-08-jsdp-sclc-tcell-poster/poster.pdf` (pdftotext) |
| 9 | T3: SCLC interior angle 61.94 degrees | G `sclc_validation/immune_axis_test/RESULTS_T3.md` lines 38-45 |
| 9 | T4 (program-level overexpression): SCLC->LUAD +0.0873 vs expression-matched null mean +0.0816, one-sided (directional) empirical p 0.4286 | G `.../RESULTS_T4.md` lines 1-40 and 43 |
| 9 | T6: one SCLC donor 74.9% of the SCLC test cells (test-only population, 3 SCLC donors); complete SCLC vs LUAD donor-level p 0.216 (19 vs 22 donors) | G `.../RESULTS_T6.md` lines 58-70 and 79-81 |
| 10 | S100A8 FDR 1.45e-224; S100A8 and S100A9 over 6 comparisons = 12 rows: concordant 0/12, same-sign 9/12; top 120: 55 ambient-flagged, 0 T-cell anchors | R `s100a8-s100a9-crossref-20260922.md` lines 92 and 105-150 (screen table `isp_plausibility_top_candidates.csv` at b99365b) |
| 10 | 0/18 studies with both normal and tumour T cells; LUAD class 27.4% metastasis | G `current_workflow/METHODS.md` lines 231-256 and 308-313 |
| 11 | Panel overexpress_n 2,424 (SCLC) constant vs delete_n 202-1,131; runner fixed 22 Sep (66d235b); panel never rerun; "a qualifier, not a retraction" | R `lung_tcell_talk_imrad_sources_20260925.md` lines 128-157 |
| 11 | Overexpress inserts into every cell, 14,738 of 15,179 calls; "Prior art in this repository, missed." | G `balanced_donor_luad/registration/PHASE5_ISP_REGISTRATION.md`, Amendment 3h (b2473ef) |
| 12 | 43 donors, 100 cells per tissue, 316M; BA 0.825, 43/43; Panel A 13 of 15 untestable; 13 of 34 testable stable; controls rho -0.62 | R `balanced-donor-null-imrad-report-20260930.md`, sections 2.1, 3.2-3.4 |
| 12 | ISP-STD-1 adopted 2026-09-28; S100 run (do ambient-high S100 genes beat their matched controls more than ambient-low ones?) negative, p = 6/70 and 34/70 | `isp-outcome-criteria.md` header; G at 53adee2 `.../results_s100_luad_20260928/RESULT.md` lines 1-8 |

## E2 results (added 2 October 2026)

E2R = Kays3/geneformer-lung-tcell `main`, merge `4cce44a` of PR #45 (branch `analysis/e2-pelka-crc-20261001`; results commit `b7369cb`, files unchanged at the merge, checked by sha256), folder `pelka_crc_e2/results/`, and the internal E2 results report `geneformer-e2-pelka-20261002.md` (passed review 2 October 2026, 12:39 JST [03:39 UTC]). Upstream sha256: `h2b_null_result.json` 48d036a8db55b1f9921f4f1250b4b57188c6c036e6f7a681db6d7faf6ad3461e; `h2c_result.json` 6e687f91059f52e1635ab27378af23e291bba0e21986cbff04f3dfa5ad4a35ab; `panel_b/outcome_rows.json` 79a8cb08979fbef8a501665ba54b109e8110bf190614e4f46da13c7605d2caa8.

| Slide | Number or statement | Source |
|---|---|---|
| 23 | Random genes (H2b, primary): Spearman ρ −0.24522, shown −0.245 (−0.25 on the lay slide); one-sided permutation p 0.006740 (100,000 permutations), shown 0.0067; 100 of 100 estimable; leave-one-out 100 of 100 pass; bootstrap stable fraction 0.7791 of 10,000, shown 78%, against the registered 0.95; status `control_draw_sensitive_open` | E2R `h2b_null_result.json` key `primary`; registration (`E2_REGISTRATION.md`, 8b11d5d) sections 6.2 and 7 |
| 23 | Control genes also negative (ρ −0.531, 231 of 241 estimable), sign-only check; populations differ, magnitudes not compared | E2R `h2b_null_result.json` key `validity_check_318_control_genes` (the key name and its note carry LUAD labels; E2 has 241 unique controls, `design.json` strata) |
| 23 | Lung reference genes (H2c): 10 testable of 13; 3 keep their lung deletion sign (GZMA, LCK, CD247); exact one-sided binomial p 121/128 = 0.95; bar 9 of 10; reading `pattern_not_replicated`; 7 or more of 10 opposite by chance: 176/1024 = 0.17 | E2R `h2c_result.json` keys `n_tested`, `del_agree`, `p_exact`, `reading`, `per_gene`; report, Discussion |
| 23 | Panel genes in colon: 1 of 28 dose-concordant (PRF1 `T_CELL_SIGNAL_TOWARD`, `COHERENT`); PRF1 `OPEN` in lung | E2R `panel_b/outcome_rows.json` (status counts: 1 TOWARD, 1 DELETION_ONLY, 26 OPEN, 4 NOT_ESTIMABLE_CONTROLS, 7 NOT_RUN); `h2c_result.json` key `descriptive.status_table` |
| 23 | Run: 369 genes × 19 donors × 2 operations = 14,022 calls; finished 2026-10-02 01:20:55 UTC = 10:20 JST; 110,083 GPU-s ISP + 7,180 s preparation = 32.6 GPU-h of the 52 authorised | E2R `isp_compute.txt`, `isp_finished_utc.txt` |
| 23 | A colon–lung difference is not attributable to tissue alone (study, dissociation, chemistry, annotation, null-gene population, fold models; 19 against 43 donors); new fold models, so the lung models were not tested | registration section 10; report, Discussion |
| 25, 28 | Summary, open-question and closing statements on the colon study | rows above |
