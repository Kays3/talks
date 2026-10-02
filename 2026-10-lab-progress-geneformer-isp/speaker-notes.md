# Reading the Current: speaker notes

Lab progress report, 1 October 2026. Kaisar Dauyey · Shinji Nakaoka. 28 slides, about 26 minutes of talk, then 5 to 10 minutes of discussion. Every number is sourced in `SOURCES.md`.

## Slide 1. Reading the Current (about 0.5 min)

This is a progress report, but I want to tell it as a story, because the most useful thing we have learned since July is not a gene. It is how easily a foundation model gives a convincing answer, and what it took for us to stop being convinced too early. I will start with a few minutes on what Geneformer is, then tell you how the project actually went, including the parts we got wrong. From that history I will draw the rules we now apply, show where we are this week, and finish with places where you could join. The image I will keep returning to is navigation: the model draws a chart, a perturbation nudges a boat, and the hard part is telling our nudge apart from the current that moves every boat.

## Slide 2. The model always answers. We spent three months learning when the answer means something. (about 1 min)

Here is the plan. Part two is new since the first version of this talk, and I think it is the most important part, because each rule in part three exists because of something that happened in part two. If a word is unfamiliar, the glossary near the end and the handout have it.

## Slide 3. The chart (about 0.2 min)

Five minutes of orientation. If you already use Geneformer, this is a chance to check that we mean the same things by the same words.

## Slide 4. Geneformer reads each cell as a ranked list of genes (about 1.4 min)

Geneformer does not read raw counts. It ranks the genes in each cell after scaling each gene by how much it is usually expressed, so a gene that is always high does not dominate, and a gene that is unusually high in this cell moves forward. The cell becomes a kind of sentence. In pretraining, the model learns to fill in masked genes from context. What we use afterwards is the model's internal representation of each cell, which we call the embedding. The gene list on the slide is invented for illustration. Sources: Theodoris and colleagues, Nature 2023, for the method; the Hugging Face model card for the size of the V2 corpus.

## Slide 5. A compass for our question, then a nudge (about 1.4 min)

Fine-tuning adapts the model to one task. For us, the task is telling tumour-infiltrating T cells apart from T cells in the same patient's normal tissue. Once the model separates the two, we can ask what happens to a tumour cell's position if we edit its sentence: remove a gene, or push it to the front. Then we measure whether the cell moved toward that patient's own normal cells. I want to stress the last line. Nothing happens to a real cell here. The answer tells us about the geometry the model has learned, which may or may not reflect biology. The figure is a sketch with invented points.

## Slide 6. How we got here (about 0.2 min)

Now the history, in order, from our own records. I will be specific about the mistakes, because they are where the rules came from.

## Slide 7. It began with a screen, and an abstract we had to support (about 1.2 min)

The project began in July with a classifier on lung T cells and a screen that deleted every gene in every held-out cell, almost three million deletions. At the same time we had submitted an abstract about T-cell dysfunction in small-cell lung cancer, a tumour that responds poorly to checkpoint immunotherapy. Our own feasibility audit on 28 July said plainly that the July work could not support the abstract's SCLC claims. So we built a dedicated SCLC line, with forty-six thousand T cells from forty-two donors. It classified well, but its normal class had one test donor, and that is worth remembering. Sources: the repository README and the 28 July feasibility audit.

## Slide 8. What we told the JSDP meeting in August (about 1.2 min)

In August we presented this at the JSDP meeting. Four genes passed in both directions, deletion toward normal and overexpression away, in every SCLC test donor, and an antigen-presentation programme the model pointed to tracked T-cell abundance in independent tissue. We also put an odd result on the poster as an open question: on the checkpoint axis the model ordered the states normal, then SCLC, then LUAD. We ended the talk by asking what SCLC T cells are if they are not exhausted. That question is what drove the next month. Sources: the JSDP talk and poster in the talks repository.

## Slide 9. Then we tested our own story, and it did not hold (about 1.2 min)

We then tried to test the ordering properly, and it did not survive. First, the three states do not lie on a line at all; they form a triangle. Second, when we overexpressed the whole exhaustion programme, SCLC cells did move toward LUAD, but expression-matched random gene sets moved them almost as far: plus 0.0873 against plus 0.0816, p 0.43. Third, two of our analyses seemed to disagree, and the disagreement turned out to be a single patient who contributed three quarters of the SCLC test cells. Counted by donor, the difference was not significant. Two lessons came out of this: compare every shift with a null, and count patients, not cells. Sources: RESULTS_T3, T4 and T6 in the repository.

## Slide 10. Our strongest hits were not what they looked like (about 1.2 min)

