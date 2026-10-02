"""Build 'Reading the Current, version 2' (lab progress talk, 2026-10-01).

Version 2 is written for students and professors together: one point per slide, stated in the title;
a figure on most slides; a progress bar; one colour per verdict (teal passed, coral failed, amber not yet
known); and one icon per check, reused wherever that check appears.

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


PARTS = ["Question", "The model", "Editing a cell", "How it fooled us", "Checks", "What we know", "Next"]


def bar(active):
    return '<div class="bar">' + "".join(
        f'<span class="{"on" if i == active else ("done" if i < active else "")}">{p}</span>' for i, p in enumerate(PARTS)) + "</div>"


S = []  # (kind, minutes, part index or None, html body, notes)


def add(kind, mins, part, body, notes):
    S.append((kind, mins, part, body, notes))


# ---------- 0. Question ----------
add("title", 0.5, None, """
<div class="kicker">Lab progress report · 1 October 2026 · version 2</div>
<h1 class="big">Reading the Current</h1>
<p class="sub">What Geneformer's "virtual gene edits" can tell us,<br>and the checks we needed before believing them</p>
<div class="byline">Kaisar Dauyey · Shinji Nakaoka<br><span>Laboratory of Mathematical Biology, Hokkaido University, Japan</span></div>
""", """This is the second version of our progress report. The first was written for people who already use Geneformer; this one is meant for everyone in the room, so I will explain each idea before using it. The story is about a model that always gives an answer, and about how we learned, mostly from our own mistakes, to tell when the answer means something.""")

add("plain", 0.8, 0, """
<h2>Our question: which genes, if changed, would push a tumour's T cells back toward normal?</h2>
<div class="qrow">
  <div class="qcell tum">T cell inside<br>a lung tumour</div>
  <div class="qarrow">change one gene<br><b>→</b><br>in the computer</div>
  <div class="qcell nor">T cell in the same<br>patient's normal lung</div>
</div>
<p class="lead">T cells are the immune cells that can kill tumour cells. Inside a tumour they often stop working well. If we knew which genes hold them in that state, we would know where to look for treatments. Testing every gene in the lab is slow and expensive, so we asked a computer model first.</p>
""", """T cells inside a tumour often look and behave differently from T cells in the same patient's healthy tissue. Our question is which genes, if we changed them, would move a tumour T cell back toward its healthy counterpart. Testing that experimentally, gene by gene, is slow. So we asked a model to make predictions first. The rest of the talk is about how far those predictions can be trusted.""")

add("plain", 0.8, 0, """
<h2>The short answer: the model always answers, so we built checks to tell when it means something</h2>
<ol class="arc">
  <li><b>The model.</b> What Geneformer is, in plain terms.</li>
  <li><b>Editing a cell.</b> How a "virtual gene edit" works and how we score it.</li>
  <li><b>How it fooled us.</b> Four moments, July to September, when a result looked real and was not, or not entirely.</li>
  <li><b>Checks.</b> Six rules we now apply, each born from one of those moments.</li>
  <li><b>What we know.</b> What our results support today, and what they do not.</li>
  <li><b>Next.</b> What we still need to test, and the paper it could become.</li>
</ol>
<p class="legend">Colour code throughout: """ + badge("pass", "passed") + " " + badge("fail", "failed") + " " + badge("open", "not yet known") + """</p>
""", """Here is the plan. The bar at the top of every slide shows where we are. One colour code runs through the whole talk: teal means a check passed, coral means it failed, amber means we do not know yet. And each of the six checks has its own small icon, which reappears whenever that check is relevant.""")

# ---------- 1. The model ----------
add("plain", 1.0, 1, f"""
<h2>Geneformer reads each cell as a list of its genes, most unusual first</h2>
<div class="split"><div>
  <p class="lead">A cell contains thousands of genes at different levels. Geneformer compares each gene with its usual level across many cells, then sorts. Genes that are always high (such as ACTB) sink; genes that make this cell distinctive rise to the top.</p>
  <p class="lead">The sorted list is the cell's "sentence". Each gene in it is a <b>token</b>, the model's word.</p>
</div><figure>{img('cell_ranking.png', 'a cell turned into a ranked list of genes')}</figure></div>
""", """Geneformer does not look at raw gene counts. For each cell it divides every gene's level by how high that gene usually is, then sorts. A housekeeping gene that is always abundant ends up near the bottom, and a gene that is unusually high in this particular cell moves to the front. The result is an ordered list, which the model treats like a sentence. The genes and bars on the slide are invented for illustration. Source: Theodoris and colleagues, Nature 2023.""")

