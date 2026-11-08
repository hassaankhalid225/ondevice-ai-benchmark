"""Flutter vs native comparisons per configuration and metric (ADR-0005)."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np
import pandas as pd

from . import CONFIG_KEYS, METRIC_FAMILIES
from .stats import compare_samples, holm
from .summarize import metric_frame, session_medians

FLUTTER = "flutter"
NATIVE = {"android": "android_native", "ios": "ios_native"}


def compare_all(df: pd.DataFrame, *, metrics: list[str] | None = None, alpha: float = 0.05,
                min_abs_delta: float = 0.33, ratio_band: tuple[float, float] = (0.95, 1.05),
                resamples: int = 10_000, seed: int = 42) -> pd.DataFrame:
    """One row per (config, metric): MWU, Holm-adjusted p (within RQ family), Cliff's delta,
    median ratio Flutter/Native with bootstrap CI, practical-significance flag, and a
    session-median robustness ratio."""
    metrics = metrics or list(METRIC_FAMILIES)
    rows = []
    for metric in metrics:
        sub = metric_frame(df, metric)
        if sub.empty:
            continue
        sess = session_medians(df, metric)
        for keys, g in sub.groupby(CONFIG_KEYS, dropna=False):
            cfg = dict(zip(CONFIG_KEYS, keys))
            native = NATIVE.get(cfg["os"])
            x = g.loc[g["platform"] == FLUTTER, metric].to_numpy(dtype=float)
            y = g.loc[g["platform"] == native, metric].to_numpy(dtype=float)
            if x.size < 2 or y.size < 2:
                continue
            c = compare_samples(x, y, resamples=resamples, seed=seed)
            s = sess
            for k, v in cfg.items():
                s = s[s[k] == v]
            sx = s.loc[s["platform"] == FLUTTER, metric]
            sy = s.loc[s["platform"] == native, metric]
            sess_ratio = float(sx.median() / sy.median()) if len(sx) and len(sy) else np.nan
            rows.append(cfg | {"metric": metric, "family": METRIC_FAMILIES[metric],
                               "native_platform": native, **asdict(c),
                               "session_median_ratio": sess_ratio})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["p_holm"] = np.nan
    for idx in out.groupby("family").groups.values():
        out.loc[idx, "p_holm"] = holm(out.loc[idx, "p"].to_numpy())
    out["significant"] = out["p_holm"] < alpha
    out["practical"] = (out["significant"]
                        & (out["delta"].abs() >= min_abs_delta)
                        & ((out["ratio_lo"] > ratio_band[1]) | (out["ratio_hi"] < ratio_band[0])))
    return out
