"""Build 'Evaluating in-silico perturbation with Geneformer' (lab progress report, version 4, 2026-10-02).

Version 3 keeps the structure of version 2 (one point per slide, stated in the title; a progress bar; one
colour per verdict: teal passed, coral failed, amber not yet known; one icon per check) and adds diagrams
of the method, data figures from the external-cohort check (E0) and the colon classifier gate (E2), and
four slides on bulk RNA-seq, including a first test of a bulk network model against measured knockouts.
Version 4 adds a part on transposable elements (the Geneformer_TE project): its design, two completed
analyses in fish, the zebrafish ground truth and the TE arm of the Freimer T-cell knockout test.

Writes ../slides.html (self-contained: arrow keys move, N shows speaker notes) and ../speaker-notes.md.
WeasyPrint turns slides.html into ../slides.pdf. Every number is listed in ../SOURCES.md.
"""
import base64, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "..", "figures")
OUT = os.path.join(HERE, "..")


def img(name, alt):
    with open(os.path.join(FIGS, name), "rb") as f:
        return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" alt="{alt}">'


# ---------- icons (one per check) and verdict badges ----------
SVG = '<svg viewBox="0 0 48 48" class="ic" aria-hidden="true">{}</svg>'
ICONS = {
    1: SVG.format('<rect x="11" y="7" width="26" height="34" rx="3" fill="none" stroke="currentColor" stroke-width="3"/>'
                  '<path d="M17 18h14M17 25h14M17 32h9" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'),
    2: SVG.format('<path d="M8 32a16 16 0 0 1 32 0" fill="none" stroke="currentColor" stroke-width="3"/>'
                  '<path d="M24 32l8-11" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="24" cy="32" r="3" fill="currentColor"/>'),
    3: SVG.format('<circle cx="24" cy="24" r="16" fill="none" stroke="currentColor" stroke-width="3"/>'
                  '<path d="M16 20h16M16 28h16" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'),
    4: SVG.format('<path d="M24 8v30M12 38h24M10 16h28" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'
                  '<path d="M10 16l-5 11h10zM38 16l-5 11h10z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>'),
    5: SVG.format('<rect x="9" y="9" width="30" height="30" rx="6" fill="none" stroke="currentColor" stroke-width="3"/>'
                  '<circle cx="17" cy="17" r="2.8" fill="currentColor"/><circle cx="24" cy="24" r="2.8" fill="currentColor"/><circle cx="31" cy="31" r="2.8" fill="currentColor"/>'),
    6: SVG.format('<circle cx="17" cy="15" r="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M8 38c0-8 4-13 9-13s9 5 9 13" fill="none" stroke="currentColor" stroke-width="3"/>'
                  '<circle cx="32" cy="15" r="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M27 26c1-1 3-1 5-1 5 0 9 5 9 13" fill="none" stroke="currentColor" stroke-width="3"/>'),
}
CHECK = {1: "Write the test down first", 2: "Check the instrument", 3: "Same cells for both edits",
         4: "Beat look-alike genes", 5: "Beat random genes", 6: "Count patients, use fixed words"}


def chk(k, small=False):
    return f'<span class="chk{" sm" if small else ""}">{ICONS[k]}<span>{k}</span></span>'


def badge(kind, text):
    sym = {"pass": "✓", "fail": "✗", "open": "?"}[kind]
    return f'<span class="badge {kind}">{sym} {text}</span>'


PARTS = ["Question", "Method", "Lessons", "Criteria", "Status", "Bulk RNA-seq", "TEs", "Next"]


def bar(active):
    return '<div class="bar">' + "".join(
        f'<span class="{"on" if i == active else ("done" if i < active else "")}">{p}</span>' for i, p in enumerate(PARTS)) + "</div>"


S = []  # (kind, minutes, part index or None, html body, notes)


def add(kind, mins, part, body, notes):
    S.append((kind, mins, part, body, notes))


# ---------- 0. Question ----------
add("title", 0.5, None, """
<div class="kicker">Lab progress report · 2 October 2026 · version 4</div>
<h1 class="big">Evaluating in-silico perturbation with Geneformer</h1>
<p class="sub">Tumour-infiltrating T cells, the criteria a result must meet,<br>and a first look at transposable-element regulation</p>
<div class="byline">Kaisar Dauyey<br><span>Laboratory of Mathematical Biology, Hokkaido University, Japan</span></div>
""", """This report covers our work since July on Geneformer and in-silico perturbation in tumour-infiltrating T cells. It is the fourth version of the talk. Compared with the third, it adds a part on our second project, which applies the same perturbation logic to transposable elements, the repeated sequences that cells keep silenced. I introduce each term before I use it, so no prior knowledge of the model is assumed.""")

add("plain", 0.8, 0, """
<h2>Question: which genes, when perturbed in silico, shift tumour-infiltrating T cells toward the normal-tissue state?</h2>
<div class="qrow">
  <div class="qcell tum">T cell in a<br>lung tumour</div>
  <div class="qarrow">perturb one gene<br><b>→</b><br>in the model</div>
  <div class="qcell nor">T cell in the same<br>donor's normal lung</div>
</div>
<p class="lead">T cells infiltrating a tumour often differ in state from T cells in the same donor's normal tissue. Genes that maintain the tumour-associated state are candidate targets. Testing each gene experimentally is slow, so we use a pretrained model to prioritise genes, and we ask how far its predictions can be trusted.</p>
""", """T cells inside a tumour often show a different transcriptional state from T cells in the same donor's normal tissue. Our question is which genes, if perturbed, would move a tumour T cell toward its normal-tissue counterpart. Experimental screens can answer that, but they are slow and expensive, so we use a pretrained model to rank genes first. Most of this talk concerns how far those rankings can be trusted.""")

add("plain", 0.7, 0, """
<h2>Outline</h2>
<ol class="arc">
  <li><b>Method.</b> The analysis pipeline, rank-value tokenisation, fine-tuning and in-silico perturbation.</li>
  <li><b>Lessons.</b> Four results from July to September that did not hold, or held only in part.</li>
  <li><b>Criteria.</b> Six checks we now apply, each traced to one of those lessons.</li>
  <li><b>Status.</b> External cohorts, the colon study and what the evidence supports.</li>
  <li><b>Bulk RNA-seq.</b> A first test of perturbation prediction on bulk profiles, against measured knockouts.</li>
  <li><b>Transposable elements.</b> The same question for TE regulators: design, two fish analyses, and two ground-truth tests (zebrafish, T-cell knockouts).</li>
  <li><b>Next.</b> Criteria, open questions and the outline of a methods paper.</li>
</ol>
<p class="legend">Colour code: """ + badge("pass", "passed") + " " + badge("fail", "failed") + " " + badge("open", "not yet known") + """</p>
""", """The talk has seven parts, shown in the bar at the top of each slide. One colour code is used throughout: teal for a check that passed, coral for one that failed, amber for a question without an answer yet. Each of the six evaluation checks has its own icon, which reappears wherever that check applies.""")

# ---------- 1. Method ----------
add("plain", 1.0, 1, f"""
<h2>The analysis runs in eight steps, from a paired cohort to a donor-level call</h2>
<figure class="full">{img('pipeline.png', 'eight-step pipeline from cohort to call')}</figure>
<p class="lead narrow">Steps 1 to 4 build and test the instrument; no perturbation is run unless both gates pass. Steps 5 to 8 perturb, score and judge each gene.</p>
""", """This is the whole analysis on one slide. We start from donors who contributed both tumour and normal-tissue T cells, at least one hundred of each. Each cell is converted to a ranked gene list, a classifier is fine-tuned to separate tumour from normal T cells with donors held out, and two gates test the instrument. Only then do we perturb genes, score the shift of each cell toward the donor's normal centroid, compare that shift with control and random genes, and make a call at the donor level. The next slides go through the steps in order. Source: the colon study registration, sections 5 and 6.""")

add("plain", 1.1, 1, f"""
<h2>Geneformer encodes each cell as a list of genes ranked by relative expression</h2>
<div class="split wide"><div>
  <p class="lead">Counts are divided by the cell's total, then by each gene's median level across the pretraining corpus, and sorted. Housekeeping genes fall; genes unusually high in this cell rise.</p>
  <p class="lead">Genes with zero counts are left out. The ranked list is the model's input; each gene is a <b>token</b>.</p>
  <p class="note">V2 models accept at most 4,096 tokens per cell.</p>
</div><figure>{img('tokenise.png', 'rank-value encoding of one cell')}</figure></div>
""", """Geneformer does not use raw counts. In its tokenizer, each gene's count is divided by the cell's total count and then by that gene's median level across the pretraining corpus, and the genes are sorted on the result. A housekeeping gene that is abundant everywhere moves down; a gene that is unusually high in this cell moves up. Genes with zero counts are not in the list at all, and the V2 models read at most 4,096 tokens. Both points matter later for bulk RNA-seq. The genes and values in the figure are invented. Sources: Theodoris and colleagues, Nature 2023, and the Geneformer tokenizer code.""")

add("plain", 0.9, 1, """
<h2>The model was pretrained on about 104 million cells by predicting masked genes</h2>
<div class="sentence"><span class="tok">CD3E</span><span class="tok">IL7R</span><span class="tok mask">?</span><span class="tok">LTB</span><span class="tok">TCF7</span><span class="tok dim">…</span></div>
<p class="caption">Pretraining task: mask a gene and predict it from the rest of the list. Illustration, not data.</p>
<p class="lead">After pretraining, the model maps each cell to a vector, its <b>embedding</b>. Cells with similar ranked lists have similar embeddings.</p>
<p class="note">We have used two model sizes; the larger is used for all results shown here unless stated.</p>
""", """Pretraining used a masked-gene task: one gene in a cell's list is hidden and the model predicts it from the others. Across about one hundred million cells, the model learns which genes tend to rank together. What we use downstream is the embedding, the model's vector for each cell; cells with similar ranked lists end up close together. We have used two model sizes, and the larger one underlies the results in this talk unless I say otherwise. Sources: Theodoris and colleagues 2023 and the model card.""")

add("plain", 1.0, 1, f"""
<h2>Fine-tuning adds one task: separating a donor's tumour T cells from normal T cells</h2>
<div class="split"><div>
  <p class="lead">The classifier is trained on some donors and scored only on donors it never saw (donor-level cross-fitting).</p>
  <p class="lead">Lung (LUAD, 43 donors): pooled held-out balanced accuracy <b>0.825</b>; all <b>43 of 43</b> donors above chance (0.5).</p>
  <p class="note">Balanced accuracy weights tumour and normal cells equally.</p>
</div><figure>{img('finetune.png', 'two groups of cells and a learned boundary')}</figure></div>
""", """Fine-tuning gives the model one additional task: telling a donor's tumour T cells from that donor's normal T cells. Donors are split into folds, and each donor is scored only by a model that never saw any of its cells. In the lung adenocarcinoma study, with 43 donors, pooled held-out balanced accuracy was 0.825, and every donor was above chance. The tumour-to-normal direction this classifier learns is the axis along which perturbations are later scored. Source: the balanced-donor classifier gate file.""")

