# 0010 · Controlled LiteRT 1.4.0 CPU Threading, `fromFile` mmap Control, and Multi-Device Expansion (`EXP-002`)

- **Status:** accepted
- **Date:** 2026-11-11
- **Deciders:** Hassaan Khalid
- **Affects:** `apps/android_native_bench`, `apps/flutter_bench`, `analysis/benchkit`, `experiments/EXP-002.md`

## Context
Paper 1 (`EXP-001` on `dev-infinix-x650c`) intentionally evaluated out-of-the-box dependency packaging (ADR-0009), where `tflite_flutter: 0.12.1` bundled `com.google.ai.edge.litert:litert:1.4.0` (C library `2.20.0`) with default `XNNPackDelegate()` (`nullptr`, 1 thread) and `Interpreter.fromAsset()` (`Model.fromBuffer` heap allocation), whereas Android Native linked `org.tensorflow:tensorflow-lite:2.16.1` with 4-thread XNNPACK and `FileChannel.map` (`mmap`).

To isolate pure framework overhead from runtime-version, threading, and asset-loading effects across both entry-tier and newer Android hardware without modifying the archived `EXP-001` dataset on `main`:

## Decision
Isolate `EXP-002` harness instrumentation on branch `exp-002`:
1. **Runtime Binary Alignment (`Priority 1.1`):** Pin Android Native (`apps/android_native_bench/app/build.gradle.kts`) to `com.google.ai.edge.litert:{litert,litert-gpu,litert-gpu-api,litert-api}:1.4.0` (C version `2.20.0`), byte-for-byte matching Flutter `tflite_flutter: 0.12.1`. Update both `JsonlExporter` files to stamp `"runtime_version": "2.20.0"`.
2. **Explicit Threading & Scope Controls (`Priority 1.1`):**
   - Pass explicit `XNNPackDelegate(options: XNNPackDelegateOptions(numThreads: config.threads))` in Flutter `BenchmarkRunner` instead of bare `nullptr` default.
   - Accept `--ei threads <N>` (`1` or `4`) and `--ez cpuOnly true|false` across both `MainActivity` entry points and `benchkit run`.
3. **Zero-Copy File Loader Control (`Priority 1.2`):**
   - Accept `--es loader asset|file` in Flutter `MainActivity` / `BenchmarkRunner` and `benchkit run`.
   - When `loader == "file"`, copy verified `.tflite` assets to app support storage *before* starting `loadSw`, then measure `Interpreter.fromFile()` (`TfLiteModelCreateFromFile` / `mmap`) cleanly to test the causal effect on `model_load_ms` and incremental `pss_mb`.
4. **Raw Data Isolation:** Route controlled `--arm` runs under `data/raw/exp002/<arm>/<device_id>/` and clear stale per-session `*_sNN.jsonl` files inside the apps and `.staging_pull` in `benchkit.runner` so `1t`, `4t`, and `file` runs never overwrite or append onto prior arms.

## Consequences
- `main` (`v0.2.0-paper1`) remains frozen and 100% reproducible against `EXP-001` and Paper 1.
- Running `EXP-002` controlled arms on Infinix Hot 8 (`dev-infinix-x650c`) and full sessions on Infinix Smart 7 requires zero code edits during hardware execution.

