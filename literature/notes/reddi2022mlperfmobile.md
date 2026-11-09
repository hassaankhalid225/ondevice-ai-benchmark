# reddi2022mlperfmobile: MLPerf Mobile Inference Benchmark

- **Citation key:** `reddi2022mlperfmobile` (in `literature/references.bib`, verified ✔)
- **Link / DOI:** MLSys 2022, vol. 4, pp. 352-369
- **Read on:** 2026-11-09 · **Relevance:** ★★★

## One-sentence summary
Presents the MLPerf Mobile benchmark suite—an industry-standard, open-source benchmarking application for measuring on-device AI performance across mobile operating systems, runtimes, and hardware accelerators.

## Method
- **Workloads:** Standardized vision (MobileNet EdgeTPU, SSD-MobileNet, DeepLabV3) and NLP (MobileBERT) tasks across FP32 and INT8 precisions.
- **Scenarios:** Single-stream (latency-critical user interaction) and continuous execution.
- **Execution harness:** Native C++ core engine packaged into platform-native harness applications (Android Java/Kotlin and iOS Objective-C/Swift).
- **Parity control:** Strict rules on model hashing, input dataset preprocessing, and minimum duration/iteration counts to achieve statistical reproducibility.

## Key results
- Hardware delegates (GPU, NNAPI, vendor DSP/NPU) achieve 2× to 8× latency speedup over multi-threaded CPU for compute-intensive vision models, but INT8 quantization is often mandatory to unlock NPU efficiency.
- Strict input dataset standardization and deterministic execution sequences are essential to prevent run-to-run noise from masking subtle framework variations.
- Emphasized that reproducible mobile AI benchmarking requires release-mode binaries, fixed environmental conditions, and explicit tracking of system thermal states.

## Relevance to our study
- Serves as the primary methodological blueprint for our benchmark harness contract (`benchmark-spec/harness-contract.md`):
  - Pre-registered models with fixed SHA-256 verification.
  - Standardized fixed input dataset (50 inputs) in identical sequential order.
  - Dedicated warmup iterations (20) followed by measured iterations (100).
  - Explicit delegate tracking (CPU with XNNPACK, GPU, NNAPI).

## Limitations / gap we fill
- MLPerf Mobile was designed specifically to compare **hardware SoCs and silicon accelerators**, not application software frameworks. Its harness is a bespoke native application that does not reflect how mobile software engineers build apps with cross-platform frameworks like Flutter.
- Does not measure or decompose the software stack overhead: Dart-to-native FFI, memory copying, and managed-language preprocessing.

## Quotable claim
> While MLPerf Mobile establishes rigorous standards for mobile hardware benchmarking, it abstracts away application-level software stacks, leaving open the question of how cross-platform frameworks influence the end-to-end user experience of on-device AI.