add("plain", 1.2, 1, f"""
<h2>An in-silico perturbation edits the token list and measures how the embedding moves</h2>
<figure class="full">{img('isp_mech.png', 'original, deleted and overexpressed token lists and the score')}</figure>
""", """This is the mechanics of in-silico perturbation, or ISP. Deletion removes gene X from the cell's ranked list. Overexpression moves X to the first position. The edited list is passed through the fine-tuned model to give a new embedding. The score is the change in cosine similarity to the goal, which is the centroid of the same donor's normal T cells. Per gene, we average over the donor's cells that carry the gene, then take the median over donors, and we require at least ten donors with at least ten such cells. Source: the colon study registration, section 6.2.""")

add("plain", 1.0, 1, f"""
<h2>The score is a movement in the model's embedding space, not a measured biological effect</h2>
<div class="split"><div>
  <p class="lead">A positive score means the edited cell moved toward the donor's normal centroid in the model's representation.</p>
  <p class="lead">Whether a real knockout or overexpression would do the same is a separate question. Answering it needs experimental data.</p>
  <p class="note">No cell is modified. The model always returns a score, whether or not the gene is relevant.</p>
</div><figure>{img('isp.png', 'an edited tumour T cell moving toward or away from the normal centroid')}</figure></div>
""", """It is worth being explicit about what the score is. A cell that moves toward the normal centroid after a deletion has moved in the model's representation, which reflects what the model learned from co-occurrence of genes. That is a prediction about biology, not a measurement of it. The model also returns a score for every gene, relevant or not. Much of the rest of the talk concerns how to decide which scores carry information.""")

add("plain", 1.1, 1, """
<h2>The first results, in July and August, appeared encouraging</h2>
<div class="two">
  <div class="card"><h3>July: genome-wide deletion screen</h3>
    <p>21,000 lung T cells, the smaller model, 2,937,776 single-gene deletions on held-out cells.</p>
    <p class="quote">Internal audit, 28 July: the adenocarcinoma and squamous-cell analyses could not on their own support the conference abstract's claims about small-cell lung cancer.</p></div>
  <div class="card"><h3>August: conference talk</h3>
    <p>A 50-gene panel in small-cell lung cancer (SCLC). Four genes passed in both directions in all three test donors: deletion shifted cells toward normal, overexpression away.</p>
    <p>TIM-3, TIGIT, CTLA-4 and IL7R, genes associated with T-cell exhaustion or persistence.</p></div>
</div>
""", """The project began in July with a screen that deleted each gene in each held-out cell, almost three million deletions in total. Our own audit at the time noted that this work could not on its own support the abstract we had submitted about small-cell lung cancer. In August we presented a 50-gene panel in small-cell lung cancer, in which four genes passed in both directions in every test donor. They were familiar genes from the exhaustion and persistence literature. Over the following weeks we found that part of that agreement came from the method rather than from biology. Sources: the repository README, the 28 July audit and the August talk.""")

# ---------- 2. Lessons ----------
add("plain", 1.1, 2, """
<h2>Lesson 1: the strongest early hits were not T-cell signals</h2>
<div class="two">
  <div class="card fail"><h3>Top of the screen</h3>
    <p>S100A8 and S100A9, among the most significant genes, shifted cells in the <i>same</i> direction under deletion and overexpression in 9 of 12 comparisons.</p>
    <p>Of the top 120 results, 55 were flagged as likely <b>ambient RNA</b>, transcripts from other cells captured during sample preparation.</p></div>
  <div class="card fail"><h3>The comparison groups</h3>
    <p>In July, tumour and normal T cells came from different studies; none of the 18 studies supplied both. The classifier could partly separate studies rather than tissues.</p>
    <p>13 of the 15 July top genes could not be tested in T cells.</p></div>
</div>
<p class="answers">Addressed by """ + chk(2, True) + " " + chk(4, True) + """</p>
""", """The first lesson came from the top of the July screen. S100A8 and S100A9 were among the most significant genes, yet deletion and overexpression shifted cells in the same direction in most comparisons, which is not what one expects from a gene that drives a state. Many top hits were consistent with ambient RNA. In addition, the July tumour and normal groups came from different studies, so the classifier may have learned study differences. When we rebuilt the study around paired donors, 13 of the 15 July genes, mostly epithelial and blood genes such as keratins, could not be tested in T cells. Checks 2 and 4 address this. Sources: the S100A8/S100A9 cross-reference report, the July methods file and the balanced-donor report.""")

add("plain", 1.0, 2, f"""
<h2>Lesson 2: one donor can dominate a cell-level comparison</h2>
<figure class="wide">{img('one_patient.png', 'one donor held 74.9 percent of the SCLC test cells')}</figure>
<p class="lead">Two analyses appeared to disagree about small-cell lung cancer. One donor supplied 74.9% of the SCLC test cells. Counted by donor (19 against 22 donors), the difference was not significant: p = 0.216.</p>
<p class="answers">Addressed by {chk(6, True)}</p>
""", """Cells from one donor are not independent observations; they share genotype, clinical history and sample handling. When one donor contributes three quarters of a group's cells, a cell-level analysis of that group largely describes that donor. Analysed at the donor level, the apparent difference between small-cell and adenocarcinoma T cells was not significant. Source: RESULTS_T6 in the repository.""")

add("plain", 1.0, 2, f"""
<h2>Lesson 3: the two perturbation arms were scored on different cells</h2>
<div class="split"><div>
  <p class="lead">In the August panel, overexpression was scored on every test cell and deletion only on cells that expressed the gene.</p>
  <p class="lead">The cause was a default in Geneformer's perturbation code: given a gene list, it inserts an overexpressed gene into every cell (14,738 of 15,179 calls in our rebuilt study).</p>
  <p class="note">The August genes carry a qualifier; they were not retracted. The panel has not been rerun.</p>
  <p class="answers">Addressed by {chk(3, True)}</p>
</div><figure>{img('unpaired.png', 'overexpression scored on 2,424 cells, deletion on 202 to 1,131')}</figure></div>
""", """The third lesson concerned our own instrument. In the August panel, deletion and overexpression were scored on different sets of cells, because the perturbation code inserts an overexpressed gene into every cell when it is given a gene list. We documented that default on 22 September and still missed its effect on the rebuilt study until 25 September. The deletion evidence for the August genes stands, so we attached a qualifier rather than retracting them. Sources: the 25 September correction and Amendment 3h of the balanced-donor registration.""")

add("current", 1.5, 2, f"""
<h2>Lesson 4: random genes show the opposed pattern we had treated as evidence</h2>
<div class="split"><div>
  <p class="lead">We ran the same pipeline on genes drawn at random from those detected in lung tumour T cells.</p>
  <p class="lead">Deletion and overexpression shifts were anti-correlated: Spearman ρ = <b>−0.593</b> (100 genes) and <b>−0.608</b> (200 genes).</p>
  <p class="note">One-sided permutation p at the test's floor, at most about 1 in 100,000.</p>
  <p class="answers">Addressed by {chk(5, True)}</p>
</div><figure>{img('null_scatter.png', 'random genes: deletion and overexpression shifts are anti-correlated')}</figure></div>
""", """This is the central result of the talk. The August genes passed because deletion and overexpression moved cells in opposite directions. When we applied the identical pipeline to random genes, they showed the same opposition. Each point is one random gene. The rank correlation was minus 0.593 for the registered one hundred genes and minus 0.608 for two hundred. The permutation p-value is at the floor of the test, so we report it as at most about one in one hundred thousand. The random genes were drawn from genes detectable in lung tumour T cells, not from the whole genome. Opposed signs are therefore the baseline, not evidence for a particular gene. Sources: the two null-study result files, hashes a00ccb2f and c9e56026.""")

# ---------- 3. Criteria ----------
add("plain", 1.0, 3, f"""
<h2>Six criteria, applied in order, stand between a result and a claim</h2>
<figure class="full">{img('criteria.png', 'six checks in order and the fixed outcome names')}</figure>
<p class="foot">Adopted on 28 September 2026 as the lab's standard for judging in-silico perturbation (ISP-STD-1).</p>
""", """Each criterion answers one of the lessons. The first three concern the experiment: register the test in advance, confirm the instrument works, and score both arms on the same cells. The last three concern interpretation: beat matched control genes, beat random genes, and count donors with a stability requirement. Every result ends in one of six fixed outcome names, and "no effect" is not one of them. We adopted these as the lab standard on 28 September. The next six slides take them in turn.""")

add("plain", 1.1, 3, f"""
<h2>{chk(1)} Register the test before any result exists</h2>
<div class="split even"><div>
  <p class="lead">Before a run, we record the test, the predicted direction, the significance threshold and the wording for each outcome. An independent reviewer approves the exact files.</p>
  <p class="lead">We also confirm that the test <b>can</b> reach significance with the expected sample size.</p>
  <p class="why">From: the August panel, where we interpreted an ordering we had not planned to test.</p>
</div><div class="box"><div class="boxhead">Example: the colon study</div>
  <p>10 lung reference genes are expected to be testable in colon. The lung pattern counts as repeated if at least <b>9 of 10</b> keep their lung direction (8 of 9 if only 9 are testable).</p>
  <p>The first review of the plan did not pass: it described the software environment as unchanged, but one library had been downgraded. The plan was corrected before the run.</p>
</div></div>
""", """Registration prevents us from choosing the test after seeing the data. Part of it is checking that the test is able to reach significance: with ten genes and a one-sided exact binomial test, agreement must reach nine of ten. Our own first registration for the colon study did not pass review, because it described the software environment as unchanged when pandas had been downgraded. Source: the colon study registration, section 6.3.""")

add("plain", 1.1, 3, f"""
<h2>{chk(2)} Confirm the instrument works before reading anything from it</h2>
<div class="split"><div>
  <p class="lead"><b>Classifier gate.</b> Held-out balanced accuracy ≥ 0.60 and more donors above chance than expected (sign test). Otherwise the study stops.</p>
  <p class="lead"><b>No-op gate.</b> Two passes with no edit must give a shift of exactly zero.</p>
  <p>Colon: {badge('pass', '0.904; 19 of 19 donors')} {badge('pass', 'no-op shift 0.0')}</p>
  <p class="why">From: the July classifier, which may have separated studies rather than tissues.</p>
</div><figure>{img('gate_strip.png', 'per-donor held-out balanced accuracy in lung and colon')}</figure></div>
""", """Two gates precede any perturbation. The classifier must work on held-out donors, and an edit that changes nothing must produce no movement. In colon, pooled held-out balanced accuracy was 0.904, every donor was above chance and the lowest was 0.655; the largest no-op shift was exactly zero. Lung and colon are shown together for context only: the colon classifiers were trained anew from the base model, so this is not evidence that the lung models transfer. Sources: the colon classifier and no-op gate files at commit 2c104ab.""")

