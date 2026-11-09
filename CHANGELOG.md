# Changelog

Format: newest first. One entry per working session. Describe *what* changed and *why*.
Categories: Added / Changed / Fixed / Data / Paper / Decisions.

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
