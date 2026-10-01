# Evaluating in-silico perturbation with Geneformer: speaker notes

Lab progress report, version 4, 2 October 2026. Kaisar Dauyey. 39 slides, about 41 minutes of talk, then 5 to 10 minutes of discussion. Every number is sourced in `SOURCES.md`.

## Slide 1. Evaluating in-silico perturbation with Geneformer (about 0.5 min)

This report covers our work since July on Geneformer and in-silico perturbation in tumour-infiltrating T cells. It is the fourth version of the talk. Compared with the third, it adds a part on our second project, which applies the same perturbation logic to transposable elements, the repeated sequences that cells keep silenced. I introduce each term before I use it, so no prior knowledge of the model is assumed.

## Slide 2. Question: which genes, when perturbed in silico, shift tumour-infiltrating T cells toward the normal-tissue state? (about 0.8 min)

T cells inside a tumour often show a different transcriptional state from T cells in the same donor's normal tissue. Our question is which genes, if perturbed, would move a tumour T cell toward its normal-tissue counterpart. Experimental screens can answer that, but they are slow and expensive, so we use a pretrained model to rank genes first. Most of this talk concerns how far those rankings can be trusted.

## Slide 3. Outline (about 0.7 min)

The talk has seven parts, shown in the bar at the top of each slide. One colour code is used throughout: teal for a check that passed, coral for one that failed, amber for a question without an answer yet. Each of the six evaluation checks has its own icon, which reappears wherever that check applies.

## Slide 4. The analysis runs in eight steps, from a paired cohort to a donor-level call (about 1 min)

This is the whole analysis on one slide. We start from donors who contributed both tumour and normal-tissue T cells, at least one hundred of each. Each cell is converted to a ranked gene list, a classifier is fine-tuned to separate tumour from normal T cells with donors held out, and two gates test the instrument. Only then do we perturb genes, score the shift of each cell toward the donor's normal centroid, compare that shift with control and random genes, and make a call at the donor level. The next slides go through the steps in order. Source: the colon study registration, sections 5 and 6.

## Slide 5. Geneformer encodes each cell as a list of genes ranked by relative expression (about 1.1 min)

Geneformer does not use raw counts. In its tokenizer, each gene's count is divided by the cell's total count and then by that gene's median level across the pretraining corpus, and the genes are sorted on the result. A housekeeping gene that is abundant everywhere moves down; a gene that is unusually high in this cell moves up. Genes with zero counts are not in the list at all, and the V2 models read at most 4,096 tokens. Both points matter later for bulk RNA-seq. The genes and values in the figure are invented. Sources: Theodoris and colleagues, Nature 2023, and the Geneformer tokenizer code.

## Slide 6. The model was pretrained on about 104 million cells by predicting masked genes (about 0.9 min)

Pretraining used a masked-gene task: one gene in a cell's list is hidden and the model predicts it from the others. Across about one hundred million cells, the model learns which genes tend to rank together. What we use downstream is the embedding, the model's vector for each cell; cells with similar ranked lists end up close together. We have used two model sizes, and the larger one underlies the results in this talk unless I say otherwise. Sources: Theodoris and colleagues 2023 and the model card.

## Slide 7. Fine-tuning adds one task: separating a donor's tumour T cells from normal T cells (about 1 min)

Fine-tuning gives the model one additional task: telling a donor's tumour T cells from that donor's normal T cells. Donors are split into folds, and each donor is scored only by a model that never saw any of its cells. In the lung adenocarcinoma study, with 43 donors, pooled held-out balanced accuracy was 0.825, and every donor was above chance. The tumour-to-normal direction this classifier learns is the axis along which perturbations are later scored. Source: the balanced-donor classifier gate file.

## Slide 8. An in-silico perturbation edits the token list and measures how the embedding moves (about 1.2 min)

This is the mechanics of in-silico perturbation, or ISP. Deletion removes gene X from the cell's ranked list. Overexpression moves X to the first position. The edited list is passed through the fine-tuned model to give a new embedding. The score is the change in cosine similarity to the goal, which is the centroid of the same donor's normal T cells. Per gene, we average over the donor's cells that carry the gene, then take the median over donors, and we require at least ten donors with at least ten such cells. Source: the colon study registration, section 6.2.

