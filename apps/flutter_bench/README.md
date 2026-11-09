# Flutter Benchmark Harness (`flutter_bench`)

**Status:** Phase 2 Complete (Ready for device execution).

A Flutter/Dart benchmark harness application adhering strictly to [`benchmark-spec/harness-contract.md`](../../benchmark-spec/harness-contract.md) and emitting records compliant with [`benchmark-spec/result-schema.json`](../../benchmark-spec/result-schema.json).

## Specifications & Toolchain (ADR-0008)
- **Framework:** Flutter SDK 3.44.5 (channel stable)
- **Language:** Dart 3.12.2
- **Key Plugins:**
  - `tflite_flutter: 0.10.4` (pins LiteRT/TFLite C runtime with `lastNativeInferenceDurationMicroSeconds`)
  - `image: 4.3.0` (pure Dart bilinear resize and decoding for realistic developer baseline)
  - `crypto: 3.0.8` (runtime model SHA-256 verification)
  - `path_provider: 2.1.6` (file I/O)
- **Package:** `pk.edu.uos.bench.flutter_bench`

## Architecture & Modules
```
lib/
├── main.dart                # App entrypoint and headless argument parsing
└── src/
    ├── config/              # Protocol constants & SHA-256 asset verification
    ├── export/              # JSONL record serializer conforming to schema 1.1
    ├── harness/             # Benchmark execution loop, timing boundaries, cooldown
    ├── metrics/             # PSS, CPU %, and thermal status via platform channel
    ├── tasks/               # Classification, Detection, and QA pipelines
    └── ui/                  # Static UI and headless autorun handler
```

## Build & Run Instructions

### 1. Build Release APK
> [!IMPORTANT]
> Never collect benchmark data using `flutter run` (debug JIT). Always use an AOT release APK.
```bash
cd apps/flutter_bench
flutter build apk --release
```

### 2. Install on Device
```bash
adb install -r build/app/outputs/flutter-apk/app-release.apk
```

### 3. Headless Execution
Trigger automated benchmark sessions headlessly via ADB intent extras:
```bash
# Run Session 1 automatically
adb shell am start -n pk.edu.uos.bench.flutter_bench/.MainActivity --es session 1 --ez autorun true
```

### 4. Pull Exported Benchmark Results
```bash
adb pull /sdcard/Android/data/pk.edu.uos.bench.flutter_bench/files/results/ data/raw/<device_id>/
```