add("plain", 0.8, 3, f"""
<h2>{chk(3)} Score both perturbations on exactly the same cells</h2>
<div class="pair">
  <div class="card fail"><h3>{badge('fail', 'August panel')}</h3><p>Overexpression: 2,424 cells for every gene.<br>Deletion: 202 to 1,131 cells.</p></div>
  <div class="card pass"><h3>{badge('pass', 'Since 25 September')}</h3><p>Both arms are analysed on the same cells, and every run checks the cell counts. (Panel code fixed 22 September; rebuilt study corrected 25 September.)</p></div>
</div>
<p class="lead narrow">Diagnostic: if one arm's cell count is constant across genes while the other varies, the arms are not paired.</p>
<p class="why">From: lesson 3.</p>
""", """The rule is that both arms are scored on the same cells. A constant cell count in one arm and a variable count in the other is a reliable sign that they are not, and that was the signature of the August panel. Every analysis since 25 September, including the colon study, re-checks the counts before analysis. Sources: the lab standard, clause B2, and Amendment 3h.""")

add("plain", 1.1, 3, f"""
<h2>{chk(4)} A gene must shift cells more than matched control genes</h2>
<div class="split"><div>
  <p class="lead">Widely detected genes shift cells more regardless of function. Each gene is compared with <b>at least 20 control genes</b> matched on detection rate and mean rank.</p>
  <p class="lead">If fewer than 20 can be found, the gene is reported as <i>not estimable</i>; the matching tolerance is never widened.</p>
  <p class="lead">Likely ambient-RNA genes and classifier-anchor genes are flagged.</p>
  <p class="why">From: lesson 1 (S100A8, ambient RNA).</p>
</div><figure>{img('baseline.png', 'a candidate inside versus outside the control spread')}</figure></div>
""", """A raw shift is hard to interpret on its own, because genes detected in many cells shift them more simply by being present. Each tested gene is therefore compared with at least twenty control genes matched on detection rate and mean rank. A gene is of interest only if it lies outside that spread. If twenty matches cannot be found, the gene is not estimable, and the matching is not loosened to force an answer. In the lung study, 13 of 34 testable T-cell genes met this criterion and were stable. Sources: the lab standard, clauses B1 and B4, and the balanced-donor report.""")

add("plain", 1.0, 3, f"""
<h2>{chk(5)} Opposed effects of the two perturbations are not, on their own, evidence</h2>
<div class="two">
  <div class="card"><h3>What the random genes show</h3>
    <p>Opposed effects are what this model and design produce for genes in general.</p>
    <p>The study's control genes agreed in sign: ρ = −0.658 (308 of 318 genes with enough data).</p></div>
  <div class="card"><h3>What they do not show</h3>
    <p>They do not remove the panel result: 13 of 34 testable T-cell genes still exceed their matched controls.</p>
    <p>Evidence now means an unusually large effect relative to this baseline, not opposite signs.</p></div>
</div>
<p class="why">From: lesson 4.</p>
""", """This criterion follows from the random-gene result. If random genes show opposed effects, opposed effects cannot support any particular gene. The control genes of the same study gave the same sign, minus 0.658; we compare such values by sign only, because they are computed on different gene sets. What remains informative is the size of an effect relative to this baseline. That is a narrower claim than the one we made in August. Sources: the null-study result file and the lab standard, clause B7.""")

add("plain", 1.0, 3, f"""
<h2>{chk(6)} Count donors, require stability, and name every outcome in advance</h2>
<div class="two">
  <div class="card"><h3>Donors and stability</h3>
    <p>The donor, not the cell, is the unit of inference.</p>
    <p>A result must hold when any single control gene is dropped, and in at least 95% of 10,000 bootstrap draws.</p></div>
  <div class="card"><h3>Fixed outcome names</h3>
    <div class="stamps"><span class="stamp pos">positive</span><span class="stamp">negative</span><span class="stamp">opposite_direction</span><span class="stamp">not_estimable</span><span class="stamp">…_open</span></div>
    <p>We do not write "no effect". A negative result means this test, at this sample size, did not meet its threshold.</p></div>
</div>
<p class="why">From: lesson 2 (one donor) and the wording of the August claims.</p>
""", """The last criterion concerns inference and language. Donors are the unit. A result must be stable to dropping any single control gene and must hold in at least 95 percent of ten thousand bootstrap draws; otherwise it is reported as open. Every outcome receives one of a small set of names fixed before the run. A negative result is reported with its direction, p-value and sample size, because a small study can miss a real effect. Our S100 ambient-RNA test in late September was negative in exactly this sense, at p = 6/70 and 34/70. Sources: the lab standard, clauses A6, B5 and B8, and the S100 result file.""")

# ---------- 4. Status ----------
add("plain", 1.2, 4, f"""
<h2>External cohorts: one colorectal cohort qualified; the independent lung cohort could not be assessed</h2>
<div class="split"><div>
  <p class="lead"><b>Pelka et al. 2021, colorectal (E2).</b> 62 patients; 36 with a normal-colon specimen; 25 with ≥100 CD4/CD8 T cells in both tissues. Restricting both tissues to unsorted cells, because sorting differed within 11 donors, leaves <b>19</b>.</p>
  <p class="lead"><b>Bischoff et al. 2021, lung (E1).</b> Data only as a Code Ocean capsule, which refused automated access. {badge('open', 'blocked')}</p>
  <p class="note">Feasibility from per-cell metadata only; no count data downloaded.</p>
</div><figure>{img('e0_cohort.png', 'T cells per donor in tumour and normal colon, Pelka et al. 2021')}</figure></div>
""", """Before any external study, we counted eligible donors from per-cell metadata alone. In the colorectal data of Pelka and colleagues, 25 donors had at least one hundred CD4 or CD8 T cells in both tumour and normal colon. In eleven of them, tumour and normal specimens differed in magnetic sorting, so the tumour-normal contrast would partly be a processing contrast. Restricting both tissues to unsorted cells left nineteen donors, the cohort used for the colon study. The figure shows counts over all processing types; the open circles are the six donors that dropped out under the unsorted restriction. The independent lung cohort could not be assessed, because its data are distributed only through a capsule that refused automated access. Sources: the E0 feasibility report and its per-donor count table.""")

add("plain", 1.3, 4, f"""
<h2>Colon study (E2): classifier gate passed, perturbation run complete</h2>
<div class="split"><div>
  <p>{badge('pass', 'registration reviewed')} {badge('pass', 'classifier gate')} {badge('pass', 'no-op gate')} {badge('pass', 'perturbation run complete')}</p>
  <p>New fold classifiers from the same base model. Pooled held-out balanced accuracy <b>0.904</b> (bar 0.60); <b>19 of 19</b> donors above chance; lowest 0.655; sign test p = 3.8 × 10⁻⁶.</p>
  <p>Perturbation run: 369 genes × 19 donors × 2 arms (14,022 calls), 02:42 JST 1 Oct to 10:20 JST 2 Oct; 32.6 GPU-hours of the 52 authorised. Results on the next slide.</p>
  <p class="note">MMR status is descriptive; no test was registered.</p>
</div><figure>{img('e2_gate.png', 'per-donor held-out balanced accuracy in the colon study')}</figure></div>
""", """The colon study repeats the lung design on the nineteen-donor cohort. Its registration was reviewed and approved before any GPU work. Five new fold classifiers were fine-tuned from the base model with the lung recipe unchanged. Pooled held-out balanced accuracy was 0.904, every donor was above chance, and the lowest donor, C134, at 0.655, also had the fewest tumour T cells. The no-op gate gave exactly zero. Mismatch-repair status is marked for description only; the lowest three donors are all MMR-proficient, but no test was registered and we draw no conclusion. The perturbation run finished at 10:20 Japan time on 2 October, using 32.6 of the 52 GPU-hours authorised; its results are on the next slide. Sources: the colon classifier gate file at commit 2c104ab, the E2 interim report and the registration.""")

add("plain", 1.6, 4, f"""
<h2>Colon results: random genes opposed in the same direction but not stably; the lung gene pattern did not replicate</h2>
<div class="split bulk zf"><figure>{img('e2_results.png', 'colon random genes, deletion against overexpression; lung reference genes, colon deletion shift')}</figure><div>
  <p><b>Random genes (primary):</b> ρ = −0.245, one-sided p = 0.0067 (100,000 permutations); all 100 leave-one-out tests pass; significant in 78% of 10,000 resamples, below the registered 95%. <code>control_draw_sensitive_open</code>: direction as in lung, not stable; open. {badge('open', 'open')}</p>
  <p>Lung gave −0.593. The control genes, a more highly detected set, were also negative (sign-only check).</p>
  <p><b>Lung reference genes:</b> 10 testable; 3 keep their lung deletion direction (p = 0.95; the bar was 9 of 10). <code>pattern_not_replicated</code>. Seven opposite signs are within chance (P = 0.17). {badge('fail', 'not replicated')}</p>
  <p><b>Panel genes in colon:</b> 1 of 28 dose-concordant (PRF1, toward normal; it was <code>OPEN</code> in lung). Lung against colon deletion medians, 27 genes: ρ −0.29, compatible with zero.</p>
</div></div>
<p class="foot">Readings were fixed before the run. A colon–lung difference is not attributable to tissue alone: study, dissociation, chemistry, annotation, null-gene population and fold models all differ, and 19 donors give less power per gene than 43. New fold models, so the lung models were not tested. Effects are a few thousandths of cosine similarity in both tissues.</p>
""", """The colon perturbation run finished at 10:20 Japan time on 2 October, and the results passed internal review. The primary question was whether random genes give opposed deletion and overexpression effects in colon as they do in lung. They do in direction: the rank correlation was minus 0.245, with a one-sided p of 0.0067, and every leave-one-out test passed. But it is much weaker than in lung, and in only 78 percent of resamples did it stay significant, against the 95 percent we registered. So the registered reading is that the direction matches lung but the result is not stable, and it stays open. The point cloud shows why: most genes sit near zero, and a few genes with large overexpression shifts carry the trend. The second question was whether the lung reference genes keep their direction. Three of ten did, where nine were needed, so the lung gene pattern did not replicate. Seven opposite signs out of ten is within what chance gives, so this does not show a reversal either, and across the 27 panel genes tested in both tissues the lung and colon deletion medians are not detectably correlated. One panel gene, PRF1, reached a dose-concordant status in colon; it was open in lung. None of these differences can be put down to tissue, because almost everything else about the two studies differs too, and colon has fewer donors. So the lung caution holds in colon: opposed deletion and overexpression shifts are not on their own evidence of a specific effect, and gene-level statuses from one tissue should not be carried to another without testing. Sources: the E2 results report, the H2b and H2c result files and the Panel B outcome rows on geneformer-lung-tcell main, merge 4cce44a, results commit b7369cb.""")
add("plain", 1.2, 4, f"""
<h2>What the results support, and what they do not</h2>
<div class="two">
  <div class="card pass"><h3>{badge('pass', 'Supported')}</h3>
    <ul class="tight">
      <li>Lung, 43 donors: a fine-tuned classifier separates tumour from normal T cells in held-out donors (0.825; 43 of 43 above chance).</li>
      <li>13 of 34 testable T-cell genes exceed their matched controls, stably.</li>
      <li>Deletion and overexpression give opposed effects for random genes.</li>
      <li>Colon, 19 donors: the tumour/normal separation is learnable (0.904; 19 of 19).</li>
      <li>Colon: the lung reference-gene pattern did not replicate (3 of 10 kept their lung direction).</li>
    </ul></div>
  <div class="card open"><h3>{badge('open', 'Not shown')}</h3>
    <ul class="tight">
      <li>That any gene regulates T-cell state. A shift in embedding space is not a mechanism.</li>
      <li>Whether the opposed effects come from the model or from lung tissue: in colon they appear in the same direction but weaker and not stable (open).</li>
      <li>What the classifier reads: T-cell state, ambient RNA or T-cell subset composition.</li>
      <li>Whether the lung models generalise to new lung donors.</li>
    </ul></div>
</div>
""", """In lung, the classifier works on held-out donors, thirteen T-cell genes exceed their matched controls, and the opposed effects of the two perturbations are generic. In colon, the classifier also works, and the lung gene pattern did not replicate; the opposed effects appear in the same direction but did not reach the registered stability bar, so that question stays open. None of this shows that a gene regulates T-cell state. We also do not know whether the classifier reads T-cell state, ambient RNA or differences in subset composition between tissues, and we have not tested the lung models on new lung donors. Sources: the balanced-donor report and the colon interim report.""")


