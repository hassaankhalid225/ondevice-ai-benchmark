# PROGRESS: Live Status

> **Update this file at the end of every working session.** It is the first thing the next
> person or agent reads. Keep "Next actions" concrete (a stranger should be able to start on it).

**Last updated:** 2026-11-11 · **Current phase:** Paper 1 Revised (10p IEEE, Zenodo DOI `10.5281/zenodo.24128933`, Ready for `exp-002`) · **Protocol:** v0.3.0

## Current focus
Campaign **EXP-001** ($N=8$ alternating sessions + $n=10$ baseline cold-launch/idle trials on `dev-infinix-x650c`), full statistical analysis (`benchkit` with multiplicative non-parametric TOST), complete **Paper Revision Checklist** across `paper/main.tex`, `paper/sections/*.tex`, and `literature/references.bib`, GitHub release **`v0.2.0-paper1`**, Zenodo archival DOI (**[`10.5281/zenodo.24128933`](https://doi.org/10.5281/zenodo.24128933)**), and ORCID linkage (**[`0009-0002-4289-2011`](https://orcid.org/0009-0002-4289-2011)**) are **complete**, with an exact **10-page IEEE conference PDF** (`paper/main.pdf`).

- **Device Evaluated:** `dev-infinix-x650c` (Infinix Hot 8 / `Infinix_X650C`, MediaTek Helio P22 MT6765, PowerVR GE8320, 3.7 GB RAM, Android 9 / API 28; runtime JSONL slug `dev-infinix-mobility-limited-infinix-x650c`).
- **Completed Dataset & Validation (`data/raw/dev-infinix-x650c/`):**
  - **283 raw JSONL files (100% PASS `benchkit validate`)**: Sessions 1–8 benchmark runs (`23,980` records) + 2 `app_baseline` JSONLs from 10 alternating cold launches (`40` records) = **24,020 raw records**.
  - **Exclusions (`data/exclusions.yaml`):** 7 Native runs (`840` records hitting MT6765/Android 9 `9223372036854776` ms clock-overflow sentinel) excluded during analysis while preserved immutable in `data/raw/`.
  - **Retained Records (`23,180`):** `19,200` `measure ok` (`11,200` Native, `8,000` Flutter), `3,840` `warmup ok` (`192` `model_load_ms` initializations), `40` `app_baseline` (`20 cold_start`, `20 idle`), `4` Session-1 early Native INT8 errors, and `96` `unsupported` delegate markers.
  - **Integrity Checks:** `500/500` comparable `(model, precision, delegate, input_index)` `output_digest` pairs match (100%); `timer_residual_ms` median = `0.0000 ms` (`max |r| = 0.0010 ms`); `thermal_status = none` across all kept records.
- **Root-Cause & Ecosystem Audit (ADR-0009):**
  - Audited release APKs (`123.83 MB` Flutter vs `65.63 MB` Native universal; `24.06 MB` vs `7.27 MB` `arm64-v8a` non-model footprint; `54.74 MB` identical `.tflite` models) and Pub/Gradle transitive bindings: traced CPU gains to `tflite_flutter 0.12.1` pulling LiteRT `1.4.0`/`2.20.0` + default single-thread `XNNPackDelegate(nullptr)` vs Maven TFLite `2.16.1` 4-thread contention, traced incremental memory (`1.25x–3.06x` over Native above idle) & CPU loading slowdowns (`3.74x–11.71x`) to `Model.fromBuffer()` unfreed `calloc<Uint8>` copies vs Native `mmap`, and updated `benchkit` to extract `warmup[0]` `model_load_ms` and `idle_pss_mb`.
- **Analysis & Paper Generation (`analysis/benchkit` + `paper/`):**
  - `data/processed/summary.csv`: **220 rows**; `data/processed/comparisons.csv`: **92 cross-platform comparisons** across RQ1, RQ2, RQ3, and RQ5 families (`n_F = 8`, `n_N \in \{5, 7, 8\}`, `n = 10` baseline launches).
  - Generated **6 vector PDFs** (`paper/figures/`) and **6 LaTeX tables** (`paper/tables/`), visually inspected for layout clarity.
  - Revised all paper sections (`00-abstract.tex` through `07-conclusion.tex`) per the Nov 11 Paper Revision Checklist: scoped Title/Option-B hardware framing, `<200`-word Abstract (`185` PDF words), protocol commit `dc45f62` wording, verified CrossRef/arXiv literature + 2023–2025 references (`31/31` cited), single Combined Research Gap, promoted `Runtime Packaging Differences`, math symbol mapping & Hypotheses table (`H1`–`H5`, `H3b` omitted), `8`-char SHA-256 table, exclusion audit flow table, horizontal hatched Fig. 2, non-parametric TOST (`3/4` GPU equivalence) & MWU `n=(8,5)` power analysis, `82%` MobileBERT FFI fix, exact per-precision bimodal Native CPU clusters, maintainer implications, thresholded practitioner matrix, and single-author bias threat; compiled exact **10-page IEEEtran PDF (`paper/main.pdf`)** with `0` leak tokens (`CLAUDE`/`ADR-`/`EXP-001`/`dev-infinix`/`TODO`), `0` Overfull boxes, clean visual PNG proof inspection, `ruff check` clean, and `23/23` `pytest` passing.

## Next actions (in order)
1. [x] Execute complete $N=8$ alternating campaign on `dev-infinix-x650c` + $n=10$ baseline cold-start/idle trials.
2. [x] Validate raw JSONLs (`283/283`), finalize exclusions (`840` sentinel records), and run `benchkit` pipeline (`summary.csv`, `comparisons.csv`, 6 figures, 6 tables).
3. [x] Audit APKs/dependencies and record ADR-0009; refine `benchkit` tests (`23/23` pass, `ruff` clean).
4. [x] Revise all paper sections (`paper/sections/*.tex`), `experiments/EXP-001.md`, `docs/`, and `CHANGELOG.md` to final verified EXP-001 numbers (`0` `\todo{}`).
5. [x] Compile `paper/main.tex` to PDF (`paper/main.pdf`, 10 pages) and visually verify all rendered proof pages (0 errors, 0 Overfull boxes, 31/31 refs resolved, 0 leak hits; Overleaf `pdflatex` path also remains supported).
6. [ ] Perform final author read-through of `paper/main.pdf`, confirm university department supervisor/template rules, and verify arXiv `cs.SE` / `cs.LG` endorsement status before Phase 7 arXiv/conference submission.
7. [ ] Begin `EXP-002` planning and hardware onboarding: connect **Infinix Smart 7** via ADB (`adb shell getprop` + `/proc/meminfo`) to verify SoC/API level and `BATTERY_PROPERTY_CHARGE_COUNTER` support before registering `docs/04-device-matrix.md`, implement unplugged `energy` and 5-minute `sustained` FPS runner loops plus matched-LiteRT control (`ADR-0010`), and add mid-range / flagship Android devices as available.

## Phase checklist
- [x] Phase 0 · Setup (2026-11-09)
- [x] Phase 1 · Literature (2026-11-09; 25 verified references, 6 reading notes)
- [x] Phase 2 · Harness apps: Flutter & Android Native (2026-11-09)
- [ ] Phase 2b · iOS app (optional / deferred)
- [x] Phase 3 · EXP-001 Entry-Tier Campaign on `dev-infinix-x650c` ($N=8$ + baseline, 2026-11-10)
- [ ] Phase 4 · Multi-tier, unplugged energy, and 5-min sustained expansion (`EXP-002+`)
- [x] Phase 5 · Analysis (`benchkit`: `summary.csv`, `comparisons.csv`, 6 PDF figures, 6 LaTeX tables)
- [x] Phase 6 · Writing (All 8 `paper/sections/*.tex` drafted & empirically revised; 0 `\todo{}`)
- [ ] Phase 7 · Release (Overleaf PDF proof + author review + arXiv preprint & conference submission)

## Paper section status
| Section | File | Status | Reviewed |
|---|---|---|---|
| Abstract | `paper/sections/00-abstract.tex` | complete (EXP-001 $N=8$ verified) | – |
| Introduction | `paper/sections/01-introduction.tex` | complete (scope aligned to EXP-001) | – |
| Related work | `paper/sections/02-related-work.tex` | complete (25 verified refs) | – |
| Methodology | `paper/sections/03-methodology.tex` | complete (ADR-0009, hygiene & stats updated) | – |
| Results | `paper/sections/04-results.tex` | complete (RQ1–RQ5 tables/figs, APK disassembly, RQ4 analysis) | – |
| Discussion | `paper/sections/05-discussion.tex` | complete (`fromBuffer`/XNNPACK fixes + decision matrix) | – |
| Threats to validity | `paper/sections/06-threats.tex` | complete (drift, glitches, USB scope, MWU power) | – |
| Conclusion | `paper/sections/07-conclusion.tex` | complete (RQ1–RQ5 answers + `EXP-002+` roadmap) | – |

## Open questions / blockers
- Does the university's mandatory research paper need a faculty supervisor assigned? **confirm with department**
- Does the first arXiv submission need an endorsement? **check arXiv `cs.LG` / `cs.SE` requirements**
- Does the department require a specific paper template vs.\ IEEEtran? **confirm with department**

## Data collected
- Device: `dev-infinix-x650c` (MediaTek Helio P22 MT6765, PowerVR GE8320, Android 9 / API 28)
- Total files: **283 raw JSONL files** in `data/raw/dev-infinix-x650c/` (**100% pass `benchkit validate`**)
- Raw records: **24,020** (`840` excluded via `data/exclusions.yaml` → **23,180 kept** = `19,200` `measure ok`, `3,840` `warmup ok`, `40` `app_baseline`, `4` s01 `error`, `96` `unsupported`)
- Processed: `data/processed/summary.csv` (**220 metric summary rows**)
- Comparisons: `data/processed/comparisons.csv` (**92 statistical comparison rows**)
