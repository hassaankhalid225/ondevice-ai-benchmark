# Harness Contract

Every benchmark app (Flutter, Android native, iOS native) **must** implement this contract
identically. This is what makes the comparison fair. Reviewers will look for exactly these
parity issues.

## 1. Inputs
- Reads `protocol.yaml` values compiled into the app (or a bundled `config.json` generated from it).
- Bundles the same input assets (`assets/inputs/...`) and the same model files.
- On start, computes SHA-256 of the model file and **refuses to run** if it doesn't match
  `models/manifest.yaml`.

## 2. Execution
```
for each config in shuffled(configs, seed = order_seed_base + session):
    wait until thermal_status <= max_thermal_status_to_start
    interpreter = create(model, delegate, threads)        # timed → model_load_ms
    for i in 0 ..< warmup + measure:
        input = inputs[i % n_inputs]
        t0; pre = preprocess(input); t1
        out = interpreter.run(pre); t2
        res = postprocess(out); t3
        native = interpreter.lastNativeInferenceDuration()    # read after t3, see below
        record(stage times, native, pss, cpu, thermal, digest(res))
    close(interpreter); sleep(cooldown)
```
- `inference_native_ms` comes from the runtime wrapper, never from an extra timer (ADR-0006):
  Flutter `interpreter.lastNativeInferenceDurationMicroSeconds / 1000`, Android
  `interpreter.getLastNativeInferenceDurationNanoseconds() / 1e6`. Both apps call the standard
  `run()` API, because this value is set only on that path.
- **No** logging, UI updates, allocations of new buffers, or disk writes inside t0–t3.
  Records are buffered in memory and flushed after the config finishes.
- Input/output buffers are allocated once per config and reused.
- Flutter: run the loop on the **main isolate** (default developer path) for the main
  study. A background-isolate variant is a separate, labelled config if added (ADR).
- UI shows only a static "running" screen (no animations) to avoid frame-rendering load.

## 3. Preprocessing (must be algorithmically identical)
| Task | Steps |
|---|---|
| Classification | decode JPEG → RGB → resize to model input (bilinear, no aspect crop) → float32 `[0,1]` (fp32) or uint8/int8 per model quantisation params → NHWC |
| Detection | same as classification at model input size |
| QA (MobileBERT) | WordPiece tokenize with the bundled vocab, max_seq_len 384, same truncation policy |

The Flutter app uses pure Dart (the `image` package) for decode/resize, because that is what
typical Flutter developers do. This is a **deliberate** realism choice and is stated in the paper.
A "native-preprocess" Flutter variant (preprocessing done via platform code) is a candidate
extension (ADR required).

## 4. Postprocessing
| Task | Output → `output_digest` |
|---|---|
| Classification | argmax → `"cls:<id>"` |
| Detection | decode boxes, score ≥ 0.5, NMS IoU 0.5 → `"det:<count>"` |
| QA | best start/end logits span → `"qa:<start>-<end>"` |

## 5. Output
- One JSON object per iteration, conforming to `result-schema.json`, written as JSONL.
- File name: `<YYYYMMDD>_<platform>_<model>_<precision>_<delegate>_s<NN>.jsonl`.
- Unsupported delegate → a single record with `status: "unsupported"` and the error message.

## 6. Parity review checklist (run before any data collection; record in the EXP log)
- [ ] Same model SHA-256 printed by both apps
- [ ] Same LiteRT version family (or difference documented in ADR)
- [ ] Same thread count / delegate options
- [ ] `output_digest` identical across platforms for all 50 inputs × all configs
- [ ] Timer positions reviewed line-by-line in both codebases
- [ ] Release build confirmed (`build_mode` field = release)

## Known unavoidable differences (document here as they're found)
- `inference_native_ms` clock: `tflite_flutter` uses `DateTime.now()` (wall clock, µs); LiteRT Java
  uses `System.nanoTime()` (monotonic, ns). Both wrap the invoke call only (ADR-0006).
