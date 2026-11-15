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
    P("[Corresponding author name]\n[Department, Institution]\n[Address]\n[E-mail]")
    P("[Date]")
    P("The Editors-in-Chief\nAdvances in Applied Energy\nElsevier")
    P("Dear Editors,")
    P("We are pleased to submit our manuscript entitled “Reliable day-ahead prediction intervals for newly "
      "metered buildings: hierarchical shrinkage conformal calibration evaluated building by building” for "
      "consideration as a Research Article in Advances in Applied Energy.")
    P("Demand-response baselines, flexibility bids and measurement-and-verification act on day-ahead prediction "
      "intervals of individual buildings, and these intervals are needed most when a building has just been "
      "connected to a platform and has almost no data. We show that standard pooled conformal calibration, "
      "although well calibrated on average, leaves "
      f"{v['main_BDG2_SCPstage_under_rate']} of newly metered BDG2 buildings with coverage more than five "
      "percentage points below the 90 % target during their first eight weeks. Our hierarchical shrinkage "
      "conformal (HSC) calibration starts from the errors of similar buildings at the same onboarding stage and "
      "shrinks toward each building's own errors as they accumulate. Applied to conformalised quantile "
      f"regression, it reduces this share to {v['main_BDG2_HSCCQR_under_rate']} on BDG2 "
      f"({v['main_UCI_CQR_under_rate']} → {v['main_UCI_HSCCQR_under_rate']} for CQR → HSC-CQR on the Portuguese UCI "
      "data) without sharper-looking but less reliable intervals, at a cost below a millisecond per building-day.")
    P("We believe the work fits the journal's focus on applied energy innovation and complements recent "
      "Advances in Applied Energy papers on load forecasting, probabilistic forecasting and transfer learning for "
      "smart buildings: it turns their forecasts into intervals that operators can trust building by building "
      "from the first days of metering. The study uses two public datasets (more than 1,100 buildings and "
      "clients), pre-registered protocols, five partition seeds, paired per-building statistical tests, "
      "leave-site-out and cross-country transfer, stress tests and an ablation of every component. All code and "
      "machine-generated results are provided for full reproducibility.")
    P("We confirm that this manuscript is original, has not been published previously, and is not under "
      "consideration for publication elsewhere. All authors have approved the manuscript and agree with its "
      "submission. The study uses only publicly available, anonymised meter data and raised no ethical issues "
      "requiring approval. The authors declare no competing interests. The use of AI-assisted tools is declared "
      "in the manuscript.")
    P("Possible reviewers (optional; to be completed by the authors): [Name, affiliation, e-mail] ×3.")
    P("Thank you for considering our submission.")
    P("Yours sincerely,\n[Corresponding author name], on behalf of all authors")
    out = os.path.join(HERE, "cover_letter.docx")
    d.save(out)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "full")
