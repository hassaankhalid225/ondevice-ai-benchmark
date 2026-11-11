# Changelog

Format: newest first. One entry per working session. Describe *what* changed and *why*.
Categories: Added / Changed / Fixed / Data / Paper / Decisions.

## 2026-11-11: Paper 1 Revision Checklist Complete (10-Page IEEE PDF, TOST Equivalence, 31 Verified Refs)

### Paper & Literature
- Executed full **Paper Revision Checklist** across `paper/main.tex`, `paper/sections/00-07.tex`, and `paper/one-pager.md`:
  - **Priority 0:** Removed internal `"CLAUDE integrity rules"`, all `ADR-*`, `EXP-001`, `dev-infinix-x650c`, `\todo`, and `"pre-registered"` tokens (`0` hits across `.tex`); fixed MobileBERT-QA FP32 GPU phrasing (`82% of the +4.90 ms end-to-end gap`), fixed `"audibly excluded"` $\to$ `"auditably excluded"`, and fixed bimodal Native MobileNetV3 CPU numbers per precision from raw session data (`92.4–129.7 ms` vs. `232.4–358.0 ms` FP32; `71.0–77.8 ms` vs. `341.7–346.5 ms` INT8).
  - **Priority 1:** Scoped Title, Abstract, RQs (`RQ3`/`RQ4` aligned to delivered metrics), and Conclusions to single entry-tier Option B hardware (`Infinix Hot 8, Helio P22, Android 9`) with repo-versioned protocol commit `dc45f62`; formally defined Hypotheses Table (`H1`, `H2`, `H3a`, `H4`, `H5`); added non-parametric multiplicative TOST (`3/4` GPU configs strictly equivalent $p_{\mathrm{TOST}} \le 0.041$; `EfficientDet-Lite0 INT8 GPU` inconclusive at $p_{\mathrm{TOST}} = 0.177, n_N=5$) and exact MWU $(8,5)$ power floor ($p_{\min}=0.001554$).
  - **Priority 2:** Trimmed Abstract to `185` words; cited Stack Overflow 2024 survey + Flutter Impeller docs; unified 4 Research Gap blocks into 1 Combined Research Gap; defined symbolic metrics + mapping table, 8-char SHA-256 model table, exclusion flow table, and promoted `Runtime Packaging Differences`; converted Fig. 2 to horizontal grayscale-hatched bars and dropped redundant single-device table columns; added maintainer implications, concrete decision thresholds, and single-author bias threat; compressed paper cleanly from `13` to **`10` IEEEtran pages** including references.
  - **Priority 3:** Audited every bibliography entry against CrossRef DOIs and original PDFs (`arXiv:2109.13963`, `arXiv:2202.06512`, `arXiv:1812.05448`); repaired DOIs/venues/pages (`willocx2016comparing` $\to$ MOBILESoft 2016, `delia2015multi` $\to$ RCIS 2015, `biornhansen2019survey` $\to$ `10.1145/3241739`, `banbury2020benchmarking`, `almeida2021smart`, `zhang2022comprehensive`) and reading notes; added verified 2023–2025 references (`horn2023native`, `nanavati2024critical`, `murthy2024mobileaibench`, `wang2025lmmeter`, `stackoverflow2024survey`, `flutterimpeller2025`; `31/31` cited).

### Changed
- `analysis/benchkit/`: added non-parametric `tost_p()` (`stats.py`) and `equivalent` column (`compare.py`); updated `figures.py` to render horizontal grayscale-hatched `rq2-stage-decomposition.pdf` with readable legend labels, mark TOST vs. inconclusive vs. practical points on ratio forest plots, and omit constant single-device columns in LaTeX tables; updated `test_pipeline.py` (`23/23` tests pass, `ruff check` clean).

## 2026-11-11: Repository Release Metadata & EXP-002 Transition (`v0.1.0-exp001`)

### Fixed
- Fixed GitHub repository URLs from `github.com/hassaankhalid/...` to `github.com/hassaankhalid225/ondevice-ai-benchmark` across `benchmark-spec/result-schema.json`, `paper/sections/07-conclusion.tex`, `paper/one-pager.md`, and `CITATION.cff` (`date-released: 2026-11-11`), and recompiled/verified `paper/main.pdf` (13 pages, page 13 URL layout verified).

