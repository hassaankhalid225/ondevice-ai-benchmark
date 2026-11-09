"""Loading raw JSONL records and applying documented exclusions."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import yaml

from . import EXCLUSIONS_PATH


def iter_jsonl_files(root: Path) -> Iterator[Path]:
    """Yield every *.jsonl file under ``root`` in a stable (sorted) order."""
    yield from sorted(Path(root).rglob("*.jsonl"))


def read_jsonl(path: Path) -> list[dict]:
    """Read one JSONL file. Blank lines are ignored."""
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``boundary_overhead_ms`` and ``timer_residual_ms`` (ADR-0006). Values are not clipped."""
    if "inference_native_ms" in df.columns and "inference_ms" in df.columns:
        df["boundary_overhead_ms"] = df["inference_ms"] - df["inference_native_ms"]
    stages = ["preprocess_ms", "inference_ms", "postprocess_ms"]
    if "end_to_end_ms" in df.columns and all(s in df.columns for s in stages):
        df["timer_residual_ms"] = df["end_to_end_ms"] - df[stages].sum(axis=1, skipna=False)
    return df


def load_raw(root: Path) -> pd.DataFrame:
    """Load all records under ``root`` into one DataFrame with a ``source_file`` column."""
    frames = []
    for path in iter_jsonl_files(root):
        recs = read_jsonl(path)
        if recs:
            df = pd.DataFrame.from_records(recs)
            df["source_file"] = str(path)
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return add_derived_metrics(pd.concat(frames, ignore_index=True))


def load_exclusions(path: Path = EXCLUSIONS_PATH) -> list[dict]:
    """Return the list of exclusion entries from ``data/exclusions.yaml`` (may be empty)."""
    if not Path(path).exists():
        return []
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return list(data.get("exclusions") or [])


def apply_exclusions(df: pd.DataFrame, exclusions: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split ``df`` into (kept, excluded) using run_id or file matches. Raw files are never touched."""
    if df.empty or not exclusions:
        return df, df.iloc[0:0]
    run_ids = {e["run_id"] for e in exclusions if e.get("run_id")}
    files = {Path(e["file"]).name for e in exclusions if e.get("file")}
    mask = df["run_id"].isin(run_ids)
    if files:
        mask |= df["source_file"].map(lambda p: Path(p).name in files)
    return df[~mask].copy(), df[mask].copy()
