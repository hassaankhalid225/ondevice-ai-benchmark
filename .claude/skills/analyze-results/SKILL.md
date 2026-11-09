---
name: analyze-results
description: Validate raw benchmark data, compute summaries and statistical comparisons, and generate paper figures/tables with the benchkit pipeline. Use for any analysis, statistics, plotting or results interpretation.
---

# Analyze Results

## Pipeline (always in this order)
```bash
make validate     # python -m benchkit validate data/raw
make summarize    # → data/processed/summary.csv
make compare      # → data/processed/comparisons.csv
make figures      # → paper/figures/*.pdf, paper/tables/*.tex
```
Code: `analysis/benchkit/` (`io.py` load+exclusions, `validate.py`, `stats.py`, `summarize.py`,
`compare.py`, `figures.py`, `cli.py`). Tests: `analysis/tests/`, run with `make test`.

## Statistical rules (ADR-0005, ADR-0007; do not change without a new ADR)
- Use `phase == "measure"` and `status == "ok"` only for latency stats; cold start from `phase == "cold_start"`.
- Summaries: median, p5, p95, IQR (never mean ± SD alone).
- Comparison per config (device × model × precision × delegate × metric), using one median per
  session (each launch for cold start): Mann–Whitney U two-sided → Holm within RQ family →
  Cliff's δ → median ratio Flutter/Native with bootstrap 95 % CI (10k resamples, seed 42).
- "Practically significant" = |δ| ≥ 0.33 AND ratio CI outside [0.95, 1.05]. Report p beside it.
- The iteration-level ratio is descriptive only.

## Adding a new analysis
1. Write a pure function in `benchkit/` with a docstring.
2. Add a unit test with a small synthetic fixture (mark `synthetic: true`).
3. Expose via CLI and Makefile target if it produces a paper artifact.
4. Figures: vector PDF, IEEE column width (3.5 in) or double (7.16 in), font ≥ 8 pt,
   colour-blind-safe palette, units on axes, generated only by code.

## Interpreting
- Report the effect and its uncertainty first, p-value second.
- A non-significant inference gap with a significant end-to-end gap is the expected story
  (H1 vs H2). Explain it with stage decomposition, not speculation.
- Write findings as bullet notes in `docs/PROGRESS.md` before turning them into prose.

## Never
- Never type numbers into the paper by hand. Use generated tables or `\input{}` macros from
  `paper/tables/`.
- Never run analysis on synthetic fixtures and present it as results.