### Changed
- Updated `README.md` status summary for release `v0.1.0-exp001` and queued `EXP-002` device onboarding (`Infinix Smart 7` ADB inspection, unplugged `energy` + 5-min `sustained` loops, and matched-LiteRT control) in `docs/PROGRESS.md`.

## 2026-11-10: EXP-001 Completion (Session 8, Baseline Launch/Idle Dataset, ADR-0009, Full $N=8$ Paper Revision)

### Decisions
- ADR-0009 (accepted): Documented LiteRT `2.20.0` (`tflite_flutter 0.12.1` / `litert 1.4.0`) vs `2.16.1` (`tensorflow-lite:2.16.1`) binary/XNNPACK drift, `Model.fromBuffer()` unfreed `calloc<Uint8>` asset copies vs Native `FileChannel.map`, Android 9 API 28 NNAPI restrictions, `data/exclusions.yaml` clock-overflow filtering, MiB vs SI decimal MB conventions, `warmup[0]` `model_load_ms` extraction, and runtime `device_id` display normalization.

### Data
- Completed Session 8 (36 JSONLs, even order: Native first, seed `20261117`, 2,892 records, 100% clean) on `dev-infinix-x650c`.
- Collected 10 alternating cold-launch (`am start -W TotalTime` / `WaitTime`) and settled idle PSS (`dumpsys meminfo TOTAL`) baseline trials per release APK, exported to 2 schema-valid `app_baseline` JSONLs (`20261110_*_app_baseline_fp32_cpu_s01.jsonl`, 40 records).
- Reached complete EXP-001 scale: **283/283 valid raw JSONL files**, **24,020 raw records** (`840` excluded across 7 Native sentinel-overflow runs via `data/exclusions.yaml` → **23,180 kept records** including `19,200` `measure ok`, `3,840` `warmup ok`, and `40` `app_baseline`), `500/500` (`100%`) `output_digest` parity, and `thermal_status = none` throughout.

### Changed
- `analysis/benchkit/`: added `idle_pss_mb` (`RQ3`) and tuple `phase` (`("cold_start", "warmup")`) support for `model_load_ms`; enabled per-launch `cold_start`/`idle` comparisons; improved forest-plot single-device labeling, error-bar lower clamping, and stage decomposition legend spacing; added `baseline_table()` (`paper/tables/rq5-baseline.tex`); refined exception handling in `runner.py` for clean `ruff` compliance; added unit test `test_warmup_model_load_idle_and_device_label` (23/23 tests pass).
- Regenerated processed datasets and artifacts: `data/processed/summary.csv` (220 rows), `data/processed/comparisons.csv` (92 rows), 6 PDFs in `paper/figures/` (`rq1-inference-ratio`, `rq2-e2e-ratio`, `rq2-stage-decomposition`, `rq3-memory-ratio`, `rq5-coldstart-ratio`, `rq5-modelload-ratio`), and 6 LaTeX tables in `paper/tables/`.

### Paper & Docs
- Revised `paper/sections/00-abstract.tex`, `01-introduction.tex`, `03-methodology.tex`, `04-results.tex`, `05-discussion.tex`, `06-threats.tex`, and `07-conclusion.tex` to exact EXP-001 $N=8$ + baseline numbers, replaced raw backticks with `\texttt{}`, fixed table environments and wide-table scaling, eliminated all `\todo{}` markers, integrated exact APK `arm64-v8a` vs universal disassembly and RQ4 correlation/shader break-even analyses, and aligned scope honestly to `dev-infinix-x650c`.
- Compiled the final 13-page IEEE PDF (`paper/main.pdf`) via portable Tectonic (`XeTeX`) and visually verified every rendered page; added cross-engine `iftex`/`TeX Gyre` font configuration plus `array`/`xurl`/`microtype` to `paper/main.tex`, fixed Equation (2) column overflow in `03-methodology.tex`, resolved math-mode `\times`/comma spacing and `List<List<double>{}>` ligatures across sections, and ragged-right aligned Table X columns in `05-discussion.tex` (0 compile errors, 0 Overfull boxes, 25/25 citations resolved).
- Added executive research portfolio summary in `paper/one-pager.md` referencing key EXP-001 findings and figures.
- Updated `docs/03-metrics.md`, `docs/04-device-matrix.md`, `experiments/EXP-001.md`, `docs/PROGRESS.md`, and `README.md`.

