# zhang2022comprehensive: A Comprehensive Benchmark of Deep Learning Libraries on Mobile Devices

- **Citation key:** `zhang2022comprehensive` (in `literature/references.bib`, verified ✔)
- **Link / DOI:** https://doi.org/10.1145/3485447.3512148 (arXiv:2202.06512, WWW 2022, pp. 3298--3307)
- **Read on:** 2026-11-09 · Re-verified: 2026-11-11 · **Relevance:** ★★★

## One-sentence summary
Evaluated six representative mobile deep learning libraries across 10 mobile devices and 15 models, demonstrating that runtime selection and operator support introduce up to an order-of-magnitude latency variation on CPU and GPU.

## Method
- **Libraries:** TensorFlow Lite (TFLite), NCNN, MNN, PyTorch Mobile, Mace, FeatherCNN (6 inference engines).
- **Hardware backends:** CPU and GPU across 10 smartphones.
- **Workloads:** 15 vision and language models.
- **Metrics:** Inference latency, cold initialization overhead, thread scaling, and INT8 quantization speedups.

## Key results (verified against arXiv:2202.06512 PDF)
- Across libraries on identical models and hardware, fastest vs. slowest engine latency averaged 7.4× overall (1.9× over 2nd-best), averaging **8.7× on CPU** and **6.0× on GPU**, and reaching up to **54.3×** in worst-case CNN execution.
- Quantization (INT8 vs. FP32) delivered only modest and inconsistent speedups (**0.8×–3.0×**), sometimes regressing depending on operator fallback.
- Operator coverage, thread scaling, and delegate initialization overheads varied sharply across native C++ engines.

## Relevance to our study
- Directly grounds **ADR-0002** (pinning LiteRT as the common baseline engine to eliminate inter-library variability).
- Informs **RQ1 and RQ4**: proves that when the runtime engine is held constant, any remaining latency differences must originate in the cross-platform application layer, language boundary, or data preprocessing pipeline.

## Limitations / gap we fill
- **Crucial gap:** The authors evaluated only standalone native C/C++ harnesses and Java/Android wrappers. They completely omitted cross-platform application frameworks (Flutter, React Native) where on-device models are actually deployed in consumer apps today.
- They did not measure preprocessing latency (e.g. image decoding, normalization in Dart vs. native) or Dart-to-C FFI marshalling boundaries.

## Quotable claim
> Mobile deep learning library performance is heavily fragmented; however, existing benchmarks evaluate runtimes strictly through native testbeds, overlooking the substantial cross-platform application wrappers that drive real-world app deployment.