add("plain", 0.9, 1, """
<h2>It learned what normal gene lists look like from about 104 million cells</h2>
<div class="sentence"><span class="tok">CD3E</span><span class="tok">IL7R</span><span class="tok mask">?</span><span class="tok">LTB</span><span class="tok">TCF7</span><span class="tok dim">…</span></div>
<p class="caption">Training game: hide a gene, ask the model to guess it from the rest of the list. Illustration, not data.</p>
<p class="lead">After playing this game on about 104 million human cells, the model places every cell at a point on an internal map, its <b>embedding</b>. Cells with similar lists land close together.</p>
<p class="note">The model comes in sizes; we have used a smaller and a larger one.</p>
""", """The model was trained by a guessing game. Hide one gene in a cell's list and ask the model to fill it in from the others. After doing that across about a hundred million cells, it has learned which genes tend to appear together. What we use is the model's internal position for each cell, its embedding: cells that look alike to the model sit close together on its map. We have used two sizes of the model, a smaller and a larger one; their sizes in parameters come up only on the summary slide, and the smaller one's 104 million parameters have nothing to do with the 104 million training cells. Sources: Theodoris and colleagues 2023 and the model card on Hugging Face.""")

add("plain", 1.0, 1, f"""
<h2>We then teach it one extra skill: telling a patient's tumour T cells from their normal T cells</h2>
<div class="split"><div>
  <p class="lead">This extra training is called <b>fine-tuning</b>. We always test it on patients the model has never seen.</p>
  <p class="lead">It worked well in lung cancer: right <b>82.5%</b> of the time, counting tumour and normal cells equally (this measure is called balanced accuracy; a coin toss scores 50%), and better than a coin toss for all <b>43 of 43</b> patients.</p>
</div><figure>{img('finetune.png', 'two clouds of cells separated by a line')}</figure></div>
""", """Next we give the model one specific task. From each patient we take T cells from the tumour and T cells from nearby normal lung, and we train the model to tell them apart. We always test it on patients it was not trained on. In our lung study, with 43 patients, it was right about 82 percent of the time when both groups are counted equally, and it beat chance for every single patient. That matters, because the edits on the next slide are measured along exactly this tumour-to-normal direction. Source: the balanced-donor lung report, classifier gate file.""")

# ---------- 2. Editing a cell ----------
add("plain", 1.2, 2, f"""
<h2>A virtual gene edit changes the list and asks where the cell moves on the map</h2>
<div class="split"><div>
  <p class="lead"><b>Delete</b> a gene: remove it from the cell's list. <b>Overexpress</b> it: move it to the top.</p>
  <p class="lead">Then measure whether the edited cell moved <b>toward the centre of that patient's normal T cells</b>. That movement is our score.</p>
  <p class="note">This is called in-silico perturbation (ISP). Nothing happens to a real cell; it is a question put to the model.</p>
</div><figure>{img('isp.png', 'an edited tumour T cell moving toward or away from normal')}</figure></div>
""", """Now the central idea. We take a tumour T cell's list and edit it in the computer. Deleting a gene removes it; overexpressing a gene moves it to the top of the list. The model reads the edited list and places the cell somewhere new. Our score is how much closer the cell came to the centre of the same patient's normal T cells. If deleting a gene moves cells toward normal, that gene might be holding them in the tumour state. I want to be clear that no real cell is touched. We are asking the model what it thinks, and its answer reflects what it has learned, which may or may not match biology.""")

add("plain", 1.2, 2, """
<h2>Our first results, in July and August, looked encouraging</h2>
<div class="two">
  <div class="card"><h3>July: a whole-genome screen</h3>
    <p>21,000 lung T cells, the smaller model, and almost 3 million single-gene deletions (2,937,776).</p>
    <p class="quote">Our own audit, 28 July: the lung adenocarcinoma and squamous-cell work could not on its own support what our conference abstract claimed about small-cell lung cancer.</p></div>
  <div class="card"><h3>August: a conference talk</h3>
    <p>We tested 50 genes in small-cell lung cancer (SCLC). Four passed in both directions in all three test patients: deleting moved cells toward normal, overexpressing moved them away.</p>
    <p>They were TIM-3, TIGIT, CTLA-4 and IL7R, genes linked to T-cell exhaustion or persistence.</p></div>
</div>
""", """The project began in July with a screen that deleted every gene in every held-out cell, almost three million deletions. Even then our own audit warned that it could not support the claims in an abstract we had submitted about small-cell lung cancer. So we built a small-cell line and, in August, presented four genes that passed in both directions in every test patient. They were familiar names from the T-cell exhaustion and persistence literature, which was reassuring. Over the next weeks we learned how much of that reassurance came from the method rather than the biology. Sources: the repository README, the 28 July audit, and the August talk.""")

