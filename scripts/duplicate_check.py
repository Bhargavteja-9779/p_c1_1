"""Duplicate-meter check (revision 1, reviewer R5): pairs of buildings whose hourly loads correlate r > 0.99
over their common valid hours (>= 2000 h). Output: tables/T_duplicates.md and printed counts."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import experiments as ex  # noqa: E402


def pairs(load, meta, thr=0.99, min_h=2000):
    X = load.reshape(load.shape[0], -1).astype(np.float64)
    V = ~np.isnan(X)
    Z = np.where(V, X, 0.0)
    out = []
    n = X.shape[0]
    for i in range(n):
        vi = V[i] & V[i + 1:]                       # (n-i-1, T)
        c = vi.sum(1)
        xi = np.where(vi, Z[i], 0.0)
        xj = np.where(vi, Z[i + 1:], 0.0)
        mi, mj = xi.sum(1) / np.maximum(c, 1), xj.sum(1) / np.maximum(c, 1)
        sxy = (xi * xj).sum(1) / np.maximum(c, 1) - mi * mj
        sxx = (xi * xi).sum(1) / np.maximum(c, 1) - mi ** 2
        syy = (xj * xj).sum(1) / np.maximum(c, 1) - mj ** 2
        r = sxy / np.sqrt(np.maximum(sxx * syy, 1e-12))
        for k in np.where((r > thr) & (c >= min_h))[0]:
            j = i + 1 + k
            out.append(dict(a=meta.index[i] if meta is not None else i, b=meta.index[j] if meta is not None else j,
                            r=round(float(r[k]), 4), common_h=int(c[k])))
    return pd.DataFrame(out)


def main():
    lines = ["**Duplicate-meter check**: building pairs with hourly-load Pearson r > 0.99 over >= 2000 common valid hours.\n"]
    for dsn in ["BDG2", "UCI"]:
        ds = ex.get_ds(dsn)
        meta = ds["meta"]
        if meta is not None and "building_id" in meta.columns:
            meta = meta.set_index("building_id")
        df = pairs(ds["load"], meta)
        lines.append(f"- {dsn}: {ds['load'].shape[0]} buildings, {len(df)} pairs with r > 0.99"
                     + (f" (involving {len(set(df.a) | set(df.b))} buildings)" if len(df) else ""))
        if len(df):
            lines.append("\n" + df.head(30).to_markdown(index=False) + "\n")
        print(dsn, len(df))
    with open(os.path.join(ex.ROOT, "tables", "T_duplicates.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
