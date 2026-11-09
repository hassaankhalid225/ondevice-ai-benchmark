# 0002 · Use LiteRT (TensorFlow Lite) as the single common runtime

- **Status:** accepted
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** apps, models, paper §Methodology

## Context
To isolate the effect of the *app platform* (Flutter vs native), the inference engine must be
the same on both sides. Candidates: LiteRT/TFLite, ONNX Runtime Mobile, MediaPipe Tasks, PyTorch ExecuTorch.

## Options considered
1. **LiteRT:** mature Flutter binding (`tflite_flutter`, Dart FFI to the C API), first-class
   Android/iOS libraries, CPU (XNNPACK) / GPU / NNAPI / Core ML delegates, large model zoo.
2. **ONNX Runtime:** Flutter bindings less mature; would add a binding-quality confound.
3. **MediaPipe Tasks:** higher-level API that hides preprocessing, so we can't decompose stages.

## Decision
LiteRT on all platforms, same `.tflite` files. Exact versions of the native LiteRT library and
`tflite_flutter` (and the LiteRT version it bundles) are pinned in a later toolchain ADR.

## Consequences
- Results generalise to LiteRT users; other runtimes are future work (threat to external validity).
- Plugin and native library may bundle different LiteRT versions. Must be checked and either
  aligned or reported.