### Fixed
- `paper/sections/04-results.tex`: repaired duplicated `\end{tabular}\end{table}` block and inaccurate earlier parity/incremental-RAM claims.
- `data/exclusions.yaml`: completed exclusion entries for Sessions 4–7 sentinel-overflow runs (totaling 7 runs / 840 records).

## 2026-11-10: Campaign Expansion through Session 7 (245 Raw Files, 21,088 Records Collected, Schema Validated)

### Added
- Session 7 Execution: executed, pulled, and validated all 36 configurations for Session 7 (odd order: Flutter first) on physical device `dev-infinix-x650c` under protocol v0.3.0 and ADR-0007.
- Dataset Scale: expanded raw empirical dataset from 209 to **245 raw JSONL files** in `data/raw/dev-infinix-x650c/` containing **21,088 total measurement records** (20,848 valid empirical records after excluding 240 hardware clock overflow records in `data/exclusions.yaml`).
- Schema Parity: **245/245 raw benchmark files (100% PASS)** verified against `benchmark-spec/result-schema.json` v1.1.
- Statistical Pipeline Re-Run: generated updated `data/processed/summary.csv` (192 rows) and `data/processed/comparisons.csv` (80 cross-platform comparisons with 10,000-resample bootstrap 95% CIs and Holm-Bonferroni adjusted p-values).
- Vector Publication Figures & Tables: regenerated all 4 publication PDF figures in `paper/figures/` and LaTeX tables in `paper/tables/`.

### Changed
- `docs/PROGRESS.md`: updated with live status through Session 7 and queued final Session 8.
- `experiments/EXP-001.md`: updated campaign logs with Session 7 completion and telemetry metrics.

## 2026-11-10: Campaign Expansion through Session 6 (209 Raw Files, 16,512 Records Collected, Schema Validated)

### Added
- Session 6 Execution: executed, pulled, and validated all 36 configurations for Session 6 (even order: Native first) on physical device `dev-infinix-x650c` under protocol v0.3.0 and ADR-0007.
- Dataset Scale: expanded raw empirical dataset from 173 to **209 raw JSONL files** in `data/raw/dev-infinix-x650c/` containing **16,512 total measurement records** (16,272 valid empirical records after excluding 240 hardware clock overflow records in `data/exclusions.yaml`).
- Schema Parity: **209/209 raw benchmark files (100% PASS)** verified against `benchmark-spec/result-schema.json` v1.1.
- Statistical Pipeline Re-Run: generated updated `data/processed/summary.csv` (192 rows) and `data/processed/comparisons.csv` (80 cross-platform comparisons with 10,000-resample bootstrap 95% CIs and Holm-Bonferroni adjusted p-values).
- Vector Publication Figures & Tables: regenerated all 4 publication PDF figures in `paper/figures/` and LaTeX tables in `paper/tables/`.

### Changed
- `docs/PROGRESS.md`: updated with live status through Session 6 and queued Session 7.
- `experiments/EXP-001.md`: updated campaign logs with Session 6 completion and telemetry metrics.

## 2026-11-10: Campaign Expansion through Session 5 (173 Raw Files, 13,620 Records Collected, Schema Validated)

