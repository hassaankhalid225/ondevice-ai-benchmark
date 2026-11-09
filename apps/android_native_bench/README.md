# Android Native Benchmark Harness (`android_native_bench`)

**Status:** Phase 2 Complete (Ready for device execution).

A pure Kotlin/Android native benchmark harness application adhering strictly to [`benchmark-spec/harness-contract.md`](../../benchmark-spec/harness-contract.md) and emitting records compliant with [`benchmark-spec/result-schema.json`](../../benchmark-spec/result-schema.json).

## Specifications & Toolchain (ADR-0008)
- **Language:** Kotlin 1.9.24 / JDK 17
- **Build System:** Gradle 8.5 with Android Gradle Plugin 8.3.2
- **SDK:** compileSdk 34, minSdk 26, targetSdk 34
- **Runtime:** LiteRT / TensorFlow Lite 2.16.1 (`org.tensorflow:tensorflow-lite:2.16.1`, GPU delegate: `2.16.1`)
- **Package:** `pk.edu.uos.bench.nativeandroid`

## Architecture & Modules
```
app/src/main/
├── assets/
│   ├── inputs/
│   │   ├── vision/          # 50 standardized test JPEGs
│   │   └── text.jsonl       # 50 SQuAD QA test prompts
│   └── models/              # Pinned .tflite models (SHA-256 verified)
└── kotlin/pk/edu/uos/bench/nativeandroid/
    ├── config/              # Protocol settings & SHA-256 asset verification
    ├── export/              # JSONL record serializer conforming to schema 1.1
    ├── harness/             # Benchmark execution loop, timing boundaries, cooldown
    ├── metrics/             # PSS (ActivityManager), CPU (/proc/self/stat), thermals
    ├── tasks/               # Classification, Detection, and QA pipelines
    └── ui/                  # Static UI and headless Intent receiver
```

## Build & Run Instructions

### 1. Build Release APK
```bash
cd apps/android_native_bench
./gradlew assembleRelease    # Windows: gradlew.bat assembleRelease
```

### 2. Install on Device
```bash
adb install -r app/build/outputs/apk/release/app-release.apk
```

### 3. Headless Execution
Trigger automated benchmark sessions headlessly via ADB intent extras:
```bash
# Run Session 1 automatically
adb shell am start -n pk.edu.uos.bench.nativeandroid/.ui.MainActivity --es session 1 --ez autorun true
```

### 4. Pull Exported Benchmark Results
```bash
adb pull /sdcard/Android/data/pk.edu.uos.bench.nativeandroid/files/results/ data/raw/<device_id>/
```