# ---------- 5. Bulk RNA-seq ----------
add("plain", 1.1, 5, f"""
<h2>Bulk RNA-seq: a bulk profile is an average over a mixed population, not a cell</h2>
<div class="split wide"><div>
  <p>Geneformer was pretrained on single-cell rank encodings. A bulk profile sums many cell types, so a gene's level reflects <b>composition</b> as well as <b>within-cell regulation</b>.</p>
  <p>Any perturbation model fitted on bulk data mixes the two: a shift could mean "this gene changes T-cell state" or "this sample has fewer T cells".</p>
  <p>Geneformer itself cannot take a bulk profile as input: the list would be cut at 4,096 tokens and lie outside the pretraining distribution.</p>
  <p>{badge('open', 'tested on three panels with a simpler model: next three slides')}</p>
</div><figure>{img('bulk_mix.png', 'composition changes the bulk level of a gene without any within-cell change')}</figure></div>
""", """We were asked whether this approach applies to bulk RNA-seq. The basic difficulty is that a bulk profile is an average over many cell types. In the schematic, gene G has the same level inside T cells in both samples, but the bulk level differs because the tumour sample contains fewer T cells. Any perturbation model fitted on bulk data inherits this mixture of composition and regulation within cells. Geneformer itself is not usable here, because a bulk profile does not resemble the single-cell lists it was trained on. We therefore tested a simpler network model on three panels of measured knockouts and knockdowns, as shown on the next three slides. The values in the figure are invented.""")

add("plain", 1.5, 5, f"""
<h2>Bulk tests: a weak, non-specific signal in one knockout set that did not replicate in a second</h2>
<div class="split bulk"><div>
  <p><b>Model.</b> Not Geneformer: a CellOracle-style linear network (ridge regression on transcription-factor-to-target edges of a promoter base network, filtered by matched ATAC-seq), fitted with each knockout left out.</p>
  <p><b>Ground truth.</b> Two CRISPR knockout sets in CD4+ T cells, 3 donors each, same laboratory: Freimer et al. 2022 (17 knockouts in the base network) and Weinstock et al. 2024 (38 new ones).</p>
  <table class="tbl mini"><tr><th>Registered test</th><th>Freimer, n = 17</th><th>Weinstock, n = 38</th></tr>
    <tr><td>Median ρ &gt; 0</td><td>0.083, p = 0.012 {badge('pass', '')}</td><td>0.033, p = 0.21 {badge('fail', '')}</td></tr>
    <tr><td>Sign agr. &gt; 0.5</td><td>0.545, p = 0.013 {badge('pass', '')}</td><td>0.517, p = 0.38 {badge('fail', '')}</td></tr>
    <tr><td>Beats shuffled network</td><td>+0.039, p = 0.19 {badge('fail', '')}</td><td>+0.035, p = 0.14 {badge('fail', '')}</td></tr>
    <tr><td>Beats random TFs</td><td>4/17, p = 0.009 {badge('pass', '')}</td><td>3/38, p = 0.30 {badge('fail', '')}</td></tr>
    <tr><td>Reading</td><td><span class="stamp">RECOVERED_NONSPECIFIC</span></td><td><span class="stamp">NOT_RECOVERED</span></td></tr></table>
  <p class="note">By the rule registered before the second run, the first reading does not replicate.</p>
</div><figure>{img('bulk_result.png', 'per-knockout rank correlation of predicted and measured shifts in the Freimer set')}</figure></div>
""", """We tested the simplest version of bulk perturbation against real knockouts, twice. The model is not Geneformer. It is a linear network in the style of CellOracle: each gene is predicted from the transcription factors that a promoter-based network allows to regulate it, restricted to promoters accessible in matched ATAC-seq. Each knockout was left out in turn, simulated by clamping the factor low, and compared with the measured shift. In the first set, from Freimer and colleagues, 17 knockouts have edges in the base network. Predictions agreed with measured shifts more often than chance, and four beat random factors, but not a shuffled network, so the registered reading was RECOVERED_NONSPECIFIC. The figure shows that set. We then repeated the identical pipeline on 38 new knockouts from Weinstock and colleagues, same laboratory and cell type. None of the four tests passed, the reading was NOT_RECOVERED, and by the rule registered beforehand the first result does not replicate. Sources: the two bulk study reports and their result tables on Geneformer_TE main (merge commits 6b637d8 and 460da8a).""")

add("plain", 1.3, 5, f"""
<h2>What the two bulk tests show, and what they leave open</h2>
<div class="two">
  <div class="card fail"><h3>{badge('fail', 'Not supported in this design')}</h3>
    <ul class="tight">
      <li>Regulator-specific prediction: as a group, the model did not beat a shuffled network (P3 failed in both sets).</li>
      <li>The Freimer signal was matched by co-expression alone (median ρ 0.21); in Weinstock both fell to chance (0.015).</li>
      <li>Fitted on unperturbed controls only, the network showed no agreement above chance in either set (median ρ −0.013 and 0.008).</li>
      <li>Predicted shifts were 55 to 85 times too small (median ratio 0.018 and 0.012).</li>
      <li>Transposable-element arm: the deposited counts had no TE rows; after re-alignment, <span class="stamp">TE_RECOVERED_NONSPECIFIC</span> (slide 35).</li>
    </ul></div>
  <div class="card open"><h3>{badge('open', 'Open')}</h3>
    <p class="small">Why the sets differ is untested. Freimer's regulators gave large, overlapping responses (median 394 responsive genes); Weinstock's gave small ones (70.5).</p>
    <p class="small">Uncontrolled differences: harvest at 5 days after electroporation versus 8 days after activation; UMI deduplication named in one study only; counting pipeline; unknown donor overlap.</p>
    <p class="small">Composition and within-cell regulation cannot be separated in bulk data. A revisit would need a composition covariate registered in advance, or single-cell or sorted data.</p></div>
</div>
""", """The pair of tests narrows the reading. As a group, the network did not beat a shuffled network in either set; the few single knockouts that did, three of 38 in the second set and none in the first, are about what chance gives. So the motif-and-promoter structure added nothing measurable beyond how many genes each factor may touch. In the first set a model-free co-expression baseline did as well as the network, and in the second both fell to chance together, so the first result was a shared response visible to plain correlation, not a property of the network. Fitted on unperturbed controls alone, which is how a bulk cohort without perturbations would have to be used, the network showed no agreement above chance in either set. Predicted magnitudes were 55 to 85 times too small. Why the two sets differ is not tested. Freimer's regulators were chosen as hits in screens and produced large, overlapping responses; Weinstock's produced much smaller ones. The runs also differ in harvest timing, deduplication, counting pipeline and possibly donors, none of which was controlled. The supported claim is narrow: in this design, bulk network perturbation is not a reliable way to predict knockout effects in T cells. Sources: the combined reading of the two bulk tests and the Weinstock report.""")

add("plain", 1.5, 5, f"""
<h2>Third panel, K562 CRISPRi: the bulk network tracks knockdowns again, and again no better than a shuffled network</h2>
<div class="split bulk zf"><div>
  <p><b>Design.</b> The same frozen method, registered before download, on a panel that differs in cell type, laboratory, perturbation and library: ENCODE CRISPRi in K562, 74 knockdowns, 48 in the base network, 34 past the registered knockdown gate (target mRNA down by at least 0.5 log2).</p>
  <p><span class="stamp">RECOVERED_NONSPECIFIC</span> {badge('pass', 'P1, P2')} {badge('fail', 'P3, P4')}<br>Median ρ 0.238 (p = 0.041); sign agreement 0.635 (p = 0.045); gain over shuffled networks −0.008 (p = 0.41); 1 of 34 beat random TFs (p = 0.83). The matched prediction ranked first for 0 of 34 knockdowns.</p>
  <p><b>Co-expression did better:</b> median ρ 0.448, 0.19 above the model (two-sided p = 0.004).</p>
  <p><b>Shared component.</b> Within a batch, the shifts of different knockdowns correlate at a median of 0.64 (batch E) and 0.60 (batch C), above the registered 0.3. Post hoc: the 14 knockdowns that did not lower their target track at a median ρ of 0.007, and deeper knockdown goes with higher ρ (Spearman −0.41, p = 0.004). So the tracking is not only the shared component; how much is target-specific the design cannot say.</p>
  <p class="note">K562 says nothing about T-cell biology. Two control replicates per batch, so responsiveness is uncalibrated. Batch C (8 scored) had a negative median ρ, batch E (26) a positive one. Without the knockdown gate (48 scored) the reading would be <code>NOT_RECOVERED</code>.</p>
</div><figure>{img('k562_result.png', 'per-knockdown rank correlation for the network model and co-expression, and model correlation against knockdown depth')}</figure></div>
""", """The third panel was chosen to arbitrate between the two T-cell readings. It uses ENCODE CRISPRi knockdowns in the leukaemia line K562, so it differs from the T-cell sets in cell type, laboratory, perturbation and library, and the method and its registered tests were frozen before download. Of 74 knockdowns, 48 target factors in the base network, and 34 lowered their own target by the registered amount. The network tracked the measured shifts, with a median correlation of 0.24 and sign agreement of 0.63, but it did not beat shuffled networks or random factors, so the reading is RECOVERED_NONSPECIFIC, as for Freimer. A model-free co-expression baseline did better, at a median of 0.45. Within each batch the knockdowns share much of their response, which on its own could produce this kind of tracking. Two checks added after the results argue that it is not the whole story: knockdowns that failed to lower their target do not track, and deeper knockdowns track better. How much of the tracking is specific to the target, the design cannot say. The upper panel shows the model and co-expression for each knockdown; the lower, post hoc panel shows the model's correlation against knockdown depth. K562 tells us nothing about T cells, the eight batch C knockdowns went the other way, and without the knockdown gate the reading would have been NOT_RECOVERED. Across the three panels: Freimer RECOVERED_NONSPECIFIC with 17 knockouts, Weinstock NOT_RECOVERED with 38, K562 RECOVERED_NONSPECIFIC with 34. Where the method tracks, it tracks without the wiring, and co-expression does as well or better. This panel sides with Freimer on whether the method tracks at all, which leaves Weinstock's null looking specific to that dataset or design. Compute was 4.04 CPU-hours against a cap of 6; the scoring was run twice and the four result files were byte-identical. Sources: the K562 run record and result tables on Geneformer_TE main, merge 73226eb, head 37b974d.""")