### Added
- Session 4 & Session 5 Execution: executed, pulled, and validated all configurations for Session 4 (even order: Native first) and Session 5 (odd order: Flutter first) on physical device `dev-infinix-x650c` under protocol v0.3.0 and ADR-0007.
- Dataset Scale: expanded raw empirical dataset from 87 to **173 raw JSONL files** in `data/raw/dev-infinix-x650c/` containing **13,620 total measurement records** (13,380 valid empirical records after excluding 240 hardware clock overflow records in `data/exclusions.yaml`).
- Schema Parity: **173/173 raw benchmark files (100% PASS)** verified against `benchmark-spec/result-schema.json` v1.1.
- Statistical Pipeline Re-Run: generated updated `data/processed/summary.csv` (192 rows) and `data/processed/comparisons.csv` (80 cross-platform comparisons with 10,000-resample bootstrap 95% CIs and Holm-Bonferroni adjusted p-values).
- Vector Publication Figures & Tables: regenerated all 4 publication PDF figures in `paper/figures/` and LaTeX tables in `paper/tables/`.

### Changed
- `docs/PROGRESS.md`: updated with live status through Session 5 and queued Session 6.
- `experiments/EXP-001.md`: updated campaign logs with Session 4 and 5 completions and telemetry metrics.

## 2026-11-09: Multi-Session Benchmark Campaign (Session 3 Flutter Integration & Dataset Expansion to 6,513 Records)

### Added
- Session 3 Flutter Suite Completion: executed, pulled, and verified all 18 configurations of Flutter for Session 3 on `dev-infinix-x650c` under protocol v0.3.0 and ADR-0007 (odd session order: Flutter first).
- Empirical Dataset Expansion: dataset expanded from 5,305 records (69 files) to **6,513 valid empirical records** across **87 raw JSONL files** in `data/raw/dev-infinix-x650c/`.
- Schema Validation Parity: all 87 raw files (100%) pass strict validation against `benchmark-spec/result-schema.json` v1.1.
- Re-computed Statistical Comparisons (`data/processed/comparisons.csv`): updated 48 cross-platform comparisons with Session 3 Flutter medians; confirmed GPU pure inference parity with Cliff's $\delta = +0.00$ on all models.
- Re-generated Publication Artifacts: re-rendered all 4 publication PDF figures in `paper/figures/` and updated LaTeX tables in `paper/tables/`.

### Changed
- `docs/PROGRESS.md`: updated live tracking for Session 3 execution and empirical dataset metrics (87 files, 6,513 records).
- `experiments/EXP-001.md`: documented Session 3 Flutter execution and updated analysis pipeline logs.

## 2026-11-09: Physical Hardware Connection, Session 1 Execution, Harness Hardening, and Real Empirical Dataset

### Added
- Physical Device Registration: registered `dev-infinix-x650c` (Infinix Hot 8 / `Infinix_X650C`, MediaTek MT6765 Helio P22 octa-core, 3.7 GB RAM, Android 9 / API 28) in `docs/04-device-matrix.md` under `tier: low`.
- First Real Empirical Dataset (`data/raw/dev-infinix-x650c/`): extracted 33 raw JSONL benchmark files from real on-device execution (18 Native Android + 15 Flutter), totaling 2,413 validated measurement records.
- First Processed Summary Dataset (`data/processed/summary.csv`): generated 160 metric summary rows computing medians, IQR, and percentiles across latency, memory PSS, and CPU metrics.
- Parity Validation: verified identical output digest (`qa:5-5`) across Flutter and Native Android for MobileBERT QA on prompt 0.

### Fixed
- Multidimensional LiteRT Tensor Mapping:
  - `ClassificationTask` (Kotlin): fixed INT8 output buffer shape from 1D `ByteArray(1001)` to 2D `Array(1) { ByteArray(1001) }` to match LiteRT tensor output shape `[1, 1001]`.
  - `DetectionTask` (Kotlin & Dart): fixed input buffer allocation to always use 4 bytes per channel (`Float32`) for both FP32 and INT8 EfficientDet-Lite0 models, matching the flatbuffer model's float input tensor `serving_default_input_tensor:0` (1,228,800 bytes).
  - `DetectionTask` & `ClassificationTask` (Dart): replaced typed `Float32List` nested outputs with standard `List.filled(..., 0.0)` to eliminate Dart runtime cast exception (`List<double> is not a subtype of Float32List`).
