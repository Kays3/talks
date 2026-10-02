# Reading the Current, version 2: speaker notes

Lab progress report, 1 October 2026. Kaisar Dauyey · Shinji Nakaoka. 26 slides, about 27 minutes of talk, then 5 to 10 minutes of discussion. Every number is sourced in `SOURCES.md`.

## Slide 1. Reading the Current (about 0.5 min)

This is the second version of our progress report. The first was written for people who already use Geneformer; this one is meant for everyone in the room, so I will explain each idea before using it. The story is about a model that always gives an answer, and about how we learned, mostly from our own mistakes, to tell when the answer means something.

## Slide 2. Our question: which genes, if changed, would push a tumour's T cells back toward normal? (about 0.8 min)

T cells inside a tumour often look and behave differently from T cells in the same patient's healthy tissue. Our question is which genes, if we changed them, would move a tumour T cell back toward its healthy counterpart. Testing that experimentally, gene by gene, is slow. So we asked a model to make predictions first. The rest of the talk is about how far those predictions can be trusted.

## Slide 3. The short answer: the model always answers, so we built checks to tell when it means something (about 0.8 min)

Here is the plan. The bar at the top of every slide shows where we are. One colour code runs through the whole talk: teal means a check passed, coral means it failed, amber means we do not know yet. And each of the six checks has its own small icon, which reappears whenever that check is relevant.

## Slide 4. Geneformer reads each cell as a list of its genes, most unusual first (about 1 min)

Geneformer does not look at raw gene counts. For each cell it divides every gene's level by how high that gene usually is, then sorts. A housekeeping gene that is always abundant ends up near the bottom, and a gene that is unusually high in this particular cell moves to the front. The result is an ordered list, which the model treats like a sentence. The genes and bars on the slide are invented for illustration. Source: Theodoris and colleagues, Nature 2023.

## Slide 5. It learned what normal gene lists look like from about 104 million cells (about 0.9 min)

The model was trained by a guessing game. Hide one gene in a cell's list and ask the model to fill it in from the others. After doing that across about a hundred million cells, it has learned which genes tend to appear together. What we use is the model's internal position for each cell, its embedding: cells that look alike to the model sit close together on its map. We have used two sizes of the model, a smaller and a larger one; their sizes in parameters come up only on the summary slide, and the smaller one's 104 million parameters have nothing to do with the 104 million training cells. Sources: Theodoris and colleagues 2023 and the model card on Hugging Face.

## Slide 6. We then teach it one extra skill: telling a patient's tumour T cells from their normal T cells (about 1 min)

Next we give the model one specific task. From each patient we take T cells from the tumour and T cells from nearby normal lung, and we train the model to tell them apart. We always test it on patients it was not trained on. In our lung study, with 43 patients, it was right about 82 percent of the time when both groups are counted equally, and it beat chance for every single patient. That matters, because the edits on the next slide are measured along exactly this tumour-to-normal direction. Source: the balanced-donor lung report, classifier gate file.

## Slide 7. A virtual gene edit changes the list and asks where the cell moves on the map (about 1.2 min)

Now the central idea. We take a tumour T cell's list and edit it in the computer. Deleting a gene removes it; overexpressing a gene moves it to the top of the list. The model reads the edited list and places the cell somewhere new. Our score is how much closer the cell came to the centre of the same patient's normal T cells. If deleting a gene moves cells toward normal, that gene might be holding them in the tumour state. I want to be clear that no real cell is touched. We are asking the model what it thinks, and its answer reflects what it has learned, which may or may not match biology.

## Slide 8. Our first results, in July and August, looked encouraging (about 1.2 min)

The project began in July with a screen that deleted every gene in every held-out cell, almost three million deletions. Even then our own audit warned that it could not support the claims in an abstract we had submitted about small-cell lung cancer. So we built a small-cell line and, in August, presented four genes that passed in both directions in every test patient. They were familiar names from the T-cell exhaustion and persistence literature, which was reassuring. Over the next weeks we learned how much of that reassurance came from the method rather than the biology. Sources: the repository README, the 28 July audit, and the August talk.

## Slide 9. Trap 1: the strongest hits were not T-cell signals (about 1.1 min)

The first trap was in the screen's top hits. S100A8 and S100A9 were among the most significant results, but deleting and adding them pushed cells the same way, which a gene that actually drives a state should not do. Many top hits looked like ambient RNA, material from other cells that ends up in a T cell's droplet. Worse, the July comparison of normal and tumour T cells used different studies for each group, so the model may have learned study differences. When we later rebuilt the study around T cells properly, thirteen of the fifteen July genes could not be tested in T cells at all; they were epithelial and blood genes such as keratins. The small icons show which checks answer this trap: checking the instrument, and comparing with look-alike genes. Sources: the S100A8/S100A9 cross-reference report, the July methods file, and the balanced-donor report.