In September we audited the whole-genome screen. Its most significant hits, S100A8 and S100A9, failed the simplest sanity check: removing and adding the gene pushed cells in the same direction. Many of the top hits looked like ambient RNA, transcripts from surrounding tissue that end up in a T cell's droplet. Then we found that the July classifier's normal class came from entirely different studies than its tumour classes, so the model could have been learning study identity. I should add that we first confused two different classifiers while working this out, which delayed the finding. Sources: the S100A8/S100A9 cross-reference report and the July METHODS file.

## Slide 11. We found two faults in our own instrument (about 1.3 min)

This was the most uncomfortable week. We discovered that the August panel had scored deletion and overexpression on different sets of cells, so the concordance part of the four August hits rested on unequal comparisons. We did not retract them, because the deletion evidence stands, but we attached a caveat and said the panel has not been rerun. The cause is a default in Geneformer itself: when given a list of genes, its overexpression mode inserts each gene into every cell. We had documented exactly this on 22 September and fixed our panel runner. Then, on 25 September, we found both the consequence for the August panel and that our rebuilt study had hit the same default. We recorded that in the amendment in those words. Sources: the 25 September correction in the talk sources file, and Amendment 3h.

## Slide 12. So we rebuilt the experiment, and wrote the rules down (about 1.2 min)

By late September we rebuilt the experiment around patients rather than cells: forty-three patients, each contributing tumour and normal T cells, equal numbers per tissue. The classifier still worked well. Most of the July gene list turned out to be epithelial and blood genes that are barely present in T cells, which tells us what the July screen had really been reading. A curated T-cell panel gave thirteen stable calls. But the control genes themselves showed a strong anti-correlation between deletion and overexpression, which made us wonder whether that pattern was generic. And on 28 September we wrote down the standard that the rest of this talk is about. Sources: the balanced-donor IMRaD report, the ISP-STD-1 standard and the S100 result file.

## Slide 13. Rules we learned (about 0.2 min)

Each of the six rules that follow answers one of the moments I just described.

## Slide 14. File the voyage plan before you sail (about 1.2 min)

Pre-registration is the rule that sounds most bureaucratic and has saved us most often. Writing the test down first stops us from choosing it after seeing the data, which is what we came close to doing with the August ordering. The attainability check matters with small samples, where some tests cannot reach p below 0.05 at all. For the colorectal comparison, ten genes are expected to be testable; at that n agreement has to reach nine of ten, and the exact bar is set by the number actually tested, under a rule fixed in advance. The first review of that plan failed for a small but real reason, an inaccurate statement about the software environment. Source: E2_REGISTRATION.md at commit 8b11d5d, section 6.3.

## Slide 15. Check the compass, then check that an anchored boat stays still (about 0.9 min)

Two checks come before any perturbation. The classifier gate asks whether the compass works on patients the model has never seen; if it fails, we stop. The July classifier is the reason we now insist on held-out patients and paired tissues. The no-op gate asks whether the boat moves when nothing has been done to it. Any non-zero shift means the pipeline itself is producing movement that would later be read as an effect. Sources: ISP-STD-1 clause B3 and the classifier rule in each registration.

## Slide 16. Compare against boats of the same build (about 0.9 min)

A raw shift means little on its own, because genes that are present in many cells move them more simply by being there. So every gene is compared with twenty or more genes that look like it in detection and rank, and if we cannot find twenty we say so rather than loosening the match. We count patients, not cells, for the reason you saw on the T6 slide. And a result has to be stable when we drop controls or resample them. These are clauses B1, B5 and B8 of the standard.

## Slide 17. Every boat drifts. Measure the drift before claiming a nudge. (about 1.8 min)

This is the result I most want you to remember. A gene that moves a cell toward normal when deleted and away when overexpressed looks like a meaningful, dose-consistent effect. After seeing the control genes, we asked what random genes do. We drew genes at random from those detectable in lung tumour T cells and ran the identical pipeline. Their deletion and overexpression shifts were strongly anti-correlated: minus 0.593 for the registered hundred, minus 0.608 when extended to two hundred. Honestly, we had half expected this after the controls, but seeing it in genes chosen by a random seed made it concrete. The p-value sits at the floor of the permutation test, so we report it as at most ten to the minus five. Sources: a5_primary_result_v2.json and n200_combined_result_v2.json, hashes a00ccb2f and c9e56026.

## Slide 18. Opposite signs for delete and overexpress are not evidence of specificity (about 1 min)

I want to be careful about what follows. The null result does not overturn the curated panel. What it removes is an argument we were tempted to make in August: that a gene behaving in opposite directions under deletion and overexpression must be acting specifically. Random genes do that too. The validity check on our control genes recovered the same sign, and we compare it with the earlier figure only by sign, because the two are computed differently. And we never call these genes genome-wide. Sources: IMRaD report rows P22 to P25.