- Flutter UI Thread Freezing: inserted event-loop microtick yields (`await Future.delayed(Duration.zero)`) between warmup and measure iterations in `BenchmarkRunner`, allowing the Flutter rendering engine to pump frames and preventing Android window manager ANR / blank screen issues.
- Result Schema v1.1 Alignment: updated both Kotlin and Dart exporters to emit `threads` (replacing legacy `cpu_threads`), populate `model_sha256`, and supply fallback `iteration: 0, input_index: 0` for error records.
- Process Watchdog & Auto-Exit: added process liveness polling (`pidof`) and idle timeout safety to `analysis/benchkit/runner.py`, preventing runner deadlocks if an app terminates or completes headless autorun.

### Changed
- `experiments/EXP-001.md`: updated with device specifications, empirical observations, and preliminary findings from Session 1.
- `docs/PROGRESS.md`: marked Session 1 complete and registered transition to multi-session execution.

## 2026-11-09: End-to-End Build Verification, Release APK Assembly, and ADB Automation Tooling

### Added
- Android Native Release Build: successfully compiled, minified, and verified release APK `apps/android_native_bench/app/build/outputs/apk/release/app-release.apk` (65.6 MB) via Gradle 8.14 and R8 shrinker.
- Flutter Release Build: successfully compiled Ahead-Of-Time release APK `apps/flutter_bench/build/app/outputs/flutter-apk/app-release.apk` (118.2 MB) via AGP 8.6.0, Compile SDK 36, NDK 28.2.13676358, and Gradle 8.14.
- Experiment Orchestrator (`analysis/benchkit/runner.py`): automated ADB-based runner supporting device hardware inspection, battery/thermal pre-flight checks, APK deployment, alternating cross-platform execution (odd sessions Flutter first, even sessions Native first), live logcat streaming, automated pull of raw JSONL results, and post-run schema validation.
- CLI & Automation targets: exposed `benchkit devices`, `benchkit check`, `benchkit install`, and `benchkit run` via `python -m benchkit` and `Makefile`.
- Runner Unit Tests (`analysis/tests/test_runner.py`): expanded test suite to 21 unit tests (all passing cleanly, 100% ruff-compliant).
- Pilot Campaign Specification (`experiments/EXP-001.md`): authored detailed execution log template ready for physical device run.

### Changed
- `apps/flutter_bench/pubspec.yaml`: upgraded `tflite_flutter` to `0.12.1` to maintain compatibility with Dart 3.12 typed data views without deprecation errors.
- `apps/android_native_bench/app/build.gradle.kts`: added `org.tensorflow:tensorflow-lite-gpu-api:2.16.1` to provide `GpuDelegateFactory.Options` for GPU delegate instantiation; migrated deprecated `aaptOptions` to modern `androidResources`.
- ADR-0008: updated toolchain pinning record to document `tflite_flutter 0.12.1`, AGP 8.6.0, and Gradle 8.14.

### Fixed
- Flutter Android resource linking: added Android styles (`LaunchTheme`, `NormalTheme`) in `res/values/styles.xml` and referenced standard app icon, resolving AAPT resource compilation errors during `assembleRelease`.
- Kotlin Gradle Plugin JVM-target compatibility: configured `kotlin.jvm.target.validation.mode=warning` in Flutter `gradle.properties` to reconcile plugin target differences under JDK 21.



## 2026-11-09: Complete Literature Review, Model Exporter, Harness Apps, and Academic Paper Draft

### Decisions
- ADR-0008 (accepted): Pin exact toolchain and dependency versions across Flutter (SDK 3.44.5, Dart 3.12.2, `tflite_flutter` 0.10.4, `image` 4.3.0) and Android Native (AGP 8.3.2, Kotlin 1.9.24, LiteRT 2.16.1 with GPU & NNAPI delegates).

