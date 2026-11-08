"""Command-line entry point: ``python -m benchkit <command>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

from . import EXCLUSIONS_PATH, FIGURES_DIR, PROCESSED_DIR, PROTOCOL_PATH, RAW_DIR, TABLES_DIR
from .compare import compare_all
from .figures import make_all
from .io import apply_exclusions, load_exclusions, load_raw
from .summarize import summarize
from .validate import validate_tree


def _load(raw: Path) -> pd.DataFrame:
    df = load_raw(raw)
    if df.empty:
        print(f"No data found under {raw}. Collect data first (skill: run-experiment).")
        sys.exit(0)
    if "synthetic" in df.columns and df["synthetic"].fillna(False).astype(bool).any() and raw.resolve() == RAW_DIR.resolve():
        sys.exit("Refusing to analyse: synthetic records found in data/raw (see CLAUDE.md rule 7).")
    kept, excluded = apply_exclusions(df, load_exclusions(EXCLUSIONS_PATH))
    print(f"Loaded {len(df):,} records; excluded {len(excluded):,} (data/exclusions.yaml).")
    return kept


def _analysis_cfg() -> dict:
    return (yaml.safe_load(PROTOCOL_PATH.read_text(encoding="utf-8")) or {}).get("analysis", {})


def cmd_validate(args: argparse.Namespace) -> int:
    reports = validate_tree(Path(args.root), allow_synthetic=args.allow_synthetic)
    if not reports:
        print(f"No .jsonl files under {args.root} (nothing to validate).")
        return 0
    bad = [r for r in reports if not r.ok]
    for r in reports:
        print(f"{'OK  ' if r.ok else 'FAIL'} {r.path} ({r.n_records} records)")
        for e in r.errors:
            print(f"      - {e}")
    print(f"\n{len(reports) - len(bad)}/{len(reports)} files valid.")
    return 1 if bad else 0


def cmd_summarize(args: argparse.Namespace) -> int:
    out = summarize(_load(Path(args.root)))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"Wrote {len(out)} rows → {args.out}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    a = _analysis_cfg()
    pe = a.get("practical_effect", {})
    out = compare_all(_load(Path(args.root)), alpha=a.get("alpha", 0.05),
                      min_abs_delta=pe.get("min_abs_cliffs_delta", 0.33),
                      ratio_band=tuple(pe.get("median_ratio_band", (0.95, 1.05))),
                      resamples=a.get("bootstrap_resamples", 10_000), seed=a.get("bootstrap_seed", 42))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"Wrote {len(out)} comparisons → {args.out}")
    return 0


def cmd_figures(args: argparse.Namespace) -> int:
    summary = pd.read_csv(args.summary)
    comps = pd.read_csv(args.comparisons)
    for p in make_all(summary, comps, Path(args.figures), Path(args.tables)):
        print(f"Wrote {p}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="benchkit", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="schema-check raw JSONL files")
    v.add_argument("root", nargs="?", default=str(RAW_DIR))
    v.add_argument("--allow-synthetic", action="store_true", help="only for test fixtures")
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("summarize", help="robust per-config summaries")
    s.add_argument("root", nargs="?", default=str(RAW_DIR))
    s.add_argument("--out", default=str(PROCESSED_DIR / "summary.csv"))
    s.set_defaults(func=cmd_summarize)

    c = sub.add_parser("compare", help="Flutter vs native statistical comparisons")
    c.add_argument("root", nargs="?", default=str(RAW_DIR))
    c.add_argument("--out", default=str(PROCESSED_DIR / "comparisons.csv"))
    c.set_defaults(func=cmd_compare)

    f = sub.add_parser("figures", help="paper figures + LaTeX tables")
    f.add_argument("--summary", default=str(PROCESSED_DIR / "summary.csv"))
    f.add_argument("--comparisons", default=str(PROCESSED_DIR / "comparisons.csv"))
    f.add_argument("--figures", default=str(FIGURES_DIR))
    f.add_argument("--tables", default=str(TABLES_DIR))
    f.set_defaults(func=cmd_figures)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
