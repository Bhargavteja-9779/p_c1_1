"""Display names used in the revised manuscript (internal method ids are kept in all result files).

PCM = pseudo-count mixture of the pooled calibration-score distribution with the building's own scores
(F = (κ F_pool + Σ own) / (κ + n + 1)); the primary method of revision 1 selects κ by leave-one-building-out
mean absolute coverage deviation (experiments/PREREGISTRATION.md, Amendment 1)."""
DISPLAY = {
    "HSC-CQR cov-κ": "PCM-CQR",
    "HSC-CQR fixed-κ": "PCM-CQR (κ = 168 h)",
    "HSC-CQR simple": "PCM-CQR (κ by LOBO-IS)",
    "HSC-CQR": "PCM-CQR + stage + kNN",
    "HSC-CQR -stage": "PCM-CQR + kNN",
    "HSC-CQR -kNN": "PCM-CQR + stage",
    "HSC-CQR -shrink": "stage+kNN prior only (κ = ∞)",
    "HSC-CQR (MLP)": "PCM-CQR (MLP)",
    "HSC": "PCM-abs + stage + kNN",
    "HSC simple": "PCM-abs",
    "HSC -stage": "PCM-abs + kNN",
    "HSC -kNN": "PCM-abs + stage",
    "HSC -shrink": "abs prior only (κ = ∞)",
}


def disp(m):
    return DISPLAY.get(m, m)
