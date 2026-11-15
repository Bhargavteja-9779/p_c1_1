"""Global forecasting models shared across buildings (trained on normalised targets y/s).

* LightGBM point model (L2)                         -> point forecast for conformal methods
* LightGBM quantile models (alpha/2, 1-alpha/2)     -> QR baseline and CQR scores
* MLP with Gaussian head (mean, log-variance; NLL)  -> deep probabilistic baseline
* MLP with quantile head (pinball loss)             -> deep quantile baseline
Hardware: CPU by default; CUDA or Apple-MPS used automatically for the MLPs if present.
"""
from __future__ import annotations

import numpy as np
import lightgbm as lgb
import torch
import torch.nn as nn

LGB_PARAMS = dict(learning_rate=0.05, num_leaves=63, min_data_in_leaf=200, feature_fraction=0.8,
                  bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, num_threads=4)


def device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def fit_lgb(X, y, Xv, yv, seed, objective="l2", alpha=None, rounds=2000):
    p = dict(LGB_PARAMS, objective="quantile" if objective == "quantile" else "l2", seed=seed,
             bagging_seed=seed, feature_fraction_seed=seed, deterministic=True, force_row_wise=True)
    if alpha is not None:
        p["alpha"] = alpha
    dtr = lgb.Dataset(X, y, free_raw_data=False)
    dv = lgb.Dataset(Xv, yv, reference=dtr)
    m = lgb.train(p, dtr, num_boost_round=rounds, valid_sets=[dv],
                  callbacks=[lgb.early_stopping(50, verbose=False)])
    return m


class _MLP(nn.Module):
    def __init__(self, d, out, width=256):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, width), nn.ReLU(), nn.Linear(width, width), nn.ReLU(),
                                 nn.Linear(width, width // 2), nn.ReLU(), nn.Linear(width // 2, out))

    def forward(self, x):
        return self.net(x)


class MLPPrep:
    """NaN -> 0 plus missingness indicators; standardisation fitted on training rows only."""

    def fit(self, X):
        self.miss_cols = np.where(np.isnan(X).any(axis=0))[0]
        Z = self._aug(X)
        self.mu = Z.mean(axis=0)
        self.sd = Z.std(axis=0) + 1e-6
        return self

    def _aug(self, X):
        M = np.isnan(X[:, self.miss_cols]).astype(np.float32)
        return np.concatenate([np.nan_to_num(X, nan=0.0), M], axis=1).astype(np.float32)

    def transform(self, X):
        return ((self._aug(X) - self.mu) / self.sd).astype(np.float32)


def fit_mlp(X, y, Xv, yv, seed, kind="gauss", quantiles=(0.05, 0.95), epochs=12, bs=4096, lr=1e-3):
    torch.manual_seed(seed)
    np.random.seed(seed)
    dev = device()
    prep = MLPPrep().fit(X)
    Xt = torch.from_numpy(prep.transform(X))
    yt = torch.from_numpy(y.astype(np.float32))
    Xvt = torch.from_numpy(prep.transform(Xv)).to(dev)
    yvt = torch.from_numpy(yv.astype(np.float32)).to(dev)
    out = 2 if kind == "gauss" else len(quantiles)
    model = _MLP(Xt.shape[1], out).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    qs = torch.tensor(quantiles, dtype=torch.float32, device=dev)

    def loss_fn(o, t):
        if kind == "gauss":
            mu, logv = o[:, 0], o[:, 1].clamp(-12, 8)
            return (0.5 * (logv + (t - mu) ** 2 / torch.exp(logv))).mean()
        d = t[:, None] - o
        return torch.maximum(qs * d, (qs - 1) * d).mean()

    best, best_state, bad = np.inf, None, 0
    g = torch.Generator().manual_seed(seed)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(Xt.shape[0], generator=g)
        for i in range(0, len(perm), bs):
            idx = perm[i:i + bs]
            o = model(Xt[idx].to(dev))
            loss = loss_fn(o, yt[idx].to(dev))
            opt.zero_grad()
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            vl = float(loss_fn(model(Xvt), yvt))
        if vl < best - 1e-5:
            best, bad = vl, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= 3:
                break
    model.load_state_dict(best_state)
    model.eval()
    return dict(model=model, prep=prep, kind=kind, quantiles=quantiles)


def predict_mlp(m, X, bs=65536):
    dev = device()
    Z = torch.from_numpy(m["prep"].transform(X))
    outs = []
    with torch.no_grad():
        for i in range(0, Z.shape[0], bs):
            outs.append(m["model"](Z[i:i + bs].to(dev)).cpu().numpy())
    o = np.concatenate(outs)
    if m["kind"] == "gauss":
        return o[:, 0], np.exp(0.5 * np.clip(o[:, 1], -12, 8))
    return np.sort(o, axis=1)  # enforce non-crossing
