---
name: benchmark-app-dev
description: Build or modify the Flutter, Android-native (Kotlin) or iOS-native (Swift) benchmark harness apps so they follow the harness contract with strict parity. Use for any work under apps/.
---

# Benchmark App Development

## Read first
1. `benchmark-spec/harness-contract.md` (the contract)
2. `benchmark-spec/protocol.yaml` (values)
3. `benchmark-spec/result-schema.json` (output format)
4. `docs/03-metrics.md` (where timers go)

## Principles
- **Parity over cleverness.** If you change something in one app, make the equivalent change in
  the other in the same PR/session. Mirror module names (`config/ harness/ tasks/ metrics/ export/ ui/`).
- **Realistic developer path.** Use each platform's typical, documented API (Flutter:
  `tflite_flutter` + `image` package; Android: LiteRT `Interpreter` / delegates). Don't
  hand-optimise one side.
- **Timed region is sacred:** no logging, I/O, UI or allocation between t0 and t3.
- **Determinism:** fixed inputs, fixed order, seeded config shuffle.
- **Fail loudly:** model SHA-256 mismatch → stop; delegate unsupported → write
  `status: unsupported` record and continue.

## Implementation order (Phase 2)
1. Shared assets: 50 vision inputs + 50 QA samples into `assets/inputs/` of both apps.
2. Android native: classification CPU path end-to-end → JSONL export → `make validate` passes.
3. Flutter: same path → validate → compare `output_digest` with native for all 50 inputs.
4. Add detection, then QA, then GPU/NNAPI delegates, then metrics samplers (PSS, CPU, thermal, battery).
5. Add headless autorun via intent extras (`session`, `autorun`).
6. Parity checklist (contract §6) → record in `experiments/EXP-001.md`.

## Verification before declaring done
- `flutter analyze` clean; Android lint clean.
- Release build installs and autoruns on a device.
- Exported JSONL passes `python -m benchkit validate <dir>`.
- Digests match across platforms.
- Versions recorded in an ADR (toolchain).

## Pitfalls to watch
- Flutter debug build (JIT) gives invalid timings. Always use `--release`.
- `tflite_flutter` may bundle a different LiteRT version than the native dependency. Check it and document it.
- GPU delegate first-run includes shader compilation, so it belongs in `model_load_ms`, not warm-up stats.
- Dart `image` decode is slow. That's a real finding, not a bug. Don't "fix" it silently (ADR for variants).
- Android: keep screen on (`FLAG_KEEP_SCREEN_ON`), and don't run measurement while the app is in background.
