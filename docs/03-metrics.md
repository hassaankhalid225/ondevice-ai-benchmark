# 03 · Metric Definitions

Every metric has one definition, used identically on every platform. Field names match
`benchmark-spec/result-schema.json`.

## Latency (per iteration, milliseconds)

Timeline of one iteration:
```
t0 ── raw input in memory (encoded JPEG bytes for vision | raw UTF-8 string for NLP)
 │  preprocess   decode/resize/normalise (vision) | tokenize (NLP) → input buffer filled
t1
 │  inference    interpreter.run(input, output) only
t2
 │  postprocess  argmax/top-k | NMS + box decode | span extraction → plain result object
t3 ── result available to app code (Dart object in Flutter, Kotlin object natively)
```
| Field | Definition |
|---|---|
| `preprocess_ms` | t1 − t0 |
| `inference_ms` | t2 − t1, the whole `run()` call as app code sees it (input copy + invoke + output copy + wrapper) |
| `inference_native_ms` | invoke call only, as reported by the runtime wrapper (see `harness-contract.md` §2). Required |
| `postprocess_ms` | t3 − t2 |
| `end_to_end_ms` | t3 − t0, measured with its own start/stop (not summed) |

Derived in analysis (ADR-0006):
- `boundary_overhead_ms` = `inference_ms − inference_native_ms`: tensor copying and wrapper code.
  The single FFI/JNI transition stays inside `inference_native_ms` on both platforms and is not
  isolated. Small negative values are possible because the timers differ; they are kept, not clipped.
- `timer_residual_ms` = `end_to_end_ms − (pre + inf + post)`: sanity check only, expected near zero.

`inference_ms` is measured in the app's own language around the `run()` call. That is deliberate:
it is what a developer experiences.

## Startup
| Field | Definition |
|---|---|
| `cold_start_ms` | process start → first inference result (`am start -W` TotalTime + app-logged first-result time; both recorded) |
| `model_load_ms` | interpreter creation + allocateTensors (+ delegate init) |

## Memory (MB = 10^6 bytes)
| Field | Definition |
|---|---|
| `pss_mb` | total PSS of the app process after the iteration (`Debug.MemoryInfo.getTotalPss()` KB → MB) |
| `idle_pss_mb` | PSS of the same app after launch, before loading the model (baseline per session) |
Derived: `model_pss_delta_mb = peak(pss_mb) − idle_pss_mb`.

## CPU
| Field | Definition |
|---|---|
| `cpu_pct` | (Δ process CPU time / Δ wall time) × 100 over the iteration. Can exceed 100 % with multiple threads |

## Energy (separate energy runs only)
| Field | Definition |
|---|---|
| `charge_counter_uah` | `BATTERY_PROPERTY_CHARGE_COUNTER` sample (µAh) |
Derived: `energy_per_inference_uah = (Δ charge over 10 min − Δ idle baseline) / number of inferences`.
This is a **proxy**, with coarse resolution. Report it as such.

## Throughput / sustained
| Field | Definition |
|---|---|
| `fps` | completed end-to-end iterations per second, 1 s windows, during the 5 min sustained run |
| `thermal_status` | Android `PowerManager.getCurrentThermalStatus()` mapped to `none/light/moderate/severe/critical/emergency/shutdown` |

## Footprint
| Metric | Definition |
|---|---|
| `apk_size_mb` | size of the release APK (universal) and per-ABI `arm64-v8a` split. Report both |
| `size_delta_mb` | harness app with model minus the same app without the model/runtime |

## Correctness (parity check, not a performance metric)
| Field | Definition |
|---|---|
| `output_digest` | top-1 class id (cls) / count of boxes with score ≥ 0.5 (det) / answer span (qa) |
