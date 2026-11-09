# Reading List

Status: `to-read` → `skimmed` → `read` (note written) → `cited`.
Relevance: ★★★ core / ★★ supporting / ★ background.

## Seed list & Core Benchmarking
| Key | Paper (short) | Theme | Rel. | Status |
|---|---|---|---|---|
| ignatov2018ai | AI Benchmark: DNNs on Android | mobile inference benchmarking | ★★★ | read |
| ignatov2019ai | AI Benchmark 2019 | mobile inference benchmarking | ★★★ | read |
| reddi2022mlperfmobile | MLPerf Mobile | benchmark methodology | ★★★ | read (note) |
| reddi2020mlperf | MLPerf Inference | benchmark methodology | ★★ | read |
| almeida2021smart | Smart at what cost? (DNNs in the wild) | on-device DNN deployment in real apps | ★★★ | read (note) |
| biornhansen2018survey | Cross-platform mobile dev survey | cross-platform frameworks | ★★★ | read |
| biornhansen2020empirical | Empirical investigation of overhead | cross-platform frameworks | ★★★ | read (note) |
| willocx2016comparing | Comparing mobile dev strategies | cross-platform performance | ★★★ | read |
| delia2015performance | Performance eval of cross-platform | cross-platform performance | ★★ | read |
| ciman2017empirical | Energy consumption cross-platform | mobile energy / cross-platform | ★★★ | read (note) |
| zhang2022comprehensive | Comprehensive benchmark of DL libraries | mobile DL library fragmentation | ★★★ | read (note) |
| xu2019first | First look at DL apps on smartphones | production mobile DL deployment | ★★★ | read (note) |
| lane2015early | Early resource characterization | edge deep learning resources | ★★ | read |
| lane2016deepx | DeepX low-power inference accelerator | mobile DNN acceleration | ★★ | read |
| banbury2021benchmarking | Benchmarking TinyML systems | edge benchmarking challenges | ★★ | read |
| georges2007statistically | Statistically rigorous Java eval | benchmarking methodology | ★★★ | read |
| barrett2017virtual | Virtual machine warmup blows hot/cold | VM warmup & benchmarking | ★★★ | read |
| wu2019machine | Machine learning at Facebook co-design | industry mobile DL deployment | ★★ | read |
| luo2020comparison | Comparison of AI models & frameworks | mobile AI benchmarking | ★★ | read |
| howard2019searching | MobileNetV3 | model | ★ | read |
| tan2020efficientdet | EfficientDet | model | ★ | read |
| sun2020mobilebert | MobileBERT | model | ★ | read |
| jacob2018quantization | Integer-only quantization | INT8 | ★★ | read |
| cliff1993dominance | Cliff's delta | statistics | ★ | read |
| holm1979simple | Holm correction | statistics | ★ | read |

## Gaps to fill (search queries)
1. `Flutter performance evaluation` / `Flutter vs native performance` / `Flutter React Native energy consumption` (addressed by Biørn-Hansen 2020, Willocx 2016, Delia 2015)
2. `cross-platform mobile framework performance comparison empirical` (addressed by Biørn-Hansen 2018, 2020)
3. `on-device deep learning inference latency smartphone benchmark` (addressed by Zhang 2022, Reddi 2022, Ignatov 2018/2019)
4. `TensorFlow Lite NNAPI GPU delegate performance evaluation` (addressed by Zhang 2022, Luo 2020)
5. `mobile deep learning frameworks comparison energy` (addressed by Almeida 2021, Ciman 2017)
6. `performance benchmarking methodology rigorous statistics` (addressed by Georges 2007, Barrett 2017)
7. `energy measurement Android battery charge counter accuracy` (addressed by Almeida 2021)
8. `Dart FFI overhead` / `language interoperability overhead mobile` (addressed by ADR-0006)

## Synthesis Themes for Related Work
- **Theme A: Mobile Deep Learning Benchmarks & Acceleration:** AI Benchmark (Ignatov), MLPerf Mobile (Reddi), DL Library Benchmark (Zhang), Edge characterization (Lane, Xu).
- **Theme B: Cross-Platform Mobile Performance & Energy:** Empirical studies of Flutter, React Native, and native runtimes (Biørn-Hansen, Willocx, Delia, Ciman).
- **Theme C: Language Boundary & Interoperability:** Managed runtimes, JNI/FFI transitions, and stage decomposition (Georges, Barrett, ADR-0006).
- **Theme D: Methodological Rigor & Non-Parametric Statistics:** Pitfalls of naive means, thermal confounding, session-level independence (Georges, Barrett, Cliff, Holm).
