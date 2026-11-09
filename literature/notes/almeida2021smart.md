# almeida2021smart: Smart at What Cost? Characterising Mobile Deep Neural Networks in the Wild

- **Citation key:** `almeida2021smart` (in `literature/references.bib`, verified ✔)
- **Link / DOI:** https://doi.org/10.1145/3487552.3487823
- **Read on:** 2026-11-09 · **Relevance:** ★★★

## One-sentence summary
Characterized the runtime performance, energy, and resource costs of deploying deep neural networks in consumer smartphone applications, demonstrating substantial variance caused by thermal throttling and background execution.

## Method
- **Methodology:** In-the-wild profiling and controlled testbeds of mobile neural network executions across diverse mobile device tiers (budget to flagship).
- **Metrics:** Latency, energy drain (via hardware power monitors and battery fuel gauges), CPU/GPU residency, and thermal dissipation over extended multi-minute runs.

## Key results
- Continuous on-device inference triggers rapid thermal throttling on mid-tier and budget smartphones, causing latency to degrade by 25%–60% within 2 to 5 minutes of continuous execution.
- Battery drain per inference is strongly dependent on whether hardware acceleration stays active or drops back to CPU due to driver or thermal limits.
- Background process interference and unconstrained OS scheduling introduce high tail latency (p95/p99) that invalidates simple mean-based reporting.

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
