"""Compare build/ with verify/ originals: every page rendered to PNG at 60 dpi
(poppler pdftoppm) and diffed pixel by pixel, plus the extracted text of every
page (pdftotext, which catches a changed digit too small to show at 60 dpi);
the abstract byte by byte."""
import filecmp, glob, os, subprocess, sys, tempfile
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW = os.path.join(ROOT, "build", "lung_tcell_talk_imrad_20260925.pdf")
OLD = os.path.join(ROOT, "verify", "original_lung_tcell_talk_imrad_20260925.pdf")
tmp = tempfile.mkdtemp()
for tag, pdf in (("old", OLD), ("new", NEW)):
    subprocess.run(["pdftoppm", "-r", "60", "-png", pdf, os.path.join(tmp, tag)], check=True)
old, new = sorted(glob.glob(f"{tmp}/old-*.png")), sorted(glob.glob(f"{tmp}/new-*.png"))
print(f"pages: original {len(old)}, rebuilt {len(new)}")
bad = []
for i, (a, b) in enumerate(zip(old, new), 1):
    A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    box = ImageChops.difference(A, B).getbbox() if A.size == B.size else "size"
    print(f"page {i:2d}: {'identical' if box is None else f'DIFFERS {box}'}")
    if box is not None:
        bad.append(i)
def page_text(pdf, n):
    return subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), pdf, "-"],
                          capture_output=True, text=True, check=True).stdout


for i in range(1, len(old) + 1):
    if page_text(OLD, i) != page_text(NEW, i):
        print(f"page {i:2d}: TEXT DIFFERS")
        bad.append(i)
print(f"text: {len(old) - len(set(bad))} of {len(old)} pages identical")
same_abs = filecmp.cmp(os.path.join(ROOT, "build", "lung_tcell_talk_imrad_abstract_20260925.md"),
                       os.path.join(ROOT, "verify", "original_lung_tcell_talk_imrad_abstract_20260925.md"), shallow=False)
print(f"abstract: {'byte-identical' if same_abs else 'DIFFERS'}")
sys.exit(1 if bad or len(old) != len(new) or not same_abs else 0)
