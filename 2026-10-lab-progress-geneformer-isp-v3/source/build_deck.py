"""Build 'Evaluating in-silico perturbation with Geneformer' (lab progress report, version 3, 2026-10-01).

Version 3 keeps the structure of version 2 (one point per slide, stated in the title; a progress bar; one
colour per verdict: teal passed, coral failed, amber not yet known; one icon per check) and adds diagrams
of the method, data figures from the external-cohort check (E0) and the colon classifier gate (E2), and
three slides on bulk RNA-seq, including a first test of a bulk network model against measured knockouts.

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


PARTS = ["Question", "Method", "Lessons", "Criteria", "Status", "Bulk RNA-seq", "Next"]


def bar(active):
    return '<div class="bar">' + "".join(
        f'<span class="{"on" if i == active else ("done" if i < active else "")}">{p}</span>' for i, p in enumerate(PARTS)) + "</div>"


S = []  # (kind, minutes, part index or None, html body, notes)


def add(kind, mins, part, body, notes):
    S.append((kind, mins, part, body, notes))


# ---------- 0. Question ----------
add("title", 0.5, None, """
<div class="kicker">Lab progress report · 1 October 2026 · version 3</div>
<h1 class="big">Evaluating in-silico perturbation with Geneformer</h1>
<p class="sub">Tumour-infiltrating T cells, the criteria a result must meet,<br>and the questions that remain open</p>
<div class="byline">Kaisar Dauyey<br><span>Laboratory of Mathematical Biology, Faculty of Advanced Life Science, Hokkaido University</span></div>
""", """This report covers our work since July on Geneformer and in-silico perturbation in tumour-infiltrating T cells. It is the third version of the talk. Compared with the second, it adds diagrams of the method, figures from the external-cohort feasibility check and the colon classifier gate, and a short section on whether the approach can be applied to bulk RNA-seq. I introduce each term before I use it, so no prior knowledge of the model is assumed.""")

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
  <li><b>Next.</b> Criteria, open questions and the outline of a methods paper.</li>
</ol>
<p class="legend">Colour code: """ + badge("pass", "passed") + " " + badge("fail", "failed") + " " + badge("open", "not yet known") + """</p>
""", """The talk has six parts, shown in the bar at the top of each slide. One colour code is used throughout: teal for a check that passed, coral for one that failed, amber for a question without an answer yet. Each of the six evaluation checks has its own icon, which reappears wherever that check applies.""")

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
<h2>Colon study (E2): registration and classifier gate passed; perturbation results pending</h2>
<div class="split"><div>
  <p>{badge('pass', 'registration reviewed')} {badge('pass', 'classifier gate')} {badge('pass', 'no-op gate')} {badge('open', 'ISP results')}</p>
  <p>New fold classifiers from the same base model. Pooled held-out balanced accuracy <b>0.904</b> (bar 0.60); <b>19 of 19</b> donors above chance; lowest 0.655; sign test p = 3.8 × 10⁻⁶.</p>
  <p>Perturbation run: 369 genes, both arms, 19 donors; started 02:42 JST, 1 October; finish expected the morning of 2 October, within a 52 GPU-hour limit.</p>
  <p class="note">MMR status is descriptive; no test was registered.</p>
</div><figure>{img('e2_gate.png', 'per-donor held-out balanced accuracy in the colon study')}</figure></div>
""", """The colon study repeats the lung design on the nineteen-donor cohort. Its registration was reviewed and approved before any GPU work. Five new fold classifiers were fine-tuned from the base model with the lung recipe unchanged. Pooled held-out balanced accuracy was 0.904, every donor was above chance, and the lowest donor, C134, at 0.655, also had the fewest tumour T cells. The no-op gate gave exactly zero. Mismatch-repair status is marked for description only; the lowest three donors are all MMR-proficient, but no test was registered and we draw no conclusion. The perturbation run is in progress and no result is shown. Sources: the colon classifier gate file at commit 2c104ab, the E2 interim report and the registration.""")

add("plain", 1.2, 4, f"""
<h2>What the results support, and what they do not</h2>
<div class="two">
  <div class="card pass"><h3>{badge('pass', 'Supported')}</h3>
    <ul class="tight">
      <li>Lung, 43 donors: a fine-tuned classifier separates tumour from normal T cells in held-out donors (0.825; 43 of 43 above chance).</li>
      <li>13 of 34 testable T-cell genes exceed their matched controls, stably.</li>
      <li>Deletion and overexpression give opposed effects for random genes.</li>
      <li>Colon, 19 donors: the tumour/normal separation is learnable (0.904; 19 of 19).</li>
    </ul></div>
  <div class="card open"><h3>{badge('open', 'Not shown')}</h3>
    <ul class="tight">
      <li>That any gene regulates T-cell state. A shift in embedding space is not a mechanism.</li>
      <li>Whether the opposed effects come from the model or from lung tissue (colon run pending).</li>
      <li>What the classifier reads: T-cell state, ambient RNA or T-cell subset composition.</li>
      <li>Whether the lung models generalise to new lung donors.</li>
    </ul></div>
