"""Editable PowerPoint version of the IMRaD deck (18 slides, 16:9).

Content comes from capture_deck.py, which runs the PDF generator itself, so
every word and number is the one in the PDF. Nothing is retyped here.

Editable by design:
- Every title, paragraph, eyebrow and footer is a native text box; slide
  titles sit in the layout's title placeholder (outline view, accessibility).
- Figures are placed pictures from data/assets/; cards are native rounded
  rectangles. There is no full-slide picture anywhere.
- Colours and fonts live in the slide master's theme: the deck palette is the
  theme colour scheme and the body/heading font is the theme font. Change them
  once in Design > Variants (or View > Slide Master) and every slide follows.
  Colours outside the 10-slot theme palette stay as fixed RGB (listed in
  README).
- Speaker notes carry the source/commit each slide cites: the slide's footer
  citation plus its row in docs/lung_tcell_talk_imrad_sources_20260925.md.
"""
from __future__ import annotations

import contextlib
import io
import os
import re

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

from capture_deck import capture, normalise_zip, plain

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "editable", "lung_tcell_talk_imrad_20260925.pptx")
SOURCES_NOTE = os.path.join(ROOT, "docs", "lung_tcell_talk_imrad_sources_20260925.md")

# Deck palette (make_lung_tcell_talk_imrad_20260925.py) -> theme colour slots.
THEME = [  # (slot xml name, hex, MSO_THEME_COLOR)
    ("dk1", "12211E", MSO_THEME_COLOR.TEXT_1),         # INK / DARK
    ("lt1", "FFFFFF", MSO_THEME_COLOR.BACKGROUND_1),   # WHITE
    ("dk2", "31423D", MSO_THEME_COLOR.TEXT_2),         # body text grey-green
    ("lt2", "F6F8F6", MSO_THEME_COLOR.BACKGROUND_2),   # PAPER
    ("accent1", "0E6E5C", MSO_THEME_COLOR.ACCENT_1),   # ACC
    ("accent2", "B4552F", MSO_THEME_COLOR.ACCENT_2),   # WARM
    ("accent3", "E08A5F", MSO_THEME_COLOR.ACCENT_3),   # WARMT
    ("accent4", "5C6B66", MSO_THEME_COLOR.ACCENT_4),   # MUT
    ("accent5", "EAF0ED", MSO_THEME_COLOR.ACCENT_5),   # BAND
    ("accent6", "F7F2EE", MSO_THEME_COLOR.ACCENT_6),   # CREAM
]
THEME_BY_HEX = {"#" + h: t for _, h, t in THEME}
THEME_FONT = "Arial"      # Helvetica's metric-compatible stand-in, present in Office everywhere
MONO_FONT = "Courier New"
UNTHEMED: set[str] = set()


def set_theme(prs: Presentation) -> None:
    theme_part = prs.slide_masters[0].part.part_related_by(RT.THEME)
    root = etree.fromstring(theme_part.blob)
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    scheme = root.find(".//a:clrScheme", ns)
    scheme.set("name", "Lung T-cell IMRaD")
    for slot, hexv, _ in THEME:
        el = scheme.find(f"a:{slot}", ns)
        for child in list(el):
            el.remove(child)
        etree.SubElement(el, f"{{{ns['a']}}}srgbClr", val=hexv)
    fonts = root.find(".//a:fontScheme", ns)
    fonts.set("name", "Lung T-cell IMRaD")
    for tag in ("majorFont", "minorFont"):
        fonts.find(f"a:{tag}/a:latin", ns).set("typeface", THEME_FONT)
    theme_part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def paint(color_format, hexv: str) -> None:
    hexv = hexv.upper()
    if hexv in THEME_BY_HEX:
        color_format.theme_color = THEME_BY_HEX[hexv]
    else:
        UNTHEMED.add(hexv)
        color_format.rgb = RGBColor.from_string(hexv[1:])


