"""Cover letter for Advances in Applied Energy (DOCX). Numbers are filled from results via values.py."""
import json
import os
import sys

from docx import Document
from docx.shared import Pt, Cm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import values as V  # noqa: E402


def build(mode="full"):
    v = V.compute(mode)
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11.5)
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2.5)
    P = d.add_paragraph
    P("P N Bhargav Teja\n[Department, Institution]\n[Address]\n[E-mail]")
    P("[Date]")
    P("The Editors-in-Chief\nAdvances in Applied Energy\nElsevier")
    P("Dear Editors,")
    import re
    title = re.search(r'title:\s*"(.*?)"', open(os.path.join(HERE, "sections", "01_front.md")).read()).group(1)
    P(f"We are pleased to submit our manuscript entitled “{title}” for consideration as a Research Article in "
      "Advances in Applied Energy.")
    P("Demand-response baselines, flexibility offers and measurement-and-verification act on day-ahead load "
      "intervals of individual buildings, and these intervals are needed most when a building has just been "
      "connected to a platform and has almost no data. We evaluate calibration strategies building by building "
      "during this onboarding period. Pooled conformalised quantile regression, although close to nominal on "
      f"average, leaves {v['x_BDG2_CQR_under']} of newly metered buildings (Building Data Genome 2) and "
      f"{v['x_UCI_CQR_under']} of new electricity clients (UCI, Portugal) with coverage more than five points below "
      "the 90 % target over their first eight weeks. Shrinking each building's calibration toward its own "
      f"recency-weighted scores reduces these shares to {v['x_BDG2_HSCCQR_recency_under']} and "
      f"{v['x_UCI_HSCCQR_recency_under']} at an equivalent interval score, and brings first-week reliability to the "
      "level of a perfectly calibrated building. We also report what the window metric hides: weekly coverage of "
      "single buildings remains noisy for every strategy, which operators need to budget for.")
    P("We believe the work fits the journal's focus on applied energy innovation and complements recent "
      "Advances in Applied Energy papers on load forecasting, probabilistic forecasting and transfer learning for "
      "buildings. The study uses two public datasets "
      f"({v['n_bdg2_plus_uci']} buildings and clients), a committed analysis protocol, one tuning rule for all "
      "strategies, nested selection, per-building confirmatory tests with site-cluster confidence intervals, a "
      "method-independent reference for sampling noise, leave-site-out and cross-country transfer and fourteen "
      "stress tests. All code and machine-generated results are provided for full reproducibility.")
    P("We confirm that this manuscript is original, has not been published previously, and is not under "
      "consideration for publication elsewhere. All authors have approved the manuscript and agree with its "
      "submission. The study uses only publicly available, anonymised meter data and raised no ethical issues "
      "requiring approval. The authors declare no competing interests and received no specific funding. The use "
      "of AI-assisted tools is declared in the manuscript.")
    P("Thank you for considering our submission.")
    P("Yours sincerely,\nP N Bhargav Teja, on behalf of all authors")
    out = os.path.join(HERE, "cover_letter.docx")
    d.save(out)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "full")