## Slide 9. The score is a movement in the model's embedding space, not a measured biological effect (about 1 min)

It is worth being explicit about what the score is. A cell that moves toward the normal centroid after a deletion has moved in the model's representation, which reflects what the model learned from co-occurrence of genes. That is a prediction about biology, not a measurement of it. The model also returns a score for every gene, relevant or not. Much of the rest of the talk concerns how to decide which scores carry information.

## Slide 10. The first results, in July and August, appeared encouraging (about 1.1 min)

The project began in July with a screen that deleted each gene in each held-out cell, almost three million deletions in total. Our own audit at the time noted that this work could not on its own support the abstract we had submitted about small-cell lung cancer. In August we presented a 50-gene panel in small-cell lung cancer, in which four genes passed in both directions in every test donor. They were familiar genes from the exhaustion and persistence literature. Over the following weeks we found that part of that agreement came from the method rather than from biology. Sources: the repository README, the 28 July audit and the August talk.

## Slide 11. Lesson 1: the strongest early hits were not T-cell signals (about 1.1 min)

The first lesson came from the top of the July screen. S100A8 and S100A9 were among the most significant genes, yet deletion and overexpression shifted cells in the same direction in most comparisons, which is not what one expects from a gene that drives a state. Many top hits were consistent with ambient RNA. In addition, the July tumour and normal groups came from different studies, so the classifier may have learned study differences. When we rebuilt the study around paired donors, 13 of the 15 July genes, mostly epithelial and blood genes such as keratins, could not be tested in T cells. Checks 2 and 4 address this. Sources: the S100A8/S100A9 cross-reference report, the July methods file and the balanced-donor report.

## Slide 12. Lesson 2: one donor can dominate a cell-level comparison (about 1 min)

Cells from one donor are not independent observations; they share genotype, clinical history and sample handling. When one donor contributes three quarters of a group's cells, a cell-level analysis of that group largely describes that donor. Analysed at the donor level, the apparent difference between small-cell and adenocarcinoma T cells was not significant. Source: RESULTS_T6 in the repository.

## Slide 13. Lesson 3: the two perturbation arms were scored on different cells (about 1 min)

The third lesson concerned our own instrument. In the August panel, deletion and overexpression were scored on different sets of cells, because the perturbation code inserts an overexpressed gene into every cell when it is given a gene list. We documented that default on 22 September and still missed its effect on the rebuilt study until 25 September. The deletion evidence for the August genes stands, so we attached a qualifier rather than retracting them. Sources: the 25 September correction and Amendment 3h of the balanced-donor registration.

## Slide 14. Lesson 4: random genes show the opposed pattern we had treated as evidence (about 1.5 min)

This is the central result of the talk. The August genes passed because deletion and overexpression moved cells in opposite directions. When we applied the identical pipeline to random genes, they showed the same opposition. Each point is one random gene. The rank correlation was minus 0.593 for the registered one hundred genes and minus 0.608 for two hundred. The permutation p-value is at the floor of the test, so we report it as at most about one in one hundred thousand. The random genes were drawn from genes detectable in lung tumour T cells, not from the whole genome. Opposed signs are therefore the baseline, not evidence for a particular gene. Sources: the two null-study result files, hashes a00ccb2f and c9e56026.

## Slide 15. Six criteria, applied in order, stand between a result and a claim (about 1 min)

Each criterion answers one of the lessons. The first three concern the experiment: register the test in advance, confirm the instrument works, and score both arms on the same cells. The last three concern interpretation: beat matched control genes, beat random genes, and count donors with a stability requirement. Every result ends in one of six fixed outcome names, and "no effect" is not one of them. We adopted these as the lab standard on 28 September. The next six slides take them in turn.

## Slide 16. 1 Register the test before any result exists (about 1.1 min)

