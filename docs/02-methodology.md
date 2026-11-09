# 02 · Methodology (Experimental Protocol)

> Machine-readable version: `benchmark-spec/protocol.yaml` (**protocol v0.3.0**).
> If this document and the YAML disagree, the YAML wins. Fix the doc and log an ADR.

## 1. Design
Full-factorial controlled experiment.

| Factor | Levels (v0.3.0) |
|---|---|
| Platform (independent variable) | `flutter`, `android_native` (+ `ios_native` optional) |
| Model | `mobilenetv3_large`, `efficientdet_lite0`, `mobilebert_qa` (see `models/manifest.yaml`) |
| Precision | `fp32`, `int8` |
| Delegate | `cpu` (XNNPACK), `gpu`, `nnapi` |
| Threads (CPU) | 4 (fixed; sensitivity run with 1 later) |
| Device | ≥ 3 Android tiers (see `04-device-matrix.md`) |

Not every model × delegate combination is supported. Unsupported combos are recorded as
`status: unsupported`, never silently dropped.

## 2. Controlled variables (parity)
Both apps MUST share (enforced by `harness-contract.md`):
- identical `.tflite` file (SHA-256 verified at app start and written in every record)
- identical runtime version family (LiteRT), same thread count, same delegate options
- identical input set: fixed list of 50 images / 50 text samples bundled as assets,
  processed in the same order
- identical preprocessing algorithm (resize → bilinear, normalisation constants, layout NHWC)
- release builds (`flutter build apk --release`; Android `release` build type, R8 on)

## 3. Device preparation (before every session)
Checklist (also in the `run-experiment` skill):
1. Battery 50–90 %, **unplugged** for energy runs, plugged for latency-only runs (logged).
2. Airplane mode ON, Wi-Fi/Bluetooth/location OFF, auto-sync OFF.
3. Screen brightness fixed (50 %), auto-brightness OFF, screen kept on by the app.
4. Close all other apps; reboot the device at the start of each day.
5. Device at room temperature: wait until `thermal_status` is `none`/`light` before starting.
6. Record ambient temperature if possible.

## 4. Run procedure
For each configuration (platform × model × precision × delegate):
1. **Cold start** measurement: force-stop app → launch via `adb shell am start -W` → app auto-runs
   the first inference and logs `cold_start_ms`. Repeat 10×.
2. **Warm-up:** 20 iterations (discarded, `phase: warmup`, still recorded).
3. **Measurement:** 100 iterations (`phase: measure`).
4. **Sessions:** repeat steps 2–3 in **8 sessions** per config, on different occasions, with
   **randomised config order** per session (seeded; order saved in the experiment log).
5. **Cooldown:** ≥ 60 s between configs, or until thermal status returns to baseline.
6. **Sustained run (FPS/thermal):** separately, 5 min continuous camera-like loop per
   config on the detection model, sampling FPS and thermal every second.
7. **Energy:** separate unplugged runs: 10 min continuous inference, battery counter
   (`BatteryManager.BATTERY_PROPERTY_CHARGE_COUNTER`) sampled every 5 s; compare against a
   10 min idle-app baseline on the same platform.

Total per device ≈ 2 platforms × 3 models × 2 precisions × 3 delegates × 8 sessions × 120 iterations.

## 5. Measurement method
- Timing with monotonic clocks: Dart `Stopwatch` (microsecond resolution), Kotlin
  `SystemClock.elapsedRealtimeNanos()`, Swift `DispatchTime.now().uptimeNanoseconds`.
- Stage boundaries are defined in `03-metrics.md`. The **same boundaries** are used on every platform.
- `inference_native_ms` is read from the runtime wrapper's own invoke timer on both platforms (ADR-0006).
- Memory: Android `Debug.getMemoryInfo()` → total PSS, sampled after each iteration
  (cheap). Peak is max over the session.
- CPU: per-process CPU time delta (`/proc/self/stat` utime+stime) / wall time.
- Results written as JSONL (one record per iteration) to app-specific storage, pulled
  with `adb pull` into `data/raw/<device_id>/`.

## 6. Data quality
- Records validated against `result-schema.json` (`make validate`).
- Outlier policy: **no removal** for main results (we report medians and percentiles, which are robust).
  Sensitivity analysis with IQR-fence trimming reported in the appendix only.
- Sessions with thermal status ≥ `severe` are flagged and excluded, with the exclusion reported.
- Correctness check: top-1 label / detection count / QA span must match between platforms
  for each input. Mismatches indicate a parity bug: stop and fix.

## 7. Statistical analysis
- Unit of analysis (ADR-0007): iteration-level for describing distributions, **one median per
  session** for all tests and effect sizes (avoids pseudo-replication: 8 sessions × 2 platforms per
  config). Cold-start metrics use each launch as the unit.
- Test: two-sided Mann–Whitney U on those values.
- Effect sizes: Cliff's δ; median ratio (Flutter/Native) with 10,000-sample bootstrap 95 % CI.
- Primary evidence: |δ| ≥ 0.33 and ratio CI outside [0.95, 1.05]. p-values are reported beside it,
  because with 8 sessions Holm-adjusted significance is hard to reach in the larger families.
- Multiple comparisons: Holm–Bonferroni per RQ family.
- Reporting: median, p5, p95, IQR. Never mean ± SD alone (latency is right-skewed).
- Implemented in `analysis/benchkit/stats.py`. Tests in `analysis/tests/`.

## 8. Threats to validity (track and expand during the study)
- **Internal:** thermal throttling, background processes, JIT/AOT differences (mitigated: release
  builds only), plugin version differences, GC pauses.
- **Construct:** battery counter is a coarse energy proxy (state it; no external power monitor).
- **External:** limited device set, LiteRT only, Android-heavy, specific Flutter/LiteRT versions.
- **Conclusion:** multiple comparisons (Holm), small session count (report CIs, not just p).