# ---------- 3. How it fooled us ----------
add("plain", 1.1, 3, """
<h2>Trap 1: the strongest hits were not T-cell signals</h2>
<div class="two">
  <div class="card fail"><h3>Top of the screen</h3>
    <p>S100A8 and S100A9, among our most significant genes, moved cells the <i>same</i> way whether deleted or overexpressed in 9 of 12 comparisons. A real driver should not.</p>
    <p>Of the top 120 results, 55 were flagged as likely <b>ambient RNA</b>: traces of other cells' genes picked up during sample preparation.</p></div>
  <div class="card fail"><h3>The "normal" group</h3>
    <p>In July, the normal and tumour T cells came from different studies: none of the 18 studies supplied both. The model could partly have learned "which lab" instead of "which tissue".</p>
    <p>Later, 13 of the 15 July top genes could not be tested in T cells at all.</p></div>
</div>
<p class="answers">Answered by """ + chk(2, True) + " " + chk(4, True) + """</p>
""", """The first trap was in the screen's top hits. S100A8 and S100A9 were among the most significant results, but deleting and adding them pushed cells the same way, which a gene that actually drives a state should not do. Many top hits looked like ambient RNA, material from other cells that ends up in a T cell's droplet. Worse, the July comparison of normal and tumour T cells used different studies for each group, so the model may have learned study differences. When we later rebuilt the study around T cells properly, thirteen of the fifteen July genes could not be tested in T cells at all; they were epithelial and blood genes such as keratins. The small icons show which checks answer this trap: checking the instrument, and comparing with look-alike genes. Sources: the S100A8/S100A9 cross-reference report, the July methods file, and the balanced-donor report.""")

add("plain", 1.0, 3, f"""
<h2>Trap 2: one patient can look like a whole group</h2>
<figure class="wide">{img('one_patient.png', 'one patient held 74.9 percent of the cells')}</figure>
<p class="lead">Two of our analyses seemed to disagree about small-cell lung cancer. The cause was one patient who supplied three quarters (74.9%) of the small-cell test cells. Counting patients instead of cells (19 against 22 patients), the difference was not significant: p = 0.216.</p>
<p class="answers">Answered by {chk(6, True)}</p>
""", """The second trap is about counting. Cells from one patient are not independent; they share that patient's genetics, history and sample handling. When one patient supplies three quarters of the small-cell test cells, a cell-level analysis of that group is mostly an analysis of that patient. Once we counted patients rather than cells, an apparent difference between small-cell and adenocarcinoma T cells was no longer significant. Source: RESULTS_T6 in the repository.""")

add("plain", 1.0, 3, f"""
<h2>Trap 3: our two edits were measured on different cells</h2>
<div class="split"><div>
  <p class="lead">In the August panel, overexpression was scored on every test cell, but deletion only on cells that already carried the gene. Comparing the two arms compared different cells.</p>
  <p class="lead">The cause was a default in Geneformer's code: given a list of genes, it inserts an overexpressed gene into every cell (14,738 of 15,179 calls in our rebuilt study).</p>
  <p class="note">We attached a caveat to the four August genes: "a qualifier, not a retraction".</p>
  <p class="answers">Answered by {chk(3, True)}</p>
</div><figure>{img('unpaired.png', 'overexpression scored on 2,424 cells, deletion on 202 to 1,131')}</figure></div>
""", """The third trap was in our own instrument. We found that the August panel had scored deletion and overexpression on different sets of cells, because of a default in Geneformer's code that inserts an overexpressed gene into every cell when it is given a gene list. We had documented that default on 22 September and still missed its effect on our rebuilt study three days later. We did not retract the August genes, since the deletion evidence stands, but we attached a caveat. The panel has not been rerun. Sources: the 25 September correction and Amendment 3h of the balanced-donor registration.""")

