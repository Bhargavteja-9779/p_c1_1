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
      "metered buildings: comparing and tuning conformal calibration strategies” for consideration as a Research "
      "Article in Advances in Applied Energy.")
    P("Demand-response baselines, flexibility commitments and measurement-and-verification act on day-ahead "
      "prediction intervals of individual buildings, and these intervals are needed most when a building has just "
      "been connected to a platform and has little data. We show that pooled conformalised quantile regression, "
      "although well calibrated on average, leaves "
      f"{v['main_BDG2_CQR_under_rate']} of newly metered BDG2 buildings (and {v['main_UCI_CQR_under_rate']} of "
      "Portuguese UCI clients) more than five percentage points below the 90 % target. Comparing seven calibration "
      "strategies under one protocol, we find that shrinking the pooled score distribution toward each building's "
      f"own accumulating errors reduces these shares to {v['main_BDG2_PCSCQR_under_rate']} and "
      f"{v['main_UCI_PCSCQR_under_rate']} at an unchanged interval score, provided the shrinkage is tuned for "
      "per-building reliability or simply fixed at one week of hourly scores; the usual interval-score tuning "
      "cannot make this choice. Adaptive conformal inference reaches similar reliability only with much wider "
      "intervals, and no strategy of comparable width makes the first week reliable — a limitation we report "
      "openly.")
    P("We believe the work fits the journal's focus on applied energy innovation: it turns the forecasts of "
      "global, transfer-learning or pretrained models into intervals that operators can trust building by "
      "building, with a one-parameter layer that costs a few hundredths of a millisecond per building-day. The "
      "study uses two public datasets (more than 1,100 buildings and clients), every site held out in turn, "
      "cross-country transfer, a disjoint calibration period, stress tests, site-level randomisation tests and a "
      "documented analysis plan with all deviations listed. All code and machine-generated results are provided "
      "for full reproducibility.")
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
