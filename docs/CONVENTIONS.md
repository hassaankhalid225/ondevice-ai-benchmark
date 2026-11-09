# Conventions

## Git
- Default branch `main`, always in a working state. Work on short-lived branches:
  `feat/flutter-harness`, `data/exp-002`, `paper/results-draft`.
- **Conventional Commits** with these scopes:
  `app-flutter`, `app-android`, `app-ios`, `spec`, `analysis`, `data`, `paper`, `lit`, `docs`, `ci`.
  Examples: `feat(app-android): add NNAPI delegate option`,
  `data(exp-003): add dev-samsung-a14 sessions 1-5`, `paper(results): add RQ2 decomposition figure`.
- Tag releases: `v0.x` during the study, `v1.0.0` at arXiv submission (tag = paper version).
- Raw data is committed (it's small JSONL). If it ever exceeds ~50 MB, move to Git LFS (ADR first).

## Files and IDs
| Thing | Pattern | Example |
|---|---|---|
| Device | `dev-<brand>-<model>` | `dev-xiaomi-redmi13c` |
| Model | from `models/manifest.yaml` | `mobilenetv3_large` |
| Platform | `flutter` · `android_native` · `ios_native` | |
| Delegate | `cpu` · `gpu` · `nnapi` · `coreml` | |
| Raw file | `data/raw/<device>/<YYYYMMDD>_<platform>_<model>_<precision>_<delegate>_s<NN>.jsonl` | `20261220_flutter_mobilenetv3_large_int8_cpu_s01.jsonl` |
| Experiment log | `experiments/EXP-<NNN>.md` | `EXP-001.md` |
| ADR | `docs/decisions/<NNNN>-<kebab-title>.md` | `0006-toolchain-versions.md` |
| Lit note | `literature/notes/<firstauthor><year>-<keyword>.md` | `ignatov2019-aibenchmark.md` |
| BibTeX key | `<firstauthor><year><firstword>` | `ignatov2019ai` |
| Figure | `paper/figures/<rq>-<what>.pdf` | `rq1-latency-ratio.pdf` |

## Code style
- **Python:** 3.10+, type hints, docstrings on public functions, `ruff` defaults, `pytest`.
- **Dart:** `flutter analyze` clean, `dart format`.
- **Kotlin:** ktlint / Android Studio defaults. **Swift:** swift-format defaults.
- Benchmark code paths must have no logging, allocation or UI work inside the timed region.

## Writing
- Paper: IEEE style, American English, present tense for results ("Flutter adds…"), past tense
  for what was done ("We measured…"). Numbers with units and a thin space: `12.3\,ms`.
- Docs: short sections, tables over prose, every doc starts with its purpose.
