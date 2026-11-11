"""Paper figures and LaTeX tables. Generated artifacts only, never hand-edit outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

IEEE_COL_IN = 3.5
IEEE_DBL_IN = 7.16
# Okabe-Ito colour-blind-safe palette
PALETTE = {"flutter": "#0072B2", "android_native": "#D55E00", "ios_native": "#009E73"}
STAGES = ["preprocess_ms", "boundary_overhead_ms", "inference_native_ms", "postprocess_ms"]
STAGE_LABELS = {
    "preprocess_ms": "Preprocess",
    "boundary_overhead_ms": "Boundary (FFI/JNI)",
    "inference_native_ms": "Native kernel",
    "postprocess_ms": "Postprocess",
}
STAGE_COLORS = ["#56B4E9", "#009E73", "#E69F00", "#CC79A7"]
STAGE_HATCHES = ["", "///", "...", "xxx"]
METRIC_AXIS_LABELS = {
    "inference_native_ms": "Pure kernel ratio (Flutter / Native)",
    "end_to_end_ms": "End-to-end latency ratio (Flutter / Native)",
    "pss_mb": "Steady-state PSS ratio (Flutter / Native)",
    "model_load_ms": "Model load time ratio (Flutter / Native)",
    "cold_start_ms": "Cold-start latency ratio (Flutter / Native)",
}
MODEL_SHORT = {
    "mobilenetv3_large": "MN3",
    "efficientdet_lite0": "ED-L0",
    "mobilebert_qa": "MB-QA",
}


def _style() -> None:
    plt.rcParams.update({
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "tight",
    })


def _short_device(device_id: str) -> str:
    d = str(device_id).removeprefix("dev-")
    if d == "infinix-mobility-limited-infinix-x650c":
        return "infinix-x650c"
    return d


def _short_model(model_id: str) -> str:
    return MODEL_SHORT.get(str(model_id), str(model_id))


def _label(row: pd.Series, *, include_device: bool = True) -> str:
    core = f"{row['model_id']} · {row['precision']} · {row['delegate']}"
    return f"{_short_device(row['device_id'])} · {core}" if include_device else core


def ratio_forest(comparisons: pd.DataFrame, metric: str, out: Path) -> Path | None:
    """Forest plot: median ratio Flutter/Native with 95% bootstrap CI per configuration."""
    d = comparisons[comparisons["metric"] == metric].copy()
    if d.empty:
        return None
    _style()
    d = d.sort_values(["model_id", "precision", "delegate", "device_id"]).reset_index(drop=True)
    multi_dev = d["device_id"].nunique() > 1
    fig, ax = plt.subplots(figsize=(IEEE_COL_IN, max(1.45, 0.24 * len(d) + 0.95)))
    ypos = np.arange(len(d))[::-1]
    practical = d["practical"].astype(bool).to_numpy()
    equiv = (d["equivalent"].astype(bool).to_numpy() if "equivalent" in d.columns
             else np.zeros(len(d), dtype=bool))
    seen: set[str] = set()
    for y, r, lo, hi, prac, eq in zip(ypos, d["ratio"], d["ratio_lo"], d["ratio_hi"], practical, equiv):
        if prac:
            kw = {"fmt": "o", "color": "#D55E00", "mfc": "#D55E00", "mec": "#D55E00", "label": "Practical diff."}
            cat = "prac"
        elif eq:
            kw = {"fmt": "s", "color": "#0072B2", "mfc": "#0072B2", "mec": "#0072B2", "label": "Equiv. (±5% TOST)"}
            cat = "eq"
        else:
            kw = {"fmt": "o", "color": "#444444", "mfc": "white", "mec": "#444444", "label": "Inconclusive"}
            cat = "inc"
        if cat in seen:
            kw.pop("label")
        seen.add(cat)
        ax.errorbar([r], [y], xerr=[[max(0.0, r - lo)], [max(0.0, hi - r)]], ms=3.5, elinewidth=1, capsize=2, **kw)
    ax.axvline(1.0, color="black", lw=0.8)
    ax.axvspan(0.95, 1.05, color="#E0E0E0", zorder=0, lw=0)
    ax.set_yticks(ypos, [_label(r, include_device=multi_dev) for _, r in d.iterrows()])
    ax.set_ylim(-0.6, len(d) - 0.4)
    ax.set_xlabel(METRIC_AXIS_LABELS.get(metric, f"Median {metric.removesuffix('_ms')} ratio (Flutter / Native)"))
    if len(seen) > 1 or len(d) > 2:
        ax.legend(frameon=False, ncols=len(seen), fontsize=6.5, loc="lower left", bbox_to_anchor=(0.0, 1.01),
                  handletextpad=0.25, columnspacing=0.7)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def stage_decomposition(summary: pd.DataFrame, out: Path) -> Path | None:
    """Horizontal stacked bars of median stage times per platform for each configuration."""
    s = summary[summary["metric"].isin(STAGES)]
    if s.empty:
        return None
    _style()
    piv = (s.pivot_table(index=["device_id", "model_id", "precision", "delegate", "platform"],
                         columns="metric", values="median")
            .reindex(columns=STAGES).fillna(0).reset_index()
            .sort_values(["device_id", "model_id", "precision", "delegate", "platform"]))
    multi_dev = piv["device_id"].nunique() > 1
    labels = [
        (f"{_short_device(r.device_id)} · " if multi_dev else "")
        + f"{_short_model(r.model_id)} · {r.precision.upper()} · {r.delegate.upper()} "
        + f"[{'F' if r.platform == 'flutter' else 'N'}]"
        for r in piv.itertuples()
    ]
    n_bars = len(piv)
    ypos = np.arange(n_bars)[::-1]
    fig, ax = plt.subplots(figsize=(IEEE_DBL_IN, max(2.8, 0.19 * n_bars + 0.6)))
    left = np.zeros(n_bars)
    for stage, col, hatch in zip(STAGES, STAGE_COLORS, STAGE_HATCHES):
        ax.barh(ypos, piv[stage], left=left, color=col, edgecolor="#333333", linewidth=0.35,
                hatch=hatch, height=0.72, label=STAGE_LABELS.get(stage, stage.removesuffix("_ms")))
        left += piv[stage].to_numpy()
    max_w = float(left.max()) if len(left) else 1.0
    ax.set_xlim(0, max_w * 1.05)
    # Subtle horizontal guides separating (model, precision, delegate) pairs
    cfg_keys = list(zip(piv["device_id"], piv["model_id"], piv["precision"], piv["delegate"]))
    for idx in range(len(cfg_keys) - 1):
        if cfg_keys[idx] != cfg_keys[idx + 1]:
            ax.axhline((ypos[idx] + ypos[idx + 1]) / 2.0, color="#CCCCCC", lw=0.45, ls=":")
    ax.set_yticks(ypos, labels, fontsize=7)
    ax.set_ylim(-0.6, n_bars - 0.4)
    ax.set_xlabel("Median stage duration (ms)")
    ax.legend(frameon=False, ncols=len(STAGES), loc="upper center", bbox_to_anchor=(0.45, 1.09), fontsize=7.5)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def comparisons_table(comparisons: pd.DataFrame, metric: str, out: Path) -> Path | None:
    """LaTeX booktabs table for one metric (to \\input{} in the paper)."""
    d = comparisons[comparisons["metric"] == metric]
    if d.empty:
        return None
    multi_dev = d["device_id"].nunique() > 1
    if multi_dev:
        lines = [r"\begin{tabular}{llllrrrrl}", r"\toprule",
                 r"Device & Model & Prec. & Deleg. & Flutter & Native & Ratio [95\% CI] & $\delta$ & $p_{\mathrm{Holm}}$ \\",
                 r"\midrule"]
    else:
        lines = [r"\begin{tabular}{lllrrrrl}", r"\toprule",
                 r"Model & Prec. & Deleg. & Flutter & Native & Ratio [95\% CI] & $\delta$ & $p_{\mathrm{Holm}}$ \\",
                 r"\midrule"]
    for r in d.sort_values(["device_id", "model_id", "precision", "delegate"]).itertuples():
        model = str(r.model_id).replace("_", r"\_")
        p = "$<$0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"
        dev_tex = _short_device(r.device_id).replace("_", r"\_")
        prefix = f"{dev_tex} & " if multi_dev else ""
        lines.append(f"{prefix}{model} & {r.precision} & {r.delegate} & {r.median_x:.2f} & {r.median_y:.2f} & "
                     f"{r.ratio:.2f} [{r.ratio_lo:.2f}, {r.ratio_hi:.2f}] & {r.delta:+.2f} & {p} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def baseline_table(comparisons: pd.DataFrame, out: Path) -> Path | None:
    """LaTeX booktabs table for app-level baseline metrics (cold_start_ms, idle_pss_mb)."""
    d = comparisons[comparisons["metric"].isin(["cold_start_ms", "idle_pss_mb"])]
    if d.empty:
        return None
    multi_dev = d["device_id"].nunique() > 1
    metric_labels = {
        "cold_start_ms": r"Cold Start (\texttt{TotalTime}, ms)",
        "idle_pss_mb": r"Idle Baseline PSS (MiB)",
    }
    if multi_dev:
        lines = [r"\begin{tabular}{llrrrrl}", r"\toprule",
                 r"Device & Baseline Metric & Flutter & Native & Ratio [95\% CI] & $\delta$ & $p_{\mathrm{Holm}}$ \\",
                 r"\midrule"]
    else:
        lines = [r"\begin{tabular}{lrrrrl}", r"\toprule",
                 r"Baseline Metric & Flutter & Native & Ratio [95\% CI] & $\delta$ & $p_{\mathrm{Holm}}$ \\",
                 r"\midrule"]
    for r in d.sort_values(["device_id", "metric"]).itertuples():
        mlabel = metric_labels.get(r.metric, str(r.metric).replace("_", r"\_"))
        p = "$<$0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"
        dev_tex = _short_device(r.device_id).replace("_", r"\_")
        prefix = f"{dev_tex} & " if multi_dev else ""
        lines.append(f"{prefix}{mlabel} & {r.median_x:.2f} & {r.median_y:.2f} & "
                     f"{r.ratio:.2f} [{r.ratio_lo:.2f}, {r.ratio_hi:.2f}] & {r.delta:+.2f} & {p} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def make_all(summary: pd.DataFrame, comparisons: pd.DataFrame, figures_dir: Path, tables_dir: Path) -> list[Path]:
    produced: list[Path | None] = [
        ratio_forest(comparisons, "inference_native_ms", figures_dir / "rq1-inference-ratio.pdf"),
        ratio_forest(comparisons, "end_to_end_ms", figures_dir / "rq2-e2e-ratio.pdf"),
        stage_decomposition(summary, figures_dir / "rq2-stage-decomposition.pdf"),
        ratio_forest(comparisons, "pss_mb", figures_dir / "rq3-memory-ratio.pdf"),
        ratio_forest(comparisons, "cold_start_ms", figures_dir / "rq5-coldstart-ratio.pdf"),
        ratio_forest(comparisons, "model_load_ms", figures_dir / "rq5-modelload-ratio.pdf"),
        comparisons_table(comparisons, "inference_native_ms", tables_dir / "rq1-inference.tex"),
        comparisons_table(comparisons, "end_to_end_ms", tables_dir / "rq2-e2e.tex"),
        comparisons_table(comparisons, "pss_mb", tables_dir / "rq3-pss.tex"),
        comparisons_table(comparisons, "cpu_pct", tables_dir / "rq3-cpu.tex"),
        comparisons_table(comparisons, "model_load_ms", tables_dir / "rq5-modelload.tex"),
        baseline_table(comparisons, tables_dir / "rq5-baseline.tex"),
    ]
    return [p for p in produced if p is not None]
