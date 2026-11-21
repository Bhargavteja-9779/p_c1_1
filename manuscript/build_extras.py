"""Highlights (separate file, 3-5 bullets <= 85 characters incl. spaces) and title page for submission."""
import os
import re

from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))


def highlights_from_front():
    s = open(os.path.join(HERE, "sections", "01_front.md")).read()
    block = s.split("# Highlights", 1)[1].split("# Abstract", 1)[0]
    return [ln[2:].strip() for ln in block.splitlines() if ln.startswith("- ")]


def title_from_front():
    s = open(os.path.join(HERE, "sections", "01_front.md")).read()
    return re.search(r'title:\s*"(.*?)"', s).group(1)


def build(values=None):
    hl = highlights_from_front()
    if values:
        hl = [re.sub(r"\{\{(.*?)\}\}", lambda m: str(values[m.group(1)]), h) for h in hl]
    assert 3 <= len(hl) <= 5, "Elsevier: 3-5 highlights"
    for h in hl:
        assert len(h) <= 85, f"highlight too long ({len(h)} > 85): {h}"
    d = Document()
    d.styles["Normal"].font.name = "Times New Roman"
    d.styles["Normal"].font.size = Pt(12)
    d.add_paragraph().add_run("Highlights").bold = True
    for h in hl:
        d.add_paragraph(h, style="List Bullet")
    d.save(os.path.join(HERE, "highlights.docx"))
    t = Document()
    t.styles["Normal"].font.name = "Times New Roman"
    t.styles["Normal"].font.size = Pt(12)
    p = t.add_paragraph()
    r = p.add_run(title_from_front())
    r.bold = True
    r.font.size = Pt(14)
    t.add_paragraph("P N Bhargav Teja^a,*, [Second Author]^b")
    t.add_paragraph("^a [Department, Institution, City, Country]; ^b [Department, Institution, City, Country]")
    t.add_paragraph("* Corresponding author: P N Bhargav Teja, [postal address], e-mail: [corresponding author e-mail] "
                    "(the e-mail address will be published).")
    t.add_paragraph("Declarations: see the manuscript (competing interests, CRediT, funding, generative-AI use, data "
                    "and code availability).")
    t.save(os.path.join(HERE, "title_page.docx"))
    print("highlights:", [len(h) for h in hl])


if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, HERE)
    vals = json.load(open(os.path.join(os.path.dirname(HERE), "results", "manuscript_values.json")))
    build(vals)
