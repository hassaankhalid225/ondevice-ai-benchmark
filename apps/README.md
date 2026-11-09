# Benchmark Harness Apps

| Folder | Stack | Status |
|---|---|---|
| [`flutter_bench/`](flutter_bench/) | Flutter (Dart 3.12.2) + `tflite_flutter` 0.10.4 | Phase 2 Complete (Ready) |
| [`android_native_bench/`](android_native_bench/) | Kotlin 1.9.24 + LiteRT Android 2.16.1 | Phase 2 Complete (Ready) |
| [`ios_native_bench/`](ios_native_bench/) | Swift + LiteRT iOS | Phase 2b (Optional) |

All apps implement **[`benchmark-spec/harness-contract.md`](../benchmark-spec/harness-contract.md)**
and write records matching **[`benchmark-spec/result-schema.json`](../benchmark-spec/result-schema.json)**.

## Shared Module Parity
Both applications mirror the identical structural components:
- `config/`: Compilation of protocol values and runtime SHA-256 asset verification.
- `harness/`: Measurement runner loop, timing boundaries ($t_0 \dots t_3$), and memory buffering.
- `tasks/`: Task pipelines (Image Classification, Object Detection, Question Answering) with identical preprocessing rules and `output_digest` contracts.
- `metrics/`: PSS memory sampling, `/proc/self/stat` CPU sampling, thermal status querying, and battery charge fuel gauge sampling.
- `export/`: Non-blocking JSONL record serialization.
- `ui/`: Static minimal screen with button and headless Intent autorun support.

## Headless Execution via ADB
```bash
# Android Native
adb shell am start -n pk.edu.uos.bench.nativeandroid/.ui.MainActivity --es session 1 --ez autorun true
adb pull /sdcard/Android/data/pk.edu.uos.bench.nativeandroid/files/results/ data/raw/<device_id>/

# Flutter
adb shell am start -n pk.edu.uos.bench.flutter_bench/.MainActivity --es session 1 --ez autorun true
adb pull /sdcard/Android/data/pk.edu.uos.bench.flutter_bench/files/results/ data/raw/<device_id>/
```
