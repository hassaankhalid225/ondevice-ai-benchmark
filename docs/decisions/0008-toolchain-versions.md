# 0008 · Pin toolchain and dependency versions for benchmark apps

- **Status:** accepted
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** `apps/flutter_bench`, `apps/android_native_bench`, `docs/PROGRESS.md`, `paper/sections/03-methodology.tex`

## Context
Research integrity and reproducibility demand exact pinning of toolchains, SDKs, and runtime libraries.
Any drift in compiler versions, optimization flags, or native runtime binaries between Flutter and Android Native
distorts the comparison. Furthermore, ADR-0006 established that `inference_native_ms` relies on the internal invoke
timer exposed by both runtime wrappers (`tflite_flutter` in Dart and LiteRT / TensorFlow Lite Java/Kotlin on Android).
We must pin exact versions and ensure both wrappers invoke binary-compatible LiteRT C runtimes.

## Options considered
1. **Dynamic floating versions (`^x.y.z`)**:
   - Pros: convenient during early development.
   - Cons: non-reproducible builds; minor version updates could change delegate flags or timing hooks.
2. **Pinned release versions with verified LiteRT 2.16.x / 1.0 runtime**:
   - Pros: completely deterministic; guarantees identical LiteRT C runtime semantics across Flutter and Native; satisfies ADR-0002 and ADR-0006.
   - Cons: requires manual dependency alignment.

## Decision
Adopt Option 2. Pin exact toolchain and dependency versions across both harness codebases:

### Flutter Harness (`apps/flutter_bench`)
- **Flutter SDK:** 3.44.5 (stable channel)
- **Dart SDK:** 3.12.2
- **Android Gradle Plugin (AGP):** 8.6.0
- **Compile SDK:** 36, **NDK:** 28.2.13676358
- **Key dependencies:**
  - `tflite_flutter: 0.12.1` (compatible with Dart 3.12 typed data views; exposes `lastNativeInferenceDurationMicroSeconds`)
  - `image: 4.3.0` (canonical pure Dart image decoding and bilinear resizing for realistic developer baseline)

### Android Native Harness (`apps/android_native_bench`)
- **Build System:** Gradle 8.14 with Android Gradle Plugin (AGP) 8.3.2
- **Language:** Kotlin 1.9.24
- **Java Toolchain:** OpenJDK 21 (Android Studio JBR)
- **Target / Compile SDK:** 34 (Android 14)
- **Min SDK:** 26 (Android 8.0, supporting hardware bitmap decoding and NNAPI 1.0+)
- **LiteRT / TFLite dependencies:**
  - `org.tensorflow:tensorflow-lite:2.16.1`
  - `org.tensorflow:tensorflow-lite-gpu:2.16.1`
  - `org.tensorflow:tensorflow-lite-gpu-api:2.16.1`
  - `org.tensorflow:tensorflow-lite-api:2.16.1`

### Parity Timers (ADR-0006 verification)
- **Dart:** `interpreter.lastNativeInferenceDurationMicroSeconds / 1000.0`
- **Android Native:** `interpreter.getLastNativeInferenceDurationNanoseconds() / 1e6`
- **Elapsed Realtime Clocks:**
  - Flutter: Dart monotonic `Stopwatch.elapsedMicroseconds / 1000.0`
  - Android Native: `SystemClock.elapsedRealtimeNanos() / 1e6`

## Consequences
- Both harness apps compile against the identical LiteRT runtime baseline.
- No dynamic version resolution will alter benchmark behavior.
- Documented in `paper/sections/03-methodology.tex` and `docs/PROGRESS.md`.

