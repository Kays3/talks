<style>body{font-size:9.6pt;line-height:1.36;max-width:none} h1{font-size:17pt;margin:0 0 4pt} p{margin:5pt 0} table{font-size:8.6pt}</style>

# Reading the Current: a one-page guide to judging an in-silico perturbation

**Lab progress report, 1 October 2026 · Kaisar Dauyey · Shinji Nakaoka**

**The idea in one line.** Geneformer draws a chart of cell states. An in-silico perturbation (ISP) nudges one cell by deleting or overexpressing a gene token, and we measure whether it moves toward a goal (the centre of the same donor's normal-tissue T cells). The model always answers, so we judge every answer against six rules from our standard, ISP-STD-1.

| Rule | In one sentence |
|---|---|
| 1. File the plan first | Register the test, direction, alpha, smallest attainable p, controls and wording before any output; an independent reviewer signs off on file hashes. |
| 2. Check the compass | Classifier gate: held-out balanced accuracy >= 0.60 and an exact two-sided sign test over donors with p <= 0.05, or the study stops. |
| 3. Anchor test | No-op gate: two independent passes with no edit must give a shift of exactly 0, or within measured noise. |
| 4. Same-build boats | >= 20 matched control genes per gene (0.5 log2 detection, 5 rank-percentile points); donors are the unit; results must be stable. |
| 5. Measure the current | Run the pipeline on random genes: the default behaviour any claimed effect must exceed. |
| 6. Fixed log words | positive, negative, opposite_direction, not_estimable, control_draw_sensitive_open, no_op_failed, not_run_by_design, stopped_not_analysed. Never "no effect". |

**How we got here.** In July a Geneformer screen and an SCLC abstract started the work; by September our own checks had shown an exhaustion shift no bigger than random genes give (p 0.4286), top hits behaving like ambient RNA, a study-confounded "normal" class and two faults in our perturbation code. Each rule below answers one of those moments.

**What we found.** Lung (43 donors): classifier balanced accuracy 0.825, all 43 donors above chance. Random genes showed a deletion/overexpression anti-correlation, Spearman rho = -0.593 (N = 100) and -0.608 (N = 200), one-sided p at the permutation floor (<= 1e-5). Opposite signs under deletion and overexpression are therefore not evidence of specificity. Colorectal (Pelka et al. 2021, 19 donors, new models fine-tuned per fold): balanced accuracy 0.904, 19 of 19 donors above chance. Colorectal perturbation screen (finished 10:20 JST, 2 October; reviewed): random genes ρ = −0.245 (p = 0.0067), same direction as lung but significant in only 78% of resamples (bar 95%), so `control_draw_sensitive_open`; 3 of 10 lung reference genes kept their direction (bar 9), `pattern_not_replicated`. Neither difference is attributable to tissue alone.

**What ISP cannot show.** Cause; whether the classifier reads T-cell state, ambient RNA or CD4:CD8 mix; accuracy against an experimental screen (none matched yet).

**Ways to join.** Re-derive a gate from its JSON file (an afternoon) · compute a test's smallest attainable p (an afternoon) · propose positive-control genes (a week) · find a T-cell CRISPR or Perturb-seq screen for ground truth (a week) · test whether rank encoding alone makes the anti-correlation (2-4 weeks) · open the independent lung cohort's Code Ocean capsule (an hour).

*Glossary.* **Token:** one gene in a cell's ranked list. **Embedding:** the model's coordinates for a cell. **Cosine shift:** change in similarity to the goal; positive means closer to normal. **Fine-tuning:** further training on one labelled task. **Balanced accuracy:** mean of true-positive and true-negative rates; 0.5 is chance. **Null control:** the same pipeline on random genes. **Permutation floor:** the smallest p a permutation test can report, 1/(permutations + 1). Every number is sourced in `SOURCES.md`.