add("current", 1.6, 3, f"""
<h2>Trap 4: even random genes show the pattern we had treated as evidence</h2>
<div class="split"><div>
  <p class="lead">Opposite effects of the two edits looked meaningful. So we ran the same pipeline on <b>random genes</b> with no known role.</p>
  <p class="lead">They did it too: rank correlation <b>−0.593</b> for 100 genes and <b>−0.608</b> for 200 (−1 is perfectly opposed, 0 unrelated).</p>
  <p class="note">Chance alone would give this at most about once in 100,000 tries, the smallest value our test can report.</p>
  <p class="answers">Answered by {chk(5, True)}</p>
</div><figure>{img('null_scatter.png', 'random genes: deletion and overexpression shifts are anti-correlated')}</figure></div>
""", """This is the result I most want you to take away. The four August genes passed because deletion and overexpression pushed cells in opposite directions. When we ran the identical pipeline on genes drawn at random, they showed the same opposition, strongly. Each dot is one random gene. The correlation was minus 0.593 for the registered hundred genes and minus 0.608 when we extended to two hundred. The p-value sits at the floor of the permutation test, so we report it as at most one in a hundred thousand. The random genes are drawn from genes detectable in lung tumour T cells, not from the whole genome. So opposite signs are the baseline, not the evidence. Sources: the two null-study result files, hashes a00ccb2f and c9e56026.""")

# ---------- 4. Checks ----------
rows = "".join(f'<div class="ck">{chk(k)}<div><b>{CHECK[k]}</b><span>{t}</span></div></div>' for k, t in [
    (1, "fix the test, the threshold and the wording before any result"),
    (2, "the model must work on unseen patients; an empty edit must give zero"),
    (3, "delete and overexpress are scored on identical cells"),
    (4, "a gene must move cells more than genes detected as often"),
    (5, "a pattern random genes also show is not evidence"),
    (6, "patients are the unit; results must be stable; outcomes get fixed names")])
add("plain", 1.0, 4, f"""
<h2>Six checks now stand between a result and a claim</h2>
<div class="cklist">{rows}</div>
<p class="foot">Written down on 28 September 2026 as the lab's standard for judging virtual gene edits (ISP-STD-1).</p>
""", """Each of these six checks answers one of the traps. The first three are about the experiment itself: decide the test in advance, make sure the instrument works, and compare like with like. The last three are about reading the result: beat genes that look similar, beat random genes, and count patients rather than cells, using fixed words for every outcome. We wrote them down as a lab standard on 28 September. The next slides take them one at a time.""")

add("plain", 1.1, 4, f"""
<h2>{chk(1)} Write the test down before any result exists</h2>
<div class="split even"><div>
  <p class="lead">Before running anything, we record the test, the direction we predict, the threshold for calling it significant, and the words we will use for each outcome. An independent reviewer signs off on the exact files.</p>
  <p class="lead">We also check that the test <b>can</b> reach significance with the data we will have. Small studies sometimes cannot.</p>
  <p class="why">Learned from: August, when we read meaning into an ordering we had not planned to test.</p>
</div><div class="box"><div class="boxhead">Example: the colon study</div>
  <p>We expect 10 lung reference genes to be testable in colon. To call the lung pattern repeated, at least <b>9 of 10</b> must keep their lung direction. (If only 9 can be tested, 8 of 9.)</p>
  <p>The first review of that plan failed: it claimed the software was unchanged, but one library had been downgraded. We corrected it before starting.</p>
</div></div>
""", """Writing the test down first sounds like bureaucracy. In practice it is what stops us from choosing a test after seeing the data, which we came close to doing in August. Part of the plan is checking that the test can reach significance at all; with ten genes, agreement has to reach nine of ten. The exact bar depends on how many genes turn out testable, and that rule is also fixed in advance. Our own first plan for the colon study failed review on a small but real point about the software environment. Source: the colon study registration, section 6.3.""")

add("plain", 1.1, 4, f"""
<h2>{chk(2)} Check the instrument before reading anything from it</h2>
<div class="split"><div>
  <p class="lead"><b>Does the model work?</b> It must tell tumour from normal T cells in patients it never saw, better than chance across patients. If not, we stop.</p>
  <p class="lead"><b>Does it stay still?</b> Run the pipeline twice on identical input with no edit. Any movement is noise that would later look like an effect.</p>
  <p>Colon, this week: {badge('pass', '90.4% right; 19 of 19 patients')} {badge('pass', 'empty edit moved 0.0')}</p>
  <p class="why">Learned from: the July model, which may have been telling studies apart.</p>
</div><figure>{img('gate_strip.png', 'per-patient accuracy in lung and colon')}</figure></div>
""", """Two checks come before any edit is made. First, the fine-tuned model has to work on patients it has never seen; in colon it was right about 90 percent of the time, every patient was above chance, and the lowest was 0.655. Second, an edit that changes nothing must produce no movement, and the largest shift we saw was exactly zero. Lung and colon are shown side by side for context only. The colon models are new, trained from the same base model, so this does not show that the lung models transfer. Sources: the colon classifier and no-op gate files at commit 2c104ab.""")