</div>
""", """In lung, the classifier works on held-out donors, thirteen T-cell genes exceed their matched controls, and the opposed effects of the two perturbations are generic. In colon, the classifier also works. None of this shows that a gene regulates T-cell state. We also do not know whether the classifier reads T-cell state, ambient RNA or differences in subset composition between tissues, and we have not tested the lung models on new lung donors. Sources: the balanced-donor report and the colon interim report.""")

add("plain", 0.9, 4, """
<h2>The possible colon outcomes and their readings were fixed before the run</h2>
<div class="two">
  <div class="card"><h3>Random genes (primary)</h3>
    <p><b>Opposed in colon as well:</b> the effect is more likely a property of the model and design than of lung tissue.</p>
    <p><b>Not opposed:</b> tissue cannot be identified as the cause; study, processing and fold models also differ.</p></div>
  <div class="card"><h3>Lung reference genes</h3>
    <p>If 10 are testable, the lung pattern counts as repeated only if at least 9 keep their lung direction (8 of 9 if 9 are testable).</p>
    <p>Results are reported only after independent review.</p></div>
</div>
""", """These readings were written into the registration before the run started. If random genes are also opposed in colon, the effect more likely belongs to the model and the design. If they are not, tissue is only one of several differences between the studies, so we could not attribute the change to it. The lung reference genes count as repeating only at nine of ten. Sources: the colon study registration, sections 6.2, 6.3 and 7.""")

# ---------- 5. Bulk RNA-seq ----------
add("plain", 1.1, 5, f"""
<h2>Bulk RNA-seq: a bulk profile is an average over a mixed population, not a cell</h2>
<div class="split wide"><div>
  <p>Geneformer was pretrained on single-cell rank encodings. A bulk profile sums many cell types, so a gene's level reflects <b>composition</b> as well as <b>within-cell regulation</b>.</p>
  <p>Any perturbation model fitted on bulk data mixes the two: a shift could mean "this gene changes T-cell state" or "this sample has fewer T cells".</p>
  <p>Geneformer itself cannot take a bulk profile as input: the list would be cut at 4,096 tokens and lie outside the pretraining distribution.</p>
  <p>{badge('open', 'tested twice with a simpler model: next two slides')}</p>
</div><figure>{img('bulk_mix.png', 'composition changes the bulk level of a gene without any within-cell change')}</figure></div>
""", """We were asked whether this approach applies to bulk RNA-seq. The basic difficulty is that a bulk profile is an average over many cell types. In the schematic, gene G has the same level inside T cells in both samples, but the bulk level differs because the tumour sample contains fewer T cells. Any perturbation model fitted on bulk data inherits this mixture of composition and regulation within cells. Geneformer itself is not usable here, because a bulk profile does not resemble the single-cell lists it was trained on. We therefore tested a simpler network model, twice, as shown on the next two slides. The values in the figure are invented.""")

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
      <li>Transposable-element arm: <span class="stamp">NOT_TESTABLE</span>; no deposited TE count table found; re-alignment ruled out.</li>
    </ul></div>
  <div class="card open"><h3>{badge('open', 'Open')}</h3>
    <p class="small">Why the sets differ is untested. Freimer's regulators gave large, overlapping responses (median 394 responsive genes); Weinstock's gave small ones (70.5).</p>
    <p class="small">Uncontrolled differences: harvest at 5 days after electroporation versus 8 days after activation; UMI deduplication named in one study only; counting pipeline; unknown donor overlap.</p>
    <p class="small">Composition and within-cell regulation cannot be separated in bulk data. A revisit would need a composition covariate registered in advance, or single-cell or sorted data.</p></div>
</div>
""", """The pair of tests narrows the reading. As a group, the network did not beat a shuffled network in either set; the few single knockouts that did, three of 38 in the second set and none in the first, are about what chance gives. So the motif-and-promoter structure added nothing measurable beyond how many genes each factor may touch. In the first set a model-free co-expression baseline did as well as the network, and in the second both fell to chance together, so the first result was a shared response visible to plain correlation, not a property of the network. Fitted on unperturbed controls alone, which is how a bulk cohort without perturbations would have to be used, the network showed no agreement above chance in either set. Predicted magnitudes were 55 to 85 times too small. Why the two sets differ is not tested. Freimer's regulators were chosen as hits in screens and produced large, overlapping responses; Weinstock's produced much smaller ones. The runs also differ in harvest timing, deduplication, counting pipeline and possibly donors, none of which was controlled. The supported claim is narrow: in this design, bulk network perturbation is not a reliable way to predict knockout effects in T cells. Sources: the combined reading of the two bulk tests and the Weinstock report.""")