# ---------- 6. Transposable elements (Geneformer_TE) ----------
add("plain", 1.2, 6, f"""
<h2>A second project asks which regulators set TE expression</h2>
<p class="lead narrow"><b>Transposable elements (TEs)</b> are repeated sequences that cells keep silenced (KRAB zinc-finger proteins with KAP1, HUSH, DNA and H3K9 methylation). Geneformer_TE applies the perturbation logic and checks of the T-cell work to TE regulators.</p>
<figure class="full tep">{img('te_pipeline.png', 'three tracks of the TE project and the state of each')}</figure>
<p class="note">Bulk results are judged against expression-matched random genes, never against zero.</p>
""", """Our second project applies the same question to transposable elements. These are repeated sequences that cells keep silenced through dedicated machinery: KRAB zinc-finger proteins with their co-repressor KAP1, the HUSH complex, DNA methylation and H3K9 methylation. The project asks which regulators set TE expression. It has three tracks. The single-cell track uses Geneformer as in the T-cell work. The bulk track uses the simple linear network from the previous part, now with TE families as targets, and runs on a CPU for any species. The third track supplies ground truth: published knockout and knockdown experiments, re-counted for TEs. The colours give the state: the single-cell track is built but not run, the bulk track has results, and the ground-truth track has two results, from zebrafish and from the Freimer T-cell knockouts. Sources: the Geneformer_TE README and handoff document.""")

add("plain", 1.0, 6, f"""
<h2>Geneformer has no TE tokens, so the single-cell track reads TE states out through a probe</h2>
<div class="two">
  <div class="card"><h3>Design</h3>
    <ul class="tight">
      <li>The vocabulary holds human genes only. TE expression defines the cell states (TE-low, TE-high within each cell type) and is read out by a linear probe from the cell embedding.</li>
      <li>A shift toward TE-high can therefore arise only through genes.</li>
      <li>A classifier gate comes first: donor-level confidence intervals, a sequencing-depth baseline, calibration and per-stratum floors.</li>
      <li>316M model in bf16, with an fp32 check run on a subset of genes.</li>
    </ul></div>
  <div class="card open"><h3>{badge('open', 'built, not run')}</h3>
    <p class="small">No human single-cell data with TE counts have been prepared. Candidates: re-process the lung T-cell atlas with a TE counter, or use a public data set with a known TE de-repression.</p>
    <p class="small">10x 3′ reads are short and often map to many TE copies, so the design stays at the TE family level.</p></div>
</div>
""", """Geneformer's vocabulary contains human genes and no transposable elements, so TEs cannot simply be deleted or overexpressed in the token list. The single-cell track reads them out instead. Within each cell type, cells are labelled TE-low or TE-high, a classifier learns that split, and a linear probe maps the cell embedding to each TE family's expression. A predicted shift toward TE-high can therefore only come through gene-level regulation. The same kind of gate as in the T-cell work runs first, with a sequencing-depth baseline, because TE fraction tracks depth and cell quality. The track is built but has not been run: we have not yet prepared human single-cell data with TE counts. Droplet reads are short and many map to several TE copies, so any claim stays at the family level. Sources: the Geneformer_TE README and design log, entries DC-01 and DC-02.""")

add("plain", 1.3, 6, f"""
<h2>In 162 fish libraries, the 30 TE regulators did no better than expression-matched random genes</h2>
<figure class="full te">{img('te_fish_null.png', 'empirical p of 30 fish TE regulators against random genes, two network modes')}</figure>
<p class="lead narrow tes">Reef fish (<i>A. polyacanthus</i>), 3 tissues × 3 CO2 groups; 30 regulators against 90 expression-matched random genes. Without that control, 32,142 of 114,720 tests reached FDR &lt; 0.05; with it, none passed, also after removing the global TE axis. {badge('fail', 'no regulator-specific signal')}</p>
""", """The bulk track was first run on a fish cohort from our ocean-acidification work: 162 bulk libraries from three tissues and three CO2 exposure groups, with genes and TE families counted from the same reads. The fish is the reef species Acanthochromis polyacanthus. Thirty TE regulators have an annotated orthologue in this fish; KAP1 and the KRAB zinc-finger family do not, because that system is largely specific to tetrapods. Taken at face value, the network produced 32,142 significant regulator-to-family effects, but ninety random genes matched for expression produced as many. Each point in the figure is one regulator's empirical p against those random genes, ranked; the points follow the line expected if no regulator differs from random genes. One regulator falls at p of 0.05 or below, where 1.5 are expected, and none survives correction. Most of the TE variation lies on one global axis, which explains 29.3 percent of the within-group TE variance and correlates at 0.87 with the TE share of reads; each regulator's predicted direction followed its correlation with that axis. Removing the axis did not reveal specific regulators either. Sources: the fish bulk run record and its random-control tables on Geneformer_TE main.""")

add("plain", 1.1, 6, f"""
<h2>Developmental CO2 lowered the gill TE share; brain and liver showed no robust shift</h2>
<figure class="full slim">{img('te_gill.png', 'strict TE share of reads by tissue and CO2 group, with 95% confidence intervals')}</figure>
<p class="lead narrow">Gill: 2.87% to 2.55% of counted reads, −11.4% [−17.2, −5.1], p = 0.0009, FDR 0.006; the effect persists after QC adjustment and outlier exclusion. Tolerant and sensitive lines did not differ (smallest FDR 0.11).</p>
<p class="note">Exploratory: not specified in the original study plan. A share of counted reads, not absolute TE expression; a shift in global TE load, not a regulator effect.</p>
""", """Because the network removes treatment differences by design, the global TE load needed its own test. In gill, fish exposed to elevated CO2 during development carried a lower share of reads from TEs: 2.87 percent in controls and 2.55 percent after exposure, a relative fall of 11.4 percent with a confidence interval from 5.1 to 17.2 percent, FDR 0.006. The effect held when we adjusted for alignment quality and when we excluded outlier libraries. The intergenerational group points the same way but its interval includes zero. Brain and liver show no robust shift; in brain, the alignment-quality covariates themselves differ by treatment, so those estimates are reported as inconclusive. CO2-tolerant and sensitive lines did not differ detectably. This analysis was not specified in the original study plan, so it is exploratory. It describes a shift in global TE load, and a follow-up found no candidate gene that explains it better than random genes; a thyroid gene set was nominal at p 0.025, FDR 0.10, and is a lead only. Sources: the TE-axis treatment report and the gene-axis report on Geneformer_TE main.""")

add("plain", 1.6, 6, f"""
<h2>Zebrafish ground truth: no TE-regulator loss shifted global TE load detectably; family leans point weakly to derepression</h2>
<div class="split bulk zf"><figure>{img('te_zebrafish.png', 'TE families up and down, and change in TE share, for 17 zebrafish perturbation studies')}</figure><div>
  <p>17 published contrasts, 14 GEO series, 112 runs (uhrf1, dnmt1, dnmt3, kdm1a, ezh2, mettl3, atrx); TEs re-counted with one pipeline, each study against its own controls.</p>
  <p><b>Prespecified, TE share:</b> 0 of 16 loss-of-function studies shifted at FDR &lt; 0.05. The one shift, human UHRF1 overexpression in liver (+29.9% [16.6, 44.5], FDR 0.011), is mostly compositional: gene-assigned reads fell (−2.55 M per library [−4.98, −0.11], p = 0.043), TE reads did not (p = 0.86).</p>
  <p><b>Exploratory, family leans:</b> loss-of-function studies with a significant lean leaned up in 6 of 8 (0.75 [0.35, 0.97], p = 0.29); for DNA-methylation regulators, 6 of 7 (0.86 [0.42, 1.00], p = 0.13). No row passes FDR. dnmt1 liver: 112 families up, 26 down, the gain in LTR families.</p>
  <p><b>Fish network directions:</b> ρ = −0.18 against the TE-share change (p = 0.50, n = 17); family leans agreed in 4 of 9 (p = 1.0), at chance level. {badge('fail', 'not supported')}</p>
</div></div>
<p class="foot">2 to 5 libraries per arm. † Post hoc flag: unique-mapping rate differs by genotype (uhrf1 liver 2023, uhrf1 larva 2020, mettl3 morphant), so their TE direction cannot be separated from library quality. Clutch blocking was added after an interim look and created one upward lean (uhrf1 liver 2020). Cross-species, cross-perturbation test with low power.</p>
""", """The zebrafish panel is the first direct measurement in this project of what TE regulators do to TEs in a vertebrate. Seventeen published contrasts were re-counted with one pipeline, and each was compared only with its own controls. On the prespecified readout, the TE share of reads, none of the sixteen loss-of-function studies shifted after correction. The one study that did is the human UHRF1 overexpression, and that rise comes mostly from fewer reads assigned to genes; TE reads per library did not change. The TE families give a more suggestive picture. Among loss-of-function studies with a significant family lean, six of eight leaned up, and six of seven when the set is restricted to DNA-methylation regulators. No row passes correction, and this pooling was defined after the prespecified tests came back nearly empty. Three studies carry a genotype-linked difference in mapping rate, flagged by a rule set after the fact, so their TE direction cannot be separated from library quality. Clutch blocking, also chosen after an interim look, created one of the upward leans. The fish network predictions did not track any of this: the rank correlation was minus 0.18, and family leans agreed in four of nine studies. With two to five libraries per arm, a firmer test needs five or more per arm, stranded libraries and mapping quality balanced across arms. Sources: the zebrafish validation report and its tables on Geneformer_TE main, commit 246c3e4.""")