add("plain", 0.8, 4, f"""
<h2>{chk(3)} Score both edits on exactly the same cells</h2>
<div class="pair">
  <div class="card fail"><h3>{badge('fail', 'August panel')}</h3><p>Overexpress: 2,424 cells for every gene.<br>Delete: 202 to 1,131 cells.</p></div>
  <div class="card pass"><h3>{badge('pass', 'Since 25 September')}</h3><p>Both edits are analysed on the same cells, and every run is checked for it. (Panel code fixed 22 September; rebuilt study corrected 25 September.)</p></div>
</div>
<p class="lead narrow">A simple warning sign: if one edit always uses the same number of cells while the other varies by gene, the arms are not paired.</p>
<p class="why">Learned from: trap 3.</p>
""", """This check is short because the rule is simple: both edits are scored on the same cells. There is also a quick way to spot a violation. If one arm has a constant cell count across genes while the other varies, the two arms cannot be paired. That is exactly the signature the August panel had. The panel code was fixed on 22 September, and the rebuilt study was corrected on 25 September by reconstructing which cells carried each gene; every analysis since, including the colon study, re-checks those counts. Sources: the lab standard, clause B2, and Amendment 3h.""")

add("plain", 1.1, 4, f"""
<h2>{chk(4)} A gene must move cells more than genes that look like it</h2>
<div class="split"><div>
  <p class="lead">Genes found in many cells move cells more, whatever they do. So each gene is compared with <b>at least 20 look-alike genes</b>, detected about as often and ranked about as high.</p>
  <p class="lead">If 20 cannot be found, the gene is reported as <i>not estimable</i>. We never loosen the match to get an answer.</p>
  <p class="lead">Genes likely to be ambient RNA, or used to build the classifier itself, are flagged.</p>
  <p class="why">Learned from: trap 1 (S100A8, ambient RNA).</p>
</div><figure>{img('baseline.png', 'a hit inside the cloud of look-alike genes versus one outside it')}</figure></div>
""", """A raw shift means little on its own. Genes that are present in many cells move them more simply by being there. So every gene we test gets a comparison set of at least twenty genes matched on how often and how highly they are detected. A gene is only interesting if it stands outside that cloud, like the teal line in the sketch. If we cannot find twenty look-alikes, we say the gene cannot be estimated, rather than widening the match. In the lung study, 13 of 34 testable T-cell genes passed this check and stayed stable. Sources: the lab standard, clauses B1 and B4, and the balanced-donor report.""")

add("plain", 1.0, 4, f"""
<h2>{chk(5)} Opposite effects of delete and overexpress are not, on their own, evidence</h2>
<div class="two">
  <div class="card"><h3>What the random genes show</h3>
    <p>Opposed effects are what this model and this design produce for genes in general. They are the baseline.</p>
    <p>The study's own control genes agreed: rank correlation −0.658 (308 of 318 genes had enough data).</p></div>
  <div class="card"><h3>What they do not show</h3>
    <p>They do not erase the panel result: 13 of 34 testable T-cell genes still beat their look-alikes.</p>
    <p>They change what counts as evidence: an unusually <i>large</i> effect, measured against the random-gene baseline, not opposite signs.</p></div>
</div>
<p class="why">Learned from: trap 4.</p>
""", """This check follows directly from the random-gene result. If random genes show opposed effects, then opposed effects cannot be the evidence for any particular gene. The study's own control genes gave the same sign, minus 0.658; we compare that with other figures by sign only, because they are computed differently. What survives is the size of an effect relative to this baseline. That is narrower than what we claimed in August, and more honest. Sources: the null-study result file and the lab standard, clause B7.""")