Registration prevents us from choosing the test after seeing the data. Part of it is checking that the test is able to reach significance: with ten genes and a one-sided exact binomial test, agreement must reach nine of ten. Our own first registration for the colon study did not pass review, because it described the software environment as unchanged when pandas had been downgraded. Source: the colon study registration, section 6.3.

## Slide 17. 2 Confirm the instrument works before reading anything from it (about 1.1 min)

Two gates precede any perturbation. The classifier must work on held-out donors, and an edit that changes nothing must produce no movement. In colon, pooled held-out balanced accuracy was 0.904, every donor was above chance and the lowest was 0.655; the largest no-op shift was exactly zero. Lung and colon are shown together for context only: the colon classifiers were trained anew from the base model, so this is not evidence that the lung models transfer. Sources: the colon classifier and no-op gate files at commit 2c104ab.

## Slide 18. 3 Score both perturbations on exactly the same cells (about 0.8 min)

The rule is that both arms are scored on the same cells. A constant cell count in one arm and a variable count in the other is a reliable sign that they are not, and that was the signature of the August panel. Every analysis since 25 September, including the colon study, re-checks the counts before analysis. Sources: the lab standard, clause B2, and Amendment 3h.

## Slide 19. 4 A gene must shift cells more than matched control genes (about 1.1 min)

A raw shift is hard to interpret on its own, because genes detected in many cells shift them more simply by being present. Each tested gene is therefore compared with at least twenty control genes matched on detection rate and mean rank. A gene is of interest only if it lies outside that spread. If twenty matches cannot be found, the gene is not estimable, and the matching is not loosened to force an answer. In the lung study, 13 of 34 testable T-cell genes met this criterion and were stable. Sources: the lab standard, clauses B1 and B4, and the balanced-donor report.

## Slide 20. 5 Opposed effects of the two perturbations are not, on their own, evidence (about 1 min)

This criterion follows from the random-gene result. If random genes show opposed effects, opposed effects cannot support any particular gene. The control genes of the same study gave the same sign, minus 0.658; we compare such values by sign only, because they are computed on different gene sets. What remains informative is the size of an effect relative to this baseline. That is a narrower claim than the one we made in August. Sources: the null-study result file and the lab standard, clause B7.

## Slide 21. 6 Count donors, require stability, and name every outcome in advance (about 1 min)

The last criterion concerns inference and language. Donors are the unit. A result must be stable to dropping any single control gene and must hold in at least 95 percent of ten thousand bootstrap draws; otherwise it is reported as open. Every outcome receives one of a small set of names fixed before the run. A negative result is reported with its direction, p-value and sample size, because a small study can miss a real effect. Our S100 ambient-RNA test in late September was negative in exactly this sense, at p = 6/70 and 34/70. Sources: the lab standard, clauses A6, B5 and B8, and the S100 result file.

## Slide 22. External cohorts: one colorectal cohort qualified; the independent lung cohort could not be assessed (about 1.2 min)

Before any external study, we counted eligible donors from per-cell metadata alone. In the colorectal data of Pelka and colleagues, 25 donors had at least one hundred CD4 or CD8 T cells in both tumour and normal colon. In eleven of them, tumour and normal specimens differed in magnetic sorting, so the tumour-normal contrast would partly be a processing contrast. Restricting both tissues to unsorted cells left nineteen donors, the cohort used for the colon study. The figure shows counts over all processing types; the open circles are the six donors that dropped out under the unsorted restriction. The independent lung cohort could not be assessed, because its data are distributed only through a capsule that refused automated access. Sources: the E0 feasibility report and its per-donor count table.

## Slide 23. Colon study (E2): registration and classifier gate passed; perturbation results pending (about 1.3 min)

The colon study repeats the lung design on the nineteen-donor cohort. Its registration was reviewed and approved before any GPU work. Five new fold classifiers were fine-tuned from the base model with the lung recipe unchanged. Pooled held-out balanced accuracy was 0.904, every donor was above chance, and the lowest donor, C134, at 0.655, also had the fewest tumour T cells. The no-op gate gave exactly zero. Mismatch-repair status is marked for description only; the lowest three donors are all MMR-proficient, but no test was registered and we draw no conclusion. The perturbation run is in progress: 278 of 369 genes were done at 02:29 Japan time on 2 October. No result is shown. Sources: the colon classifier gate file at commit 2c104ab, the E2 interim report and the registration.

