"""Capture the IMRaD deck's content, exactly as the PDF generator lays it out,
for the editable Office versions (make_pptx.py, make_docx.py).

Nothing is retyped. This runs make_lung_tcell_talk_imrad_20260925.py itself
against a recording canvas: every background, card, text string, text frame
(with the paragraphs ReportLab actually placed in it) and image is recorded
per slide, in drawing order, with its position in points. The PDF generator
on disk is not modified; its output goes to memory, not build/.

In memory only, one line is tagged so the slide title can go into PowerPoint's
title placeholder: title() marks the frame it draws as the slide title.
"""
from __future__ import annotations

import html
import io
import os
import re
from html.parser import HTMLParser

import reportlab.pdfgen.canvas as rl_canvas
import reportlab.platypus as rl_platypus
from reportlab.platypus import Paragraph
from reportlab.platypus.flowables import Image as RLImage

SRC = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(SRC, "make_lung_tcell_talk_imrad_20260925.py")

_RealCanvas = rl_canvas.Canvas
_RealFrame = rl_platypus.Frame


def hexcol(c) -> str:
    return "#%02X%02X%02X" % tuple(round(v * 255) for v in (c.red, c.green, c.blue))


class RecordingCanvas(_RealCanvas):
    def __init__(self, filename, *a, **k):
        super().__init__(io.BytesIO(), *a, **k)
        self.meta = {}
        self.slides = [[]]
        self._fill = None
        self._stroke = None
        self._font = ("Helvetica", 12)
        self.next_is_title = False

    def _rec(self, kind, **d):
        self.slides[-1].append({"kind": kind, **d})

    def setTitle(self, t):
        self.meta["title"] = t
        super().setTitle(t)

    def setAuthor(self, a):
        self.meta["author"] = a
        super().setAuthor(a)

    def setSubject(self, s):
        self.meta["subject"] = s
        super().setSubject(s)

    def setFillColor(self, c, alpha=None):
        self._fill = hexcol(c)
        super().setFillColor(c, alpha)

    def setStrokeColor(self, c, alpha=None):
        self._stroke = hexcol(c)
        super().setStrokeColor(c, alpha)

    def setFont(self, name, size, leading=None):
        self._font = (name, size)
        super().setFont(name, size, leading)

    def rect(self, x, y, w, h, stroke=1, fill=0):
        self._rec("rect", x=x, y=y, w=w, h=h, fill=self._fill if fill else None,
                  stroke=self._stroke if stroke else None)
        super().rect(x, y, w, h, stroke, fill)

    def roundRect(self, x, y, w, h, radius, stroke=1, fill=0):
        self._rec("roundrect", x=x, y=y, w=w, h=h, r=radius, fill=self._fill if fill else None,
                  stroke=self._stroke if stroke else None)
        super().roundRect(x, y, w, h, radius, stroke, fill)

    def drawString(self, x, y, text, *a, **k):
        self._rec("string", x=x, y=y, text=text, font=self._font[0], size=self._font[1],
                  color=self._fill, align="left")
        super().drawString(x, y, text, *a, **k)

    def drawRightString(self, x, y, text, *a, **k):
        self._rec("string", x=x, y=y, text=text, font=self._font[0], size=self._font[1],
                  color=self._fill, align="right")
        super().drawRightString(x, y, text, *a, **k)

    def drawImage(self, image, x, y, width=None, height=None, *a, **k):
        path = image if isinstance(image, str) else getattr(image, "fileName", None)
        assert isinstance(path, str) and os.path.exists(path), f"image source not a file: {image!r}"
        # Flowables draw after canvas.translate(); map to page coordinates.
        ma, mb, mc, md, me, mf = self._currentMatrix
        assert mb == 0 and mc == 0, "rotated/skewed image not supported"
        self._rec("image", path=path, x=ma * x + me, y=md * y + mf, w=ma * width, h=md * height)
        return super().drawImage(image, x, y, width, height, *a, **k)

    def showPage(self):
        self.slides.append([])
        super().showPage()