## Slide 10. Trap 2: one patient can look like a whole group (about 1 min)

The second trap is about counting. Cells from one patient are not independent; they share that patient's genetics, history and sample handling. When one patient supplies three quarters of the small-cell test cells, a cell-level analysis of that group is mostly an analysis of that patient. Once we counted patients rather than cells, an apparent difference between small-cell and adenocarcinoma T cells was no longer significant. Source: RESULTS_T6 in the repository.

## Slide 11. Trap 3: our two edits were measured on different cells (about 1 min)

The third trap was in our own instrument. We found that the August panel had scored deletion and overexpression on different sets of cells, because of a default in Geneformer's code that inserts an overexpressed gene into every cell when it is given a gene list. We had documented that default on 22 September and still missed its effect on our rebuilt study three days later. We did not retract the August genes, since the deletion evidence stands, but we attached a caveat. The panel has not been rerun. Sources: the 25 September correction and Amendment 3h of the balanced-donor registration.

## Slide 12. Trap 4: even random genes show the pattern we had treated as evidence (about 1.6 min)

This is the result I most want you to take away. The four August genes passed because deletion and overexpression pushed cells in opposite directions. When we ran the identical pipeline on genes drawn at random, they showed the same opposition, strongly. Each dot is one random gene. The correlation was minus 0.593 for the registered hundred genes and minus 0.608 when we extended to two hundred. The p-value sits at the floor of the permutation test, so we report it as at most one in a hundred thousand. The random genes are drawn from genes detectable in lung tumour T cells, not from the whole genome. So opposite signs are the baseline, not the evidence. Sources: the two null-study result files, hashes a00ccb2f and c9e56026.

## Slide 13. Six checks now stand between a result and a claim (about 1 min)

Each of these six checks answers one of the traps. The first three are about the experiment itself: decide the test in advance, make sure the instrument works, and compare like with like. The last three are about reading the result: beat genes that look similar, beat random genes, and count patients rather than cells, using fixed words for every outcome. We wrote them down as a lab standard on 28 September. The next slides take them one at a time.

## Slide 14. 1 Write the test down before any result exists (about 1.1 min)

Writing the test down first sounds like bureaucracy. In practice it is what stops us from choosing a test after seeing the data, which we came close to doing in August. Part of the plan is checking that the test can reach significance at all; with ten genes, agreement has to reach nine of ten. The exact bar depends on how many genes turn out testable, and that rule is also fixed in advance. Our own first plan for the colon study failed review on a small but real point about the software environment. Source: the colon study registration, section 6.3.

## Slide 15. 2 Check the instrument before reading anything from it (about 1.1 min)

Two checks come before any edit is made. First, the fine-tuned model has to work on patients it has never seen; in colon it was right about 90 percent of the time, every patient was above chance, and the lowest was 0.655. Second, an edit that changes nothing must produce no movement, and the largest shift we saw was exactly zero. Lung and colon are shown side by side for context only. The colon models are new, trained from the same base model, so this does not show that the lung models transfer. Sources: the colon classifier and no-op gate files at commit 2c104ab.

## Slide 16. 3 Score both edits on exactly the same cells (about 0.8 min)

This check is short because the rule is simple: both edits are scored on the same cells. There is also a quick way to spot a violation. If one arm has a constant cell count across genes while the other varies, the two arms cannot be paired. That is exactly the signature the August panel had. The panel code was fixed on 22 September, and the rebuilt study was corrected on 25 September by reconstructing which cells carried each gene; every analysis since, including the colon study, re-checks those counts. Sources: the lab standard, clause B2, and Amendment 3h.

## Slide 17. 4 A gene must move cells more than genes that look like it (about 1.1 min)

A raw shift means little on its own. Genes that are present in many cells move them more simply by being there. So every gene we test gets a comparison set of at least twenty genes matched on how often and how highly they are detected. A gene is only interesting if it stands outside that cloud, like the teal line in the sketch. If we cannot find twenty look-alikes, we say the gene cannot be estimated, rather than widening the match. In the lung study, 13 of 34 testable T-cell genes passed this check and stayed stable. Sources: the lab standard, clauses B1 and B4, and the balanced-donor report.

## Slide 18. 5 Opposite effects of delete and overexpress are not, on their own, evidence (about 1 min)

This check follows directly from the random-gene result. If random genes show opposed effects, then opposed effects cannot be the evidence for any particular gene. The study's own control genes gave the same sign, minus 0.658; we compare that with other figures by sign only, because they are computed differently. What survives is the size of an effect relative to this baseline. That is narrower than what we claimed in August, and more honest. Sources: the null-study result file and the lab standard, clause B7.

