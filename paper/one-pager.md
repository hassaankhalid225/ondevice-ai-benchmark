# One-Page Summary: Cross-Platform vs. Native On-Device AI Inference (EXP-001)

**Author:** Hassaan Khalid (BS Software Engineering, University of Sargodha)  
**Title:** *Cross-Platform vs. Native: A Performance Benchmark of On-Device Deep Learning Inference in Flutter and Native Android Applications*  
**Code, Protocol & Raw Dataset:** `github.com/hassaankhalid225/ondevice-ai-benchmark` (MIT)

## Problem & Protocol
Mobile teams increasingly ship on-device deep learning inside cross-platform frameworks like Flutter rather than Native Android (Kotlin), yet lack controlled empirical evidence on the latency, memory, startup, and binary size trade-offs of invoking native LiteRT C/C++ engines through Dart FFI and pure-Dart preprocessing pipelines.

Under pre-registered Protocol `v0.3.0`, we built parity-checked release applications (`flutter_bench` AOT + `android_native_bench` R8-minified) executing **3 architectures** (MobileNetV3-Large, EfficientDet-Lite0, MobileBERT-QA) × **2 precisions** (FP32, INT8) × **3 delegates** (CPU/XNNPACK, GPU, NNAPI) using SHA-256-pinned `.tflite` models (`54.74 MB`) and 100 identical inputs per modality. On entry-tier `dev-infinix-x650c` (MediaTek Helio P22, PowerVR GE8320, 3.7 GB RAM, Android 9), we completed **8 alternating sessions** (`283` schema-validated JSONLs, `24,020` raw records, `23,180` retained after `840` MT6765 clock-sentinel exclusions) plus **10 alternating cold-launch/idle baseline trials**, achieving **100% functional parity** (`500/500` `output_digest` matches). All statistical tests compare independent **session medians** ($n_F = 8$, $n_N \in \{5, 7, 8\}$; two-sided Mann–Whitney $U$, Holm–Bonferroni $\alpha = 0.05$, Cliff's $\delta$, 10,000-resample bootstrap 95% CIs).

## Key Empirical Findings (EXP-001)

1. **GPU Kernel Parity vs. CPU Package Drift (`inference_native_ms`):**
   On all 4 hardware-accelerated GPU configs, Flutter matches Native Android within 4% ($\mathcal{R} = 0.99\text{--}1.04$, $|\delta| \le 0.31$, $p_{\mathrm{Holm}} = 1.000$; e.g., MobileBERT-QA FP32 GPU `53.60` vs. `53.41 ms`). Conversely, default CPU builds show Flutter *faster* on FP32 MobileBERT-QA (`116.02` vs. `232.80 ms`, $\mathcal{R} = 0.50$, $p_{\mathrm{Holm}} = 0.003$) and EfficientDet-Lite0 (`101.80` vs. `136.45 ms`, $\mathcal{R} = 0.75$, $p_{\mathrm{Holm}} = 0.042$) because `pub.dev`'s `tflite_flutter 0.12.1` pulls LiteRT `2.20.0` with default single-thread XNNPACK rather than Maven `2.16.1`'s 4-thread contention (ADR-0009).
2. **Preprocessing—Not FFI—Drives End-to-End Vision Slowdowns (`end_to_end_ms`):**
   Pure Dart `image` decoding/resizing (`68.53–103.17 ms` vs. Native `8.64–24.56 ms`, $4.20\times\text{--}10.48\times$) slows GPU EfficientDet-Lite0 end-to-end latency by $2.00\times$ FP32 (`156.13` vs. `77.99 ms`, $p_{\mathrm{Holm}} = 0.008$) and $1.91\times$ INT8 (`176.17` vs. `92.33 ms`, $p_{\mathrm{Holm}} = 0.036$). Dart FFI boundary marshalling adds only `0.88–4.63 ms` (though recursive `[1, 384]` logit copies on MobileBERT-QA elevate relative FFI ratios to $11.90\times\text{--}18.22\times$ and add `+4.90 ms` / $1.09\times$ on FP32 GPU).
3. **Both Idle Baseline and Incremental RAM Are Higher in Flutter (`pss_mb`):**
   At settled idle, Flutter uses $2.14\times$ Native PSS (`71.29` vs. `33.30 MiB`, $+37.99\text{ MiB}$, $p_{\mathrm{Holm}} = 0.003$). Under inference (`107.86–200.36 MiB` vs. `55.77–86.64 MiB`, $1.72\times\text{--}2.64\times$, $p_{\mathrm{Holm}} \le 0.024$), *incremental* memory above idle still exceeds Native by $+7.24$ to $+83.18\text{ MiB}$ ($1.25\times\text{--}3.06\times$) because `Interpreter.fromAsset()` copies flatbuffers via `calloc<Uint8>` without freeing native memory (contrasted with Native zero-copy `FileChannel.map`), also slowing larger CPU model initialization $3.74\times\text{--}11.71\times$.
4. **Delegate Break-Even & Quantization Trade-Offs (RQ4):**
   GPU compilation costs `1.63–4.20 s` one-time startup on both stacks; slow Dart preprocessing reduces EfficientDet FP32 per-frame GPU savings (`21.6` vs. `73.9 ms/iter`), delaying GPU break-even from `32` (Native) to `114` (Flutter) inferences (`10` vs. `28` on MobileBERT FP32). INT8 accelerates CPU (`25.8%–56.7%`) and saves Flutter RAM (`18%–27%`), yet slows entry PowerVR GPU execution (`12.3%–27.0%`).
5. **Startup & Footprint (RQ5):**
   Flutter adds $+45.5\text{ ms}$ ($+10.8\%$) cold launch (`468.50` vs. `423.00 ms` `TotalTime`, $p_{\mathrm{Holm}} = 0.005$) and $+16.79\text{ MB}$ single-ABI `arm64-v8a` non-model binary overhead (`24.06` vs. `7.27 MB`; universal APKs `123.83` vs. `65.63 MB`).

## Key Figures
- Pipeline stage decomposition: [`paper/figures/rq2-stage-decomposition.pdf`](figures/rq2-stage-decomposition.pdf)
- Pure inference forest plot: [`paper/figures/rq1-inference-ratio.pdf`](figures/rq1-inference-ratio.pdf)
- Memory PSS ratio forest plot: [`paper/figures/rq3-memory-ratio.pdf`](figures/rq3-memory-ratio.pdf)
