# On-Device AI Benchmark: Flutter vs Native

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24128933.svg)](https://doi.org/10.5281/zenodo.24128933)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--4289--2011-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0002-4289-2011)

> **Research question:** What does it cost, in latency, memory, CPU, energy, startup time and
> app size, to run on-device deep learning through **Flutter** instead of **native** Android/iOS
> code, when the model, runtime and inputs are held identical?

**Status:** Release [`v0.2.0-paper1`](https://github.com/hassaankhalid225/ondevice-ai-benchmark/releases/tag/v0.2.0-paper1) (DOI [`10.5281/zenodo.24128933`](https://doi.org/10.5281/zenodo.24128933)) — Campaign EXP-001 ($N=8$ sessions on `dev-infinix-x650c`, 283 JSONL files / 23,180 kept records), reproducible `benchkit` statistical pipeline (including non-parametric TOST equivalence & single-device table formatting), and compiled **10-page IEEE paper** (`paper/main.pdf`, 31 CrossRef/PDF-verified references, zero `\todo` markers) are complete. Next: `exp-002` branch prepares controlled CPU matched-LiteRT (`1t`/`4t`), `fromFile()`/`mmap`, and second-device (`Infinix Smart 7`) runs. See [`docs/PROGRESS.md`](docs/PROGRESS.md) and [`experiments/EXP-001.md`](experiments/EXP-001.md).

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

See [`CITATION.cff`](CITATION.cff) or use the archived Zenodo release DOI [`10.5281/zenodo.24128933`](https://doi.org/10.5281/zenodo.24128933):

```bibtex
@software{khalid2026ondevice,
  author  = {Khalid, Hassaan},
  title   = {On-Device AI Benchmark: Flutter vs Native},
  year    = {2026},
  version = {0.2.0},
  doi     = {10.5281/zenodo.24128933},
  url     = {https://doi.org/10.5281/zenodo.24128933}
}
```

## License

Code: MIT ([`LICENSE`](LICENSE)). Paper text and figures: © the authors, all rights reserved until publication.