class RecordingFrame(_RealFrame):
    def __init__(self, x1, y1, width, height, *a, **k):
        super().__init__(x1, y1, width, height, *a, **k)
        self.box = (x1, y1, width, height)

    def addFromList(self, drawlist, canv):
        wanted = list(drawlist)
        is_title = getattr(canv, "next_is_title", False)
        canv.next_is_title = False
        paras = [f for f in wanted if isinstance(f, Paragraph)]
        rec = {"kind": "frame", "x": self.box[0], "y": self.box[1], "w": self.box[2], "h": self.box[3],
               "title": is_title, "paras": []}
        if paras:
            canv._rec(**rec)
        super().addFromList(drawlist, canv)
        # Anything left in drawlist did not fit and is NOT in the PDF; mirror that.
        placed = [f for f in wanted if not any(f is g for g in drawlist)]
        if paras:
            canv.slides[-1][-1]["paras"] = [para_record(p) for p in placed if isinstance(p, Paragraph)]
            canv.slides[-1][-1]["dropped"] = sum(1 for f in drawlist if isinstance(f, Paragraph))


def para_record(p: Paragraph) -> dict:
    s = p.style
    return {"markup": p.text if hasattr(p, "text") else p._text if hasattr(p, "_text") else "",
            "font": s.fontName, "size": s.fontSize, "leading": s.leading,
            "color": hexcol(s.textColor), "space_after": s.spaceAfter,
            "runs": markup_runs(getattr(p, "text", ""), s.fontName, s.fontSize, hexcol(s.textColor))}


class _Runs(HTMLParser):
    def __init__(self, font, size, color):
        super().__init__(convert_charrefs=True)
        self.stack = [{"bold": font.endswith("Bold"), "italic": "Oblique" in font, "mono": font.startswith("Courier"),
                       "size": size, "color": color}]
        self.runs = []

    def handle_starttag(self, tag, attrs):
        top = dict(self.stack[-1])
        a = dict(attrs)
        if tag == "b":
            top["bold"] = True
        elif tag == "i":
            top["italic"] = True
        elif tag == "font":
            if "face" in a:
                top["mono"] = a["face"].startswith("Courier")
                top["bold"] = top["bold"] or a["face"].endswith("Bold")
            if "size" in a:
                top["size"] = float(a["size"])
            if "color" in a:
                top["color"] = a["color"].upper()
        self.stack.append(top)

    def handle_endtag(self, tag):
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_data(self, data):
        if data:
            self.runs.append({"text": data, **self.stack[-1]})


def markup_runs(markup: str, font: str, size: float, color: str) -> list[dict]:
    # ReportLab collapses whitespace like HTML; &nbsp; survives as U+00A0.
    text = re.sub(r"\s+", " ", markup.replace("&nbsp;", " ")).strip()
    parser = _Runs(font, size, color)
    parser.feed(text)
    parser.close()
    runs = [r for r in parser.runs if r["text"]]
    for r in runs:
        r["text"] = html.unescape(r["text"])
    return runs


def plain(runs: list[dict]) -> str:
    return "".join(r["text"] for r in runs)


def capture() -> dict:
    src = open(DECK, encoding="utf-8").read()
    anchor = "def title(c, txt, y, size=25, col=INK, width=None):\n    h = size * 2.6\n"
    assert src.count(anchor) == 1, "title() helper changed; update capture_deck.py"
    src = src.replace(anchor, anchor + "    c.next_is_title = True\n")
    rl_canvas.Canvas = RecordingCanvas
    rl_platypus.Frame = RecordingFrame
    try:
        ns = {"__file__": DECK, "__name__": "deck_capture"}
        exec(compile(src, DECK, "exec"), ns)
    finally:
        rl_canvas.Canvas = _RealCanvas
        rl_platypus.Frame = _RealFrame
    c = ns["c"]
    slides = [s for s in c.slides if s]
    return {"meta": c.meta, "width": ns["W"], "height": ns["H"], "slides": slides,
            "page_count": ns["PAGES"]}


if __name__ == "__main__":
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        d = capture()
    print(f"{len(d['slides'])} slides captured")
    for i, s in enumerate(d["slides"], 1):
        kinds = {}
        for e in s:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        dropped = sum(e.get("dropped", 0) for e in s if e["kind"] == "frame")
        t = next((plain(p["runs"]) for e in s if e["kind"] == "frame" and e["title"] for p in e["paras"]), "")
        print(f"{i:2d} {kinds} dropped={dropped} | {t[:70]}")


def normalise_zip(path: str, when=(2026, 9, 25, 23, 57, 44)) -> None:
    """Office files are zip containers stamped with the build time; rewrite every
    entry with one fixed timestamp so a rebuild is byte-identical."""
    import zipfile
    with zipfile.ZipFile(path) as z:
        entries = [(i, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(path, "w") as z:
        for info, data in entries:
            fixed = zipfile.ZipInfo(info.filename, date_time=when)
            fixed.compress_type = zipfile.ZIP_DEFLATED
            fixed.external_attr = info.external_attr
            z.writestr(fixed, data)
