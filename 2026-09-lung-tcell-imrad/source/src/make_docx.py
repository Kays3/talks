"""Editable Word report of the IMRaD talk.

Built only from what the talk already says:
- Abstract: the four sections of make_lung_tcell_talk_imrad_abstract_20260925.py.
- Introduction / Methods / Results / Discussion / Limitations: the slides'
  own text, captured from the PDF generator (capture_deck.py) and grouped by
  each slide's section label. Every sentence and number is the slide's,
  verbatim; a slide's title becomes a Heading 2, a card's bold lead line
  stays a bold line, and side-by-side cards become a Word table.
- Figures: the slide images, with numbered captions (Word SEQ fields).
- References/Sources: the per-slide table of the sources note, plus the data
  files this package ships (data/MANIFEST.tsv).
No [TODO] marker remains: the human decided contact, talk length and byline on
2026-09-29. todo() is kept for any future open decision.
"""
from __future__ import annotations

import contextlib
import csv
import datetime as dt
import io
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

from capture_deck import capture, normalise_zip, plain
import make_lung_tcell_talk_imrad_abstract_20260925 as abstract

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "editable", "lung_tcell_report_imrad_20260925.docx")
SOURCES_NOTE = os.path.join(ROOT, "docs", "lung_tcell_talk_imrad_sources_20260925.md")
MANIFEST = os.path.join(ROOT, "data", "MANIFEST.tsv")
MM = 72 / 25.4

SECTION_OF = [  # slide section label prefix -> report section
    ("BACKGROUND", "Introduction"),
    ("INTRODUCTION", "Introduction"),
    ("METHODS", "Methods"),
    ("RESULTS", "Results"),
    ("DISCUSSION · SYNTHESIS", "Discussion"),
    ("DISCUSSION · LIMITATIONS", "Limitations"),
]


def todo(paragraph, text):
    run = paragraph.add_run(f"[TODO] {text}")
    run.bold = True
    run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return run


def add_field(paragraph, instr, cached):
    """A real Word field (TOC, SEQ): Word/LibreOffice update it; `cached` shows until then."""
    for kind, text in (("begin", None), ("instr", instr), ("separate", None), ("text", cached), ("end", None)):
        run = paragraph.add_run()
        if kind in ("begin", "separate", "end"):
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            if kind == "begin":
                fc.set(qn("w:dirty"), "true")
            run._r.append(fc)
        elif kind == "instr":
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = f" {instr} "
            run._r.append(it)
        else:
            run.text = text


def add_runs(paragraph, runs):
    for r in runs:
        run = paragraph.add_run(r["text"])
        run.bold = r["bold"] or None
        run.italic = r["italic"] or None
        if r["mono"]:
            run.font.name = "Courier New"


def para(doc_or_cell, p):
    out = doc_or_cell.add_paragraph()
    add_runs(out, p["runs"])
    return out


def sources_table_rows():
    rows = []
    for line in open(SOURCES_NOTE, encoding="utf-8"):
        if re.match(r"^\| \d+ \| ", line) and line.count("|") == 5:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
    return [r for r in rows if len(r) == 4]


def md_inline(paragraph, text):
    """Sources-note cells: `code` -> Courier New, **bold** -> bold; nothing else."""
    for part in re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", text):
        if not part:
            continue
        if part.startswith("`"):
            paragraph.add_run(part[1:-1]).font.name = "Courier New"
        elif part.startswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        else:
            paragraph.add_run(part)


def slide_parts(slide, H):
    eyebrow = next(e["text"] for e in slide if e["kind"] == "string" and e["y"] > H - 40 * MM)
    footer = [e["text"] for e in slide if e["kind"] == "string" and e["y"] < 12 * MM
              and not re.fullmatch(r"\d+ / \d+", e["text"])]
    frames = [e for e in slide if e["kind"] == "frame" and e["paras"]]
    title = [e for e in frames if e["title"]]
    body = [e for e in frames if not e["title"]]
    images = [e for e in slide if e["kind"] == "image" and not e["path"].endswith("qr.png")]
    return eyebrow, footer, title, body, images