add("plain", 1.0, 4, f"""
<h2>{chk(6)} Count patients, demand stable results, and name every outcome in advance</h2>
<div class="two">
  <div class="card"><h3>Patients and stability</h3>
    <p>The patient, not the cell, is the unit of evidence.</p>
    <p>A result must survive dropping any single control gene, and hold in at least 95% of 10,000 resamplings.</p></div>
  <div class="card"><h3>Fixed words</h3>
    <div class="stamps"><span class="stamp pos">positive</span><span class="stamp">negative</span><span class="stamp">opposite_direction</span><span class="stamp">not_estimable</span><span class="stamp">open</span></div>
    <p>We never write "no effect". A negative result means this test, at this size, did not meet its bar.</p></div>
</div>
<p class="why">Learned from: trap 2 (one patient) and the August wording.</p>
""", """The last check is about inference and language. We count patients. A result has to be stable: it must hold when we drop any single control gene and in at least 95 percent of ten thousand resamplings, otherwise we call it open. And every outcome gets one of a few labels fixed before the run. The phrase we never use is "no effect"; a small study can miss a real effect, so a negative result is reported with its direction, p and sample size. Our S100 ambient-RNA test in late September was negative in exactly this sense, at p = 6/70 and 34/70. Sources: the lab standard, clauses A6, B5 and B8, and the S100 result file.""")

# ---------- 5. What we know ----------
add("plain", 1.3, 5, f"""
<h2>What our results support today, and what they do not</h2>
<div class="two">
  <div class="card pass"><h3>{badge('pass', 'Supported (lung, 43 patients)')}</h3>
    <ul class="tight">
      <li>A fine-tuned model separates tumour from normal T cells in unseen patients (82.5%; 43 of 43 above chance).</li>
      <li>13 of 34 testable T-cell genes move cells more than their look-alikes, stably.</li>
      <li>Delete and overexpress give opposed effects for random genes too.</li>
      <li>Colon: the tumour/normal split is learnable too (90.4%; 19 of 19).</li>
      <li>Colon: the lung gene pattern did not repeat (3 of 10 genes kept their lung direction).</li>
    </ul></div>
  <div class="card open"><h3>{badge('open', 'Not shown')}</h3>
    <ul class="tight">
      <li>That any gene controls T-cell state. A move on the model's map is not a mechanism.</li>
      <li>Whether the opposed effects come from the model or from lung tissue: in colon they point the same way but are not stable (next slide).</li>
      <li>What the classifier actually reads: T-cell state, ambient RNA, or the mix of T-cell types.</li>
      <li>Whether the lung models work on new lung patients.</li>
    </ul></div>
</div>
""", """Here is where the evidence stands. In lung, the classifier works on unseen patients, a curated set of thirteen T-cell genes passes the look-alike check, and the opposed effects of the two edits are generic. In colon, the classifier also works, and the lung gene pattern did not repeat. What we cannot say is just as important. None of this shows that a gene controls T-cell state; a shift on the model's map is not a mechanism. We do not know whether the classifier is reading T-cell state, ambient RNA or simply a different mix of T-cell types between tissues. And we have not yet tested the lung models on new lung patients. Sources: the balanced-donor report and the colon interim report.""")

add("plain", 1.4, 5, f"""
<h2>The colon test: random genes were opposed again, but not reliably; the lung gene pattern did not repeat</h2>
<div class="two">
  <div class="card open"><h3>{badge('open', 'Open')} Random genes</h3>
    <p>Delete and overexpress again pushed random genes in opposite directions: rank correlation −0.25 (lung: −0.59), p = 0.0067.</p>
    <p>It survived dropping any one gene, but held in only 78% of resamplings; we required 95%.</p>
    <p>Our pre-written reading: same direction as lung, not stable, so the question stays open.</p></div>
  <div class="card fail"><h3>{badge('fail', 'Not repeated')} Lung reference genes</h3>
    <p>Of 10 lung genes we could test, 3 kept their lung direction; we required 9. Seven pointing the other way is within what chance gives.</p>
    <p>One gene, PRF1, met all its pre-set tests in colon; in lung it was undecided.</p></div>
</div>
<p class="foot">We cannot blame tissue for the differences: the colon data come from another study, with different sample handling, new models and fewer patients (19 against 43).</p>
""", """The colon run finished on the morning of 2 October, and the results have passed internal review. The first question was whether random genes are opposed in colon too. They are, in the same direction as in lung, but more weakly, and the pattern held in only 78 percent of resamplings, short of the 95 percent we required before starting. So by the reading we wrote down in advance, the direction matches lung but the result is not stable, and the question stays open. The second question was whether the lung reference genes keep their direction. Three of ten did, where we needed nine, so the lung gene pattern did not repeat. Seven pointing the other way is about what chance would give, so this is not a reversal either. One gene, PRF1, met all its pre-set tests in colon, though it was undecided in lung. None of these differences can be put down to tissue, because the colon study differs from the lung studies in almost every other way too, and it has fewer patients. Sources: the colon study results report and its result files on geneformer-lung-tcell main, merge 4cce44a.""")

