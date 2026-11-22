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
    P("Aggregators and demand-response programmes check the performance of each enrolled building in each "
      "settlement period, so they need day-ahead load intervals that are reliable building by building and week by "
      "week, from the first days after a building is metered. We show that pooled conformal calibration, although "
      f"well calibrated on average, leaves {v['tt_BDG2_CQR_wk_late']} of newly metered buildings (Building Data "
      f"Genome 2) and {v['tt_UCI_CQR_wk_late']} of new electricity clients (UCI, Portugal) under-covered in a "
      "typical week. We propose two-timescale shrinkage conformal calibration (TTSC), which combines a prior learned "
      "from previously onboarded buildings with a per-building correction from the last week's misses. It reduces "
      f"these shares to {v['tt_BDG2_TTSC_wk_late']} and {v['tt_UCI_TTSC_wk_late']}, below a static-calibration oracle "
      "reference, and reduces failed weekly performance checks of capacity-headroom offers, "
      "with results confirmed on runs held out from the method's design, on unseen sites, after cross-country "
      "transfer and in fourteen stress tests.")
    P("We believe the work fits the journal's focus on applied energy innovation and complements recent "
      "Advances in Applied Energy papers on load forecasting, probabilistic forecasting and transfer learning for "
      "buildings. The study uses two public datasets "
      f"({v['n_bdg2_plus_uci']} buildings and clients), one tuning rule for all strategies, per-building "
      "confirmatory tests with site-cluster confidence intervals and a method-independent reference for sampling "
      "noise. The code will be made available on request.")
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
