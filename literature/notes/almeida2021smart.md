# almeida2021smart: Smart at What Cost? Characterising Mobile Deep Neural Networks in the Wild

- **Citation key:** `almeida2021smart` (in `literature/references.bib`, verified ✔)
- **Link / DOI:** https://doi.org/10.1145/3487552.3487863 (arXiv:2109.13963, IMC 2021, pp. 658--672)
- **Read on:** 2026-11-09 · Re-verified: 2026-11-11 · **Relevance:** ★★★

## One-sentence summary
Characterized the runtime performance and battery behavior of mobile deep neural networks across device tiers in the wild, demonstrating wide device-tier dispersion, non-linear FLOP-to-latency scaling under thermal throttling and scheduler policies, and multi-thread contention slowdowns.

## Method
- **Methodology:** Large-scale device-tier measurements spanning low-end (Samsung Galaxy A20), mid-tier (Galaxy A70), and flagship (Galaxy S21) Android smartphones running diverse DNN workloads across CPU, GPU, and NPU backends.
- **Metrics:** Inference latency, FPS/battery drain under sustained runs, thermal throttling effects, and CPU core affinity/thread scaling.

## Key results (verified against arXiv:2109.13963 PDF)
- **Device-tier disparity:** Across models, low-end A20 and mid-tier A70 handsets executed at an average 3.4× and 1.51× slower than the flagship S21, respectively.
- **Thermal throttling & scheduler effects:** Latency does not scale linearly with model FLOPs on mobile SoCs due to hardware/driver optimizations, scheduler policies, and thermal throttling during sustained runs.
- **Thread contention:** Adding CPU threads without core affinity or matching big.LITTLE topologies can degrade rather than improve mobile CPU inference throughput.

## Relevance to our study
- Directly informs the rigorous thermal protocol in `benchmark-spec/protocol.yaml`:
  - 60s mandatory cooldown between configurations.
  - Verification that `thermal_status <= light` prior to launching runs.
  - Automatic exclusion of runs where thermal state reaches `severe` (ADR-0005, protocol v0.3.0).
- Strongly reinforces **ADR-0005 and ADR-0007**: using non-parametric medians, percentiles (p5, p95), and session-level aggregation rather than naive means that are distorted by thermal skew.

## Limitations / gap we fill
- Evaluated models solely within native test harnesses; did not investigate the impact of modern cross-platform mobile frameworks or language-boundary tensor conversion.

## Quotable claim
> Device heating and dynamic voltage and frequency scaling rapidly degrade on-device inference speed, mandating strict inter-run cooldown protocols, non-parametric analysis, and robust session-level measurement.

