# 00 · Project Overview

## Working title
**Cross-Platform vs Native: A Performance Benchmark of On-Device Deep Learning Inference in
Flutter and Native Android/iOS Applications**

## People
| Role | Name | Contact | Notes |
|---|---|---|---|
| Author / PI (student) | Hassaan Khalid | – | BSSE final year, University of Sargodha |
| Supervisor | None | – | Independent work; to be shared with professors at other universities later |
| Co-supervisor / collaborator | _optional_ | – | e.g. a host professor (Sakura Science) |

## Problem
Flutter is widely used for production mobile apps, and on-device inference (LiteRT/TFLite,
Core ML, NNAPI) is becoming standard in consumer apps. In Flutter, every inference call
crosses a language boundary (Dart → C via FFI, or platform channels), and preprocessing such
as image decode, resize and normalise often runs in Dart. **No controlled, reproducible study
quantifies this overhead** across model types, precisions, hardware delegates and device tiers.
Developers choose stacks based on anecdotes.

## Goal
Quantify the performance difference between Flutter and native implementations of identical
on-device inference workloads, explain where the difference comes from, and give developers
evidence-based guidance.

## Contributions (planned, to be validated by results)
1. **C1, Benchmark suite:** open-source, parity-checked Flutter and native harness apps with a
   shared protocol and result schema.
2. **C2, Empirical study:** measurements across 3 tasks × 2 precisions × up to 3 delegates ×
   3+ devices, analysed with non-parametric statistics and effect sizes.
3. **C3, Overhead decomposition:** breakdown of end-to-end latency into preprocessing,
   boundary-crossing, inference and postprocessing, showing *where* Flutter pays (or doesn't).
4. **C4, Practitioner guidelines:** a decision table for when Flutter is good enough and when
   native code (or a native plugin) is justified.

## Scope
**In scope:** Android (primary), iOS (if hardware is available), LiteRT runtime, vision and
NLP models under 100 MB, single-model inference, foreground app.
**Out of scope (future work):** React Native / KMP / .NET MAUI, on-device LLMs > 1B params,
training on device, background or batch inference, ONNX Runtime / MediaPipe comparisons.
These may become a follow-up paper.

## Target venues (verify deadlines each cycle)
1. **arXiv** preprint (cs.LG / cs.SE / cs.PF): first public version.
2. University mandatory research paper submission (confirm format with the department).
3. IEEE-indexed conferences in Pakistan/region (e.g. ICOSST, FIT, ICET, INMIC). Check current CFPs.
4. Stretch: MobileSoft (ICSE co-located), EuroMLSys, or an edge-AI / TinyML workshop.

## Related use
This work is evidence for applications to short-term research programs (Sakura Science, KAUST VSRP,
Sabancı PURE, USTC FuSEP, EEML). Keep a 1-page summary + key figure ready in `paper/one-pager.md`
once results exist.
