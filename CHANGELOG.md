# Changelog

Format: newest first. One entry per working session. Describe *what* changed and *why*.
Categories: Added / Changed / Fixed / Data / Paper / Decisions.

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
