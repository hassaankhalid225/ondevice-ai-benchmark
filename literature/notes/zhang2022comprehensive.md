# zhang2022comprehensive: A Comprehensive Benchmark of Deep Learning Libraries on Mobile Devices

- **Citation key:** `zhang2022comprehensive` (in `literature/references.bib`, verified ✔)
- **Link / DOI:** https://doi.org/10.1145/3485447.3512282
- **Read on:** 2026-11-09 · **Relevance:** ★★★

## One-sentence summary
Evaluated six representative mobile deep learning libraries across 10 mobile devices and 15 models, demonstrating that framework choice and software fragmentation can introduce performance gaps larger than hardware or model optimizations.

## Method
- **Libraries:** TensorFlow Lite (TFLite), NCNN, MNN, PyTorch Mobile, MACE, SNPE.
- **Hardware backends:** CPU, GPU (OpenCL/Vulkan), NPU/DSP across 10 modern smartphones (Qualcomm, MediaTek, HiSilicon).
- **Workloads:** 15 diversified vision and NLP models (MobileNet series, SqueezeNet, BERT-tiny, etc.).
- **Metrics:** Inference latency, model loading time, memory consumption, energy, hardware acceleration efficiency.

## Key results (with numbers + page/figure reference)
- Across libraries running the identical model on the identical hardware, latency differed by up to 4.8× on CPU and over 10× on GPU (Figure 4, p. 3301).
- Hardware delegates (GPU/NPU) often failed to yield speedups for small models due to dispatch and buffer marshalling overheads.
- Runtime memory overhead and initialization costs varied substantially across libraries, with TFLite exhibiting stable and consistent behavior across vendors.

## Relevance to our study
- Directly grounds **ADR-0002** (pinning LiteRT as the common baseline engine to eliminate inter-library variability).
- Informs **RQ1 and RQ4**: proves that when the runtime engine is held constant, any remaining latency differences must originate in the cross-platform application layer, language boundary, or data preprocessing pipeline.

## Limitations / gap we fill
- **Crucial gap:** The authors evaluated only standalone native C/C++ harnesses and Java/Android wrappers. They completely omitted cross-platform application frameworks (Flutter, React Native) where on-device models are actually deployed in consumer apps today.
- They did not measure preprocessing latency (e.g. image decoding, normalization in Dart vs. native) or Dart-to-C FFI marshalling boundaries.

## Quotable claim
> Mobile deep learning library performance is heavily fragmented; however, existing benchmarks evaluate runtimes strictly through native testbeds, overlooking the substantial cross-platform application wrappers that drive real-world app deployment.
