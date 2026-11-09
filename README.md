# On-Device AI Benchmark: Flutter vs Native

> **Research question:** What does it cost, in latency, memory, CPU, energy, startup time and
> app size, to run on-device deep learning through **Flutter** instead of **native** Android/iOS
> code, when the model, runtime and inputs are held identical?

**Status:** Phase 0 (project setup) complete. See [`docs/PROGRESS.md`](docs/PROGRESS.md).

## Why this matters

Cross-platform frameworks like Flutter now ship a large share of new mobile apps, and on-device
AI is moving from flagship demos into everyday apps. Developers choosing a stack have little
controlled evidence about the inference overhead Flutter introduces (Dart↔native FFI calls,
tensor marshalling, image preprocessing in Dart, isolate scheduling). This project gives
that evidence under a controlled, reproducible protocol.

## What's compared

| Dimension | Levels |
|---|---|
| App platform | Flutter (Dart + `tflite_flutter`), Native Android (Kotlin + LiteRT), Native iOS (Swift + LiteRT, optional) |
| Model / task | Image classification (MobileNetV3), Object detection (EfficientDet-Lite0), NLP (MobileBERT) |
| Precision | FP32, INT8 |
| Delegate | CPU (XNNPACK), GPU, NNAPI (Android) / Core ML (iOS) where supported |
| Device tier | Low-end, mid-range, high-end Android (+ one iPhone if available) |

Metrics: inference latency, end-to-end latency, cold start, peak/steady memory, CPU utilisation,
energy proxy (battery drain), sustained FPS, APK/IPA size delta. Definitions are in
[`docs/03-metrics.md`](docs/03-metrics.md).

## Repository layout

See [CLAUDE.md §4](CLAUDE.md#4-repository-map) for the full map. In short: `docs/` (plan and
method), `benchmark-spec/` (protocol and data contract), `apps/` (harness apps), `data/` (raw
and processed results), `analysis/` (Python statistics pipeline), `paper/` (IEEE LaTeX).

## Quickstart (analysis pipeline)

```bash
python -m venv .venv
. .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r analysis/requirements.txt
make test                            # or: cd analysis && python -m pytest
make validate summarize compare figures
```

## Reproducibility

- Protocol is versioned in `benchmark-spec/protocol.yaml`; each raw record stores the version.
- Models are pinned by SHA-256 in `models/manifest.yaml`.
- Device state (OS, battery, thermal, build mode) is logged with every run.
- All figures and tables in the paper are regenerated from `data/raw/` with one command.

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

Code: MIT ([`LICENSE`](LICENSE)). Paper text and figures: © the authors, all rights reserved until publication.