## Slide 19. Write the log in a fixed vocabulary. Never "no effect". (about 0.9 min)

The last rule is about language. Every outcome gets one of eight labels fixed before the run. The phrase we never use is "no effect". A negative result only means this test, at this size, did not meet its criterion; we report its direction, p and n so a reader can judge what it rules out. The S100 run was negative in exactly this sense. Fixed words stop us drifting into stronger language than the data support. Source: ISP-STD-1 clause A6.

## Slide 20. What ISP cannot show, however clean the result (about 0.8 min)

Even a result that passes every rule has limits. It tells us how the model responds to an edited input, not that the gene regulates anything in a living cell. The classifier may be reading T-cell state, ambient RNA or the balance of CD4 and CD8 cells, and our checks cannot separate these. And we cannot talk about accuracy in the usual sense until we compare with an experimental perturbation screen in T cells, which we have not yet done.

## Slide 21. This week (about 0.2 min)

With that history and those rules in place, here is where we are this week.

## Slide 22. Colorectal cancer (Pelka et al. 2021): the classifier gate passed (about 1.3 min)

The colorectal study repeats the whole design in a different tissue, using public data from Pelka and colleagues. We kept nineteen patients whose samples were processed the same way in both tissues. Five new models were trained from the base weights. Every patient was above chance, and the lowest was 0.655. The lung value of 0.825 is shown only for context; one study against five, different processing and fewer patients mean we should not read the difference biologically. And because these are new models, this says nothing about whether the lung models transfer. Sources: classifier_gate.json and noop_gate.json at commit 2c104ab, and the interim report of 1 October, which passed internal review.

## Slide 23. Colorectal perturbation screen: same direction as lung but not stable; the lung gene pattern did not replicate (about 1.5 min)

The colorectal run finished at 10:20 Japan time on 2 October, inside the compute we registered, and the results passed internal review before I put them here. The primary question was whether random genes are anti-correlated in colon as in lung. They are, in the same direction: the rank correlation was minus 0.245, with a one-sided p of 0.0067, and no single gene carries it. But the pattern stayed significant in only 78 percent of resamples, short of the 95 percent we set in advance, so by our own rule it is reported as open. For the lung reference genes, three of ten kept their lung direction where nine were needed, so the lung pattern did not replicate; seven opposite signs is within what chance gives, so this is not a reversal. The right-hand card is the set of readings we fixed before the run, with the two outcomes that occurred marked. Neither difference from lung can be put down to tissue, because study, sample handling, chemistry, the fold models and the number of patients all differ. Sources: the E2 results report and the H2b, H2c and Panel B result files on geneformer-lung-tcell main, merge 4cce44a, and E2_REGISTRATION.md sections 6.2, 6.3 and 7.

## Slide 24. Uncharted waters (about 0.2 min)

We have more open questions than people. Each task on the next slides is sized so that one person could start this month.

## Slide 25. What we do not know yet (about 1.1 min)

These are the gaps. The anti-correlation needs an explanation; one idea is that deleting a token and moving it to the front are near-opposite operations for any gene, simply because of how rank encoding works. We do not know whether the lung models transfer. We cannot say what the classifier reads. We have no experimental ground truth in these T cells. And without positive controls, a negative result could just mean the test was insensitive. The August question, what SCLC T cells are if not exhausted, is also still open.

## Slide 26. Six ways in, from an hour to a month (about 1.2 min)

If any of this interests you, here are ways in. The first two need a laptop and an afternoon, and they teach the two habits that would have saved us the most trouble since July: recompute numbers from the source file, and know the smallest p-value your test can reach before running it. The next two are literature tasks that fill our biggest gaps. The fifth is a small research project that could become a short paper. The last is practical: one dataset is packaged in a way our scripts cannot open, and someone with a browser can tell us what is inside. Please come and talk to me afterwards.

## Slide 27. Words on the chart (about 0.3 min)

The glossary is here for reference and on the handout. I will not read it aloud.

## Slide 28. The current is not the enemy. It is the baseline. (about 0.3 min)

To close: looking back over three months, almost every correction came from measuring something we had taken for granted, such as the study behind a class, the cells behind an arm, the patient behind a shift, or the drift behind a nudge. The anti-correlation in random genes is not a failure of the method. It is the baseline any claimed effect has to exceed. In colon the baseline points the same way but is not yet stable, so whether it belongs to the model or to lung is still open. Thank you; I am happy to take questions, and to talk about any of the entry tasks.
