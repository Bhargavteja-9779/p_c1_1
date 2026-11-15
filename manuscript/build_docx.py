"""Build the submission manuscript (DOCX + PDF) from section sources, generated tables/figures and
machine-written result files. No number in the manuscript is typed by hand: every {{token}} is
filled by manuscript/values.py from results/*.

    python manuscript/build_docx.py [--mode full|quick]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from references import REFS  # noqa: E402
import values as V  # noqa: E402


def include_tables(text):
    """<<TABLE:MS_name|tbl:label>> -> caption line + generated markdown table (tables/MS_name.*)."""
    def rep(m):
        name, lab = m.group(1), m.group(2)
        md = open(os.path.join(ROOT, "tables", name + ".md")).read().strip()
        cap = open(os.path.join(ROOT, "tables", name + ".caption.txt")).read().strip()
        return f"Table: {cap} {{#{lab}}}\n\n{md}\n"
    return re.sub(r"<<TABLE:([\w\-.]+)\|(tbl:[\w-]+)>>", rep, text)


def number_labels(text):
    """Assign numbers to {#eq:..}, {#fig:..}, {#tbl:..}, {#sec:..} in order of appearance."""
    nums = {}
    cnt = {"eq": 0, "fig": 0, "tbl": 0}
    sec = [0, 0, 0]
    out_lines = []
    for line in text.split("\n"):
        m = re.match(r"^(#{1,3}) (.*?)(\s*\{#(sec:[\w-]+)\})?\s*$", line)
        if m and not line.startswith("####"):
            lvl = len(m.group(1))
            title = m.group(2)
            if title.lower().startswith(("abstract", "highlights", "references", "acknowledg", "declaration",
                                         "data and code", "credit", "nomenclature", "appendix", "supplementary",
                                         "keywords", "graphical")) or lvl == 1 and title.startswith("TITLE"):
                out_lines.append(f"{m.group(1)} {title}")
                continue
            sec[lvl - 1] += 1
            for k in range(lvl, 3):
                sec[k] = 0
            n = ".".join(str(x) for x in sec[:lvl])
            if m.group(4):
                nums[m.group(4)] = n
            out_lines.append(f"{m.group(1)} {n}{'.' if lvl == 1 else ''} {title}")
            continue
        out_lines.append(line)
    text = "\n".join(out_lines)
    for kind in ["eq", "fig", "tbl"]:
        for m in re.finditer(r"\{#(" + kind + r":[\w-]+)\}", text):
            cnt[kind] += 1
            nums[m.group(1)] = str(cnt[kind])
    # equations: $$ ... $$ {#eq:x} -> number inside the display math
    def eqrep(m):
        body, lab = m.group(1), m.group(2)
        return f"$$\n{body.strip()}\\qquad\\qquad ({nums[lab]})\n$$"
    text = re.sub(r"\$\$\s*\n(.*?)\n\$\$\s*\{#(eq:[\w-]+)\}", eqrep, text, flags=re.S)
    # figure captions
    def figrep(m):
        cap, path, lab = m.group(1), m.group(2), m.group(3)
        return f"![**Fig. {nums[lab]}.** {cap}]({path}){{width=16.5cm}}"
    text = re.sub(r"!\[(.*?)\]\((.*?)\)\{#(fig:[\w-]+)\}", figrep, text, flags=re.S)
    # table captions: line ": caption {#tbl:x}" before a table
    text = re.sub(r"^Table: (.*?) \{#(tbl:[\w-]+)\}", lambda m: f"**Table {nums[m.group(2)]}.** {m.group(1)}",
                  text, flags=re.M)
    # references to labels
    def refrep(m):
        lab = m.group(1)
        if lab not in nums:
            raise KeyError("unknown label " + lab)
        return nums[lab]
    text = re.sub(r"\[-@((?:eq|fig|tbl|sec):[\w-]+)\]", refrep, text)
    return text


def cite(text):
    order = []
    def rep(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        ns = []
        for k in keys:
            if k not in REFS:
                raise KeyError("missing reference " + k)
            if k not in order:
                order.append(k)
            ns.append(order.index(k) + 1)
        ns = sorted(ns)
        # compress ranges
        parts, i = [], 0
        while i < len(ns):
            j = i
            while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
                j += 1
            parts.append(f"{ns[i]}–{ns[j]}" if j - i >= 2 else ",".join(str(x) for x in ns[i:j + 1]))
            i = j + 1
        return "[" + ",".join(parts) + "]"
    text = re.sub(r"\[(@[\w\-]+(?:;\s*@[\w\-]+)*)\]", rep, text)
    refs = "\n".join(f"{i + 1}. {REFS[k]}" for i, k in enumerate(order))
    return text, refs, order


def fill_tokens(text, vals):
    def rep(m):
        k = m.group(1).strip()
        if k not in vals:
            raise KeyError("unfilled token " + k)
        return str(vals[k])
    return re.sub(r"\{\{(.*?)\}\}", rep, text)


def make_reference_docx(path):
    """Reference styles: Times New Roman 12 pt, double spacing (Elsevier initial-submission friendly)."""
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_LINE_SPACING
    subprocess.run(["pandoc", "-o", path, "--print-default-data-file", "reference.docx"], check=True,
                   stdout=open(path, "wb"))
    d = Document(path)
    for st in d.styles:
        try:
            f = st.font
        except Exception:
            continue
        if f is not None:
            f.name = "Times New Roman"
            f.color.rgb = None
    for name in ["Normal", "Body Text", "First Paragraph", "Compact", "Bibliography", "Block Text"]:
        if name in [s.name for s in d.styles]:
            s = d.styles[name]
            s.font.size = Pt(12)
            s.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            s.paragraph_format.space_after = Pt(0)
    for name, size in [("Heading 1", 13), ("Heading 2", 12), ("Heading 3", 12), ("Title", 16)]:
        if name in [s.name for s in d.styles]:
            s = d.styles[name]
            s.font.size = Pt(size)
            s.font.bold = True
            s.font.italic = name == "Heading 3"
            s.paragraph_format.space_before = Pt(12)
            s.paragraph_format.space_after = Pt(6)
    for name in ["Caption", "Image Caption", "Table Caption"]:
        if name in [s.name for s in d.styles]:
            d.styles[name].font.size = Pt(10)
            d.styles[name].font.italic = False
    for sec in d.sections:
        sec.left_margin = sec.right_margin = Cm(2.5)
        sec.top_margin = sec.bottom_margin = Cm(2.5)
    d.save(path)


def postprocess(path):
    """Line numbers (continuous), page numbers in footer, table font size."""
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt
    d = Document(path)
    for sec in d.sections:
        sp = sec._sectPr
        ln = OxmlElement("w:lnNumType")
        ln.set(qn("w:countBy"), "1")
        ln.set(qn("w:restart"), "continuous")
        ln.set(qn("w:distance"), "283")
        sp.append(ln)
        p = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
        p.alignment = 1
        r = p.add_run()
        for t, txt in [("begin", None), (None, "PAGE"), ("end", None)]:
            if t:
                fc = OxmlElement("w:fldChar")
                fc.set(qn("w:fldCharType"), t)
                r._r.append(fc)
            else:
                it = OxmlElement("w:instrText")
                it.text = txt
                r._r.append(it)
    for tb in d.tables:
        tb.style = d.styles["Table"] if "Table" in [s.name for s in d.styles] else tb.style
        for row in tb.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.paragraph_format.line_spacing = 1.0
                    for run in para.runs:
                        run.font.size = Pt(8)
    d.save(path)


def build(mode="full", out_name="Final_Manuscript"):
    vals = V.compute(mode)
    secs = sorted(glob.glob(os.path.join(HERE, "sections", "*.md")))
    text = "\n\n".join(open(s).read() for s in secs)
    text = fill_tokens(text, vals)
    text = include_tables(text)
    text = number_labels(text)
    text, refs, order = cite(text)
    text = text.replace("<<REFERENCES>>", refs)
    md = os.path.join(HERE, out_name + ".md")
    open(md, "w").write(text)
    json.dump(order, open(os.path.join(HERE, "citation_order.json"), "w"), indent=1)
    refdoc = os.path.join(HERE, "reference_style.docx")
    make_reference_docx(refdoc)
    out = os.path.join(HERE, out_name + ".docx")
    subprocess.run(["pandoc", md, "-o", out, "--reference-doc", refdoc, "--resource-path", ROOT,
                    "-f", "markdown+tex_math_dollars+pipe_tables+implicit_figures"], check=True, cwd=ROOT)
    postprocess(out)
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", HERE, out], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    except Exception as e:  # PDF is optional
        print("PDF conversion failed:", e)
    print("built", out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    a = ap.parse_args()
    build(a.mode)