## Slide 19. 6 Count patients, demand stable results, and name every outcome in advance (about 1 min)

The last check is about inference and language. We count patients. A result has to be stable: it must hold when we drop any single control gene and in at least 95 percent of ten thousand resamplings, otherwise we call it open. And every outcome gets one of a few labels fixed before the run. The phrase we never use is "no effect"; a small study can miss a real effect, so a negative result is reported with its direction, p and sample size. Our S100 ambient-RNA test in late September was negative in exactly this sense, at p = 6/70 and 34/70. Sources: the lab standard, clauses A6, B5 and B8, and the S100 result file.

## Slide 20. What our results support today, and what they do not (about 1.3 min)

Here is where the evidence stands. In lung, the classifier works on unseen patients, a curated set of thirteen T-cell genes passes the look-alike check, and the opposed effects of the two edits are generic. In colon, the classifier also works, and the lung gene pattern did not repeat. What we cannot say is just as important. None of this shows that a gene controls T-cell state; a shift on the model's map is not a mechanism. We do not know whether the classifier is reading T-cell state, ambient RNA or simply a different mix of T-cell types between tissues. And we have not yet tested the lung models on new lung patients. Sources: the balanced-donor report and the colon interim report.

## Slide 21. The colon test: random genes were opposed again, but not reliably; the lung gene pattern did not repeat (about 1.4 min)

The colon run finished on the morning of 2 October, and the results have passed internal review. The first question was whether random genes are opposed in colon too. They are, in the same direction as in lung, but more weakly, and the pattern held in only 78 percent of resamplings, short of the 95 percent we required before starting. So by the reading we wrote down in advance, the direction matches lung but the result is not stable, and the question stays open. The second question was whether the lung reference genes keep their direction. Three of ten did, where we needed nine, so the lung gene pattern did not repeat. Seven pointing the other way is about what chance would give, so this is not a reversal either. One gene, PRF1, met all its pre-set tests in colon, though it was undecided in lung. None of these differences can be put down to tissue, because the colon study differs from the lung studies in almost every other way too, and it has fewer patients. Sources: the colon study results report and its result files on geneformer-lung-tcell main, merge 4cce44a.

## Slide 22. Summary 1: the evaluation criteria we found, each traced to evidence (about 1.3 min)

This table is the first half of what I would call our contribution so far. Each criterion on the left is now lab practice, and each one is tied to a specific piece of evidence on the right, from our own work. I want to be precise about the status. These are established as practice in our lab, with sources for every row. They have not yet been tested by anyone else, and some, like the 95 percent stability bar, are choices we made rather than results we derived.

## Slide 23. Summary 2: what we still need to test (about 1.4 min)

The second half is what we do not know. The colon test has a first answer: random genes were opposed in the same direction as in lung, but not stably, so whether the effect belongs to the model or to lung stays open; the lung gene pattern did not repeat. The lung transfer test is blocked, because the one independent lung dataset we found is packaged in a way we could not access. Three studies are planned without new GPU work, or with modest GPU work: swapping the goal to see whether the opposed effects depend on it, re-analysing within T-cell subsets, and comparing the model with a readable baseline built from published T-cell programs. Two questions have not started: whether model size changes the results, and whether the method recovers genes we already know matter. Without that last one, a negative result is hard to interpret. Sources: the next-cycle proposal, the independent-data design and the E0 feasibility report.

## Slide 24. Together these could become one paper on how to judge virtual gene edits (about 1.3 min)

If the open studies come through, the material could become one methods paper. A working title would be "Opposite by default". The slide separates three things. The result is established, but narrowly: in lung T cells, with the larger model and our design, random genes gave opposed effects. The argument we would make from it, that gene-level claims need these baselines and checks, is a recommendation, not a finding; paired cells and patient-level counting come from the other traps. Whether the result holds in other tissues, under other goals and for other model sizes is still a hypothesis. Figures one, two, four and five could be drawn today from results we have. Figures three and six need the studies on the previous slide. The colon result, open for random genes and not repeated for the lung genes, changes the paper's shape rather than removing it, because the lung evidence and the traps stand on their own.

## Slide 25. The model always answers. The checks tell us when to listen. (about 0.4 min)

To close: almost every correction since July came from measuring something we had taken for granted, such as the studies behind a group, the cells behind an edit, the patient behind a difference, or the random genes behind a pattern. The opposed effects in random genes are not a failure of the method; they are the baseline any claim has to beat. Thank you. I am happy to take questions, and if any of the open studies interests you, please come and talk to me.

## Slide 26. Glossary: the few terms we kept (about 0.3 min)

The glossary is here and on the handout for reference. I will not read it aloud.