## Slide 24. What the results support, and what they do not (about 1.2 min)

In lung, the classifier works on held-out donors, thirteen T-cell genes exceed their matched controls, and the opposed effects of the two perturbations are generic. In colon, the classifier also works. None of this shows that a gene regulates T-cell state. We also do not know whether the classifier reads T-cell state, ambient RNA or differences in subset composition between tissues, and we have not tested the lung models on new lung donors. Sources: the balanced-donor report and the colon interim report.

## Slide 25. The possible colon outcomes and their readings were fixed before the run (about 0.9 min)

These readings were written into the registration before the run started. If random genes are also opposed in colon, the effect more likely belongs to the model and the design. If they are not, tissue is only one of several differences between the studies, so we could not attribute the change to it. The lung reference genes count as repeating only at nine of ten. Sources: the colon study registration, sections 6.2, 6.3 and 7.

## Slide 26. Bulk RNA-seq: a bulk profile is an average over a mixed population, not a cell (about 1.1 min)

We were asked whether this approach applies to bulk RNA-seq. The basic difficulty is that a bulk profile is an average over many cell types. In the schematic, gene G has the same level inside T cells in both samples, but the bulk level differs because the tumour sample contains fewer T cells. Any perturbation model fitted on bulk data inherits this mixture of composition and regulation within cells. Geneformer itself is not usable here, because a bulk profile does not resemble the single-cell lists it was trained on. We therefore tested a simpler network model, twice, as shown on the next two slides. The values in the figure are invented.

## Slide 27. Bulk tests: a weak, non-specific signal in one knockout set that did not replicate in a second (about 1.5 min)

We tested the simplest version of bulk perturbation against real knockouts, twice. The model is not Geneformer. It is a linear network in the style of CellOracle: each gene is predicted from the transcription factors that a promoter-based network allows to regulate it, restricted to promoters accessible in matched ATAC-seq. Each knockout was left out in turn, simulated by clamping the factor low, and compared with the measured shift. In the first set, from Freimer and colleagues, 17 knockouts have edges in the base network. Predictions agreed with measured shifts more often than chance, and four beat random factors, but not a shuffled network, so the registered reading was RECOVERED_NONSPECIFIC. The figure shows that set. We then repeated the identical pipeline on 38 new knockouts from Weinstock and colleagues, same laboratory and cell type. None of the four tests passed, the reading was NOT_RECOVERED, and by the rule registered beforehand the first result does not replicate. Sources: the two bulk study reports and their result tables on Geneformer_TE main (merge commits 6b637d8 and 460da8a).

## Slide 28. What the two bulk tests show, and what they leave open (about 1.3 min)

The pair of tests narrows the reading. As a group, the network did not beat a shuffled network in either set; the few single knockouts that did, three of 38 in the second set and none in the first, are about what chance gives. So the motif-and-promoter structure added nothing measurable beyond how many genes each factor may touch. In the first set a model-free co-expression baseline did as well as the network, and in the second both fell to chance together, so the first result was a shared response visible to plain correlation, not a property of the network. Fitted on unperturbed controls alone, which is how a bulk cohort without perturbations would have to be used, the network showed no agreement above chance in either set. Predicted magnitudes were 55 to 85 times too small. Why the two sets differ is not tested. Freimer's regulators were chosen as hits in screens and produced large, overlapping responses; Weinstock's produced much smaller ones. The runs also differ in harvest timing, deduplication, counting pipeline and possibly donors, none of which was controlled. The supported claim is narrow: in this design, bulk network perturbation is not a reliable way to predict knockout effects in T cells. Sources: the combined reading of the two bulk tests and the Weinstock report.

## Slide 29. A second project asks which regulators set transposable-element expression (about 1.2 min)

