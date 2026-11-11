# One-Page Summary: Flutter vs. Native Android On-Device Inference (Entry-Tier Benchmark)

**Author:** Hassaan Khalid (BS Software Engineering, University of Sargodha)  
**Title:** *Flutter vs. Native Android for On-Device Inference: An Empirical Benchmark on Entry-Tier Hardware*  
**Code, Protocol & Raw Dataset:** `https://github.com/hassaankhalid225/ondevice-ai-benchmark` (MIT)

## Problem & Protocol
Mobile teams increasingly ship on-device deep learning inside cross-platform frameworks like Flutter rather than Native Android (Kotlin), yet lack controlled empirical evidence on the latency, memory, CPU, startup, and binary size trade-offs of invoking native LiteRT C/C++ engines through Dart FFI and pure-Dart preprocessing pipelines.

Under Protocol `v0.3.0` (fixed before data collection at commit `dc45f62`), we built parity-checked release applications (`flutter_bench` AOT + `android_native_bench` R8-minified) executing **3 architectures** (MobileNetV3-Large, EfficientDet-Lite0, MobileBERT-QA) × **2 precisions** (FP32, INT8) × **3 delegates** (CPU/XNNPACK, GPU, NNAPI) using SHA-256-pinned `.tflite` models (`54.74 MB`) and 50 canonical inputs per modality. On an entry-tier Android 9 smartphone (`Infinix Hot 8` / `dev-infinix-x650c`, MediaTek Helio P22, PowerVR GE8320, 3.7 GB RAM), we completed **8 alternating sessions** (`283` schema-validated JSONLs, `24,020` raw records, `23,180` retained after `840` MT6765 clock-sentinel exclusions) plus **10 alternating cold-launch/idle baseline trials**, achieving **100% functional parity** (`500/500` `output_digest` matches). All statistical tests compare independent **session medians** ($n_F = 8$, $n_N \in \{5, 7, 8\}$; two-sided Mann–Whitney $U$, Holm–Bonferroni $\alpha = 0.05$, Cliff's $\delta$, 10,000-resample bootstrap 95% CIs, and non-parametric multiplicative TOST within $[0.95, 1.05]$).

## Key Empirical Findings (Entry-Tier Campaign)

1. **GPU TOST Equivalence vs. CPU Ecosystem Package Drift (`inference_native_ms`):**
   Three of four mutually supported GPU configurations achieve strict non-parametric $\pm 5\%$ TOST equivalence ($\mathcal{R} = 0.99\text{--}1.00$, $p_{\mathrm{TOST}} \in [0.001, 0.041]$; e.g., MobileBERT-QA FP32 GPU `53.60` vs. `53.41 ms`), while EfficientDet-Lite0 INT8 GPU ($\mathcal{R} = 1.04\,[0.94, 1.08]$, $n_N=5$, $p_{\mathrm{TOST}} = 0.177$) stays inconclusive. On default CPU builds, Flutter outpaces Native on FP32 MobileBERT-QA (`116.02` vs. `232.80 ms`, $\mathcal{R} = 0.50$, $p_{\mathrm{Holm}} = 0.003$) and EfficientDet-Lite0 (`101.80` vs. `136.45 ms`, $\mathcal{R} = 0.75$, $p_{\mathrm{Holm}} = 0.042$) because `pub.dev`'s `tflite_flutter 0.12.1` pulls LiteRT `2.20.0` with default single-thread `XNNPackDelegate(nullptr)` rather than Maven `2.16.1`'s 4-thread Cortex-A53 contention (ADR-0009).
2. **Preprocessing—Not FFI—Drives End-to-End Vision Slowdowns (`end_to_end_ms`):**
   Pure Dart `image` decoding/resizing (`68.53–103.17 ms` vs. Native `8.64–24.56 ms`, `4.20–10.48×`) slows GPU EfficientDet-Lite0 end-to-end latency by `2.00×` FP32 (`156.13` vs. `77.99 ms`, $p_{\mathrm{Holm}} = 0.008$) and `1.91×` INT8 (`176.17` vs. `92.33 ms`, $p_{\mathrm{Holm}} = 0.036$). Dart FFI boundary marshalling adds only `0.88–4.63 ms` (though recursive `[1, 384]` logit copies on MobileBERT-QA elevate relative FFI ratios to `11.90–18.22×` and contribute `82%` of the `+4.90 ms` gap on FP32 GPU).
3. **Both Idle Baseline and Incremental RAM Are Higher in Flutter (`pss_mb`):**
   At settled idle, Flutter uses `2.14×` Native PSS (`71.29` vs. `33.30 MiB`, `+37.99 MiB`, $p_{\mathrm{Holm}} = 0.003$). Under inference (`107.86–200.36 MiB` vs. `55.77–86.64 MiB`, `1.72–2.64×`, $p_{\mathrm{Holm}} \le 0.024$), *incremental* memory above idle still exceeds Native by `+7.24` to `+83.18 MiB` (`1.25–3.06×`) because `Interpreter.fromAsset()` copies flatbuffers via `calloc<Uint8>` without freeing native memory (contrasted with Native zero-copy `FileChannel.map`), also slowing larger CPU model initialization `3.74–11.71×`.
4. **Delegate Break-Even & Quantization Trade-Offs (RQ4):**
   GPU compilation costs `1.63–4.20 s` one-time startup on both stacks; slow Dart preprocessing reduces EfficientDet FP32 per-frame GPU savings (`21.6` vs. `73.9 ms/iter`), delaying GPU break-even from `32` (Native) to `114` (Flutter) inferences (`10` vs. `28` on MobileBERT FP32). INT8 accelerates CPU (`25.8%–56.7%`) and saves Flutter RAM (`18%–27%`), yet slows entry PowerVR GPU execution (`12.3%–27.0%`).
5. **Startup & Footprint (RQ5):**
   Flutter adds `+45.5 ms` (`+10.8%`) cold launch (`468.50` vs. `423.00 ms` `TotalTime`, $p_{\mathrm{Holm}} = 0.005$) and `+16.79 MB` single-ABI `arm64-v8a` non-model binary overhead (`24.06` vs. `7.27 MB`; universal APKs `123.83` vs. `65.63 MB`).

## Key Figures
- Pipeline stage decomposition: [`paper/figures/rq2-stage-decomposition.pdf`](figures/rq2-stage-decomposition.pdf)
- Pure inference forest plot: [`paper/figures/rq1-inference-ratio.pdf`](figures/rq1-inference-ratio.pdf)
- Memory PSS ratio forest plot: [`paper/figures/rq3-memory-ratio.pdf`](figures/rq3-memory-ratio.pdf)
