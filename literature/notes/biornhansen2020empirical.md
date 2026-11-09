# biornhansen2020empirical: An Empirical Investigation of Performance Overhead in Cross-Platform Mobile Development Frameworks

- **Citation key:** `biornhansen2020empirical` (in `literature/references.bib`, verified ✔)
- **Link / DOI:** https://doi.org/10.1007/s10664-020-09827-6
- **Read on:** 2026-11-09 · **Relevance:** ★★★

## One-sentence summary
Conducted a controlled empirical evaluation of cross-platform frameworks (including Flutter, React Native, and Xamarin) against native Android and iOS, measuring CPU, memory, and launch time overhead across standard UI and computation workloads.

## Method
- **Frameworks:** Native Android (Java/Kotlin), Native iOS (Swift), Flutter, React Native, Xamarin Forms.
- **Workloads:** Standard computational tasks (sorting, math operations, JSON parsing) and UI operations (list view rendering, animations).
- **Metrics:** Execution duration, CPU utilization percentage, RAM/PSS footprint, application binary size, cold startup time.
- **Devices:** Multiple physical Android and iOS handsets across generations.

## Key results
- Flutter exhibited CPU performance approaching native execution for standard algorithmic tasks due to Dart Ahead-Of-Time (AOT) compilation to ARM machine code.
- Flutter consistently consumed more baseline memory (RAM) than native Android/iOS due to the bundled Dart runtime environment and Skia rendering pipeline.
- Flutter cold-start times were slightly longer than native due to runtime bootstrap, but significantly outperformed interpreted JavaScript bridge architectures.
- Heavy computational tasks that relied on pure language processing revealed non-negligible discrepancies between Dart VM execution and native compiled code.

## Relevance to our study
- Directly grounds **RQ2, RQ3, and RQ5**: supports our hypotheses that Flutter incurs a fixed baseline memory footprint and cold-start penalty due to runtime embedding.
- Validates our experimental design requirement of testing exclusively in **release AOT mode** (`flutter build apk --release`), as JIT debug modes distort execution metrics.

## Limitations / gap we fill
- Evaluated only synthetic toy workloads (e.g. bubble sort, Fibonacci) and basic UI navigation.
- Completely omitted on-device machine learning / deep learning inference workloads, where tensor operations, native FFI boundaries, and high-throughput vision preprocessing dominate runtime performance.
- Did not decompose latency into preprocessing, boundary transition, and pure computation stages.

## Quotable claim
> While cross-platform frameworks like Flutter achieve near-native UI responsiveness through AOT compilation, empirical analysis demonstrates measurable resource premiums in memory footprint and binary size, leaving hardware-accelerated machine learning workloads uncharacterized.