# ---------- 6. Next ----------
found = "".join(f"<tr><td>{chk(k, True)}</td><td>{c}</td><td>{e}</td></tr>" for k, c, e in [
    (1, "Register test, direction, threshold, reachable p and wording first", "August ordering read without a plan"),
    (2, "Classifier works on held-out paired donors; a no-op gives zero", "July groups came from different studies (0 of 18)"),
    (3, "Both perturbations on identical cells", "2,424 vs 202 to 1,131 cells; code default 14,738 of 15,179"),
    (4, "Exceed 20 or more matched control genes; flag ambient genes", "S100A8 and S100A9: same direction in 9 of 12; 55 of top 120 ambient"),
    (5, "Exceed the random-gene baseline; opposed signs are not evidence", "Random genes: ρ −0.593 (100), −0.608 (200)"),
    (6, "Donors as the unit; stable in 95% of resamplings; fixed outcome names", "One donor held 74.9% of the SCLC test cells")])
add("plain", 1.2, 6, f"""
<h2>Summary 1: the evaluation criteria, each traced to evidence</h2>
<table class="tbl"><tr><th></th><th>Criterion {badge('pass', 'adopted')}</th><th>Evidence behind it</th></tr>{found}</table>
<p class="foot">Status: lab practice (ISP-STD-1, 28 September 2026). Not yet published or tested by other groups.</p>
""", """Each criterion on the left is now lab practice, and each is tied to a documented episode on the right. These are established as practice in our lab, with sources for every row. They have not been tested by other groups, and some, such as the 95 percent stability threshold, are choices rather than derived results.""")

todo = "".join(f"<tr><td>{badge(s, l)}</td><td>{q}</td><td>{h}</td></tr>" for s, l, q, h in [
    ("open", "running", "Are the opposed effects a property of the model or of lung?", "Colon study (E2): gate passed, results pending"),
    ("open", "blocked", "Do the lung models generalise to new lung donors?", "E1: the one candidate dataset is not accessible"),
    ("open", "planned", "Are the opposed effects the same for an unrelated goal?", "Swap the goal centroid"),
    ("open", "planned", "Is the 13-gene result cell state or T-cell subset composition?", "Re-analyse within T-cell subsets"),
    ("open", "planned", "Can a simpler, interpretable method match the classifier?", "T-cell program scores (TCAT, Kotliar et al. 2025)"),
    ("open", "not started", "Do results depend on model size (104M vs 316M parameters)?", "Re-run a subset on both sizes"),
    ("open", "not started", "Does the method recover genes known to matter?", "Positive controls; experimental CRISPR screens in T cells"),
    ("fail", "not supported", "Does bulk network ISP recover knockout-specific targets?", "Two registered tests, 55 knockouts: non-specific, then not replicated")])
add("plain", 1.3, 6, f"""
<h2>Summary 2: what remains to be tested</h2>
<table class="tbl compact"><tr><th>Status</th><th>Question</th><th>Approach</th></tr>{todo}</table>
<p class="foot">All rows but the last are open. The bulk row has a result: not supported in this design.</p>
""", """This is what we do not yet know. The colon study is running, with its gate passed. Transfer to new lung donors is blocked by data access. Three studies are planned with little or no new GPU work: swapping the goal, re-analysing within T-cell subsets, and comparing the classifier with an interpretable baseline built from published T-cell programs. Model size and positive controls have not started; without positive controls, a negative result is hard to interpret. The bulk RNA-seq row now has a result: across two registered tests on 55 knockouts, the bulk network did not recover regulator-specific effects, and its one weak positive did not replicate. Sources: the next-cycle proposal, the independent-data design and the E0 feasibility report.""")

