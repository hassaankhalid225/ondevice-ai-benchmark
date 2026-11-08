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
STAGES = ["preprocess_ms", "inference_ms", "postprocess_ms"]
STAGE_COLORS = ["#56B4E9", "#E69F00", "#CC79A7"]


def _style() -> None:
    plt.rcParams.update({
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "tight",
    })


def _label(row: pd.Series) -> str:
    return f"{row['device_id'].removeprefix('dev-')} · {row['model_id']} · {row['precision']} · {row['delegate']}"


def ratio_forest(comparisons: pd.DataFrame, metric: str, out: Path) -> Path | None:
    """Forest plot: median ratio Flutter/Native with 95% bootstrap CI per configuration."""
    d = comparisons[comparisons["metric"] == metric].copy()
    if d.empty:
        return None
    _style()
    d = d.sort_values(["model_id", "precision", "delegate", "device_id"]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(IEEE_COL_IN, 0.22 * len(d) + 0.8))
    ypos = np.arange(len(d))[::-1]
    practical = d["practical"].astype(bool).to_numpy()
    for y, r, lo, hi, prac in zip(ypos, d["ratio"], d["ratio_lo"], d["ratio_hi"], practical):
        col = "#D55E00" if prac else "#555555"   # orange = practically significant
        ax.errorbar([r], [y], xerr=[[r - lo], [hi - r]], fmt="o", ms=3, color=col, elinewidth=1, capsize=2)
    ax.axvline(1.0, color="black", lw=0.8)
    ax.axvspan(0.95, 1.05, color="#DDDDDD", zorder=0, lw=0)
    ax.set_yticks(ypos, [_label(r) for _, r in d.iterrows()])
    ax.set_xlabel(f"Median {metric.removesuffix('_ms')} ratio (Flutter / Native)")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def stage_decomposition(summary: pd.DataFrame, out: Path) -> Path | None:
    """Stacked bars of median stage times per platform for each (model, precision, delegate) on each device."""
    s = summary[summary["metric"].isin(STAGES)]
    if s.empty:
        return None
    _style()
    piv = s.pivot_table(index=["device_id", "model_id", "precision", "delegate", "platform"],
                        columns="metric", values="median").reindex(columns=STAGES).fillna(0).reset_index()
    labels = [f"{r.model_id}·{r.precision}·{r.delegate}\n{r.platform.replace('_native', ' native')}"
              for r in piv.itertuples()]
    fig, ax = plt.subplots(figsize=(IEEE_DBL_IN, 2.4))
    bottom = np.zeros(len(piv))
    for stage, col in zip(STAGES, STAGE_COLORS):
        ax.bar(range(len(piv)), piv[stage], bottom=bottom, color=col, label=stage.removesuffix("_ms"))
        bottom += piv[stage].to_numpy()
    ax.set_xticks(range(len(piv)), labels, rotation=90)
    ax.set_ylabel("Median time (ms)")
    ax.legend(frameon=False, ncols=3)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def comparisons_table(comparisons: pd.DataFrame, metric: str, out: Path) -> Path | None:
    """LaTeX booktabs table for one metric (to \\input{} in the paper)."""
    d = comparisons[comparisons["metric"] == metric]
    if d.empty:
        return None
    lines = [r"\begin{tabular}{llllrrrrl}", r"\toprule",
             r"Device & Model & Prec. & Deleg. & Flutter & Native & Ratio [95\% CI] & $\delta$ & $p_{\mathrm{Holm}}$ \\",
             r"\midrule"]
    for r in d.sort_values(["device_id", "model_id", "precision", "delegate"]).itertuples():
        dev = r.device_id.removeprefix("dev-").replace("_", r"\_")
        model = r.model_id.replace("_", r"\_")
        p = "$<$0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"
        lines.append(f"{dev} & {model} & {r.precision} & {r.delegate} & {r.median_x:.2f} & {r.median_y:.2f} & "
                     f"{r.ratio:.2f} [{r.ratio_lo:.2f}, {r.ratio_hi:.2f}] & {r.delta:+.2f} & {p} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def make_all(summary: pd.DataFrame, comparisons: pd.DataFrame, figures_dir: Path, tables_dir: Path) -> list[Path]:
    produced: list[Path | None] = [
        ratio_forest(comparisons, "inference_ms", figures_dir / "rq1-inference-ratio.pdf"),
        ratio_forest(comparisons, "end_to_end_ms", figures_dir / "rq2-e2e-ratio.pdf"),
        stage_decomposition(summary, figures_dir / "rq2-stage-decomposition.pdf"),
        ratio_forest(comparisons, "pss_mb", figures_dir / "rq3-memory-ratio.pdf"),
        ratio_forest(comparisons, "cold_start_ms", figures_dir / "rq5-coldstart-ratio.pdf"),
        comparisons_table(comparisons, "inference_ms", tables_dir / "rq1-inference.tex"),
        comparisons_table(comparisons, "end_to_end_ms", tables_dir / "rq2-e2e.tex"),
    ]
    return [p for p in produced if p is not None]
