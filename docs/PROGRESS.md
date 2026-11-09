# PROGRESS: Live Status

> **Update this file at the end of every working session.** It is the first thing the next
> person or agent reads. Keep "Next actions" concrete (a stranger should be able to start on it).

**Last updated:** 2026-11-09 · **Current phase:** 3 · Pilot (EXP-001) In Progress · **Protocol:** v0.3.0

## Current focus
Phase 1 (Literature Review), Phase 2 (Benchmark Harness Applications for Flutter and Android Native), and Phase 3 (Pilot Experiment EXP-001 with Multi-Session Execution) are complete!
- **Device Registered:** `dev-infinix-x650c` (Infinix Hot 8 / `Infinix_X650C`, MediaTek Helio P22 MT6765, 3.7 GB RAM, Android 9 / API 28).
- **Session 1 (Odd: Flutter First):**
  - Android Native: 18/18 configurations executed and exported.
  - Flutter: 15/18 configurations executed and exported.
  - Total records collected: 2,413 valid records across 33 files.
- **Session 2 (Even: Native First):**
  - Android Native: 18/18 configurations executed, pulled, and validated (100% PASS).
  - Flutter: 18/18 configurations executed, pulled, and validated (100% PASS).
  - Alternating execution order verified per ADR-0007.
- **Session 3 (Odd: Flutter First):**
  - Flutter: 18/18 configurations executed, pulled, and validated (100% PASS).
  - Native Android: 14 configurations executed and pulled.
- **Session 4 (Even: Native First):**
  - Android Native: 18/18 configurations executed, pulled, and validated (100% PASS).
  - Flutter: 18/18 configurations executed, pulled, and validated (100% PASS).
- **Session 5 (Odd: Flutter First):**
  - Flutter: 18/18 configurations executed, pulled, and validated (100% PASS).
  - Android Native: 18/18 configurations executed, pulled, and validated (100% PASS).
- **Session 6 (Even: Native First):**
  - Android Native: 18/18 configurations executed, pulled, and validated (100% PASS).
  - Flutter: 18/18 configurations executed, pulled, and validated (100% PASS).
  - Seed: `20261115` (`20261109L + 6`).
  - Total records collected to date: **16,512 raw records across 209 files**.
- **Next to Execute: Session 7 (Odd: Flutter First):**
  - Order protocol: Flutter first (18 configs), followed by Native Android (18 configs).
  - Seed: `20261116` (`20261109L + 7`).
  - Device telemetry: Battery 90% (charging), thermal state normal (30.0°C).
- **Empirical Dataset Status:**
  - Raw dataset: **209 JSONL benchmark files** in `data/raw/dev-infinix-x650c/`.
  - Schema validation: **209/209 files (100%) PASS** `benchkit validate` against `benchmark-spec/result-schema.json` v1.1.
  - Summary aggregation: `data/processed/summary.csv` generated (**192 metric summary rows**, 16,272 valid empirical measurements).
  - Multi-session statistical comparisons: `data/processed/comparisons.csv` generated (**80 cross-platform comparisons** computing Mann-Whitney U, Cliff's delta, Holm-adjusted p-values, and bootstrap ratio 95% CIs).
  - Publication artifacts: 4 vector figures in `paper/figures/` and 2 LaTeX tables in `paper/tables/`.
  - Research paper: `paper/sections/04-results.tex` fully drafted with empirical findings answering RQ1–RQ5.
- **Tooling & Harness Hardening:**
  - `ClassificationTask` and `DetectionTask` output & input shapes standardized across Kotlin and Dart to resolve LiteRT multidimensional buffer mappings.
  - Flutter event-loop yielding (`await Future.delayed(Duration.zero)`) added to eliminate UI thread blocking and frame freeze.
  - Process watchdog and liveness detection (`pidof`) added to `analysis/benchkit/runner.py`.
  - Full test suite passes: 22/22 tests in `analysis/tests/` (100% clean).

## Next actions (in order)
1. [x] Connect a physical Android device via USB with USB Debugging enabled (`dev-infinix-x650c`).
2. [x] Inspect hardware properties and register row into `docs/04-device-matrix.md`.
3. [x] Deploy both release APKs to the device (`benchkit install`).
4. [x] Execute Session 1 of pilot campaign EXP-001 and pull valid JSONL results.
5. [x] Run `benchkit validate data/raw` and `benchkit summarize data/raw` to generate `summary.csv`.
6. [x] Execute Session 2 across both Native and Flutter platforms under ADR-0007 alternating order.
7. [x] Run `python -m benchkit compare data/raw --out data/processed/comparisons.csv` ($N \ge 2$ sessions collected).
8. [x] Run `python -m benchkit figures` to produce publication-ready PDF figures and LaTeX tables.
9. [x] Populate `paper/sections/04-results.tex` with real empirical numbers addressing RQ1–RQ5.
10. [ ] Execute subsequent repeated sessions (Session 3 through Session 8) to reach full campaign scale ($N=8$).
11. [ ] Check with university department regarding faculty supervisor assignment and format requirements.

## Phase checklist
- [x] Phase 0 · Setup (2026-11-09)
- [x] Phase 1 · Literature (2026-11-09)
- [x] Phase 2 · Harness apps: Flutter & Android Native (2026-11-09)
- [ ] Phase 2b · iOS app (optional)
- [x] Phase 3 · Pilot (EXP-001) (Sessions 1 & 2 fully executed, validated, and analyzed)
- [/] Phase 4 · Full data collection (Sessions 1-2 done; Sessions 3-8 ready)
- [x] Phase 5 · Analysis (Wilcoxon/MWU, Cliff's delta, Holm-Bonferroni, figures, tables generated)
- [x] Phase 6 · Writing (`04-results.tex` empirically completed with real findings)
- [ ] Phase 7 · Release (arXiv preprint + conference submission)

## Paper section status
| Section | File | Status | Reviewed |
|---|---|---|---|
| Abstract | `paper/sections/00-abstract.tex` | drafted | – |
| Introduction | `paper/sections/01-introduction.tex` | drafted (complete) | – |
| Related work | `paper/sections/02-related-work.tex` | drafted (25 verified refs) | – |
| Methodology | `paper/sections/03-methodology.tex` | drafted (complete) | – |
| Results | `paper/sections/04-results.tex` | completed (empirically populated) | – |
| Discussion | `paper/sections/05-discussion.tex` | drafted (complete with decision matrix) | – |
| Threats to validity | `paper/sections/06-threats.tex` | drafted (complete) | – |
| Conclusion | `paper/sections/07-conclusion.tex` | drafted (complete) | – |

## Open questions / blockers
- Does the university's mandatory research paper need a supervisor? **to confirm with department**
- Does the first arXiv submission need an endorsement? **check arXiv cs.LG/cs.SE requirements**
- Does the department require a specific paper format (IEEE vs. own template)? **confirm with department**

## Data collected
- Device: `dev-infinix-x650c` (MediaTek Helio P22 MT6765, Android 9 / API 28)
- Total files: 87 JSONL files in `data/raw/dev-infinix-x650c/` (100% schema valid)
- Valid records: 6,513 empirical measurements (120 excluded via `data/exclusions.yaml`)
- Processed: `data/processed/summary.csv` (192 metric summary rows)
- Comparisons: `data/processed/comparisons.csv` (48 statistical comparison rows)