add("plain", 1.7, 6, f"""
<h2>Freimer TE arm: TE shifts mostly within a control-only null (post hoc); the network's TE predictions were non-specific</h2>
<div class="split bulk zf"><figure>{img('te_freimer.png', 'responsive TE subfamilies per knockout against a control-only null, and per-knockout rho of the network and its controls')}</figure><div>
  <p>96 libraries re-aligned with multimappers kept; rules registered before any TE count. Gates passed: gene counts matched the deposited ones (Spearman 0.976 to 0.980, 96 of 96); 712 TE subfamilies expressed.</p>
  <p><b>Observed:</b> 15 of 17 representable knockouts had ≥ 10 responsive subfamilies (median 19, range 11 to 57). A control-only null (post hoc; one AAVS1 library per donor as pseudo-knockout): median 7, 95th percentile 37, 25% reach 10. Only CBFB exceeds it (57, p = 0.010); for genes, 14 of 17 knockouts do.</p>
  <p><b>Reading <span class="stamp">TE_RECOVERED_NONSPECIFIC</span></b> (n = 15): P1 median ρ 0.18 (p = 0.001) and P2 sign 0.64 (p = 0.010) pass; P3 gain over shuffled 0.007 (p = 0.34) and P4, 1 of 15 beating random TFs (p = 0.54), fail. Co-expression alone: ρ 0.13. {badge('fail', 'non-specific')}</p>
  <p><b>Host-gene transcription:</b> 83.3% of TE counts intronic, 4.0% exonic or UTR, 5.5% distal. Distal loci only (S-TE2), the read-through check, left 3 scorable knockouts, too few to test.</p>
</div></div>
<p class="foot"><b>Null result:</b> the knockouts do not detectably shift TE subfamilies beyond library-to-library variation among controls (CBFB the one possible exception, post hoc). Because P1 and P2 were scored on subfamilies selected at near-chance rates, the TE reading carries less weight than the gene reading. EM-assigned multimappers; 3′ tag-seq misses TE transcription away from poly-A sites.</p>
""", """This is the second ground-truth test, and it returns to the Freimer T-cell knockouts. The deposited counts had no TE rows, so we re-aligned all 96 libraries with multimapping reads kept, under rules registered before any TE count existed. The re-aligned gene counts matched the deposited ones, and 712 TE subfamilies were expressed, so both gates passed. A cross-host check on the way caught unseeded deduplication; a fixed seed made the two hosts byte-identical and the affected samples were redone. Fifteen of the seventeen knockouts the network can represent had at least ten responsive subfamilies. A null built after review from the control libraries alone puts that in proportion: a control library standing in for a knockout reaches a median of seven, and a quarter reach ten, so only CBFB exceeds what controls do among themselves; STAT5A, at 39, sits just past the shaded band but its empirical p is 0.051. For genes, fourteen of seventeen knockouts exceed the same null. The network's predicted TE shifts agreed with the measured ones above chance, but not better than a shuffled network, and only one knockout beat random factors, so the reading is non-specific, as for genes. Most TE reads in these 3-prime tag libraries sit in introns, so a knockout that regulates TEs cannot be separated from one that changes transcription of the genes containing them; the distal-locus test meant to do that left only three knockouts. On these data the knockouts change gene expression and, with one possible exception, do not detectably shift TE subfamilies. Asking the TE question properly needs full-length total-RNA data. Sources: the TE-arm report and the run record and tables on Geneformer_TE main, merge c17d39b, PR head eef6e18.""")

add("plain", 1.1, 6, f"""
<h2>What the TE work shows so far, and what it does not</h2>
<div class="two">
  <div class="card pass"><h3>{badge('pass', 'Supported')}</h3>
    <ul class="tight">
      <li>A co-variation network did not meet the registered bar for specific prediction in any controlled test: 162 fish libraries (no regulator beat random genes), human knockouts and knockdowns (slides 27-29), Freimer TEs (slide 35).</li>
      <li>Without random-gene controls the same run would have reported 32,142 significant regulator-to-family tests.</li>
      <li>Developmental CO2 lowered the gill TE share by 11.4% (exploratory).</li>
      <li>Zebrafish: no loss-of-function study shifted global TE share (0 of 16); fish network directions agreed at chance level (4 of 9).</li>
      <li>Freimer T cells: TE subfamily shifts did not exceed a control-only null, CBFB aside (post hoc).</li>
    </ul></div>
  <div class="card open"><h3>{badge('open', 'Not shown')}</h3>
    <ul class="tight">
      <li>Any regulator-to-TE effect, in fish or in T cells.</li>
      <li>Whether Geneformer ISP can rank TE regulators: the single-cell track has not run.</li>
      <li>Whether a TE shift in T cells can be separated from host-gene transcription: 83% of TE counts in these 3′ libraries are intronic.</li>
      <li>Whether DNA-methylation loss de-represses TEs: 6 of 7 zebrafish leans point up, exploratory and not significant.</li>
      <li>What the global TE axis is biologically: intronic or nascent RNA, or cell composition.</li>
    </ul></div>
</div>
""", """The supported findings are narrow. A network built from natural co-variation did not meet the registered bar for specific prediction in any controlled test. In 162 fish libraries no regulator beat random genes. In the Freimer knockouts it beat random transcription factors in 4 of 17 cases but not shuffled networks, in the Weinstock knockouts it beat neither, and in the K562 knockdowns it beat neither while co-expression did better. In fish, the random-gene control is what shows it; without that control, the same run would have looked like thirty-two thousand findings. That is the bulk counterpart of the random-gene baseline from the T-cell work. Developmental CO2 exposure lowered the gill TE share, as an exploratory result. In zebrafish, no loss-of-function study shifted the global TE share, and the fish network directions agreed with the measured family leans at chance level. We have not shown any regulator-to-TE effect; the zebrafish family leans after loss of DNA-methylation regulators point toward derepression, but only in exploratory tests that do not pass correction. In the Freimer T-cell knockouts, the TE subfamily shifts did not exceed what control libraries show among themselves, CBFB aside, and the network's TE predictions were no better than a shuffled network's. We do not know whether Geneformer can rank TE regulators, because that track has not run, or whether a TE response in T cells can be told apart from host-gene transcription, because most TE reads in those libraries are intronic. The global TE axis is also unexplained; it could reflect intronic or nascent RNA, or cell composition. The single-cell track is also where this project and the colon T-cell work would meet, if human single-cell data with TE counts were prepared. Sources: the fish run records and reports on Geneformer_TE main.""")

# ---------- 7. Next ----------
found = "".join(f"<tr><td>{chk(k, True)}</td><td>{c}</td><td>{e}</td></tr>" for k, c, e in [
    (1, "Register test, direction, threshold, reachable p and wording first", "August ordering read without a plan"),
    (2, "Classifier works on held-out paired donors; a no-op gives zero", "July groups came from different studies (0 of 18)"),
    (3, "Both perturbations on identical cells", "2,424 vs 202 to 1,131 cells; code default 14,738 of 15,179"),
    (4, "Exceed 20 or more matched control genes; flag ambient genes", "S100A8 and S100A9: same direction in 9 of 12; 55 of top 120 ambient"),
    (5, "Exceed the random-gene baseline; opposed signs are not evidence", "Random genes: ρ −0.593 (100), −0.608 (200)"),
    (6, "Donors as the unit; stable in 95% of resamplings; fixed outcome names", "One donor held 74.9% of the SCLC test cells")])
add("plain", 1.2, 7, f"""
<h2>Summary 1: the evaluation criteria, each traced to evidence</h2>
<table class="tbl"><tr><th></th><th>Criterion {badge('pass', 'adopted')}</th><th>Evidence behind it</th></tr>{found}</table>
<p class="foot">Status: lab practice (ISP-STD-1, 28 September 2026). Not yet published or tested by other groups.</p>
""", """Each criterion on the left is now lab practice, and each is tied to a documented episode on the right. These are established as practice in our lab, with sources for every row. They have not been tested by other groups, and some, such as the 95 percent stability threshold, are choices rather than derived results.""")

todo = "".join(f"<tr><td>{badge(s, l)}</td><td>{q}</td><td>{h}</td></tr>" for s, l, q, h in [
    ("open", "open", "Are the opposed effects a property of the model or of lung?", "Colon (E2): same direction, weaker, not stable; lung gene pattern not replicated"),
    ("open", "blocked", "Do the lung models generalise to new lung donors?", "E1: the one candidate dataset is not accessible"),
    ("open", "planned", "Are the opposed effects the same for an unrelated goal?", "Swap the goal centroid"),
    ("open", "planned", "Is the 13-gene result cell state or T-cell subset composition?", "Re-analyse within T-cell subsets"),
    ("open", "planned", "Can a simpler, interpretable method match the classifier?", "T-cell program scores (TCAT, Kotliar et al. 2025)"),
    ("open", "not started", "Do results depend on model size (104M vs 316M parameters)?", "Re-run a subset on both sizes"),
    ("open", "not started", "Does the method recover genes known to matter?", "Positive controls; experimental CRISPR screens in T cells"),
    ("fail", "not supported", "Does bulk network ISP recover knockout-specific targets?", "Three registered panels, 89 knockouts and knockdowns: non-specific, not replicated, non-specific again in K562"),
    ("fail", "not supported", "Did the fish network predict TE responses to regulator loss in zebrafish?", "17 contrasts: ρ −0.18, leans agree 4 of 9; loss leaned up 6 of 8, 6 of 7 for DNA methylation (exploratory)"),
    ("fail", "not supported", "Does the bulk network predict TE responses to T-cell knockouts?", "Freimer TE arm: non-specific; only CBFB above a control-only null (post hoc)"),
    ("open", "not started", "Can Geneformer ISP rank TE regulators in single cells?", "Needs single-cell data with TE counts")])
add("plain", 1.3, 7, f"""
<h2>Summary 2: what remains to be tested</h2>
<table class="tbl compact dense"><tr><th>Status</th><th>Question</th><th>Approach</th></tr>{todo}</table>
<p class="foot">All rows but three are open. The bulk, zebrafish and T-cell TE rows have results: not supported in this design.</p>
""", """This is what we do not yet know. The colon study has finished: random genes were opposed in the same direction as in lung but not stably, so the first question stays open, and the lung gene pattern did not replicate. Transfer to new lung donors is blocked by data access. Three studies are planned with little or no new GPU work: swapping the goal, re-analysing within T-cell subsets, and comparing the classifier with an interpretable baseline built from published T-cell programs. Model size and positive controls have not started; without positive controls, a negative result is hard to interpret. The bulk RNA-seq row now has a result: across three registered panels with 89 knockouts and knockdowns, the bulk network did not recover regulator-specific effects; its weak positive in Freimer did not replicate in Weinstock, and in K562 it tracked again without beating shuffled networks or co-expression. The last three rows come from the TE project. In zebrafish, the fish network directions agreed with measured TE responses at chance level; in the Freimer T-cell knockouts, TE shifts mostly stayed within a control-only null and the network's TE predictions were non-specific; and the single-cell TE track needs data we have not prepared. Sources: the next-cycle proposal, the independent-data design and the E0 feasibility report.""")

