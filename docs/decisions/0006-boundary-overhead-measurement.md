# 0006 · Measure boundary overhead with the runtime's native inference timer

- **Status:** accepted
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** protocol v0.1.0 → v0.2.0, result schema 1.0 → 1.1, both harness apps, analysis, RQ1/RQ2, paper §Methodology/§Results

## Context
Protocol v0.1.0 defined `boundary_overhead_ms = end_to_end_ms − (pre + inf + post)`. The stages
t0–t3 are contiguous, so this expression can only capture timer gaps and is close to zero by
construction. The real language-boundary cost (copying tensors, wrapper code) sits inside
`inference_ms`, because that timer wraps the whole `run()` call. Contribution C3 and RQ2 depend on
separating it, yet the field that allows this (`inference_native_ms`) was only a stretch goal.
RQ1 also said "`interpreter.run` only" while the Flutter timer includes the wrapper.

Source check (2026-11-09, main branches; re-check against the pinned versions):
- `tflite_flutter` `Interpreter.runInference`: copies inputs with `setTo`, then times only `invoke()`
  and exposes `lastNativeInferenceDurationMicroSeconds`. Outputs are copied after the timer stops.
- LiteRT Java `NativeInterpreterWrapper.run`: copies inputs, then times only the JNI `run` call and
  exposes `getLastNativeInferenceDurationNanoseconds()`. Outputs are copied after the timer stops.

## Options considered
1. **Keep the v0.1.0 formula**: no work, but it cannot answer RQ2 or support C3.
2. **Own C shim with a native clock around `TfLiteInterpreterInvoke`**: most exact, but replaces the
   normal call path in both apps and adds code that must itself be kept at parity.
3. **Read the timer each runtime wrapper already exposes**: no change to the call path, same
   measurement position on both platforms. Does not isolate the single FFI/JNI transition.

## Decision
Use option 3. `inference_native_ms` is required on every `ok` warm-up/measure record.
`boundary_overhead_ms = inference_ms − inference_native_ms`. RQ1 uses `inference_native_ms`;
`inference_ms` (what app code experiences) moves to RQ2.

## Consequences
- Both harness apps read the runtime's value after t3, outside all timed regions.
- `boundary_overhead_ms` measures input/output tensor copying plus wrapper code. The one FFI/JNI
  transition stays inside `inference_native_ms` on both platforms; state this in the paper.
- The two timers differ: `tflite_flutter` uses `DateTime.now()` (wall clock, microseconds), Java uses
  `System.nanoTime()`. The wall clock can be adjusted, so small negative overheads are possible.
  They are kept, not clipped. Airplane mode (protocol) removes network time updates.
- `end_to_end_ms − (pre + inf + post)` remains only as a sanity check named `timer_residual_ms`.
- No data exists under v0.1.0, so nothing is invalidated.
