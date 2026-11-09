# 0005 · Non-parametric statistics with effect sizes and bootstrap CIs

- **Status:** partly superseded by 0007 (unit of analysis, practical-significance rule); the tests and effect sizes still apply
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** analysis, paper §Methodology/§Results

## Context
Mobile latency distributions are right-skewed, multi-modal (big.LITTLE cores, DVFS) and contain
outliers (GC, interrupts). Mean ± SD and t-tests are inappropriate. Benchmarking literature
increasingly asks for effect sizes and confidence intervals rather than bare p-values.

## Decision
- Summaries: median, p5, p95, IQR.
- Test: two-sided Mann–Whitney U per configuration; Holm–Bonferroni per RQ family; α = 0.05.
- Effect size: Cliff's δ (|δ| < 0.147 negligible, < 0.33 small, < 0.474 medium, else large)
  and median ratio Flutter/Native with percentile bootstrap 95 % CI (10,000 resamples, seed 42).
- Robustness: repeat main comparison on session-level medians.

## Consequences
- Implemented once in `analysis/benchkit/stats.py` with unit tests; the paper cites the method.
- Changing any of this requires a new ADR.