Our second project applies the same question to transposable elements. These are repeated sequences that cells keep silenced through dedicated machinery: KRAB zinc-finger proteins with their co-repressor KAP1, the HUSH complex, DNA methylation and H3K9 methylation. The project asks which regulators set TE expression. It has three tracks. The single-cell track uses Geneformer as in the T-cell work. The bulk track uses the simple linear network from the previous part, now with TE families as targets, and runs on a CPU for any species. The third track supplies ground truth: published knockout and knockdown experiments, re-counted for TEs. The colours give the state: the single-cell track is built but not run, the bulk track has results, and the ground-truth track is running. Sources: the Geneformer_TE README and handoff document.

## Slide 30. Geneformer has no TE tokens, so the single-cell track reads TE states out through a probe (about 1 min)

Geneformer's vocabulary contains human genes and no transposable elements, so TEs cannot simply be deleted or overexpressed in the token list. The single-cell track reads them out instead. Within each cell type, cells are labelled TE-low or TE-high, a classifier learns that split, and a linear probe maps the cell embedding to each TE family's expression. A predicted shift toward TE-high can therefore only come through gene-level regulation. The same kind of gate as in the T-cell work runs first, with a sequencing-depth baseline, because TE fraction tracks depth and cell quality. The track is built but has not been run: we have not yet prepared human single-cell data with TE counts. Droplet reads are short and many map to several TE copies, so any claim stays at the family level. Sources: the Geneformer_TE README and design log, entries DC-01 and DC-02.

## Slide 31. In 162 fish libraries, the 30 TE regulators did no better than expression-matched random genes (about 1.3 min)

The bulk track was first run on a fish cohort from our ocean-acidification work: 162 bulk libraries from three tissues and three CO2 exposure groups, with genes and TE families counted from the same reads. Thirty TE regulators have an annotated orthologue in this fish; KAP1 and the KRAB zinc-finger family do not, because that system is largely specific to tetrapods. Taken at face value, the network produced 32,142 significant regulator-to-family effects, but ninety random genes matched for expression produced as many. Each point in the figure is one regulator's empirical p against those random genes, ranked; the points follow the line expected if no regulator differs from random genes. One regulator falls at p of 0.05 or below, where 1.5 are expected, and none survives correction. Most of the TE variation lies on one global axis, and each regulator's predicted direction followed its correlation with that axis. Removing the axis did not reveal specific regulators either. Sources: the fish bulk run record and its random-control tables on Geneformer_TE main.

## Slide 32. Developmental CO2 lowered the gill TE share; brain and liver showed no robust shift (about 1.1 min)

Because the network removes treatment differences by design, the global TE load needed its own test. In gill, fish exposed to elevated CO2 during development carried a lower share of reads from TEs: 2.87 percent in controls and 2.55 percent after exposure, a relative fall of 11.4 percent with a confidence interval from 5.1 to 17.2 percent, FDR 0.006. The effect held when we adjusted for alignment quality and when we excluded outlier libraries. The intergenerational group points the same way but its interval includes zero. Brain and liver show no robust shift; in brain, the alignment-quality covariates themselves differ by treatment, so those estimates are reported as inconclusive. CO2-tolerant and sensitive lines did not differ detectably. This analysis was not specified in the original study plan, so it is exploratory. It describes a shift in global TE load, and a follow-up found no candidate gene that explains it better than random genes; a thyroid gene set was nominal at p 0.025, FDR 0.10, and is a lead only. Sources: the TE-axis treatment report and the gene-axis report on Geneformer_TE main.

## Slide 33. Two tests against measured TE responses are running; no results are shown (about 1.3 min)