add("plain", 1.3, 7, f"""
<h2>These results could form one methods paper on evaluating in-silico perturbation</h2>
<div class="paper">
  <p class="ptitle">Working title: "Opposite by default: baselines that in-silico perturbation in single-cell foundation models needs"</p>
  <p><b>Result.</b> {badge('pass', 'established in lung, larger model, our design')} Random genes give opposed deletion and overexpression effects (ρ −0.59 and −0.61).</p><p><b>Argument.</b> Gene-level claims therefore need matched-control and random-gene baselines, paired cells, donor-level counting and a registered plan.</p><p>{badge('open', 'hypotheses')} The same holds in other tissues, for other goals and model sizes.</p><p><b>Bulk.</b> {badge('fail', 'not supported')} Across three registered panels (89 knockouts and knockdowns), a bulk network model did not recover regulator-specific effects; where it tracked, co-expression did as well or better.</p>
  <div class="figs four">
    <div class="pf pass"><b>Fig. 1</b> Design and the six checks</div>
    <div class="pf pass"><b>Fig. 2</b> Random-gene baseline in lung</div>
    <div class="pf open"><b>Fig. 3</b> Colon, and a swapped goal</div>
    <div class="pf pass"><b>Fig. 4</b> Four failure modes the checks catch</div>
    <div class="pf pass"><b>Fig. 5</b> T-cell genes against matched controls</div>
    <div class="pf open"><b>Fig. 6</b> Model size, new lung donors, known genes</div>
    <div class="pf pass"><b>Fig. 7</b> Bulk network ISP against two knockout sets</div>
  </div>
</div>
""", """If the open studies are completed, the material could form one methods paper. The slide separates three things. The result is established, but narrowly: in lung T cells, with the larger model and our design, random genes gave opposed effects. The argument, that gene-level claims need these baselines and checks, is a recommendation drawn from it. Extension to other tissues, goals and model sizes is a hypothesis. The bulk line is now a negative result with a narrow scope: in this design, bulk network perturbation did not predict knockout effects. Figures one, two, four, five and seven could be drawn from results we have; figures three and six need the studies on the previous slide. The colon result, open on the primary question and not replicated for the lung genes, changes the paper's emphasis rather than removing it, because the lung evidence and the documented failure modes stand on their own.""")

add("plain", 1.5, 7, f"""
<h2>Eight tests: the bulk network's agreement was matched or exceeded by its controls; Geneformer's lung gene results did not replicate</h2>
<ul class="synth">
  <li><b>Two kinds of test.</b> Bulk linear network, six tests: five compare predictions with measured perturbations, one is a control test of the fish regulator calls. Geneformer, two tests: perturbation outputs against matched controls and a random-gene null, then a second tissue. No Geneformer prediction has been checked against a measured perturbation.</li>
  <li><b>Bulk network, human perturbations.</b> Freimer <code>RECOVERED_NONSPECIFIC</code> (P3 gain over a shuffled network +0.039, p = 0.19); Weinstock <code>NOT_RECOVERED</code> (all four tests fail); K562 CRISPRi <code>RECOVERED_NONSPECIFIC</code> (P3 −0.008, p = 0.41; co-expression baseline 0.45 beats the model); Freimer TE subfamilies <code>TE_RECOVERED_NONSPECIFIC</code> (P3 0.007, p = 0.34). At the panel level (P3) the gain over shuffled wiring was not distinguishable from zero in any of the four.</li>
  <li><b>Fish regulator calls.</b> Indistinguishable from expression-matched random genes (p = 0.70; 0 of 30 after FDR); their directions did not track zebrafish knockouts (ρ −0.18, p = 0.50; 4 of 9 studies).</li>
  <li><b>Geneformer, lung to colon.</b> The classifier transfers (balanced accuracy 0.825, then 0.904); the deletion/overexpression anti-correlation appears in the same direction but is not stable (ρ −0.593, then −0.245; 78% of resamples against a 95% bar); the lung gene pattern did not replicate (3 of 10 keep their sign, within chance).</li>
  <li><b>TE biology, exploratory.</b> Gill TE share lower after developmental CO2 (−11.4% [−17.2, −5.1]; 54 libraries; not decomposed into TE and gene reads). Zebrafish loss-of-function leans 6 of 8 up (p = 0.29), consistent with derepression and not significant.</li>
</ul>
<p class="foot">The eight tests share data and methods and amount to three or four questions. At this power, a negative or open reading leaves room for effects the registered controls could not separate.</p>
""", """This slide puts the two projects side by side. The bulk network was tested six times, five of them against measured perturbations, and Geneformer twice, against controls and then in a second tissue; no Geneformer prediction has yet been checked against a measured perturbation. For the bulk network, wherever predictions tracked the measured effects, a shuffled network or co-expression alone tracked them as well. For Geneformer, the random-gene null showed a built-in sign structure, and the lung gene results did not replicate in colon. Replication was the informative step in both lines. Weinstock removed the weak agreement seen in Freimer and K562 restored it without the specificity, and colon did not reproduce the lung gene statuses, with low power and a real difference not separable. The two TE-biology items are exploratory. Several of the checks that shaped these readings were added in review and are post hoc, such as the control-only null, the mapping covariate and the read-total decomposition; none changed a registered status. What would change the picture is a measured single-cell perturbation ground truth for Geneformer, such as CRISPR or Perturb-seq screens in T cells; a full-length, stranded, total-RNA perturbation dataset with a control-only null registered in advance for the TE question; and better-replicated zebrafish loss-of-function studies. Sources: the cross-project synthesis report and the merged reports behind each line, all already cited on earlier slides.""")

add("end", 0.6, None, """
<h2 class="endh">Summary</h2>
<ol class="endlist">
  <li>In lung, random genes give opposed deletion and overexpression effects (ρ −0.59 to −0.61). Gene-level claims must exceed this baseline.</li>
  <li>Six evaluation criteria, each traced to a documented error, are now lab practice. In colon, random genes were opposed in the same direction but not stably (open); the lung gene pattern did not replicate.</li>
  <li>On bulk RNA-seq, a simple network model did not recover regulator-specific knockout effects in three registered panels (89 knockouts and knockdowns); where it tracked, co-expression did as well or better.</li>
  <li>For transposable elements, the same network did no better than random genes in 162 fish libraries, and in zebrafish its directions agreed with measured TE responses at chance level; in T-cell knockouts, TE shifts mostly stayed within a control-only null (post hoc; CBFB the exception).</li>
</ol>
<div class="byline">Every number is sourced in SOURCES.md in this talk's folder.</div>
""", """To summarise: the opposed effects of the two perturbations in random genes are the baseline that any gene-level claim has to exceed. The six criteria came from our own errors and are now how we evaluate every run; in colon, random genes were opposed in the same direction as in lung but not stably, so that question stays open, and the lung gene pattern did not replicate. On bulk RNA-seq, three registered panels of measured knockouts and knockdowns did not support regulator-specific prediction; the first panel's weak signal did not replicate, and the third tracked again without beating co-expression. For transposable elements, the same network did no better than random genes in fish, its directions agreed with measured zebrafish TE responses only at chance level, and in the T-cell knockouts the TE shifts mostly stayed within what control libraries show among themselves, CBFB the exception in a check added after the results. Thank you; I am glad to take questions.""")

add("plain", 0.3, None, """
<h2>Glossary</h2>
<dl class="gloss">
  <dt>Geneformer</dt><dd>A transformer model pretrained on about 104 million single cells, each encoded as a ranked gene list.</dd>
  <dt>Token</dt><dd>One gene in a cell's ranked list.</dd>
  <dt>Embedding</dt><dd>The model's vector for a cell; similar cells have similar embeddings.</dd>
  <dt>Fine-tuning</dt><dd>Further training on one task, here tumour versus normal T cells.</dd>
  <dt>In-silico perturbation (ISP)</dt><dd>Deleting a gene from, or moving it to the top of, a cell's list and measuring the embedding shift.</dd>
  <dt>Balanced accuracy</dt><dd>Accuracy averaged over the two classes; 0.5 is chance.</dd>
  <dt>Ambient RNA</dt><dd>Transcripts from other cells captured during sample preparation.</dd>
  <dt>Matched control genes</dt><dd>Genes with similar detection rate and mean rank to the gene tested.</dd>
  <dt>Spearman ρ</dt><dd>Rank correlation, from −1 (opposed) through 0 to 1 (aligned).</dd>
  <dt>p-value</dt><dd>How often chance alone would give a result at least this extreme.</dd>
  <dt>Registration</dt><dd>Recording the test, threshold and wording before any result exists.</dd>
  <dt>GPU-hour</dt><dd>One hour of computation on one graphics processor.</dd>
  <dt>Bulk RNA-seq</dt><dd>Sequencing of RNA pooled from all cells in a sample.</dd>
  <dt>Pseudo-bulk</dt><dd>A bulk-like profile made by summing single-cell data per sample.</dd>
  <dt>Gene regulatory network</dt><dd>A map of which transcription factors may regulate which genes.</dd>
  <dt>Transposable element (TE)</dt><dd>A repeated sequence that can copy itself in the genome; most copies are silenced.</dd>
</dl>
""", """The glossary is for reference and is repeated on the handout.""")


