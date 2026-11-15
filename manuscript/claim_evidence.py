"""Claim-evidence audit helper (Phase 22).

For every sentence of the manuscript sources that contains a {{token}} or a comparative/qualitative claim
keyword, list: section, sentence, tokens -> filled values -> source of each token. Output:
REVIEW/claim_evidence_map.md. Qualitative claims without tokens are flagged for manual mapping.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CLAIM_WORDS = re.compile(r"\b(better|worse|improv|reduc|outperform|more reliable|less|fails?|failure|robust|"
                         r"significant|persist|negligible|similar|comparable|largest|smallest|no measurable|"
                         r"decisive|first|novel|never|always|all methods|none)\b", re.I)


def source_of(tok):
    if tok.startswith(("main_", "lso_", "xds_")):
        return "results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)"
    if tok.startswith("test_"):
        return "results/statistics.csv (src/statistics/analysis.py::paired_tests)"
    if tok.startswith("rob_"):
        return "results/seed_level_metrics.csv, exp=robust"
    if tok.startswith(("tuned_", "cost_", "point_")):
        return "results/run_info.json"
    if tok.startswith("sens_"):
        return "results/sensitivity.csv"
    if tok.startswith(("floor_", "nvalid_")):
        return "Monte Carlo from per-building n_valid (manuscript/values.py)"
    if tok.startswith("red_"):
        return "derived relative reduction (manuscript/values.py)"
    if tok in ("n_bdg2", "n_uci", "n_sites", "n_bdg2_plus_uci"):
        return "data/processed after quality filter (src/data/datasets.py)"
    if tok in ("ABSTRACT", "ERROR_ANALYSIS_TEXT"):
        return "generated text (manuscript/values.py) from results/*.json/csv"
    return "manuscript/values.py"


def run(mode="full"):
    vals = json.load(open(os.path.join(ROOT, "results", f"manuscript_values{'_quick' if mode == 'quick' else ''}.json")))
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "sections", "*.md"))):
        sec = os.path.basename(f)
        text = open(f).read()
        text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
        for para in text.split("\n\n"):
            if para.startswith(("|", "<<TABLE", "![")):
                continue
            for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", para.replace("\n", " ")):
                toks = re.findall(r"\{\{(.*?)\}\}", sent)
                if not toks and not CLAIM_WORDS.search(sent):
                    continue
                rows.append((sec, sent.strip(), [(t, vals.get(t, "MISSING"), source_of(t)) for t in toks]))
    out = ["# Claim–evidence map (auto-generated; qualitative claims require manual evidence column)\n"]
    for sec, sent, toks in rows:
        out.append(f"### {sec}\n> {sent[:600]}\n")
        if toks:
            for t, v, s in toks:
                vv = str(v)
                out.append(f"- `{t}` = {vv[:120]} ← {s}")
        else:
            out.append("- **qualitative claim — evidence to be mapped manually**")
        out.append("")
    os.makedirs(os.path.join(ROOT, "REVIEW"), exist_ok=True)
    open(os.path.join(ROOT, "REVIEW", "claim_evidence_map.md"), "w").write("\n".join(out))
    print(len(rows), "claims mapped")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