def sources_rows() -> dict[int, str]:
    rows = {}
    for line in open(SOURCES_NOTE, encoding="utf-8"):
        m = re.match(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| (.+) \|\s*$", line)
        if m and "Slide" not in line and int(m.group(1)) <= 18 and line.count("|") == 5:
            rows[int(m.group(1))] = f"{m.group(2).strip()}: {m.group(3).strip()}. Source: {m.group(4).strip()}"
    return rows


class Geo:
    def __init__(self, prs, w_pt, h_pt):
        self.sx = prs.slide_width / w_pt
        self.sy = prs.slide_height / h_pt
        self.h = h_pt

    def box(self, x, y_bottom, w, h):
        """ReportLab box (origin bottom-left, points) -> EMU left, top, width, height."""
        return (Emu(round(x * self.sx)), Emu(round((self.h - y_bottom - h) * self.sy)),
                Emu(round(w * self.sx)), Emu(round(h * self.sy)))


def fill_runs(paragraph, runs):
    for r in runs:
        run = paragraph.add_run()
        run.text = r["text"]
        f = run.font
        f.size = Pt(r["size"])
        f.bold = r["bold"]
        f.italic = r["italic"]
        if r["mono"]:
            f.name = MONO_FONT
        paint(f.color, r["color"])


def text_frame_setup(tf):
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0


def write_paras(tf, paras):
    first = True
    for p in paras:
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.alignment = PP_ALIGN.LEFT
        para.line_spacing = Pt(p["leading"])
        para.space_after = Pt(p["space_after"])
        para.space_before = Pt(0)
        fill_runs(para, p["runs"])


M_PT = 20 * 72 / 25.4
# 2026-09-28: readable redraws (src/make_readable_figures.py) replace these two
# originals in the Office files; the 25 Sep PDF keeps the *_orig.png files.
READABLE = {
    "detection_orig.png": os.path.join(ROOT, "data", "assets", "detection.png"),
    "fig_t6_reversal_orig.png": os.path.join(ROOT, "data", "assets", "fig_t6_reversal.png"),
}
MM_PT = 72 / 25.4


def flat(shp):
    shp.shadow.inherit = False
    style = shp._element.find(qn("p:style"))
    if style is not None:
        style.find(qn("a:effectRef")).set("idx", "0")


def md_runs(text, size, color, bold=False, italic=False):
    """**bold** markup -> run dicts (the added material's only markup)."""
    runs = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part:
            runs.append({"text": part, "size": size, "bold": bold or i % 2 == 1, "italic": italic,
                         "mono": False, "color": color})
    return runs


def textbox(slide, g, x, y, w, h, paras, stats, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(*g.box(x, y, w, h))
    text_frame_setup(tb.text_frame)
    first = True
    for runs, leading, after in paras:
        para = tb.text_frame.paragraphs[0] if first else tb.text_frame.add_paragraph()
        first = False
        para.alignment = align
        para.line_spacing = Pt(leading)
        para.space_after = Pt(after)
        para.space_before = Pt(0)
        fill_runs(para, runs)
    stats["text_boxes"] += 1
    return tb


def page_footer(slide, g, deck, pos, total, right, stats, dark=False):
    col = "#9A877C" if dark else "#7A8A85"
    y = 11 * MM_PT
    for text, x, w, align, mono in (("%d / %d" % (pos, total), M_PT, 60 * MM_PT, PP_ALIGN.LEFT, True),
                                    (right, M_PT, deck["width"] - 2 * M_PT, PP_ALIGN.RIGHT, False)):
        if not text:
            continue
        tb = textbox(slide, g, x, y + 8.5 * 0.905 - 8.5 * 1.25, w, 8.5 * 1.25,
                     [([{"text": text, "size": 8.5, "bold": False, "italic": False, "mono": mono, "color": col}],
                       8.5 * 1.25, 0)], stats, align)
        tb.text_frame.word_wrap = False


def plain_line(slide, g, deck, text, stats, dark=False, top_mm=27.0):
    """The added 'In plain words' line: a band between the content and the footer,
    from 15 mm up to `top_mm` (just under the lowest picture or card)."""
    col = "#E08A5F" if dark else "#0E6E5C"
    textbox(slide, g, M_PT, 15 * MM_PT, deck["width"] - 2 * M_PT, (top_mm - 15) * MM_PT,
            [(md_runs(text, 9.5, col, italic=True), 12.5, 0)], stats)


def card_shape(slide, g, x, y, w, h, fill="#FFFFFF", stroke="#DCE3DF"):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *g.box(x, y, w, h))
    shp.adjustments[0] = min(0.5, 4 * MM_PT / min(w, h))
    shp.fill.solid()
    paint(shp.fill.fore_color, fill)
    paint(shp.line.color, stroke)
    shp.line.width = Pt(0.6)
    flat(shp)
    return shp


def native_table(slide, g, x, y_top, widths_mm, header, rows, size=9.5, row_h_mm=8.0):
    """Native table; each row is as tall as its longest wrapped cell (Arial
    averages ~0.5 em per character), never shorter than row_h_mm."""
    def lines(text, w_mm):
        usable = (w_mm - 4) * MM_PT
        return max(1, -(-len(text.replace("**", "")) * 0.5 * size // usable))
    heights = []
    for r in [header] + rows:
        n = max(lines(t, w) for t, w in zip(r, widths_mm))
        heights.append(max(row_h_mm, 2.5 + n * size * 1.2 / MM_PT))
    h = sum(heights) * MM_PT
    n_rows = len(rows) + 1
    frame = slide.shapes.add_table(n_rows, len(header), *g.box(x, y_top - h, sum(widths_mm) * MM_PT, h))
    tbl = frame.table
    for j, w in enumerate(widths_mm):
        tbl.columns[j].width = Emu(round(w * MM_PT * g.sx))
    for i in range(n_rows):
        tbl.rows[i].height = Emu(round(heights[i] * MM_PT * g.sy))
        for j in range(len(header)):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Emu(round(2 * MM_PT * g.sx))
            cell.margin_top = cell.margin_bottom = Emu(round(1 * MM_PT * g.sy))
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            text = header[j] if i == 0 else rows[i - 1][j]
            tf = cell.text_frame
            tf.word_wrap = True
            para = tf.paragraphs[0]
            fill_runs(para, md_runs(text, size, "#FFFFFF" if i == 0 else "#12211E", bold=(i == 0)))
            cell.fill.solid()
            paint(cell.fill.fore_color, "#0E6E5C" if i == 0 else ("#FFFFFF" if i % 2 else "#EAF0ED"))
    return frame, h


def render_new(slide, g, deck, spec, pos, total, stats):
    W, H = deck["width"], deck["height"]
    slide.background.fill.solid()
    paint(slide.background.fill.fore_color, "#F6F8F6")
    # eyebrow
    tb = textbox(slide, g, M_PT, H - 24 * MM_PT + 9 * 0.905 - 9 * 1.25, W - 2 * M_PT, 9 * 1.25,
                 [([{"text": spec["eyebrow"].upper(), "size": 9, "bold": True, "italic": False, "mono": True,
                     "color": "#0E6E5C"}], 9 * 1.25, 0)], stats)
    tb.text_frame.word_wrap = False
    # title, in the layout's title placeholder
    tp = slide.shapes.title
    th = 21 * 2.6
    tp.left, tp.top, tp.width, tp.height = g.box(M_PT, H - 42 * MM_PT - th, 290 * MM_PT, th)
    text_frame_setup(tp.text_frame)
    tp.text_frame.clear()
    fill_runs(tp.text_frame.paragraphs[0], md_runs(spec["title"], 21, "#12211E", bold=True))
    tp.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    tp.text_frame.paragraphs[0].line_spacing = Pt(21 * 1.16)
    stats["text_boxes"] += 1
    top = 124 * MM_PT                       # content area: 124 mm down to 30 mm
    if spec.get("intro"):
        paras = [(md_runs(t, 11, "#31423D"), 15, 4) for t in spec["intro"]]
        h = sum(15 * (1 + len(t) // 150) + 4 for t in spec["intro"])
        textbox(slide, g, M_PT, top - h, W - 2 * M_PT, h, paras, stats)
        top -= h + 4 * MM_PT
    if spec.get("cards"):
        n = len(spec["cards"])
        gap = 6 * MM_PT
        cw = (W - 2 * M_PT - gap * (n - 1)) / n
        y0, ch = 30 * MM_PT, top - 30 * MM_PT
        for i, (head, texts) in enumerate(spec["cards"]):
            x = M_PT + i * (cw + gap)
            card_shape(slide, g, x, y0, cw, ch)
            stats["shapes"] += 1
            paras = [(md_runs(head, 14, "#12211E", bold=True), 18, 6)]
            paras += [(md_runs(t, 11.5, "#31423D"), 15.5, 6) for t in texts]
            textbox(slide, g, x + 6 * MM_PT, y0 + 4 * MM_PT, cw - 12 * MM_PT, ch - 9 * MM_PT, paras, stats)
    if spec.get("table"):
        t = spec["table"]
        row_h = 7.0 if len(t["rows"]) > 10 else 9.0
        _, th_ = native_table(slide, g, M_PT, top, t["widths_mm"], t["header"], t["rows"],
                              size=8.8 if len(t["rows"]) > 10 else 9.5, row_h_mm=row_h)
        stats["tables"] = stats.get("tables", 0) + 1
        top -= th_ + 5 * MM_PT
    if spec.get("image"):
        from PIL import Image as _I
        iw, ih = _I.open(spec["image"]).size
        avail_w, avail_h = W - 2 * M_PT, top - 28 * MM_PT
        s_ = min(avail_w / iw, avail_h / ih)
        slide.shapes.add_picture(spec["image"], *g.box(M_PT, top - ih * s_, iw * s_, ih * s_))
        stats["pictures"] += 1
    if spec.get("intro_after"):
        h = 30
        textbox(slide, g, M_PT, top - h, W - 2 * M_PT, h, [(md_runs(t, 10, "#31423D"), 13.5, 3)
                                                              for t in spec["intro_after"]], stats)
    if spec.get("plain"):
        plain_line(slide, g, deck, spec["plain"], stats)
    page_footer(slide, g, deck, pos, total, spec.get("footer"), stats)


def build() -> dict:
    from additions import APPENDIX_START, NEW, ORDER, PLAIN, QUESTIONS_MIN, SLOT_MIN, TIMING, mmss
    with contextlib.redirect_stdout(io.StringIO()):
        deck = capture()
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)   # 13.333 x 7.5 in, 16:9
    set_theme(prs)
    layout = next(l for l in prs.slide_layouts if l.name == "Title Only")
    g = Geo(prs, deck["width"], deck["height"])
    notes_rows = sources_rows()
    stats = {"slides": 0, "text_boxes": 0, "pictures": 0, "shapes": 0, "tables": 0}
    total = len(ORDER)

    for pos, (kind, key) in enumerate(ORDER, 1):
        slide = prs.slides.add_slide(layout)
        where = "appendix" if pos >= APPENDIX_START else "main talk"
        talk_s = sum(TIMING.values())
        if pos in TIMING:
            timing = (f"[{mmss(TIMING[pos])}] Timing budget for this slide; cumulative "
                      f"{mmss(sum(v for k, v in TIMING.items() if k <= pos))} of {mmss(talk_s)} speaking "
                      f"({SLOT_MIN}-min slot = ~{SLOT_MIN - QUESTIONS_MIN} min talk + ~{QUESTIONS_MIN} min questions).")
        else:
            timing = "[--] Appendix: not in the timed talk; show only if asked."
        if kind == "new":
            spec = NEW[key]
            render_new(slide, g, deck, spec, pos, total, stats)
            notes = [timing, f"Slide {pos} of {total} ({where}). ADDED 2026-09-28 (not in the 25 Sep deck)."] + spec["notes"]
            slide.notes_slide.notes_text_frame.text = "\n".join(notes)
            stats["slides"] += 1
            continue
        n = key
        elements = deck["slides"][n - 1]
        renumber = lambda t: f"{pos} / {total}" if re.fullmatch(r"\d+ / \d+", t) else t
        footer_texts = []
        title_ph = slide.shapes.title
        title_used = False
        footer_texts = []
        for e in elements:
            k = e["kind"]
            if k == "rect" and e["w"] >= deck["width"] - 1 and e["h"] >= deck["height"] - 1:
                slide.background.fill.solid()
                paint(slide.background.fill.fore_color, e["fill"])
            elif k in ("rect", "roundrect"):
                shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if k == "roundrect" else MSO_SHAPE.RECTANGLE,
                                             *g.box(e["x"], e["y"], e["w"], e["h"]))
                if k == "roundrect":
                    shp.adjustments[0] = min(0.5, e["r"] / min(e["w"], e["h"]))
                if e["fill"]:
                    shp.fill.solid()
                    paint(shp.fill.fore_color, e["fill"])
                else:
                    shp.fill.background()
                if e["stroke"]:
                    paint(shp.line.color, e["stroke"])
                    shp.line.width = Pt(0.6)
                else:
                    shp.line.fill.background()
                shp.shadow.inherit = False
                # The default shape style references the theme's effect (a drop shadow in
                # LibreOffice); point it at "no effect" so cards stay flat as in the PDF.
                style = shp._element.find(qn("p:style"))
                if style is not None:
                    style.find(qn("a:effectRef")).set("idx", "0")
                shp.text_frame.text = ""
                stats["shapes"] += 1
            elif k == "image":
                path = READABLE.get(os.path.basename(e["path"]), e["path"])
                x, y, w, h = e["x"], e["y"], e["w"], e["h"]
                if path != e["path"]:
                    # redrawn figure: fit it inside the original slot, keeping its own aspect
                    from PIL import Image as _I
                    iw, ih = _I.open(path).size
                    s_ = min(w / iw, h / ih)
                    y += h - ih * s_          # top-aligned, like the Frame placed the original
                    w, h = iw * s_, ih * s_
                slide.shapes.add_picture(path, *g.box(x, y, w, h))
                stats["pictures"] += 1
            elif k == "string":
                size = e["size"]
                top_y = e["y"] + size * 0.905          # baseline -> top of line box (Helvetica ascent)
                h = size * 1.25
                if e["align"] == "right":
                    x0, w = 20 * 72 / 25.4, e["x"] - 20 * 72 / 25.4
                else:
                    x0, w = e["x"], deck["width"] - e["x"] - 20 * 72 / 25.4
                tb = slide.shapes.add_textbox(*g.box(x0, top_y - h, w, h))
                tf = tb.text_frame
                text_frame_setup(tf)
                tf.word_wrap = False
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.RIGHT if e["align"] == "right" else PP_ALIGN.LEFT
                fill_runs(p, [{"text": renumber(e["text"]), "size": size, "bold": e["font"].endswith("Bold"),
                               "italic": False, "mono": e["font"].startswith("Courier"), "color": e["color"]}])
                if e["y"] < 12 * 72 / 25.4 and not re.fullmatch(r"\d+ / \d+", e["text"]):
                    footer_texts.append(e["text"])
                stats["text_boxes"] += 1
            elif k == "frame":
                paras = e["paras"]
                if not paras:
                    continue
                # Slide 1 draws its title straight into a frame; its leading bold >= 20 pt
                # paragraphs are the title there.
                lead = []
                if e["title"]:
                    lead = paras
                elif n == 1 and not title_used:
                    while len(lead) < len(paras) and paras[len(lead)]["font"].endswith("Bold") \
                            and paras[len(lead)]["size"] >= 20:
                        lead.append(paras[len(lead)])
                rest = paras[len(lead):]
                top = e["y"] + e["h"]
                if lead and not title_used:
                    # A title() frame keeps its full height (room for a second line);
                    # slide 1's title is only the leading part of a larger frame.
                    lead_h = e["h"] if e["title"] else sum(p["leading"] + p["space_after"] for p in lead)
                    title_ph.left, title_ph.top, title_ph.width, title_ph.height = g.box(e["x"], top - lead_h, e["w"], lead_h)
                    tf = title_ph.text_frame
                    text_frame_setup(tf)
                    tf.clear()
                    write_paras(tf, lead)
                    for para in tf.paragraphs:
                        para.alignment = PP_ALIGN.LEFT
                    title_used = True
                    top -= lead_h
                    stats["text_boxes"] += 1
                if rest:
                    tb = slide.shapes.add_textbox(*g.box(e["x"], e["y"], e["w"], top - e["y"]))
                    text_frame_setup(tb.text_frame)
                    write_paras(tb.text_frame, rest)
                    stats["text_boxes"] += 1
        if not title_used:
            title_ph._element.getparent().remove(title_ph._element)
        dark = any(e["kind"] == "rect" and e["fill"] in ("#12211E",) for e in elements)
        if n in PLAIN:
            lowest = min([e["y"] for e in elements if e["kind"] in ("image", "roundrect") and e["y"] > 14 * MM_PT]
                         + [27 * MM_PT])
            plain_line(slide, g, deck, PLAIN[n], stats, dark=dark, top_mm=min(27.0, lowest / MM_PT - 1.0))
        notes = [timing, f"Slide {pos} of {total} ({where}); slide {n} of the 25 Sep deck, content unchanged"
                 + (" apart from the added 'In plain words' line." if n in PLAIN else ".")]
        if footer_texts:
            notes.append("Cited on the slide: " + " | ".join(footer_texts))
        if n in notes_rows:
            notes.append("Sources note (docs/lung_tcell_talk_imrad_sources_20260925.md, row for original slide "
                         f"{n}): " + notes_rows[n])
        notes.append("Commits cited are in geneformer-lung-tcell; the files themselves are in this package under "
                     "data/git/<commit>/ (see data/MANIFEST.tsv).")
        slide.notes_slide.notes_text_frame.text = "\n".join(notes)
        stats["slides"] += 1

    cp = prs.core_properties
    cp.title = deck["meta"]["title"]
    cp.author = deck["meta"]["author"]
    cp.subject = deck["meta"]["subject"] + "; editable version with 2026-09-28 additions"
    cp.last_modified_by = ""
    cp.revision = 1
    import datetime as _dt
    cp.created = cp.modified = _dt.datetime(2026, 9, 28, 9, 0, 0)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prs.save(OUT)
    normalise_zip(OUT)
    stats["unthemed_colours"] = sorted(UNTHEMED)
    return stats


if __name__ == "__main__":
    s = build()
    print(f"wrote {OUT}")
    print(s)