def build() -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        deck = capture()
    H = deck["height"]
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Mm(22))
    # Page numbers, bottom centre (house rule of 2026-09-30: every report PDF carries "Page N of M").
    foot = sec.footer.paragraphs[0]
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    foot.add_run("Page ")
    add_field(foot, "PAGE", "1")
    foot.add_run(" of ")
    add_field(foot, "NUMPAGES", "1")
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)
    for name in ("Title", "Heading 1", "Heading 2", "Heading 3", "Caption"):
        doc.styles[name].font.name = "Arial"

    # ---- Title block -------------------------------------------------------
    doc.add_paragraph(abstract.TITLE, style="Title")
    s1 = deck["slides"][0]
    sub = next(e for e in s1 if e["kind"] == "frame")["paras"][2]
    para(doc, sub).runs[0].italic = True
    p = doc.add_paragraph()
    p.add_run("Kaisar Dauyey · Shinji Nakaoka").bold = True
    p = doc.add_paragraph("Laboratory of Mathematical Biology, Faculty of Advanced Life Science, Hokkaido University")
    doc.add_paragraph("Contact: k.dauyey.bio.nu@gmail.com")
    from additions import APPENDIX_START, QUESTIONS_MIN, SLOT_MIN, TIMING, mmss
    doc.add_paragraph(f"Talk length: within {SLOT_MIN} minutes; the time slot itself is not fixed. The main talk "
                      f"(slides 1-{APPENDIX_START - 1}) is budgeted at {mmss(sum(TIMING.values()))} of speaking, "
                      f"leaving about {QUESTIONS_MIN} minutes for questions; per-slide budgets are in the "
                      f"deck's speaker notes. The abstract has no stated word limit.")
    doc.add_paragraph("Written report of the IMRaD oral presentation built 2026-09-25 23:57 JST (14:57Z). Every "
                      "sentence and number below is taken from the deck or its abstract; sources are listed at "
                      "the end.")
    doc.add_paragraph("Contents", style="Heading 1")
    add_field(doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u',
              "Right-click and choose Update Field to build the table of contents.")

    # ---- Abstract ----------------------------------------------------------
    doc.add_heading("Abstract", level=1)
    for label, text in abstract.SECTIONS:
        p = doc.add_paragraph()
        p.add_run(f"{label}: ").bold = True
        p.add_run(text)

    # ---- Body: original slides (verbatim) + material added 2026-09-28 ------
    from additions import NEW, PLAIN, REFERENCES, SRC
    fig_n = 0
    current = None

    def heading1(section):
        nonlocal current
        if section != current:
            doc.add_heading(section, level=1)
            current = section

    def plain_para(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.italic = True

    def word_table(header, rows, widths):
        t = doc.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"
        t.autofit = False
        for j, h in enumerate(header):
            t.cell(0, j).paragraphs[0].add_run(h).bold = True
        for r in rows:
            cells = t.add_row().cells
            for j, v in enumerate(r):
                md_inline(cells[j].paragraphs[0], v)
        for col, w in zip(t.columns, widths):
            col.width = Mm(w)
        for row in t.rows:
            for cell, w in zip(row.cells, widths):
                cell.width = Mm(w)
                for p_ in cell.paragraphs:
                    for r_ in p_.runs:
                        r_.font.size = Pt(9)
        doc.add_paragraph()

    def md_para(text):
        p = doc.add_paragraph()
        md_inline(p, text)
        return p

    def added(key, section):
        spec = NEW[key]
        heading1(section)
        doc.add_heading(spec["title"], level=2)
        note = doc.add_paragraph()
        r = note.add_run("Added 2026-09-28 for a general genetics audience; not in the 25 Sep deck.")
        r.italic = True
        r.font.size = Pt(8.5)
        for t_ in spec.get("intro", []):
            md_para(t_)
        for head, texts in spec.get("cards", []):
            p = doc.add_paragraph()
            p.add_run(head).bold = True
            for t_ in texts:
                md_para(t_)
        if spec.get("table"):
            tb = spec["table"]
            scale = 166 / sum(tb["widths_mm"])
            word_table(tb["header"], tb["rows"], [w * scale for w in tb["widths_mm"]])
        for t_ in spec.get("intro_after", []):
            md_para(t_)
        if spec.get("plain"):
            plain_para(spec["plain"])
        p = doc.add_paragraph()
        r = p.add_run("Sources: " + " | ".join(spec["notes"]))
        r.italic = True
        r.font.size = Pt(8)

    def original(n, section):
        nonlocal fig_n
        slide = deck["slides"][n - 1]
        eyebrow, footer, title, body, images = slide_parts(slide, H)
        heading1(section or next(s for prefix, s in SECTION_OF if eyebrow.startswith(prefix)))
        doc.add_heading(" ".join(plain(p["runs"]) for f in title for p in f["paras"]), level=2)
        # Side-by-side cards (3+ frames sharing a baseline) -> one Word table.
        by_y: dict[int, list] = {}
        for f in body:
            by_y.setdefault(round(f["y"]), []).append(f)
        done = set()
        for f in body:
            row = by_y[round(f["y"])]
            if len(row) >= 3:
                if id(row[0]) in done:
                    continue
                done.add(id(row[0]))
                row = sorted(row, key=lambda e: e["x"])
                t = doc.add_table(rows=2, cols=len(row))
                t.style = "Table Grid"
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                for j, card in enumerate(row):
                    head, *rest = card["paras"]
                    hc = t.cell(0, j).paragraphs[0]
                    add_runs(hc, head["runs"])
                    for r in hc.runs:
                        r.bold = True
                    bc = t.cell(1, j)
                    for k, p_ in enumerate(rest):
                        add_runs(bc.paragraphs[0] if k == 0 else bc.add_paragraph(), p_["runs"])
                doc.add_paragraph()
            else:
                for p_ in f["paras"]:
                    para(doc, p_)
        if n in PLAIN:
            plain_para(PLAIN[n])
        for im in images:
            fig_n += 1
            width = Mm(160) if im["w"] > 110 * MM else Mm(120)
            base = os.path.basename(im["path"])
            redrawn = base in ("detection_orig.png", "fig_t6_reversal_orig.png")
            path = os.path.join(ROOT, "data", "assets", base.replace("_orig", "")) if redrawn else im["path"]
            doc.add_picture(path, width=width)
            cap = doc.add_paragraph(style="Caption")
            cap.add_run("Figure ")
            add_field(cap, "SEQ Figure \\* ARABIC", str(fig_n))
            cap.add_run(f". Slide {n} of the 25 Sep deck: " + " ".join(plain(p["runs"]) for f in title for p in f["paras"])
                        + "." + (f" Source: {footer[0]}." if footer else "")
                        + f" Image: data/assets/{os.path.basename(path)}"
                        + (" (readable redraw of 2026-09-28, same data; original: data/assets/" + base + ")." if redrawn else "."))
            if base == "detection_orig.png":
                doc.add_picture(os.path.join(ROOT, "data", "assets", "detection_rank_report.png"), width=Mm(150))
                cap = doc.add_paragraph(style="Caption")
                cap.add_run(f"Figure {fig_n} (continued), panel b: all 31 immune / lineage genes ranked by deletion "
                            "shift, SCLC → normal. Panel b of the same original figure, drawn separately so its gene "
                            "names stay readable. Image: data/assets/detection_rank_report.png.")
        if footer:
            p = doc.add_paragraph()
            r = p.add_run(f"Source (slide {n} of the 25 Sep deck): {footer[0]}")
            r.italic = True
            r.font.size = Pt(8.5)

    added("background", "Introduction")
    added("poster", "Introduction")
    for n in (2, 3, 4):
        original(n, "Introduction")
    added("methods_plain", "Methods")
    for n in (5, 6, 7, 8):
        original(n, None)
    for n in (9, 10, 11, 12, 13, 14):
        original(n, None)
    added("s100", "Results")
    original(17, None)
    doc.add_heading("The S100 ISP result in context (added 2026-09-28)", level=2)
    doc.add_paragraph(
        "The pre-registered S100 in silico perturbation test (Results) was negative in both LUAD comparisons: the "
        "four S100 genes at high ambient-RNA risk did not beat their detection-matched controls more than the four "
        "at low risk. The test was small (4 v 4; the smallest attainable p is 2/70), so it could only have passed "
        "on a complete separation of the two groups, and no claim is drawn from the low-risk genes' high scores. "
        "It neither confirms nor contradicts the S100A8/S100A9 findings above: those two genes are classifier "
        "anchors and were deliberately excluded from the test.")
    p = doc.add_paragraph()
    r = p.add_run("Sources: " + SRC["s100_result"] + "; " + SRC["isp_std"])
    r.italic = True
    r.font.size = Pt(8)
    original(18, None)
    added("glossary", "Glossary")
    heading1("Appendix")
    doc.add_paragraph("Deep-dive material kept for questions; in the talk these are backup slides.")
    original(15, "Appendix")
    original(16, "Appendix")
    added("s100_table", "Appendix")

    # ---- References / Sources ---------------------------------------------
    doc.add_heading("References and sources", level=1)
    doc.add_paragraph("Literature cited in the added sections (each DOI checked on Crossref, 2026-09-28):")
    for i, ref in enumerate(REFERENCES, 1):
        doc.add_paragraph(f"{i}. {ref}")
    doc.add_paragraph("Package sources for the added sections:")
    for v in SRC.values():
        p = doc.add_paragraph()
        md_inline(p, v)
    doc.add_paragraph("Per-slide sources, from docs/lung_tcell_talk_imrad_sources_20260925.md (commits are in "
                      "the geneformer-lung-tcell repository).")
    rows = sources_table_rows()
    t = doc.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    for j, h in enumerate(("Slide", "Section", "Claim", "Source")):
        t.cell(0, j).paragraphs[0].add_run(h).bold = True
    for r in rows:
        cells = t.add_row().cells
        for j, v in enumerate(r):
            md_inline(cells[j].paragraphs[0], v)
    doc.add_paragraph()
    doc.add_paragraph("Data files shipped with this report's build package (data/MANIFEST.tsv).")
    man = list(csv.DictReader(open(MANIFEST, newline=""), delimiter="\t"))
    t = doc.add_table(rows=1, cols=3)
    t.style = "Table Grid"
    for j, h in enumerate(("File", "Origin", "sha256 (first 16)")):
        t.cell(0, j).paragraphs[0].add_run(h).bold = True
    for m in man:
        cells = t.add_row().cells
        cells[0].paragraphs[0].add_run(m["file"]).font.name = "Courier New"
        cells[1].paragraphs[0].add_run(f"{m['origin_path']} ({m['origin_commit_or_location']})")
        cells[2].paragraphs[0].add_run(m["sha256"][:16]).font.name = "Courier New"
    for table, widths in ((doc.tables[-2], (12, 26, 52, 76)), (doc.tables[-1], (60, 82, 24))):
        table.autofit = False
        for col, w in zip(table.columns, widths):
            col.width = Mm(w)          # the grid (LibreOffice reads this)
        for row in table.rows:
            for cell, w in zip(row.cells, widths):
                cell.width = Mm(w)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p_ in cell.paragraphs:
                    for r in p_.runs:
                        r.font.size = Pt(8.5)

    cp = doc.core_properties
    cp.title = abstract.TITLE
    cp.author = "Kaisar Dauyey; Shinji Nakaoka"
    cp.subject = "IMRaD report of the lung T-cell oral presentation, 2026-09-25"
    cp.last_modified_by = ""
    cp.revision = 1
    cp.created = cp.modified = dt.datetime(2026, 9, 28, 9, 0, 0)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc.save(OUT)
    normalise_zip(OUT)

    words = sum(len(p.text.split()) for p in doc.paragraphs)
    table_words = sum(len(c.text.split()) for t in doc.tables for row in t.rows for c in row.cells)
    return {"figures": fig_n, "tables": len(doc.tables), "words_body": words, "words_in_tables": table_words}


if __name__ == "__main__":
    s = build()
    print(f"wrote {OUT}")
    print(s)
