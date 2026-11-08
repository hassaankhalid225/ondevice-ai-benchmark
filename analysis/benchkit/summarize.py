"""Per-configuration, per-platform robust summaries."""

from __future__ import annotations

import pandas as pd

from . import CONFIG_KEYS, DEFAULT_PHASE, METRIC_FAMILIES, METRIC_PHASE
from .stats import describe


def metric_frame(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Rows usable for ``metric``: right phase, status ok, non-null value."""
    phase = METRIC_PHASE.get(metric, DEFAULT_PHASE)
    if df.empty or metric not in df.columns:
        return df.iloc[0:0]
    sel = (df["phase"] == phase) & (df["status"] == "ok") & df[metric].notna()
    return df.loc[sel]


def summarize(df: pd.DataFrame, metrics: list[str] | None = None) -> pd.DataFrame:
    """Long-format table: CONFIG_KEYS + platform + metric + describe() columns."""
    metrics = metrics or list(METRIC_FAMILIES)
    rows = []
    for metric in metrics:
        sub = metric_frame(df, metric)
        if sub.empty:
            continue
        for keys, g in sub.groupby(CONFIG_KEYS + ["platform"], dropna=False):
            row = dict(zip(CONFIG_KEYS + ["platform"], keys))
            row["metric"] = metric
            row["n_sessions"] = int(g["session"].nunique())
            row.update(describe(g[metric].to_numpy()))
            rows.append(row)
    return pd.DataFrame(rows)


def session_medians(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """One row per (config, platform, session) with the session median: for robustness checks."""
    sub = metric_frame(df, metric)
    if sub.empty:
        return sub
    return (sub.groupby(CONFIG_KEYS + ["platform", "session"], dropna=False)[metric]
               .median().reset_index())