add("plain", 1.3, 6, f"""
<h2>These results could form one methods paper on evaluating in-silico perturbation</h2>
<div class="paper">
  <p class="ptitle">Working title: "Opposite by default: baselines that in-silico perturbation in single-cell foundation models needs"</p>
  <p><b>Result.</b> {badge('pass', 'established in lung, larger model, our design')} Random genes give opposed deletion and overexpression effects (ρ −0.59 and −0.61).</p><p><b>Argument.</b> Gene-level claims therefore need matched-control and random-gene baselines, paired cells, donor-level counting and a registered plan.</p><p>{badge('open', 'hypotheses')} The same holds in other tissues, for other goals and model sizes.</p><p><b>Bulk.</b> {badge('fail', 'not supported')} Across two registered tests (55 knockouts), a bulk network model did not recover regulator-specific effects; its one weak positive was matched by co-expression and did not replicate.</p>
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
""", """If the open studies are completed, the material could form one methods paper. The slide separates three things. The result is established, but narrowly: in lung T cells, with the larger model and our design, random genes gave opposed effects. The argument, that gene-level claims need these baselines and checks, is a recommendation drawn from it. Extension to other tissues, goals and model sizes is a hypothesis. The bulk line is now a negative result with a narrow scope: in this design, bulk network perturbation did not predict knockout effects. Figures one, two, four, five and seven could be drawn from results we have; figures three and six need the studies on the previous slide. A negative colon result would change the paper's emphasis rather than remove it, because the lung evidence and the documented failure modes stand on their own.""")

add("end", 0.6, None, """
<h2 class="endh">Summary</h2>
<ol class="endlist">
  <li>In lung, random genes give opposed deletion and overexpression effects (ρ −0.59 to −0.61). Gene-level claims must exceed this baseline.</li>
  <li>Six evaluation criteria, each traced to a documented error, are now lab practice. In colon the instrument passed its gates; results are pending.</li>
  <li>On bulk RNA-seq, a simple network model did not recover regulator-specific knockout effects in two registered tests (55 knockouts); the first test's weak signal did not replicate.</li>
</ol>
<div class="byline">Every number is sourced in SOURCES.md in this talk's folder.</div>
""", """To summarise: the opposed effects of the two perturbations in random genes are the baseline that any gene-level claim has to exceed. The six criteria came from our own errors and are now how we evaluate every run; the colon study has passed its gates and its results are pending. On bulk RNA-seq, two registered tests against measured knockouts did not support regulator-specific prediction, and the first test's weak signal did not replicate. Thank you; I am glad to take questions.""")

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
.foot{position:absolute;left:70px;right:70px;bottom:30px;font-size:17px;color:#4a5a6e}
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
.split.bulk{grid-template-columns:1.05fr 0.95fr;gap:22px;align-items:center} .split.bulk figure img{max-height:540px;width:auto;max-width:100%;display:block;margin:0 auto} .split.bulk p{font-size:17.5px;line-height:1.32;margin:0 0 8px} .tbl.mini{font-size:17px;margin:4px 0 10px} .tbl.mini td,.tbl.mini th{padding:4px 8px;font-size:16.5px} .tbl.mini .badge{font-size:14px;padding:2px 9px}
.slide .card .stamp{font-size:15px;padding:2px 8px}
.split.wide{grid-template-columns:0.72fr 1.45fr;gap:26px} .split.wide p{font-size:21.5px;line-height:1.38;margin:0 0 12px} .split.wide .lead{font-size:22.5px}
figure.full img{width:100%;display:block;margin:0 auto 14px} figure.full.slim img{width:80%;margin-bottom:10px}
.tri{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px;margin-top:6px} .tri .card p{font-size:20.5px} .tri .card p.small{font-size:17.5px;color:#33445a}
.two-col{columns:2;column-gap:36px} .two-col li{font-size:19px;line-height:1.32;margin-bottom:5px;break-inside:avoid}
.tbl.compact td{padding:5px 10px;font-size:19.5px}
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
          f"Lab progress report, version 3, 1 October 2026. Kaisar Dauyey. {n} slides, about {total:.0f} minutes of talk, then 5 to 10 minutes of discussion. Every number is sourced in `SOURCES.md`.", ""]
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
