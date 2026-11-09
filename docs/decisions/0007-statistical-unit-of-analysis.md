# 0007 · Statistical unit of analysis for Flutter vs native tests

- **Status:** accepted (partly supersedes ADR-0005)
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** protocol v0.2.0 → v0.3.0, `analysis/benchkit/compare.py`, `docs/02-methodology.md` §7, paper §Methodology

## Context
`docs/02-methodology.md` §7 says tests use session-level medians to avoid pseudo-replication, then
names per-iteration Mann–Whitney U as the primary test. ADR-0005 and `compare.py` use the per-iteration
version. The two cannot both be primary.

- **Per-iteration test:** iterations in one session share thermal state, background load and DVFS
  behaviour, so they are not independent. With 500 values per platform, p-values become very small
  even for tiny session-to-session effects.
- **Session-level test:** valid unit, but the exact Mann–Whitney p-value has a floor of
  2 / C(2n, n), and Holm multiplies the smallest p by the family size.

Assuming 54 configurations (3 models × 2 precisions × 3 delegates × 3 devices), before removing
unsupported combinations:

| Sessions per platform (n) | Smallest two-sided p | Largest family it can pass (p × m < 0.05) |
|---|---|---|
| 5 (current) | 0.00794 | 6 |
| 6 | 0.00216 | 23 |
| 7 | 0.000583 | 85 |
| 8 | 0.000155 | 321 |

Family sizes: RQ1 = 54; RQ3 = 108 (2 metrics); RQ2 = 270 (5 metrics). At n = 5 no comparison can be
significant in any family. Even at n = 8, RQ2 can pass only with complete separation of the two
platforms: the next possible p (0.000311) × 270 = 0.084.

## Options considered
1. **Keep per-iteration MWU as primary** (status quo): no change and high power, but reviewers can
   reject it as pseudo-replication, and p-values overstate certainty.
2. **Session-level MWU, 5 sessions**: valid unit, but cannot reach significance after Holm (table above).
3. **Session-level MWU, 8 sessions, with effect size and CI as the primary evidence**: stays
   non-parametric and consistent with ADR-0005. Adds 3 sessions; cooldown alone adds about 108 min per
   device (36 configs × 60 s × 3). The practical-significance rule would rest on the ratio CI and
   effect size, with p-values reported as secondary.
4. **Welch t-test / CI on log session medians, 5 or 8 sessions**: no p-value floor and a direct CI for
   the ratio, but relies on approximate normality of a few session medians. Reverses the ADR-0005 preference.
5. **Mixed-effects model on log latency (session as random effect)**: uses all data correctly, but
   with few sessions the estimates are unstable and the method is harder to defend at this level.

## Decision
Option 3. The independent unit is the session, with 8 sessions per configuration.
- For each configuration and metric, the input is one median per session. Mann–Whitney U, Cliff's δ
  and the bootstrap ratio CI are all computed on those medians. Holm stays per RQ family.
- Cold-start metrics use each launch as the unit, because each launch is a separate process.
- "Practically significant" = |δ| ≥ 0.33 AND the ratio CI lies outside [0.95, 1.05]. The Holm-adjusted
  p-value is reported beside it but is not part of this rule.
- The iteration-level median ratio is kept as a descriptive column only.

## Consequences
- Collection takes longer: 3 more sessions per configuration, per device.
- With 8 sessions per platform, CIs are wide and a percentile bootstrap on so few values can be too
  narrow. Report them as they are and state this limit in the paper.
- Cliff's δ has coarse steps with 8 values per side. Interpret it together with the ratio.
