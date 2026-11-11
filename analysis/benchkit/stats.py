"""Statistical primitives (ADR-0005). Keep pure, tested, and dependency-light."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import mannwhitneyu


def describe(x: np.ndarray) -> dict[str, float]:
    """Robust summary: n, median, p5, p25, p75, p95, IQR."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if x.size == 0:
        return {k: float("nan") for k in ("n", "median", "p5", "p25", "p75", "p95", "iqr")} | {"n": 0}
    p5, p25, p50, p75, p95 = np.percentile(x, [5, 25, 50, 75, 95])
    return {"n": int(x.size), "median": p50, "p5": p5, "p25": p25, "p75": p75, "p95": p95, "iqr": p75 - p25}


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Cliff's delta = P(X > Y) - P(X < Y), computed in O(n log n) via the Mann-Whitney U statistic."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size == 0 or y.size == 0:
        return float("nan")
    u1 = mannwhitneyu(x, y, alternative="two-sided", method="asymptotic").statistic
    return float(2.0 * u1 / (x.size * y.size) - 1.0)


def cliffs_magnitude(delta: float) -> str:
    """Romano et al. thresholds: negligible < .147 <= small < .33 <= medium < .474 <= large."""
    a = abs(delta)
    if np.isnan(a):
        return "n/a"
    if a < 0.147:
        return "negligible"
    if a < 0.33:
        return "small"
    if a < 0.474:
        return "medium"
    return "large"


def bootstrap_median_ratio_ci(x: np.ndarray, y: np.ndarray, *, resamples: int = 10_000,
                              seed: int = 42, level: float = 0.95) -> tuple[float, float, float]:
    """Median(x)/median(y) with a percentile bootstrap CI. Returns (ratio, lo, hi)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ratio = float(np.median(x) / np.median(y))
    rng = np.random.default_rng(seed)
    mx = np.median(x[rng.integers(0, x.size, size=(resamples, x.size))], axis=1)
    my = np.median(y[rng.integers(0, y.size, size=(resamples, y.size))], axis=1)
    alpha = (1 - level) / 2
    lo, hi = np.quantile(mx / my, [alpha, 1 - alpha])
    return ratio, float(lo), float(hi)


def tost_p(x: np.ndarray, y: np.ndarray, *, bounds: tuple[float, float] = (0.95, 1.05)) -> float:
    """Non-parametric multiplicative TOST p-value using two one-sided Mann-Whitney U tests
    against ratio bounds [lo, hi]: tests H01: X <= lo*Y vs X > lo*Y and H02: X >= hi*Y vs X < hi*Y."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size == 0 or y.size == 0:
        return float("nan")
    p_lo = float(mannwhitneyu(x, bounds[0] * y, alternative="greater").pvalue)
    p_hi = float(mannwhitneyu(x, bounds[1] * y, alternative="less").pvalue)
    return float(max(p_lo, p_hi))


def holm(pvalues: np.ndarray) -> np.ndarray:
    """Holm-Bonferroni step-down adjusted p-values (monotone, capped at 1). NaNs pass through."""
    p = np.asarray(pvalues, dtype=float)
    out = np.full_like(p, np.nan)
    valid = ~np.isnan(p)
    pv = p[valid]
    m = pv.size
    if m == 0:
        return out
    order = np.argsort(pv)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pv[idx])
        adj[idx] = min(1.0, running)
    out[valid] = adj
    return out


@dataclass
class Comparison:
    n_x: int
    n_y: int
    median_x: float
    median_y: float
    u: float
    p: float
    tost_p: float
    delta: float
    magnitude: str
    ratio: float
    ratio_lo: float
    ratio_hi: float


def compare_samples(x: np.ndarray, y: np.ndarray, *, resamples: int = 10_000, seed: int = 42,
                    equivalence_band: tuple[float, float] = (0.95, 1.05)) -> Comparison:
    """Full two-sample comparison: x = Flutter, y = native by convention."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    y = np.asarray(y, dtype=float)
    y = y[~np.isnan(y)]
    res = mannwhitneyu(x, y, alternative="two-sided")
    eq_p = tost_p(x, y, bounds=equivalence_band)
    d = cliffs_delta(x, y)
    r, lo, hi = bootstrap_median_ratio_ci(x, y, resamples=resamples, seed=seed)
    return Comparison(int(x.size), int(y.size), float(np.median(x)), float(np.median(y)),
                      float(res.statistic), float(res.pvalue), eq_p, d, cliffs_magnitude(d), r, lo, hi)
