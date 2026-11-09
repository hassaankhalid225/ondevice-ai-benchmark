# xu2019first: A First Look at Deep Learning Apps on Smartphones

- **Citation key:** `xu2019first` (in `literature/references.bib`, verified ✔)
- **Link / DOI:** https://doi.org/10.1145/3308558.3313591
- **Read on:** 2026-11-09 · **Relevance:** ★★★

## One-sentence summary
Presents the first comprehensive empirical study of deep learning applications in the wild by analyzing 16,500 popular Android applications, revealing the prevalence, architectures, and execution frameworks of production on-device deep learning.

## Method
- **Dataset:** 16,500 top Android apps scraped from Google Play across categories.
- **Analysis:** Automated static program analysis and binary inspection tool to detect embedded deep learning frameworks, model binaries, and operator signatures.
- **Classification:** Categorized models by architecture, parameter size, input modalities, and target use cases.

## Key results
- Over 200 popular apps already packaged on-device deep learning models, with computer vision (image classification, object detection, facial recognition) representing over 75% of use cases.
- MobileNet, SqueezeNet, and SSD architectures dominated production deployments due to memory and latency constraints.
- TensorFlow Lite was identified as the predominant mobile runtime across apps.
- Discovered that most models in production are bundled directly within the app assets and invoked synchronously on the main thread or worker threads.

## Relevance to our study
- Validates the selection of models in `models/manifest.yaml` (MobileNetV3 for classification, EfficientDet-Lite0 / SSD for detection, MobileBERT for NLP).
- Justifies evaluating the default main-isolate / main-thread invocation path (ADR-0004, harness contract §2) as representative of real-world app architectures.

## Limitations / gap we fill
- Strictly observational static analysis of APK contents; did not perform controlled runtime performance benchmarking.
- Did not examine the performance contrast between native Android apps and cross-platform apps executing deep learning models.

## Quotable claim
> On-device deep learning has moved rapidly into consumer apps, with vision workloads and lightweight architectures dominating mobile deployments, yet little is known about how host application framework architectures affect inference efficiency.
