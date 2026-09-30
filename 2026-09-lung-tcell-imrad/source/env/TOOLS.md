# Environment

The original build ran on 2026-09-25 at 23:57 JST and was reproduced on 2026-09-28 and 2026-09-30,
on macOS 26 (Darwin 25.2, Apple Silicon).

| Tool | Version | Needed for |
|---|---|---|
| Python | 3.13.12 (Anaconda build) | build (any CPython 3.10+ should work; only 3.13 has been verified) |
| reportlab | 5.0.1 | build |
| pillow | 12.2.0 | build (PNG embedding, via reportlab) |
| charset-normalizer | 3.4.4 | build (reportlab dependency) |
| python-pptx | 1.0.2 | `./build.sh office` |
| python-docx | 1.2.0 | `./build.sh office` |
| lxml / XlsxWriter / typing_extensions | 6.1.1 / 3.2.9 / 4.15.0 | `./build.sh office` (python-pptx / python-docx dependencies) |
| matplotlib / numpy / pandas / scipy | 3.10.8 / 2.4.4 / 2.3.3 / 1.17.1 | `./build.sh office` (the two readable figure redraws, `src/make_readable_figures.py`) |
| poppler (`pdftoppm`, `pdftotext`, `pdffonts`) | 26.08.0 (Homebrew) | `./build.sh verify` |
| LibreOffice (`soffice`) | 26.2.5.2 | overflow and content checks in `./build.sh office` (skipped with a message if absent); PDF exports in `./build.sh publish` (required) |

`requirements.txt` pins every Python package: three for the 25 Sep PDF and nine more for `office`.
`wheels/` holds those wheels for macOS arm64 / CPython 3.13, so on that platform `./build.sh`
creates `.venv` offline. On any other platform pip downloads the same pinned versions from PyPI.

The 25 Sep PDF build does not need matplotlib. Its four audit figures are shipped as PNGs in
`data/assets/`, and their generator is kept for reference in `src/reference/` (see the README).