# ---------- 6. Next ----------
found = "".join(f"<tr><td>{chk(k, True)}</td><td>{c}</td><td>{e}</td></tr>" for k, c, e in [
    (1, "Register test, direction, threshold, reachable p and wording first", "August ordering read without a plan"),
    (2, "Model must work on unseen, paired patients; empty edit gives zero", "July groups came from different studies (0 of 18)"),
    (3, "Both edits on identical cells", "2,424 vs 202 to 1,131 cells; code default 14,738 of 15,179"),
    (4, "Beat 20 or more look-alike genes; flag ambient genes", "S100A8 and S100A9: same direction in 9 of 12; 55 of top 120 ambient"),
    (5, "Beat random genes; opposite signs are not evidence", "Random genes: −0.593 (100), −0.608 (200)"),
    (6, "Count patients; stable in 95% of resamplings; fixed outcome names", "One patient held 74.9% of the SCLC test cells")])
add("plain", 1.3, 6, f"""
<h2>Summary 1: the evaluation criteria we found, each traced to evidence</h2>
<table class="tbl"><tr><th></th><th>Criterion {badge('pass', 'adopted')}</th><th>Evidence that taught it</th></tr>{found}</table>
<p class="foot">Status: adopted as lab practice (ISP-STD-1, 28 September 2026). Established as practice, not yet published or tested by others.</p>
""", """This table is the first half of what I would call our contribution so far. Each criterion on the left is now lab practice, and each one is tied to a specific piece of evidence on the right, from our own work. I want to be precise about the status. These are established as practice in our lab, with sources for every row. They have not yet been tested by anyone else, and some, like the 95 percent stability bar, are choices we made rather than results we derived.""")

todo = "".join(f"<tr><td>{badge(s, l)}</td><td>{q}</td><td>{h}</td></tr>" for s, l, q, h in [
    ("open", "open", "Are the opposed effects a property of the model or of lung?", "Colon (E2): same direction, not stable; lung gene pattern did not repeat"),
    ("open", "blocked", "Do the lung models work on new lung patients?", "E1: the one candidate dataset is not yet accessible"),
    ("open", "planned", "Are the opposed effects the same whatever the goal? (calibrating the random-gene baseline)", "Swap the goal for an unrelated one"),
    ("open", "planned", "Is the 13-gene result cell state, or just a different mix of T-cell types?", "Re-analyse within T-cell subsets"),
    ("open", "planned", "Can a simple, readable method match the model's 82.5%?", "T-cell program scores (TCAT, Kotliar et al. 2025)"),
    ("open", "not started", "Do results change with model size (104M vs 316M parameters)?", "Re-run a subset on both sizes"),
    ("open", "not started", "Does the method find genes we already know matter?", "Positive controls; real gene-editing screens in T cells")])
add("plain", 1.4, 6, f"""
<h2>Summary 2: what we still need to test</h2>
<table class="tbl"><tr><th>Status</th><th>Question</th><th>How</th></tr>{todo}</table>
<p class="foot">All rows are open. The colon row has a first answer: open for random genes, not repeated for the lung genes.</p>
""", """The second half is what we do not know. The colon test has a first answer: random genes were opposed in the same direction as in lung, but not stably, so whether the effect belongs to the model or to lung stays open; the lung gene pattern did not repeat. The lung transfer test is blocked, because the one independent lung dataset we found is packaged in a way we could not access. Three studies are planned without new GPU work, or with modest GPU work: swapping the goal to see whether the opposed effects depend on it, re-analysing within T-cell subsets, and comparing the model with a readable baseline built from published T-cell programs. Two questions have not started: whether model size changes the results, and whether the method recovers genes we already know matter. Without that last one, a negative result is hard to interpret. Sources: the next-cycle proposal, the independent-data design and the E0 feasibility report.""")

