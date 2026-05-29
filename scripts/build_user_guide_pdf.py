"""Render docs/USER_GUIDE.md to a branded PDF (docs/USER_GUIDE.pdf).

Lightweight Markdown→PDF using fpdf2 (already a backend dependency). Handles
headings, bullets, tables (as plain rows), and paragraphs — enough for the
user guide. Run from the repo root:

    python scripts/build_user_guide_pdf.py
"""

from __future__ import annotations

import pathlib
import re

from fpdf import FPDF

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "USER_GUIDE.md"
OUT = ROOT / "docs" / "USER_GUIDE.pdf"
PURPLE = (110, 86, 207)


def _safe(text: str) -> str:
    # strip markdown emphasis/inline code and coerce to latin-1 for core fonts
    text = re.sub(r"[*`_]", "", text)
    return text.encode("latin-1", "replace").decode("latin-1")


def build() -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_fill_color(*PURPLE)
    pdf.rect(0, 0, 210, 22, "F")
    pdf.set_xy(12, 6)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _safe("DClaw SEO — User Guide"), ln=1)
    pdf.ln(14)
    pdf.set_text_color(30, 30, 30)

    for raw in SRC.read_text().splitlines():
        line = raw.rstrip()
        pdf.set_x(pdf.l_margin)  # ensure full line width is available
        if not line or set(line) <= {"-", "|", " "}:
            if not line:
                pdf.ln(2)
            continue
        if line.startswith("# "):
            continue  # title already rendered in the banner
        if line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(*PURPLE)
            pdf.multi_cell(0, 7, _safe(line[3:]))
            pdf.set_text_color(30, 30, 30)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _safe(line[4:]))
        elif line.startswith(("- ", "* ")):
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, "  - " + _safe(line[2:]))
        elif line.startswith("|"):
            pdf.set_font("Helvetica", "", 9)
            cells = [c.strip() for c in line.strip("|").split("|")]
            pdf.multi_cell(0, 5, _safe("  " + " | ".join(cells)))
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, _safe(line))

    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