CSS = """
:root{--ink:#1d2b3a;--paper:#fbf8f2;--pass:#2a7f7a;--fail:#c4553a;--open:#c99a2e;--grey:#8a96a6;--tum:#7a5ea8;--nor:#3f7cbf;--line:#e3dccd}
@page{size:1280px 752px;margin:0 0 32px 0;background:var(--paper);
  @bottom-center{content:"Page " counter(page) " of " counter(pages);font-family:"Avenir Next","Helvetica Neue",sans-serif;font-size:14px;color:#8a96a6}}
*{box-sizing:border-box}
html,body{margin:0;background:#16212e;color:var(--ink);font-family:"Avenir Next","Helvetica Neue",Arial,sans-serif}
.slide{width:1280px;height:720px;position:relative;overflow:hidden;background:var(--paper);padding:70px 70px 40px;margin:24px auto;page-break-after:always;break-after:page}
.slide.title,.slide.end{background:var(--ink);color:var(--paper);display:flex;flex-direction:column;justify-content:center;padding-top:40px}
.slide.current{background:#f6f1e6}
.slide.plain,.slide.current{display:flex;flex-direction:column;justify-content:center;padding-top:74px;padding-bottom:36px}
.slide.plain>*,.slide.current>*{flex:none} .slide.plain .foot{position:static;margin-top:14px}
h1,h2,h3{font-family:"Iowan Old Style",Georgia,serif;font-weight:600;margin:0 0 18px;line-height:1.14}
h1.big{font-size:66px;color:var(--paper)} h2{font-size:38px;max-width:1140px} h3{font-size:23px;margin-bottom:10px}
.kicker{font-size:16px;letter-spacing:.14em;text-transform:uppercase;color:var(--open);margin-bottom:14px;font-weight:600}
.sub{font-family:"Iowan Old Style",Georgia,serif;font-size:28px;color:#d7dee7;margin:6px 0 0}
.byline{position:absolute;left:70px;bottom:52px;font-size:21px} .byline span{font-size:16px;color:#aab6c4}
p,li,dd{font-size:25px;line-height:1.4} .lead{font-size:26px;line-height:1.42;max-width:1140px;margin:0 0 16px}
.note{font-size:21px;color:#4a5a6e;font-style:italic} .small{font-size:17px}
.why{font-size:21px;color:#4a5a6e;border-left:4px solid var(--grey);padding-left:12px;margin-top:10px}
.quote{font-family:"Iowan Old Style",Georgia,serif;font-style:italic;font-size:21px}
.bar{position:absolute;top:20px;left:70px;right:70px;display:flex;gap:6px}
.bar span{flex:1;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:#a3acb8;border-top:5px solid #e6e0d3;padding-top:5px}
.bar span.done{border-top-color:#b9c2cc;color:#7d8896} .bar span.on{border-top-color:var(--ink);color:var(--ink);font-weight:700}
.two{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:8px}
.split{display:grid;grid-template-columns:0.95fr 1.2fr;gap:34px;align-items:center} .split.even{grid-template-columns:1.1fr 1fr;align-items:start}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px 26px}
.card.pass{border-top:6px solid var(--pass)} .card.fail{border-top:6px solid var(--fail)} .card.open{border-top:6px dashed var(--open)}
.card p{font-size:23px;margin:0 0 12px}
figure{margin:0} figure img{width:100%;border-radius:10px;border:1px solid var(--line)} figure.wide img{width:76%;display:block;margin:8px auto 18px}
.box{background:var(--ink);color:var(--paper);border-radius:14px;padding:24px 28px} .box p{font-size:23px}
.boxhead{font-size:15px;letter-spacing:.12em;text-transform:uppercase;color:var(--open);margin-bottom:10px;font-weight:600}
.badge{display:inline-block;font-family:"Avenir Next",sans-serif;font-size:17px;font-weight:600;padding:3px 12px;border-radius:999px;color:#fff;white-space:nowrap}
.badge.pass{background:var(--pass)} .badge.fail{background:var(--fail)} .badge.open{background:var(--open)}
h3 .badge{font-size:19px}
.legend{font-size:23px;margin-top:26px}
.chk{display:inline-block;white-space:nowrap;color:var(--ink);background:#efe9dc;border-radius:10px;padding:2px 10px 2px 4px;vertical-align:middle;line-height:1}
.chk .ic{width:40px;height:40px;display:inline-block;vertical-align:middle} .chk span{display:inline-block;vertical-align:middle;margin-left:3px;font-weight:700;font-size:20px;font-family:"Avenir Next",sans-serif}
.chk.sm .ic{width:28px;height:28px} .chk.sm span{font-size:16px}
h2 .chk{margin-right:8px;transform:translateY(-3px)}
.answers{font-size:21px;color:#4a5a6e;margin-top:12px}
.qrow{display:grid;grid-template-columns:1fr .8fr 1fr;gap:20px;align-items:center;margin:14px 0 22px}
.qcell{border-radius:18px;padding:44px 20px;text-align:center;color:#fff;font-size:28px;font-weight:600}
.qcell.tum{background:var(--tum)} .qcell.nor{background:var(--nor)}
.qarrow{text-align:center;font-size:22px;color:#4a5a6e} .qarrow b{font-size:54px;color:var(--ink);line-height:1}
.arc{margin:6px 0 0;padding-left:30px} .arc li{font-size:26px;margin-bottom:12px}
.sentence{display:flex;gap:12px;margin:22px 0 6px}
.tok{font-family:Menlo,monospace;font-size:26px;padding:12px 18px;border-radius:10px;color:#fff;background:var(--nor)}
.tok.mask{background:var(--ink);min-width:80px;text-align:center} .tok.dim{background:var(--grey)}
.caption{font-size:18px;color:#6a788a;margin:0 0 18px}
.cklist{display:grid;grid-template-columns:1fr 1fr;gap:8px 28px;margin-top:0}
.ck{display:flex;gap:14px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:12px;padding:8px 14px}
.ck b{display:block;font-size:24px} .ck div span{display:block;font-size:20px;color:#4a5a6e;line-height:1.3}
.foot{position:absolute;left:70px;right:70px;bottom:30px;font-size:17px;color:#4a5a6e} ul.synth{margin:6px 0 0;padding-left:22px} ul.synth li{font-size:19.5px;line-height:1.34;margin:0 0 11px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin:6px 0 20px}
.stamps{display:flex;flex-wrap:wrap;gap:10px;margin:4px 0 14px}
.stamp{display:inline-block;font-family:Menlo,monospace;font-size:17px;padding:5px 12px;border:1.5px solid var(--ink);border-radius:6px}
.stamp.pos{border-color:var(--pass);color:var(--pass)}
.tight{padding-left:22px;margin:0} .tight li{font-size:21px;line-height:1.36;margin-bottom:10px}
.tbl{width:100%;border-collapse:collapse;font-size:22px;margin-top:4px}
.tbl th{text-align:left;font-size:18px;letter-spacing:.08em;text-transform:uppercase;color:#6a788a;padding:6px 10px;border-bottom:2px solid var(--ink)}
.tbl td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:middle;line-height:1.3}
.tbl .badge{font-size:17px}
.paper{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px 28px}
.paper p{font-size:22px;margin:0 0 12px} .ptitle{font-family:"Iowan Old Style",Georgia,serif;font-style:italic;font-size:24px!important}
.figs{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:8px}
.pf{font-size:20px;border-radius:10px;padding:12px 14px;background:#faf7f0;border-left:6px solid var(--pass)} .pf.open{border-left:6px dashed var(--open)}
.gloss{display:grid;grid-template-columns:330px 1fr;gap:8px 24px} .gloss dt{font-family:"Iowan Old Style",Georgia,serif;font-weight:600;font-size:22px} .gloss dd{margin:0;font-size:20.5px;line-height:1.35}
.narrow{max-width:1040px}
.split.bulk{grid-template-columns:1.05fr 0.95fr;gap:22px;align-items:center} .split.bulk figure img{max-height:540px;width:auto;max-width:100%;display:block;margin:0 auto} .split.bulk p{font-size:17.5px;line-height:1.32;margin:0 0 8px} .split.bulk.zf{grid-template-columns:1fr 1fr;gap:26px} .split.bulk.zf p{font-size:16.5px;line-height:1.3;margin:0 0 9px} .split.bulk.zf figure img{max-height:468px} .tbl.mini{font-size:17px;margin:4px 0 10px} .tbl.mini td,.tbl.mini th{padding:4px 8px;font-size:16.5px} .tbl.mini .badge{font-size:14px;padding:2px 9px}
.slide .card .stamp{font-size:15px;padding:2px 8px}
.split.wide{grid-template-columns:0.72fr 1.45fr;gap:26px} .split.wide p{font-size:21.5px;line-height:1.38;margin:0 0 12px} .split.wide .lead{font-size:22.5px}
figure.full img{width:100%;display:block;margin:0 auto 14px} figure.full.slim img{width:80%;margin-bottom:10px}
.tri{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px;margin-top:6px} .tri .card p{font-size:20.5px} .tri .card p.small{font-size:17.5px;color:#33445a}
.two-col{columns:2;column-gap:36px} .two-col li{font-size:19px;line-height:1.32;margin-bottom:5px;break-inside:avoid}
.tbl.compact td{padding:5px 10px;font-size:19.5px} .tbl.dense td{padding:3px 8px;font-size:16px;line-height:1.22} .tbl.dense .badge{font-size:13.5px;padding:2px 9px}
figure.full.te img{width:80%;margin-bottom:10px} figure.full.tep img{width:88%;margin:2px auto 6px} .lead.tes{font-size:21px} .tecol{column-gap:30px} .tecol p{font-size:16.5px;line-height:1.3;margin:0 0 7px;break-inside:avoid} figure.full.slim img{max-height:292px;width:auto;max-width:86%}
.figs.four{grid-template-columns:repeat(4,1fr)} .figs.four .pf{font-size:17.5px;padding:9px 11px}
.endh{color:var(--paper);font-size:46px} .endlist{padding-left:34px;margin:0;max-width:1100px} .endlist li{color:#e6ebf1;font-size:25px;line-height:1.4;margin-bottom:16px}
.gloss{gap:4px 22px!important} .gloss dt{font-size:19px!important} .gloss dd{font-size:17.5px!important;line-height:1.28!important}

.pnum{position:absolute;right:26px;bottom:12px;font-size:13px;color:var(--grey)}
.notes{display:none;width:1280px;margin:-12px auto 24px;background:#fffdf7;border-radius:0 0 12px 12px;padding:16px 26px;font-family:"Iowan Old Style",Georgia,serif;font-size:17px;line-height:1.5;color:#26354a}
@media screen{body.deck .slide{display:none;margin:0 auto} body.deck .slide.on{display:block} body.deck .slide.on{display:flex}
  body.deck{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh}
  .help{color:#8a96a6;font-size:13px;text-align:center;margin:10px}}
@media print{html,body{background:var(--paper)} .slide{margin:0} .notes,.help{display:none!important} .pnum{display:none}}
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
    for k, (kind, mins, part, body, notes) in enumerate(S, 1):
        top = bar(part) if part is not None else ""
        parts.append(f'<section class="slide {kind}">{top}{body}<div class="pnum">{k} / {n}</div></section>')
        parts.append(f'<aside class="notes"><b>Speaker notes, slide {k} (about {mins:g} min).</b> {html.escape(notes)}</aside>')
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evaluating in-silico perturbation with Geneformer</title><style>{CSS}</style></head><body>
{''.join(parts)}
<div class="help">← → to move · N for speaker notes · click right or left half · print or PDF: slides.pdf</div>
<script>{JS}</script></body></html>"""
    with open(os.path.join(OUT, "slides.html"), "w") as f:
        f.write(doc)
    total = sum(s[1] for s in S)
    md = ["# Evaluating in-silico perturbation with Geneformer: speaker notes", "",
          f"Lab progress report, version 4, 2 October 2026. Kaisar Dauyey. {n} slides, about {total:.0f} minutes of talk, then 5 to 10 minutes of discussion. Every number is sourced in `SOURCES.md`.", ""]
    for k, (kind, mins, part, body, notes) in enumerate(S, 1):
        title = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body, re.S)
        t = re.sub(r"<svg.*?</svg>", "", title.group(1), flags=re.S) if title else kind
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()
        md += [f"## Slide {k}. {html.unescape(t)} (about {mins:g} min)", "", notes, ""]
    with open(os.path.join(OUT, "speaker-notes.md"), "w") as f:
        f.write("\n".join(md))
    print("slides", n, "minutes", round(total, 1))


if __name__ == "__main__":
    build()
