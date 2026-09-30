#!/usr/bin/env bash
# One command: ./build.sh          -> builds build/ (creates env/.venv on first run)
#              ./build.sh verify   -> also compares build/ with verify/originals page by page
#              ./build.sh office   -> also builds editable/ (.pptx + .docx) and checks them
#                                     (overflow + content) through LibreOffice if soffice is installed
#              ./build.sh publish  -> office, then copies slides/report/abstract (+ PDF exports) and
#                                     figures/ one level up, for the audience (needs LibreOffice)
# Set PYTHON=/path/to/python3 to use an existing interpreter instead of env/.venv.
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d data/git ] || [ ! -f data/git_facts.json ]; then
  # Public clone: the unpublished results in data/git/ and data/git_facts.json are not included
  # (see README.md, "What is not in this repository"), so nothing can be regenerated. Check instead
  # that every published file is intact, then stop.
  echo "data/git/ and data/git_facts.json are not in this repository (unpublished results); the talk"
  echo "cannot be rebuilt from a public clone. Checking the published files against SHA256SUMS instead:"
  ( cd .. && shasum -a 256 -c source/SHA256SUMS --quiet ) || { echo "SHA256SUMS: mismatch (see above)"; exit 1; }
  echo "all files in source/SHA256SUMS match"
  exit 0
fi
if [ -z "${PYTHON:-}" ]; then
  if [ ! -x env/.venv/bin/python ]; then
    python3 -m venv env/.venv
    env/.venv/bin/pip install -q --no-index --find-links env/wheels -r env/requirements.txt 2>/dev/null \
      || env/.venv/bin/pip install -q -r env/requirements.txt
  fi
  PYTHON=env/.venv/bin/python
fi
"$PYTHON" src/lung_tcell_talk_imrad_figures_20260925.py
"$PYTHON" src/make_lung_tcell_talk_imrad_20260925.py
"$PYTHON" src/make_lung_tcell_talk_imrad_abstract_20260925.py
( cd build && shasum -a 256 *.pdf *.md > BUILD_SHA256SUMS && cat BUILD_SHA256SUMS )
if [ "${1:-}" = "verify" ]; then "$PYTHON" src/verify_pages.py; fi
if [ "${1:-}" = "office" ] || [ "${1:-}" = "publish" ]; then
  "$PYTHON" src/make_readable_figures.py
  "$PYTHON" src/make_pptx.py
  "$PYTHON" src/make_docx.py
  if command -v soffice >/dev/null 2>&1; then
    "$PYTHON" src/check_office.py "$(mktemp -d)"
  else
    echo "soffice (LibreOffice) not found: editable/ built but NOT checked for overflow"
  fi
fi
if [ "${1:-}" = "publish" ]; then
  command -v soffice >/dev/null 2>&1 || { echo "publish needs LibreOffice (soffice) for the PDF exports"; exit 1; }
  "$PYTHON" src/publish.py
fi
