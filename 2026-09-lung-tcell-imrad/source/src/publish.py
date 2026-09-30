"""Publish the audience-facing files one level up (./build.sh publish runs this last).

Copies the final deck, report and abstract out of source/ into the talk folder with plain names,
exports both Office files to PDF with LibreOffice (headless, fresh profile), and copies every
figure the deck uses into figures/ under a readable name. Nothing is retyped or redrawn here.

The two PDFs are LibreOffice exports of the final .pptx/.docx: the 26-slide deck exists only in the
Office emitters (src/make_pptx.py, src/make_docx.py), not in the 25 Sep ReportLab generator, which
still builds the original 18-slide outline (source/build/). LibreOffice embeds font subsets with
fresh random prefixes on every run, so the PDF bytes differ between exports; the pptx/docx they come
from are byte-reproducible, and SHA256SUMS pins the published PDF bytes.
Usage: python3 src/publish.py
"""
import os
import shutil
import subprocess
import tempfile

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # source/
TALK = os.path.dirname(SRC)                                          # the talk folder

FILES = {
    "slides.pptx": "editable/lung_tcell_talk_imrad_20260925.pptx",
    "report.docx": "editable/lung_tcell_report_imrad_20260925.docx",
    "abstract.md": "build/lung_tcell_talk_imrad_abstract_20260925.md",
}
PDFS = {"slides.pdf": "slides.pptx", "report.pdf": "report.docx"}
# figure (as used in the final deck) -> readable name; slide numbers are the final 26-slide deck
FIGURES = {
    "screen_b.png": "slide06_four-replicated-hits.png",
    "confusion.png": "slide08_classifier-confusion-matrix.png",
    "spatial.png": "slide12_spatial-tissue-validation.png",
    "detection.png": "slide13_sparse-genes-fake-big-effects.png",
    "fig_t6_reversal.png": "slide14_sclc-vs-luad-donor-level.png",
    "fig_concordance.png": "slide15_s100a8-s100a9-concordance.png",
    "fig_ambient_breakdown.png": "slide16_ambient-breakdown-top120.png",
    "fig_bf16_canary.png": "slide23_bf16-vs-fp32-precision.png",
    "network_c.png": "slide24_interaction-neighbourhood.png",
    "detection_rank.png": "slide26_immune-genes-ranked-by-deletion.png",
}


def main():
    for dst, src in FILES.items():
        shutil.copyfile(os.path.join(SRC, src), os.path.join(TALK, dst))
    with tempfile.TemporaryDirectory() as tmp:
        for dst, office in PDFS.items():
            subprocess.run(["soffice", "--headless", f"-env:UserInstallation=file://{tmp}/profile",
                            "--convert-to", "pdf", "--outdir", tmp, os.path.join(TALK, office)],
                           check=True, capture_output=True)
            shutil.copyfile(os.path.join(tmp, os.path.splitext(office)[0] + ".pdf"), os.path.join(TALK, dst))
    figdir = os.path.join(TALK, "figures")
    os.makedirs(figdir, exist_ok=True)
    for src, dst in FIGURES.items():
        shutil.copyfile(os.path.join(SRC, "data", "assets", src), os.path.join(figdir, dst))
    for name in list(FILES) + list(PDFS):
        print(f"wrote {os.path.join(TALK, name)}")
    print(f"wrote {len(FIGURES)} figures to {figdir}")


if __name__ == "__main__":
    main()