add("plain", 1.3, 6, f"""
<h2>Together these could become one paper on how to judge virtual gene edits</h2>
<div class="paper">
  <p class="ptitle">Working title: "Opposite by default: baselines that in-silico perturbation in single-cell foundation models needs"</p>
  <p><b>Result.</b> {badge('pass', 'established in lung, larger model, our design')} Random genes give opposed delete and overexpress effects (rank correlation −0.59 and −0.61).</p><p><b>Our argument.</b> Gene-level claims therefore need look-alike and random-gene baselines; the traps add paired cells, patient-level counting and a plan filed first.</p><p>{badge('open', 'hypothesis')} The same holds in other tissues, for other goals and model sizes.</p>
  <div class="figs">
    <div class="pf pass"><b>Fig. 1</b> Design and the six checks</div>
    <div class="pf pass"><b>Fig. 2</b> Random-gene baseline in lung</div>
    <div class="pf open"><b>Fig. 3</b> The same in colon, and under a swapped goal</div>
    <div class="pf pass"><b>Fig. 4</b> Four traps the checks catch</div>
    <div class="pf pass"><b>Fig. 5</b> T-cell genes against look-alikes</div>
    <div class="pf open"><b>Fig. 6</b> Model size, new lung patients, known genes</div>
  </div>
</div>
""", """If the open studies come through, the material could become one methods paper. A working title would be "Opposite by default". The slide separates three things. The result is established, but narrowly: in lung T cells, with the larger model and our design, random genes gave opposed effects. The argument we would make from it, that gene-level claims need these baselines and checks, is a recommendation, not a finding; paired cells and patient-level counting come from the other traps. Whether the result holds in other tissues, under other goals and for other model sizes is still a hypothesis. Figures one, two, four and five could be drawn today from results we have. Figures three and six need the studies on the previous slide. The colon result, open for random genes and not repeated for the lung genes, changes the paper's shape rather than removing it, because the lung evidence and the traps stand on their own.""")

add("end", 0.4, None, """
<h1 class="big">The model always answers.<br>The checks tell us when to listen.</h1>
<p class="sub">Measure what random genes do first, then claim what one gene does.</p>
<div class="byline">Every number is sourced in SOURCES.md in this talk's folder.</div>
""", """To close: almost every correction since July came from measuring something we had taken for granted, such as the studies behind a group, the cells behind an edit, the patient behind a difference, or the random genes behind a pattern. The opposed effects in random genes are not a failure of the method; they are the baseline any claim has to beat. Thank you. I am happy to take questions, and if any of the open studies interests you, please come and talk to me.""")

add("plain", 0.3, None, """
<h2>Glossary: the few terms we kept</h2>
<dl class="gloss">
  <dt>Geneformer</dt><dd>A model trained on about 104 million cells, each written as a ranked list of genes.</dd>
  <dt>Token</dt><dd>One gene in a cell's list: the model's word.</dd>
  <dt>Embedding</dt><dd>A cell's position on the model's internal map; similar cells sit close together.</dd>
  <dt>Fine-tuning</dt><dd>Extra training on one task, here tumour versus normal T cells.</dd>
  <dt>In-silico perturbation (ISP)</dt><dd>A virtual gene edit: delete a gene from the list or move it to the top, then measure where the cell moves.</dd>
  <dt>Balanced accuracy</dt><dd>How often the model is right, counting both groups equally; 50% is a coin toss.</dd>
  <dt>Ambient RNA</dt><dd>Genetic material from other cells picked up during sample preparation.</dd>
  <dt>Look-alike (matched control) genes</dt><dd>Genes detected about as often and ranked about as high as the gene being tested.</dd>
  <dt>Rank correlation (ρ)</dt><dd>From −1 (perfectly opposed) through 0 (unrelated) to 1 (perfectly aligned).</dd>
  <dt>p-value (p)</dt><dd>How often chance alone would give a result at least this strong; small means unlikely by chance.</dd>
  <dt>GPU-hour</dt><dd>One hour of work on one graphics processor, the chip that runs the model.</dd>
  <dt>Pre-registration</dt><dd>Writing down the test, its threshold and its wording before any result exists.</dd>
</dl>
""", """The glossary is here and on the handout for reference. I will not read it aloud.""")


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
<title>Reading the Current, version 2</title><style>{CSS}</style></head><body>
{''.join(parts)}
<div class="help">← → to move · N for speaker notes · click right or left half · print or PDF: slides.pdf</div>
<script>{JS}</script></body></html>"""
    with open(os.path.join(OUT, "slides.html"), "w") as f:
        f.write(doc)
    total = sum(s[1] for s in S)
    md = ["# Reading the Current, version 2: speaker notes", "",
          f"Lab progress report, 1 October 2026. Kaisar Dauyey · Shinji Nakaoka. {n} slides, about {total:.0f} minutes of talk, then 5 to 10 minutes of discussion. Every number is sourced in `SOURCES.md`.", ""]
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
