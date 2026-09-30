"""Check the editable Office files (./build.sh office runs this last).

Converts both files to PDF with LibreOffice (headless) into <out_dir>, then:
- overflow: every word LibreOffice renders on a slide must lie inside a text
  box of that slide (2 pt tolerance), i.e. no text spills out of its box;
- content: each slide's words (as a multiset, line breaks ignored) must equal
  the reference PDF's words for that page;
- report: the .docx must convert, and its page count is printed.
Usage: python3 src/check_office.py <out_dir>
"""
import os
import re
import subprocess
import sys

from pptx import Presentation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PPTX = os.path.join(ROOT, "editable", "lung_tcell_talk_imrad_20260925.pptx")
DOCX = os.path.join(ROOT, "editable", "lung_tcell_report_imrad_20260925.docx")
REF = os.path.join(ROOT, "build", "lung_tcell_talk_imrad_20260925.pdf")
EMU_PT = 12700


def convert(path, out):
    profile = "file://" + os.path.join(out, "lo_profile")
    subprocess.run(["soffice", "--headless", f"-env:UserInstallation={profile}", "--convert-to", "pdf",
                    "--outdir", out, path], check=True, capture_output=True)
    return os.path.join(out, os.path.splitext(os.path.basename(path))[0] + ".pdf")


def page_words(pdf, i):
    t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout
    # pdftotext drops the hyphen when a hyphenated word breaks across lines in one
    # renderer and not the other ("donor-level" vs "donorlevel"); compare without "-".
    return sorted(w.replace("-", "") for w in t.split())


def main(out):
    os.makedirs(out, exist_ok=True)
    pdf = convert(PPTX, out)
    prs = Presentation(PPTX)
    bbox = os.path.join(out, "pptx_bbox.html")
    subprocess.run(["pdftotext", "-bbox", pdf, bbox], check=True)
    pages = re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', open(bbox, encoding="utf-8").read(), re.S)
    outside = 0
    for n, ((pw, _ph, body), slide) in enumerate(zip(pages, prs.slides), 1):
        k = float(pw) / (prs.slide_width / EMU_PT)
        boxes = [(s.left / EMU_PT * k, s.top / EMU_PT * k, (s.left + s.width) / EMU_PT * k, (s.top + s.height) / EMU_PT * k)
                 for s in slide.shapes if (s.has_text_frame and s.text_frame.text.strip()) or s.has_table]
        for x0, y0, x1, y1, w in re.findall(
                r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', body):
            x0, y0, x1, y1 = map(float, (x0, y0, x1, y1))
            if not any(a - 2 <= x0 and x1 <= c + 2 and b - 2 <= y0 and y1 <= d + 2 for a, b, c, d in boxes):
                print(f"  slide {n}: word outside every text box: {w!r} at ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
                outside += 1
    # Original slides: words must equal the 25 Sep PDF page, apart from the page
    # number and the added "In plain words" line. Added slides: words must equal the
    # text in additions.py (so nothing was clipped away or duplicated).
    from additions import NEW, ORDER, PLAIN
    num = re.compile(r"^\d+$|^/$")
    differ = 0
    for pos, (kind, key) in enumerate(ORDER, 1):
        got = [w for w in page_words(pdf, pos) if not num.match(w)]
        if kind == "orig":
            want = [w for w in page_words(REF, key) if not num.match(w)]
            if key in PLAIN:
                want = sorted(want + [w.replace("-", "") for w in PLAIN[key].split()])
        else:
            spec = NEW[key]
            texts = [spec["eyebrow"].upper(), spec["title"]] + spec.get("intro", []) + spec.get("intro_after", [])
            for head, body in spec.get("cards", []):
                texts += [head] + body
            if spec.get("table"):
                texts += spec["table"]["header"] + [c for r in spec["table"]["rows"] for c in r]
            texts += [spec.get("plain", ""), spec.get("footer", "")]
            want = sorted(w.replace("-", "") for w in " ".join(texts).replace("**", "").split() if not num.match(w))
        want = [w for w in want if not num.match(w)]
        if sorted(got) != sorted(want):
            differ += 1
            sa, sb = set(want), set(got)
            print(f"  slide {pos} ({kind} {key}): expected-only {sorted(sa - sb)[:8]}; rendered-only {sorted(sb - sa)[:8]}")
    print(f"pptx: {len(prs.slides)} slides; words outside their text box: {outside}; "
          f"slides whose words differ from their source: {differ}")
    missing = verbatim_check()
    dpdf = convert(DOCX, out)
    info = subprocess.run(["pdfinfo", dpdf], capture_output=True, text=True, check=True).stdout
    print(f"docx: converted, {info.split('Pages:')[1].split()[0]} pages")
    return 1 if outside or differ or missing else 0


def verbatim_check():
    """Every slide paragraph (slides 2-18) and every abstract section must occur
    verbatim in the report's text (body paragraphs and table cells)."""
    import contextlib
    import io
    from docx import Document
    from capture_deck import capture, plain
    import make_lung_tcell_talk_imrad_abstract_20260925 as abstract
    with contextlib.redirect_stdout(io.StringIO()):
        deck = capture()
    d = Document(DOCX)
    text = "\n".join([p.text for p in d.paragraphs] +
                     [p.text for t in d.tables for r in t.rows for c in r.cells for p in c.paragraphs])
    wanted = [plain(p["runs"]) for s in deck["slides"][1:] for e in s if e["kind"] == "frame" for p in e["paras"]]
    wanted += [t for _, t in abstract.SECTIONS]
    missing = [w for w in wanted if w not in text]
    for w in missing:
        print(f"  report is missing verbatim: {w[:90]!r}")
    print(f"docx: {len(wanted) - len(missing)} of {len(wanted)} slide/abstract paragraphs present verbatim")
    return len(missing)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