Two tests compare predictions with measured TE responses. Neither has produced a result, and I show none. The zebrafish panel re-counts TEs in seventeen published knockout, knockdown and overexpression contrasts of TE regulators, from fourteen GEO series. For each study it measures the TE share of reads and the balance of TE families going up and down, and it asks two questions: whether loss of a silencer de-represses TEs, and whether the fish bulk network predicted the right direction. A direction call requires both a corrected significance below 0.05 and at least a five percent change in TE share. At 02:35 Japan time, 53 of the 112 samples had been counted; counting should finish around six or seven in the morning, and the report goes through review before it reaches a slide. The second test returns to the Freimer T-cell knockouts. The reads are re-aligned with multimapping reads kept, so that genes and TEs come from the same reads. Two gates come first: if the re-aligned gene counts disagree with the deposited ones, the analysis stops, and if fewer than twenty TE subfamilies are expressed, the TE arm is reported as not testable. The rules were registered at 02:12 Japan time, before any data were downloaded, and the alignments are expected between half past five and half past six this morning. Sources: the zebrafish run record, the handoff document and the registered amendment A3 for the TE arm.

## Slide 34. What the TE work shows so far, and what it does not (about 1.1 min)

The supported findings are narrow. A network built from natural co-variation has shown no regulator-specific signal wherever it was tested with proper controls: in the fish cohort and in the two T-cell knockout sets. In fish, the random-gene control is what shows it; without that control, the same run would have looked like thirty-two thousand findings. That is the bulk counterpart of the random-gene baseline from the T-cell work. Developmental CO2 exposure lowered the gill TE share, as an exploratory result. We have not shown any regulator-to-TE effect. We do not know whether Geneformer can rank TE regulators, because that track has not run, or whether any prediction matches a measured TE response, because both tests are still running. The global TE axis is also unexplained; it could reflect intronic or nascent RNA, or cell composition. The single-cell track is also where this project and the colon T-cell work would meet, if human single-cell data with TE counts were prepared. Sources: the fish run records and reports on Geneformer_TE main.

## Slide 35. Summary 1: the evaluation criteria, each traced to evidence (about 1.2 min)

Each criterion on the left is now lab practice, and each is tied to a documented episode on the right. These are established as practice in our lab, with sources for every row. They have not been tested by other groups, and some, such as the 95 percent stability threshold, are choices rather than derived results.

## Slide 36. Summary 2: what remains to be tested (about 1.3 min)

This is what we do not yet know. The colon study is running, with its gate passed. Transfer to new lung donors is blocked by data access. Three studies are planned with little or no new GPU work: swapping the goal, re-analysing within T-cell subsets, and comparing the classifier with an interpretable baseline built from published T-cell programs. Model size and positive controls have not started; without positive controls, a negative result is hard to interpret. The bulk RNA-seq row now has a result: across two registered tests on 55 knockouts, the bulk network did not recover regulator-specific effects, and its one weak positive did not replicate. The last three rows come from the TE project: two tests against measured TE responses are running, and the single-cell TE track needs data we have not prepared. Sources: the next-cycle proposal, the independent-data design and the E0 feasibility report.

## Slide 37. These results could form one methods paper on evaluating in-silico perturbation (about 1.3 min)

If the open studies are completed, the material could form one methods paper. The slide separates three things. The result is established, but narrowly: in lung T cells, with the larger model and our design, random genes gave opposed effects. The argument, that gene-level claims need these baselines and checks, is a recommendation drawn from it. Extension to other tissues, goals and model sizes is a hypothesis. The bulk line is now a negative result with a narrow scope: in this design, bulk network perturbation did not predict knockout effects. Figures one, two, four, five and seven could be drawn from results we have; figures three and six need the studies on the previous slide. A negative colon result would change the paper's emphasis rather than remove it, because the lung evidence and the documented failure modes stand on their own.

## Slide 38. Summary (about 0.6 min)

To summarise: the opposed effects of the two perturbations in random genes are the baseline that any gene-level claim has to exceed. The six criteria came from our own errors and are now how we evaluate every run; the colon study has passed its gates and its results are pending. On bulk RNA-seq, two registered tests against measured knockouts did not support regulator-specific prediction, and the first test's weak signal did not replicate. For transposable elements, the same network did no better than random genes in fish, and the tests against measured TE responses are still running. Thank you; I am glad to take questions.

## Slide 39. Glossary (about 0.3 min)

The glossary is for reference and is repeated on the handout.