### Added
- Literature review: verified all 13 seed references with authoritative DOIs and publisher metadata; expanded bibliography to 25 verified references in `literature/references.bib`.
- Literature notes: authored comprehensive reading notes for 6 core papers in `literature/notes/` (`zhang2022comprehensive`, `biornhansen2020empirical`, `xu2019first`, `almeida2021smart`, `reddi2022mlperfmobile`, `ciman2017empirical`).
- Dataset generator: `models/scripts/generate_shared_inputs.py` generating 50 standardized vision test JPEGs (`assets/inputs/vision/`) and 50 SQuAD QA test prompts (`assets/inputs/text.jsonl`).
- Model exporter: `models/scripts/export_benchmark_models.py` generating all 6 LiteRT flatbuffer models (MobileNetV3-Large, EfficientDet-Lite0, MobileBERT-QA in FP32 & INT8 post-training quantization).
- Model synchronization: `models/scripts/sync_assets_to_apps.py` deploying shared inputs and models into both harness app asset directories.
- Android Native Harness: complete Kotlin application in `apps/android_native_bench/` implementing `harness-contract.md` with modular architecture (`config`, `export`, `harness`, `metrics`, `tasks`, `ui`), model SHA-256 validation, timing boundaries, and headless ADB Intent autorun.
- Flutter Harness: complete Flutter application in `apps/flutter_bench/` implementing `harness-contract.md` with zero `flutter analyze` lint issues, pure Dart preprocessing, platform channels for PSS/CPU/thermal sampling, and headless autorun.
- Paper drafting: authored publication-grade IEEE conference paper sections in `paper/sections/` (`00-abstract.tex`, `01-introduction.tex`, `02-related-work.tex`, `03-methodology.tex`, `04-results.tex`, `05-discussion.tex`, `06-threats.tex`, `07-conclusion.tex`), featuring a practitioner decision matrix table and full research question alignment.

### Fixed
- Pinned delegate compatibility in Flutter `tflite_flutter` harness: mapped XNNPACK CPU delegate and GpuDelegateV2, gracefully reporting unsupported NNAPI bindings per contract specifications.
- Cleaned unused imports across Dart codebases, achieving 100% clean `flutter analyze`.

### Changed
- `models/manifest.yaml`: updated with verified SHA-256 digests, file sizes, licenses, and official sources.
- `docs/PROGRESS.md`: marked Phase 1 and Phase 2 complete; transitioned current phase to Phase 3 (Pilot EXP-001).


## 2026-11-09: Session-level statistics; project is independent

### Decisions
- ADR-0007 (accepted): the session is the unit of analysis, with 8 sessions per configuration.
  Effect size and ratio CI are the primary evidence; p-values are reported beside them.

### Changed
- Protocol v0.3.0. Comparisons now run on session medians (each launch for cold start).
- The project has no supervisor; docs, roadmap and the paper's author block reflect this.

## 2026-11-09: Boundary-overhead measurement fixed

### Decisions
- ADR-0006 (accepted): boundary overhead is now `inference_ms − inference_native_ms`, using each
  runtime wrapper's own invoke timer. The old formula was near zero by construction.

### Changed
- Protocol v0.2.0 and result schema 1.1: `inference_native_ms` is required. No data existed under v0.1.0.
- RQ1 now uses `inference_native_ms`; `inference_ms` and `boundary_overhead_ms` are in the RQ2 family.
- Harness contract, metric definitions, methodology and experiment template updated to match.
- Analysis derives `boundary_overhead_ms` and `timer_residual_ms`; the stage figure shows boundary
  overhead as its own stage. Tests cover the derived metrics and the new required field.

## 2026-11-09: Project initialised

### Added
- Repository scaffold: CLAUDE.md operating manual, AGENTS.md, README, docs set (overview,
  research questions, methodology, metrics, device matrix, roadmap, progress, conventions).
- ADRs 0001–0005 (ADR process, LiteRT as common runtime, Android-first scope, in-app harness
  with JSONL export, non-parametric statistics).
- Benchmark spec: `protocol.yaml` v0.1.0, `result-schema.json`, `harness-contract.md`.
- Model registry `models/manifest.yaml` (hashes pending).
- `analysis/benchkit` Python pipeline (validate, summarize, compare, figures) with pytest suite
  on synthetic fixtures.
- IEEE conference paper skeleton in `paper/`.
- Literature seed list and BibTeX (entries flagged for DOI verification).
- Claude skills: literature-review, benchmark-app-dev, run-experiment, analyze-results,
  paper-writing, progress-update.
