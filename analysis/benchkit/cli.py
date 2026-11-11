"""Command-line entry point: ``python -m benchkit <command>``."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml

from . import EXCLUSIONS_PATH, FIGURES_DIR, PROCESSED_DIR, PROTOCOL_PATH, RAW_DIR, TABLES_DIR
from .compare import compare_all
from .figures import make_all
from .io import apply_exclusions, load_exclusions, load_raw
from .runner import get_connected_devices, inspect_device, install_apks, preflight_check, run_session
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


def cmd_devices(args: argparse.Namespace) -> int:
    devices = get_connected_devices()
    if not devices:
        print("No ADB devices connected.")
        return 0
    print(f"Connected devices ({len(devices)}):")
    for d in devices:
        print(f"  - Serial: {d['serial']} ({d['state']}) | {d['info']}")
        try:
            info = inspect_device(d['serial'])
            print(f"    Suggested ID: {info['device_id']}")
            print(f"    Hardware: SoC={info['soc']}, RAM={info['ram']}, OS={info['os']}")
            print(f"    Markdown Row: | `{info['device_id']}` | <tier> | {info['model']} | {info['soc']} | {info['ram']} | {info['os']} | Hassaan | ready |")
        except (RuntimeError, subprocess.SubprocessError, KeyError, OSError) as e:
            print(f"    Inspection failed: {e}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    install_apks(serial=args.serial)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    ok = preflight_check(serial=args.serial)
    return 0 if ok else 1


def cmd_run(args: argparse.Namespace) -> int:
    run_session(
        session=args.session,
        device_id=args.device,
        serial=args.serial,
        threads=args.threads,
        cpu_only=args.cpu_only,
        loader=args.loader,
        arm=args.arm,
        platform_filter=args.platform,
    )
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

    dev = sub.add_parser("devices", help="list and inspect connected ADB devices")
    dev.set_defaults(func=cmd_devices)

    chk = sub.add_parser("check", help="pre-flight device environment check")
    chk.add_argument("--serial", "-s", default=None, help="device serial")
    chk.set_defaults(func=cmd_check)

    inst = sub.add_parser("install", help="deploy release APKs to connected device")
    inst.add_argument("--serial", "-s", default=None, help="device serial")
    inst.set_defaults(func=cmd_install)

    r = sub.add_parser("run", help="orchestrate automated experiment session on device")
    r.add_argument("--device", "-d", required=True, help="registered device_id (e.g. dev-infinix-x650c)")
    r.add_argument("--session", "-k", type=int, default=1, help="session index (1..8)")
    r.add_argument("--serial", "-s", default=None, help="device serial")
    r.add_argument("--threads", "-t", type=int, default=4, help="explicit CPU/XNNPACK thread count (e.g. 1 or 4)")
    r.add_argument("--cpu-only", action="store_true", help="run only CPU delegate (6 model x precision configs)")
    r.add_argument("--loader", choices=["asset", "file"], default="asset", help="Flutter model loader mode (asset=fromBuffer calloc, file=fromFile mmap)")
    r.add_argument("--arm", default=None, help="optional EXP-002 arm subdirectory (e.g. matched_1t, matched_4t, mmap_4t)")
    r.add_argument("--platform", choices=["both", "flutter", "native"], default="both", help="restrict execution to one platform (e.g. flutter for loader control)")
    r.set_defaults(func=cmd_run)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
