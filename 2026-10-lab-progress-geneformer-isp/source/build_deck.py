"""Build the lab progress talk 'Reading the Current' (2026-10-01; v2 adds the project history).

Writes ../slides.html (self-contained deck: arrow keys to move, N toggles speaker notes, P prints),
../speaker-notes.md (one section per slide), and is followed by WeasyPrint for ../slides.pdf.
Every number on a slide is listed in SOURCES.md with its file, commit or hash.
"""
import base64, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "..", "figures")
OUT = os.path.join(HERE, "..")


def img(name):
    with open(os.path.join(FIGS, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


CONT_A, CONT_B = img("contours_a.png"), img("contours_b.png")

# Each slide: (kind, minutes, html body, speaker notes). kind sets the background treatment.
S = []

S.append(("title", 0.5, f"""
<div class="kicker">Lab progress report · 1 October 2026</div>
<h1 class="big">Reading the Current</h1>
<p class="sub">What three months of Geneformer work taught us<br>about believing a model's answer</p>
<div class="byline">Kaisar Dauyey · Shinji Nakaoka<br><span>Laboratory of Mathematical Biology, Faculty of Advanced Life Science, Hokkaido University</span></div>
<div class="rose">✦</div>
""", """This is a progress report, but I want to tell it as a story, because the most useful thing we have learned since July is not a gene. It is how easily a foundation model gives a convincing answer, and what it took for us to stop being convinced too early. I will start with a few minutes on what Geneformer is, then tell you how the project actually went, including the parts we got wrong. From that history I will draw the rules we now apply, show where we are this week, and finish with places where you could join. The image I will keep returning to is navigation: the model draws a chart, a perturbation nudges a boat, and the hard part is telling our nudge apart from the current that moves every boat."""))

S.append(("plain", 1.0, """
<div class="kicker">Today</div>
<h2>The model always answers. We spent three months learning when the answer means something.</h2>
<div class="three five">
  <div class="card"><div class="num">I</div><h3>The chart</h3><p>Geneformer and in-silico perturbation, from zero.</p></div>
  <div class="card"><div class="num">II</div><h3>How we got here</h3><p>July to September, including what we got wrong.</p></div>
  <div class="card accent"><div class="num">III</div><h3>Rules we learned</h3><p>Six checks we now apply before believing a result.</p></div>
  <div class="card"><div class="num">IV</div><h3>This week</h3><p>The same design, tried in colorectal cancer.</p></div>
  <div class="card"><div class="num">V</div><h3>Join us</h3><p>Open questions and small tasks.</p></div>
</div>
<p class="foot">Unfamiliar words are collected in a glossary on slide 27 and on the handout.</p>
""", """Here is the plan. Part two is new since the first version of this talk, and I think it is the most important part, because each rule in part three exists because of something that happened in part two. If a word is unfamiliar, the glossary near the end and the handout have it."""))

S.append(("section", 0.2, """<div class="partno">I</div><h1>The chart</h1><p class="sub">Geneformer for beginners</p>""",
          """Five minutes of orientation. If you already use Geneformer, this is a chance to check that we mean the same things by the same words."""))

S.append(("plain", 1.4, """
<div class="kicker">I · Cells as sentences</div>
<h2>Geneformer reads each cell as a ranked list of genes</h2>
<div class="sentence">
  <span class="tok t1">CD3E</span><span class="tok t2">IL7R</span><span class="tok t3">CCR7</span><span class="tok t4">LTB</span><span class="tok t5">CD3D</span><span class="tok t6">TCF7</span><span class="tok t7">GZMK</span><span class="tok t8">…</span>
</div>
<p class="caption">An illustrative T cell, written as genes ordered from most to least characteristic. Each gene in the list is a <b>token</b>, the model's word. Not real data.</p>
<p class="lead">The model divides each gene's expression by how high that gene usually is, then sorts. Housekeeping genes sink and the genes that make this cell distinctive rise to the front. A transformer (a neural network that reads sequences) then learns to guess hidden genes from the rest of the list, across tens of millions of cells; the V2 models saw about 104 million cells. What we keep is the model's internal position for each cell, its <b>embedding</b>: a point on the chart.</p>
""", """Geneformer does not read raw counts. It ranks the genes in each cell after scaling each gene by how much it is usually expressed, so a gene that is always high does not dominate, and a gene that is unusually high in this cell moves forward. The cell becomes a kind of sentence. In pretraining, the model learns to fill in masked genes from context. What we use afterwards is the model's internal representation of each cell, which we call the embedding. The gene list on the slide is invented for illustration. Sources: Theodoris and colleagues, Nature 2023, for the method; the Hugging Face model card for the size of the V2 corpus."""))

S.append(("plain", 1.4, f"""
<div class="kicker">I · Fine-tuning and perturbation</div>
<div class="split">
  <div>
    <h2>A compass for our question, then a nudge</h2>
    <p class="lead">We first <b>fine-tune</b> the model on one distinction: tumour T cells against the same patient's normal-tissue T cells. Then we edit a cell's sentence. <b>Deleting</b> a gene removes its token; <b>overexpressing</b> it moves the token to the front. We measure whether the cell moved toward the centre of that patient's normal T cells: the change in similarity to that goal (the cosine shift; positive means closer to normal).</p>
    <p class="note">In-silico perturbation (ISP) is a question we put to the model, not an experiment on cells.</p>
  </div>
  <figure><img src="{img('isp_schematic.png')}" alt="ISP schematic"></figure>
</div>
""", """Fine-tuning adapts the model to one task. For us, the task is telling tumour-infiltrating T cells apart from T cells in the same patient's normal tissue. Once the model separates the two, we can ask what happens to a tumour cell's position if we edit its sentence: remove a gene, or push it to the front. Then we measure whether the cell moved toward that patient's own normal cells. I want to stress the last line. Nothing happens to a real cell here. The answer tells us about the geometry the model has learned, which may or may not reflect biology. The figure is a sketch with invented points."""))

S.append(("section", 0.2, """<div class="partno">II</div><h1>How we got here</h1><p class="sub">July to September, including what we got wrong</p>""",
          """Now the history, in order, from our own records. I will be specific about the mistakes, because they are where the rules came from."""))

S.append(("plain", 1.2, """
<div class="kicker">II · July</div>
<h2>It began with a screen, and an abstract we had to support</h2>
<div class="two">
  <div class="card"><h3>The July screen</h3>
    <p>21,000 lung T cells in three classes: adenocarcinoma (LUAD), squamous carcinoma (LUSC) and normal tissue, using the smaller Geneformer model (104 million parameters). Accuracy 0.7834, and 2,937,776 held-out deletions of single genes in single cells.</p></div>
  <div class="card"><h3>Our own audit, 28 July</h3>
    <p class="quote">"The present LUAD/LUSC exploratory work cannot by itself substantiate the abstract's SCLC claims."</p>
    <p>So we built a small-cell lung cancer (SCLC) line: 46,140 T cells from 42 patients (we use "donor" and "patient" for the same thing), held-out accuracy 0.919. The normal test class was a single patient, 566 cells.</p></div>
</div>
""", """The project began in July with a classifier on lung T cells and a screen that deleted every gene in every held-out cell, almost three million deletions. At the same time we had submitted an abstract about T-cell dysfunction in small-cell lung cancer, a tumour that responds poorly to checkpoint immunotherapy. Our own feasibility audit on 28 July said plainly that the July work could not support the abstract's SCLC claims. So we built a dedicated SCLC line, with forty-six thousand T cells from forty-two donors. It classified well, but its normal class had one test donor, and that is worth remembering. Sources: the repository README and the 28 July feasibility audit."""))

S.append(("plain", 1.2, """
<div class="kicker">II · August</div>
<h2>What we told the JSDP meeting in August</h2>
<ul class="pts">
  <li>We deleted and overexpressed 50 genes. Four genes passed in both directions in all three SCLC test patients: deleting them moved cells toward normal and overexpressing moved them away. They were TIM-3 (HAVCR2), TIGIT, CTLA-4 and IL7R, all linked to T-cell exhaustion or persistence. (Slide 18 shows why that pattern alone is not enough.)</li>
  <li>In independent SCLC tissue (spatial transcriptomics), an antigen-presentation programme the model pointed to tracked T-cell abundance: ρ = 0.361, 7.95 standard deviations above a null of 100 random gene sets matched on mean expression. The broader dysfunction benchmark gave ρ = 0.161.</li>
  <li>The poster flagged one thing as open. Along an axis built from immune-checkpoint genes, the model placed the states as Normal &lt; SCLC &lt; LUAD, which is not what we expected.</li>
</ul>
<p class="note">We closed the talk with a question: "if SCLC T cells are not exhausted, what are they, and why does ICI still fail?" (ICI: immune checkpoint inhibitors.)</p>
""", """In August we presented this at the JSDP meeting. Four genes passed in both directions, deletion toward normal and overexpression away, in every SCLC test donor, and an antigen-presentation programme the model pointed to tracked T-cell abundance in independent tissue. We also put an odd result on the poster as an open question: on the checkpoint axis the model ordered the states normal, then SCLC, then LUAD. We ended the talk by asking what SCLC T cells are if they are not exhausted. That question is what drove the next month. Sources: the JSDP talk and poster in the talks repository."""))

S.append(("plain", 1.2, """
<div class="kicker">II · Late August to mid September</div>
<h2>Then we tested our own story, and it did not hold</h2>
<div class="three">
  <div class="card"><h3>Not a line</h3><p>The three cell states form a triangle in the model's space (SCLC interior angle 61.94°). So there is no single exhaustion axis to move along.</p></div>
  <div class="card"><h3>Inside the null</h3><p>Overexpressing an exhaustion gene programme in SCLC cells moved them toward LUAD by +0.0873. Expression-matched random gene sets did almost as much, +0.0816 on average; one-sided p = 0.4286. Our shift was no bigger than random genes give.</p></div>
  <div class="card"><h3>One patient</h3><p>An apparent conflict between two analyses came from one SCLC patient holding 74.9% of the SCLC test cells. Counting patients instead (19 vs 22): p = 0.216.</p></div>
</div>
""", """We then tried to test the ordering properly, and it did not survive. First, the three states do not lie on a line at all; they form a triangle. Second, when we overexpressed the whole exhaustion programme, SCLC cells did move toward LUAD, but expression-matched random gene sets moved them almost as far: plus 0.0873 against plus 0.0816, p 0.43. Third, two of our analyses seemed to disagree, and the disagreement turned out to be a single patient who contributed three quarters of the SCLC test cells. Counted by donor, the difference was not significant. Two lessons came out of this: compare every shift with a null, and count patients, not cells. Sources: RESULTS_T3, T4 and T6 in the repository."""))

S.append(("plain", 1.2, """
<div class="kicker">II · September</div>
<h2>Our strongest hits were not what they looked like</h2>
<div class="two">
  <div class="card"><h3>The top of the screen</h3>
    <p>S100A8 had a false discovery rate of 1.45 × 10<sup>−224</sup>. Yet across S100A8 and S100A9 in six state-to-state comparisons (12 rows), deleting and overexpressing moved cells the <i>same</i> way in 9. A dose-responsive driver cannot do that.</p>
    <p>Of the top 120 rows, 55 were flagged as likely ambient RNA from surrounding tissue; none was one of our T-cell anchor genes.</p></div>
  <div class="card"><h3>The July "normal" class</h3>
    <p>None of the 18 studies contributed both normal and tumour T cells. "Normal versus tumour" had partly been "these studies versus those studies".</p>
    <p>The July adenocarcinoma class was also 27.4% metastatic tissue.</p></div>
</div>
""", """In September we audited the whole-genome screen. Its most significant hits, S100A8 and S100A9, failed the simplest sanity check: removing and adding the gene pushed cells in the same direction. Many of the top hits looked like ambient RNA, transcripts from surrounding tissue that end up in a T cell's droplet. Then we found that the July classifier's normal class came from entirely different studies than its tumour classes, so the model could have been learning study identity. I should add that we first confused two different classifiers while working this out, which delayed the finding. Sources: the S100A8/S100A9 cross-reference report and the July METHODS file."""))

S.append(("plain", 1.3, """
<div class="kicker">II · 22 to 25 September</div>
<h2>We found two faults in our own instrument</h2>
<div class="two">
  <div class="card"><h3>Two arms, two cell sets</h3>
    <p>The August panel overexpressed each gene into all 2,424 SCLC test cells but deleted it only in cells that carried it (202 to 1,131). The arms were scored on different cells.</p>
    <p>We added a caveat to the four August hits, "a qualifier, not a retraction". The panel has not been rerun.</p></div>
  <div class="card"><h3>A silent default</h3>
    <p>When given a list of genes, Geneformer's own code inserts an overexpressed gene into every cell, whether or not the cell expressed it: 14,738 of 15,179 calls in our rebuilt study.</p>
    <p>We had written this down on 22 September and missed it three days later. Our amendment says so: "Prior art in this repository, missed."</p></div>
</div>
""", """This was the most uncomfortable week. We discovered that the August panel had scored deletion and overexpression on different sets of cells, so the concordance part of the four August hits rested on unequal comparisons. We did not retract them, because the deletion evidence stands, but we attached a caveat and said the panel has not been rerun. The cause is a default in Geneformer itself: when given a list of genes, its overexpression mode inserts each gene into every cell. We had documented exactly this on 22 September and fixed our panel runner. Then, on 25 September, we found both the consequence for the August panel and that our rebuilt study had hit the same default. We recorded that in the amendment in those words. Sources: the 25 September correction in the talk sources file, and Amendment 3h."""))

S.append(("plain", 1.2, """
<div class="kicker">II · Late September</div>
<h2>So we rebuilt the experiment, and wrote the rules down</h2>
<ul class="pts">
  <li><b>A cleaner design:</b> 43 adenocarcinoma patients, each with tumour and normal T cells, 100 cells per tissue, the larger Geneformer model (316 million parameters). The classifier reached 0.825 balanced accuracy, with all 43 patients above chance.</li>
  <li><b>The July list fell away:</b> 13 of its 15 genes could not be tested in T cells at all (keratins, a mucin, a haemoglobin chain). Of 34 testable T-cell genes, 13 gave stable calls.</li>
  <li><b>A warning sign:</b> even the matched control genes showed deletion and overexpression shifts anti-correlated, ρ = −0.62.</li>
  <li><b>28 September:</b> the lab adopted a written standard for judging ISP (ISP-STD-1). Its worked example asked whether S100 genes with high ambient-RNA risk beat their matched controls more than low-risk S100 genes do. The answer was negative in both contrasts (p = 6/70 and 34/70).</li>
</ul>
""", """By late September we rebuilt the experiment around patients rather than cells: forty-three patients, each contributing tumour and normal T cells, equal numbers per tissue. The classifier still worked well. Most of the July gene list turned out to be epithelial and blood genes that are barely present in T cells, which tells us what the July screen had really been reading. A curated T-cell panel gave thirteen stable calls. But the control genes themselves showed a strong anti-correlation between deletion and overexpression, which made us wonder whether that pattern was generic. And on 28 September we wrote down the standard that the rest of this talk is about. Sources: the balanced-donor IMRaD report, the ISP-STD-1 standard and the S100 result file."""))

S.append(("section", 0.2, """<div class="partno">III</div><h1>Rules we learned</h1><p class="sub">How we now judge an ISP result (ISP-STD-1)</p>""",
          """Each of the six rules that follow answers one of the moments I just described."""))

S.append(("plain", 1.2, """
<div class="kicker">III · Rule 1</div>
<h2>File the voyage plan before you sail</h2>
<div class="split even">
  <div>
    <p class="lead">Before any output exists, we write down the test, its predicted direction, whether it is one- or two-sided, the significance threshold (alpha), and the <b>smallest p-value the test can actually reach</b> at our sample size. We also fix the controls, the budget and the words we will use for each outcome. Someone independent checks it, and the sign-off names file hashes.</p>
    <p class="why">Why: in August we read meaning into an ordering before we had a test for it.</p>
  </div>
  <div class="box">
    <div class="boxhead">From this week</div>
    <p>The colorectal (E2) test uses 13 lung reference genes, of which 10 are <b>expected</b> to be testable in colon, so the expected n = 10. At n = 10 a one-sided binomial test needs <b>at least 9 of 10</b> genes to agree (P = 11/1024 = 0.011; 8 of 10 gives 0.055). If n ends at 9, the bar is 8 of 9. We wrote the rule down before any number existed.</p>
    <p>The first review of the E2 plan was not passed: it claimed an unchanged software environment, but pandas had been downgraded since the lung runs. The record was corrected before the GPU started.</p>
  </div>
</div>
""", """Pre-registration is the rule that sounds most bureaucratic and has saved us most often. Writing the test down first stops us from choosing it after seeing the data, which is what we came close to doing with the August ordering. The attainability check matters with small samples, where some tests cannot reach p below 0.05 at all. For the colorectal comparison, ten genes are expected to be testable; at that n agreement has to reach nine of ten, and the exact bar is set by the number actually tested, under a rule fixed in advance. The first review of that plan failed for a small but real reason, an inaccurate statement about the software environment. Source: E2_REGISTRATION.md at commit 8b11d5d, section 6.3."""))

S.append(("plain", 0.9, """
<div class="kicker">III · Rules 2 and 3</div>
<h2>Check the compass, then check that an anchored boat stays still</h2>
<div class="two">
  <div class="card"><h3>Classifier gate</h3>
    <p>If the fine-tuned model cannot tell tumour from normal in patients it never saw, there is no axis to measure along.</p>
    <p class="rule">Pass: pooled held-out balanced accuracy ≥ 0.60 <i>and</i> an exact two-sided sign test over patients, p ≤ 0.05. Fail: stop before any perturbation.</p>
    <p class="why">Why: the July classifier could not be told apart from a study classifier.</p></div>
  <div class="card"><h3>No-op gate</h3>
    <p>Run the pipeline twice on identical input with no edit, as two independent forward passes.</p>
    <p class="rule">Pass: every per-cell shift is exactly 0, or within measured noise.</p>
    <p class="why">Why: in gene-list mode, our code once overexpressed into every cell without our asking (14,738 of 15,179 calls).</p></div>
</div>
""", """Two checks come before any perturbation. The classifier gate asks whether the compass works on patients the model has never seen; if it fails, we stop. The July classifier is the reason we now insist on held-out patients and paired tissues. The no-op gate asks whether the boat moves when nothing has been done to it. Any non-zero shift means the pipeline itself is producing movement that would later be read as an effect. Sources: ISP-STD-1 clause B3 and the classifier rule in each registration."""))

S.append(("plain", 0.9, """
<div class="kicker">III · Rule 4</div>
<h2>Compare against boats of the same build</h2>
<div class="split even">
  <div>
    <p class="lead">Each tested gene is compared with at least 20 control genes matched within 0.5 log<sub>2</sub> on detection and within 5 rank-percentile points. If we cannot find 20, the gene is <i>not estimable</i>; we never widen the tolerances. Patients, not cells, are the unit. A result must survive dropping any single control, and hold in at least 95% of 10,000 bootstrap draws.</p>
    <p class="why">Why: S100A8 topped the screen on significance alone, and one patient once carried three quarters of the SCLC test cells.</p>
  </div>
  <div class="box"><div class="boxhead">Why matching matters</div>
    <p>Highly detected genes move cells more, whatever they do biologically. A gene is only interesting if it moves cells <i>more than genes that are detected as often</i>.</p>
    <p class="small">In the lung panel, 318 control genes were matched to the curated genes.</p></div>
</div>
""", """A raw shift means little on its own, because genes that are present in many cells move them more simply by being there. So every gene is compared with twenty or more genes that look like it in detection and rank, and if we cannot find twenty we say so rather than loosening the match. We count patients, not cells, for the reason you saw on the T6 slide. And a result has to be stable when we drop controls or resample them. These are clauses B1, B5 and B8 of the standard."""))

S.append(("current", 1.8, f"""
<div class="kicker">III · Rule 5 · the current</div>
<div class="split">
  <div>
    <h2>Every boat drifts. Measure the drift before claiming a nudge.</h2>
    <p>The control genes' −0.62 made us ask: what do <b>random genes</b> do? We ran the full pipeline on random genes with no known link to tumour versus normal (lung, 43 patients). Each dot is one random gene: x = how far deleting it moves cells toward normal, y = how far overexpressing it does (as ranks).</p>
    <p class="big-num">ρ = −0.593 <span>(N = 100)</span></p>
    <p class="big-num">ρ = −0.608 <span>(N = 200, confirming)</span></p>
    <p class="small">One-sided p at the floor of 100,000 permutations (≤ 1e-5); stable in every leave-one-gene-out and all 10,000 bootstrap draws.</p>
    <p class="why">Why: even our matched control genes anti-correlated (ρ = −0.62).</p>
  </div>
  <figure><img src="{img('null_scatter.png')}" alt="null scatter"></figure>
</div>
""", """This is the result I most want you to remember. A gene that moves a cell toward normal when deleted and away when overexpressed looks like a meaningful, dose-consistent effect. After seeing the control genes, we asked what random genes do. We drew genes at random from those detectable in lung tumour T cells and ran the identical pipeline. Their deletion and overexpression shifts were strongly anti-correlated: minus 0.593 for the registered hundred, minus 0.608 when extended to two hundred. Honestly, we had half expected this after the controls, but seeing it in genes chosen by a random seed made it concrete. The p-value sits at the floor of the permutation test, so we report it as at most ten to the minus five. Sources: a5_primary_result_v2.json and n200_combined_result_v2.json, hashes a00ccb2f and c9e56026."""))

S.append(("plain", 1.0, """
<div class="kicker">III · Rule 5 · what the current does and does not mean</div>
<h2>Opposite signs for delete and overexpress are not evidence of specificity</h2>
<div class="two">
  <div class="card"><h3>What it shows</h3>
    <p>An anti-correlation between deletion and overexpression exists for genes in general, in this model and this design. It is part of the baseline.</p>
    <p>A validity check on the study's own control genes (308 of the 318 had enough data) gave ρ = −0.658, the same sign as the −0.62 seen earlier. We compare the two by sign only.</p></div>
  <div class="card"><h3>What it does not show</h3>
    <p>It does not erase the panel result: 13 of 34 testable T-cell genes still beat their matched controls.</p>
    <p>It narrows what that result can mean. Opposite signs alone are expected; an unusual <i>size</i> of effect, measured against this null, is the more specific evidence.</p></div>
</div>
<p class="foot">Now in the standard as clause B7. The random genes are "eligible genes detectable in LUAD tumour T cells", not the whole genome.</p>
""", """I want to be careful about what follows. The null result does not overturn the curated panel. What it removes is an argument we were tempted to make in August: that a gene behaving in opposite directions under deletion and overexpression must be acting specifically. Random genes do that too. The validity check on our control genes recovered the same sign, and we compare it with the earlier figure only by sign, because the two are computed differently. And we never call these genes genome-wide. Sources: IMRaD report rows P22 to P25."""))

S.append(("plain", 0.9, """
<div class="kicker">III · Rule 6</div>
<h2>Write the log in a fixed vocabulary. Never "no effect".</h2>
<div class="stamps">
  <span class="stamp pos">positive</span><span class="stamp">negative</span><span class="stamp">opposite_direction</span><span class="stamp">not_estimable</span>
  <span class="stamp">control_draw_sensitive_open</span><span class="stamp warn">no_op_failed</span><span class="stamp">not_run_by_design</span><span class="stamp">stopped_not_analysed</span>
</div>
<p class="why">Why: in August we called an unexplained ordering a finding, and later had to add "a qualifier, not a retraction" to our hits.</p>
<p class="lead narrow">A <b>negative</b> result means the registered criterion was not met. We report it with its direction, p and n, because a small study can miss a real effect. A result in the wrong direction is labelled <b>opposite_direction</b> and never counted as support. A result that is right in direction but unstable across control draws stays <b>open</b>.</p>
""", """The last rule is about language. Every outcome gets one of eight labels fixed before the run. The phrase we never use is "no effect". A negative result only means this test, at this size, did not meet its criterion; we report its direction, p and n so a reader can judge what it rules out. The S100 run was negative in exactly this sense. Fixed words stop us drifting into stronger language than the data support. Source: ISP-STD-1 clause A6."""))

S.append(("plain", 0.8, """
<div class="kicker">III · Where the chart ends</div>
<h2>What ISP cannot show, however clean the result</h2>
<div class="three">
  <div class="card"><h3>Cause</h3><p>A shift in embedding space is the model's geometry, not a mechanism. No gene is shown to regulate T-cell state.</p></div>
  <div class="card"><h3>Origin of the signal</h3><p>The classifier may read T-cell state, ambient RNA from the surrounding tissue, or the CD4:CD8 mix. The gates cannot tell these apart.</p></div>
  <div class="card"><h3>Ground truth</h3><p>Accuracy needs a real perturbation screen in the same cell type (standard section D). We do not yet have one for these T cells.</p></div>
</div>
""", """Even a result that passes every rule has limits. It tells us how the model responds to an edited input, not that the gene regulates anything in a living cell. The classifier may be reading T-cell state, ambient RNA or the balance of CD4 and CD8 cells, and our checks cannot separate these. And we cannot talk about accuracy in the usual sense until we compare with an experimental perturbation screen in T cells, which we have not yet done."""))

S.append(("section", 0.2, """<div class="partno">IV</div><h1>This week</h1><p class="sub">Does any of this hold outside lung?</p>""",
          """With that history and those rules in place, here is where we are this week."""))

S.append(("plain", 1.3, f"""
<div class="kicker">IV · Does the compass work in new waters?</div>
<div class="split">
  <div>
    <h2>Colorectal cancer (Pelka et al. 2021): the classifier gate passed</h2>
    <p class="lead">We took 19 patients whose tumour and normal samples were both unsorted, 100 T cells per patient per tissue, and fine-tuned <b>new models</b> from the base Geneformer-V2-316M, one per fold. These are not the lung models, and this is not zero-shot.</p>
    <p class="lead">Pooled balanced accuracy was <b>0.904</b>, with <b>19 of 19</b> patients above chance (lowest 0.655) and a two-sided sign test p = 1/262,144. Folds ranged from 0.866 to 0.935, and the no-op gate's largest shift was 0.0.</p>
    <p class="note">This shows the tumour/normal split is learnable in colon. It does not show that the lung classifier transfers.</p>
  </div>
  <figure><img src="{img('gate_strip.png')}" alt="gate strip"></figure>
</div>
""", """The colorectal study repeats the whole design in a different tissue, using public data from Pelka and colleagues. We kept nineteen patients whose samples were processed the same way in both tissues. Five new models were trained from the base weights. Every patient was above chance, and the lowest was 0.655. The lung value of 0.825 is shown only for context; one study against five, different processing and fewer patients mean we should not read the difference biologically. And because these are new models, this says nothing about whether the lung models transfer. Sources: classifier_gate.json and noop_gate.json at commit 2c104ab, and the interim report of 1 October, which passed internal review."""))

S.append(("plain", 1.5, """
<div class="kicker">IV · Results, after review</div>
<h2>Colorectal perturbation screen: same direction as lung but not stable; the lung gene pattern did not replicate</h2>
<div class="two">
  <div class="card"><h3>What the run found (finished 10:20 JST, 2 October)</h3>
    <p><b>Random genes (primary).</b> ρ = −0.245 over 100 genes, one-sided p = 0.0067; every leave-one-out test passes, but only 78% of 10,000 resamples stay significant, against the registered 95%. Status <code>control_draw_sensitive_open</code>: direction as in lung, not stable; open. Lung gave −0.593.</p>
    <p><b>Lung reference genes.</b> 3 of 10 keep their lung direction, where 9 were needed (p = 0.95): <code>pattern_not_replicated</code>. One panel gene, PRF1, is dose-concordant in colon; it was open in lung.</p>
    <p class="small">369 genes × 19 patients × delete and overexpress; 32.6 GPU-hours of the 52 registered. A colon–lung difference cannot be put down to tissue alone.</p></div>
  <div class="card slot"><h3>What each registered outcome would tell us</h3>
    <p><b>Random genes (primary).</b> Status <code>positive</code>: the anti-correlation appears in colon too, so it is more likely a property of the model and this design than of lung. <code>negative</code> (the anti-correlation did not appear) or <code>opposite_direction</code>: cannot be put down to tissue alone, since study, protocol, chemistry and the fine-tune all differ. <code>control_draw_sensitive_open</code>: stays open. <b>This is the outcome.</b></p>
    <p><b>Lung reference genes.</b> <code>pattern_holds</code> if enough keep their lung direction (at n = 10, at least 9); <code>pattern_not_replicated</code> otherwise (<b>the outcome</b>); <code>not_testable</code> if fewer than 5 can be tested. Holding would not make any gene a regulator.</p></div>
</div>
""", """The colorectal run finished at 10:20 Japan time on 2 October, inside the compute we registered, and the results passed internal review before I put them here. The primary question was whether random genes are anti-correlated in colon as in lung. They are, in the same direction: the rank correlation was minus 0.245, with a one-sided p of 0.0067, and no single gene carries it. But the pattern stayed significant in only 78 percent of resamples, short of the 95 percent we set in advance, so by our own rule it is reported as open. For the lung reference genes, three of ten kept their lung direction where nine were needed, so the lung pattern did not replicate; seven opposite signs is within what chance gives, so this is not a reversal. The right-hand card is the set of readings we fixed before the run, with the two outcomes that occurred marked. Neither difference from lung can be put down to tissue, because study, sample handling, chemistry, the fold models and the number of patients all differ. Sources: the E2 results report and the H2b, H2c and Panel B result files on geneformer-lung-tcell main, merge 4cce44a, and E2_REGISTRATION.md sections 6.2, 6.3 and 7."""))

S.append(("section", 0.2, """<div class="partno">V</div><h1>Uncharted waters</h1><p class="sub">Open questions, and how to join</p>""",
          """We have more open questions than people. Each task on the next slides is sized so that one person could start this month."""))

S.append(("plain", 1.1, """
<div class="kicker">V · Open questions</div>
<h2>What we do not know yet</h2>
<ol class="qs">
  <li><b>Why does the current exist?</b> Is the delete/overexpress anti-correlation a property of rank encoding, of the model, or of lung biology? (The colorectal run gave a first answer: same direction as lung, but not stable.)</li>
  <li><b>Does the lung compass transfer?</b> Applying the frozen lung models to an independent lung cohort is planned, but the one candidate's data are not yet accessible to us.</li>
  <li><b>What does the classifier read?</b> T-cell state, ambient RNA, or CD4:CD8 composition?</li>
  <li><b>Where is ground truth?</b> No T-cell perturbation screen has yet been matched to our readout.</li>
  <li><b>Positive controls.</b> We have no registered genes known to drive this tumour/normal T-cell axis, so a negative result is hard to interpret.</li>
</ol>
""", """These are the gaps. The anti-correlation needs an explanation; one idea is that deleting a token and moving it to the front are near-opposite operations for any gene, simply because of how rank encoding works. We do not know whether the lung models transfer. We cannot say what the classifier reads. We have no experimental ground truth in these T cells. And without positive controls, a negative result could just mean the test was insensitive. The August question, what SCLC T cells are if not exhausted, is also still open."""))

S.append(("plain", 1.2, """
<div class="kicker">V · Join the crew</div>
<h2>Six ways in, from an hour to a month</h2>
<div class="tasks">
  <div class="task"><span class="t">1 afternoon</span><b>Re-derive a gate.</b> Recompute the colorectal pooled balanced accuracy and sign-test p from <code>classifier_gate.json</code>. No GPU.</div>
  <div class="task"><span class="t">1 afternoon</span><b>Find the floor.</b> For a planned n, compute the smallest attainable p of a sign test and of a Wilcoxon test, with ties. This is the attainability check.</div>
  <div class="task"><span class="t">1 week</span><b>Propose positive controls.</b> From the literature, list genes known to shift T cells between tumour and normal states, with sources.</div>
  <div class="task"><span class="t">1 week</span><b>Find ground truth.</b> Survey published CRISPR or Perturb-seq screens in primary human T cells that could be matched to our readout.</div>
  <div class="task"><span class="t">2–4 weeks</span><b>Explain the current.</b> Test on synthetic sentences whether rank encoding alone produces the anti-correlation.</div>
  <div class="task"><span class="t">1 hour</span><b>Open a door.</b> Help us check whether the independent lung cohort's data package (a Code Ocean capsule) contains per-cell metadata.</div>
</div>
""", """If any of this interests you, here are ways in. The first two need a laptop and an afternoon, and they teach the two habits that would have saved us the most trouble since July: recompute numbers from the source file, and know the smallest p-value your test can reach before running it. The next two are literature tasks that fill our biggest gaps. The fifth is a small research project that could become a short paper. The last is practical: one dataset is packaged in a way our scripts cannot open, and someone with a browser can tell us what is inside. Please come and talk to me afterwards."""))

S.append(("plain", 0.3, """
<div class="kicker">Glossary</div>
<h2>Words on the chart</h2>
<dl class="gloss">
  <dt>Geneformer</dt><dd>A transformer pretrained on single-cell transcriptomes, each cell written as a ranked gene list.</dd>
  <dt>Token</dt><dd>One gene in a cell's ranked list: the model's word.</dd>
  <dt>Transformer</dt><dd>A neural network that reads sequences, here gene lists.</dd>
  <dt>Donor</dt><dd>The patient a sample came from; we use donor and patient interchangeably.</dd>
  <dt>Embedding</dt><dd>The model's internal coordinates for a cell; nearby cells look alike to the model.</dd>
  <dt>Fine-tuning</dt><dd>Further training on one labelled task, here tumour vs normal T cells.</dd>
  <dt>ISP</dt><dd>In-silico perturbation: delete or overexpress a gene token and measure the embedding shift toward a goal.</dd>
  <dt>Cosine shift</dt><dd>The change in a cell's similarity to the goal after an edit; positive means closer to normal.</dd>
  <dt>Goal centroid</dt><dd>The average embedding of a donor's own normal-tissue T cells.</dd>
  <dt>Balanced accuracy</dt><dd>The mean of the true-positive and true-negative rates; 0.5 is chance.</dd>
  <dt>Ambient RNA</dt><dd>Transcripts from surrounding tissue captured in a cell's droplet.</dd>
  <dt>Matched controls</dt><dd>Genes chosen to resemble the tested gene in detection and rank, used as its comparison set.</dd>
  <dt>Null control</dt><dd>The same pipeline on random genes, to measure the effect expected by default.</dd>
  <dt>Pre-registration</dt><dd>Writing down the test, its threshold and its wording before any result exists.</dd>
  <dt>Permutation floor</dt><dd>The smallest p a permutation test can report: 1/(permutations + 1).</dd>
</dl>
""", """The glossary is here for reference and on the handout. I will not read it aloud."""))

S.append(("end", 0.3, """
<h1 class="big">The current is not the enemy.<br>It is the baseline.</h1>
<p class="sub">We learned to measure it first, then claim the nudge.</p>
<div class="byline">Sources for every number: SOURCES.md in this talk's folder · ISP-STD-1 · E2 registration (commit 8b11d5d)</div>
""", """To close: looking back over three months, almost every correction came from measuring something we had taken for granted, such as the study behind a class, the cells behind an arm, the patient behind a shift, or the drift behind a nudge. The anti-correlation in random genes is not a failure of the method. It is the baseline any claimed effect has to exceed. In colon the baseline points the same way but is not yet stable, so whether it belongs to the model or to lung is still open. Thank you; I am happy to take questions, and to talk about any of the entry tasks."""))


CSS = f"""
:root{{--ink:#13233a;--paper:#f4efe4;--teal:#2a7f7a;--brass:#b8862b;--coral:#c4553a;--foam:#4f9d8a;--mist:#8a96a6}}
@page{{size:1280px 752px;margin:0 0 32px 0;background:var(--paper);
  @bottom-center{{content:"Page " counter(page) " of " counter(pages);font-family:"Avenir Next","Helvetica Neue",sans-serif;font-size:13px;color:#8a96a6}}}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:#0d1828;color:var(--ink);font-family:"Avenir Next","Helvetica Neue",Arial,sans-serif}}
.slide{{width:1280px;height:720px;position:relative;overflow:hidden;background:var(--paper);padding:56px 72px 40px;margin:24px auto;page-break-after:always;break-after:page}}
.slide::before{{content:"";position:absolute;inset:0;background:url({CONT_B}) center/cover no-repeat;opacity:.55;pointer-events:none}}
.slide.current::before,.slide.title::before,.slide.end::before{{background-image:url({CONT_A});opacity:.9}}
.slide.section{{background:var(--ink);color:var(--paper);display:flex;flex-direction:column;justify-content:center}}
.slide.section::before{{background-image:url({CONT_A});opacity:.35;filter:invert(1)}}
.slide>*{{position:relative}}
h1,h2,h3{{font-family:"Iowan Old Style",Georgia,serif;font-weight:600;margin:0 0 14px;line-height:1.12}}
h1{{font-size:60px}} h1.big{{font-size:74px;margin-top:70px}} h2{{font-size:36px;max-width:1100px}} h3{{font-size:23px;color:var(--teal)}}
.section h1{{font-size:76px;color:var(--paper)}} .partno{{font-family:"Iowan Old Style",Georgia,serif;font-size:120px;color:var(--brass);line-height:1}}
.kicker{{font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:var(--brass);margin-bottom:10px;font-weight:600}}
.sub{{font-family:"Iowan Old Style",Georgia,serif;font-size:27px;color:#3d4d63;margin:6px 0 0}} .section .sub{{color:#c9d3df}}
.byline{{position:absolute;left:72px;bottom:48px;font-size:20px}} .byline span{{font-size:16px;color:#55647a}}
.rose{{position:absolute;right:90px;top:70px;font-size:120px;color:var(--brass);opacity:.8}}
p,li,dd{{font-size:20px;line-height:1.42}} .small{{font-size:16px;color:#3d4d63}} .note{{font-size:18px;color:var(--teal);font-style:italic}}
.pts{{padding-left:22px;margin:10px 0}} .pts li{{margin:0 0 10px}} .narrow{{max-width:1000px}}
.three{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:22px}} .two{{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:16px}}
.card{{background:rgba(255,255,255,.62);border:1px solid #d9cfbb;border-radius:14px;padding:22px 24px}} .card.accent{{border:2px solid var(--brass)}}
.card .num{{font-family:"Iowan Old Style",Georgia,serif;font-size:42px;color:var(--brass)}}
.three.five{{grid-template-columns:repeat(5,1fr);gap:16px}} .five .card{{padding:18px 18px}} .five p{{font-size:17px}}
.lead{{font-size:21px;line-height:1.45;max-width:1120px}} .why{{font-size:17px;color:var(--coral);font-style:italic;margin-top:8px}}
.quote{{font-family:"Iowan Old Style",Georgia,serif;font-style:italic;font-size:21px;color:var(--ink)}}
.rule{{font-size:18px;border-left:3px solid var(--teal);padding-left:10px}}
.foot{{position:absolute;left:72px;right:72px;bottom:34px;font-size:17px;color:#3d4d63}}
.split{{display:grid;grid-template-columns:1fr 1.05fr;gap:30px;align-items:center}} .split.even{{grid-template-columns:1.1fr 1fr;align-items:start}}
figure{{margin:0}} figure img{{width:100%;border-radius:10px;border:1px solid #d9cfbb}}
.box{{background:var(--ink);color:var(--paper);border-radius:14px;padding:22px 26px}} .box p{{font-size:18px}} .box .small{{color:#c9d3df}}
.boxhead{{font-size:14px;letter-spacing:.12em;text-transform:uppercase;color:var(--brass);margin-bottom:8px;font-weight:600}}
.sentence{{display:flex;gap:10px;margin:26px 0 6px;flex-wrap:wrap}}
.tok{{font-family:"Menlo",monospace;font-size:24px;padding:10px 16px;border-radius:8px;color:#fff;background:var(--teal)}}
.t2{{opacity:.92}}.t3{{opacity:.84}}.t4{{opacity:.76}}.t5{{opacity:.68}}.t6{{opacity:.6}}.t7{{opacity:.52}}.t8{{background:var(--mist)}}
.caption{{font-size:15px;color:#55647a;margin:0 0 14px}}
.big-num{{font-family:"Iowan Old Style",Georgia,serif;font-size:46px;margin:8px 0;color:var(--ink)}} .big-num span{{font-size:22px;color:#55647a}}
.stamps{{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0 22px}}
.stamp{{font-family:"Menlo",monospace;font-size:19px;padding:8px 14px;border:2px solid var(--ink);border-radius:6px;transform:rotate(-1.2deg);background:rgba(255,255,255,.6)}}
.stamp.pos{{border-color:var(--teal);color:var(--teal)}} .stamp.warn{{border-color:var(--coral);color:var(--coral)}}
.slot{{border:2px dashed var(--brass)}} .placeholder{{color:var(--brass);font-style:italic}}
.qs li{{font-size:20px;margin-bottom:12px;max-width:1080px}}
.tasks{{display:grid;grid-template-columns:1fr 1fr;gap:14px 26px;margin-top:10px}}
.task{{font-size:17.5px;line-height:1.38;background:rgba(255,255,255,.62);border-left:4px solid var(--teal);padding:10px 14px;border-radius:6px}}
.task .t{{display:inline-block;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--brass);margin-right:8px;font-weight:600}}
code{{font-family:Menlo,monospace;font-size:.9em}}
.gloss{{display:grid;grid-template-columns:230px 1fr;gap:6px 22px;margin-top:8px}} .gloss dt{{font-family:"Iowan Old Style",Georgia,serif;font-weight:600;font-size:19px}} .gloss dd{{margin:0;font-size:17px;line-height:1.35}}
.pnum{{position:absolute;right:28px;bottom:14px;font-size:13px;color:var(--mist)}} .section .pnum{{color:#55647a}}
.notes{{display:none;width:1280px;margin:-12px auto 24px;background:#fffdf7;border-radius:0 0 12px 12px;padding:16px 26px;font-family:"Iowan Old Style",Georgia,serif;font-size:17px;line-height:1.5;color:#26354a}}
body.shownotes .notes{{display:block}}
@media screen{{body.deck .slide{{display:none;margin:0 auto}} body.deck .slide.on{{display:block}} body.deck .slide.section.on{{display:flex}}
  body.deck{{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh}}
  .help{{color:#8a96a6;font-size:13px;text-align:center;margin:10px}}}}
@media print{{html,body{{background:var(--paper)}} .slide{{margin:0}} .notes,.help{{display:none!important}} .pnum{{display:none}}}}
"""

JS = """
const sl=[...document.querySelectorAll('.slide')], nt=[...document.querySelectorAll('.notes')];
let i=0; document.body.classList.add('deck');
function show(k){i=Math.max(0,Math.min(sl.length-1,k));sl.forEach((s,j)=>s.classList.toggle('on',j===i));
  nt.forEach((n,j)=>n.style.display=(document.body.classList.contains('shownotes')&&j===i)?'block':'none');
  try{history.replaceState(null,'','#'+(i+1))}catch(e){}}
document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))show(i+1);
  else if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);
  else if(e.key==='n'||e.key==='N'){document.body.classList.toggle('shownotes');show(i)}
  else if(e.key==='Home')show(0); else if(e.key==='End')show(sl.length-1);});
document.addEventListener('click',e=>{if(e.target.closest('.notes'))return; show(e.clientX>innerWidth/2?i+1:i-1)});
show((parseInt(location.hash.slice(1))||1)-1);
"""


def build():
    n = len(S)
    parts = []
    for k, (kind, mins, body, notes) in enumerate(S, 1):
        parts.append(f'<section class="slide {kind}">{body}<div class="pnum">{k} / {n}</div></section>')
        parts.append(f'<aside class="notes"><b>Speaker notes, slide {k} (about {mins:g} min).</b> {html.escape(notes)}</aside>')
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reading the Current</title><style>{CSS}</style></head><body>
{''.join(parts)}
<div class="help">← → to move · N for speaker notes · click right or left half · print or PDF: slides.pdf</div>
<script>{JS}</script></body></html>"""
    with open(os.path.join(OUT, "slides.html"), "w") as f:
        f.write(doc)
    total = sum(s[1] for s in S)
    md = ["# Reading the Current: speaker notes", "",
          f"Lab progress report, 1 October 2026. Kaisar Dauyey · Shinji Nakaoka. {n} slides, about {total:.0f} minutes of talk, then 5 to 10 minutes of discussion. Every number is sourced in `SOURCES.md`.", ""]
    for k, (kind, mins, body, notes) in enumerate(S, 1):
        import re
        title = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body, re.S)
        t = re.sub(r"<[^>]+>", " ", title.group(1)).replace("  ", " ").strip() if title else kind
        md += [f"## Slide {k}. {html.unescape(t)} (about {mins:g} min)", "", notes, ""]
    with open(os.path.join(OUT, "speaker-notes.md"), "w") as f:
        f.write("\n".join(md))
    print("slides", n, "minutes", round(total, 1))


if __name__ == "__main__":
    build()
