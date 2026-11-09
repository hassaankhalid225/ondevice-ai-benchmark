# 01 · Research Questions & Hypotheses

Hypotheses are written **before** data collection (pre-registration style) so the analysis
can't be bent to fit results. If a hypothesis changes, record it in an ADR. Never edit history.

## RQ1: Inference latency
*Is there a statistically and practically significant difference in pure inference latency
(the runtime invoke call only, `inference_native_ms`, ADR-0006) between Flutter and native apps for
the same model, delegate and device?*

- **H1₀:** No difference in median inference latency.
- **H1₁:** Flutter median inference latency differs from native.
- *Expectation:* small or no difference, because both call the same C runtime. Overhead should be
  mostly outside the kernel. A null result here is a **valid and useful finding**.

## RQ2: End-to-end latency and its decomposition
*How much of the end-to-end time (input → result) differs, and which stage accounts for it?*

- **H2₁:** Flutter end-to-end latency is higher than native, and the gap is driven by
  preprocessing and tensor marshalling, not by inference.
- Stages measured: `preprocess_ms`, `inference_ms`, `inference_native_ms`, `postprocess_ms`,
  `end_to_end_ms` (boundary overhead = `inference_ms − inference_native_ms`, ADR-0006).

## RQ3: Resource cost
*Do Flutter apps use more memory (PSS), CPU, and energy for the same workload?*

- **H3a₁:** Flutter peak/steady PSS is higher (Dart VM + engine baseline). Report both absolute
  and *delta over idle app baseline*.
- **H3b₁:** Energy per inference differs. Measured as battery-drain proxy (see `03-metrics.md`).

## RQ4: Interaction effects
*Does the Flutter–native gap depend on model size/type, precision (FP32/INT8), delegate
(CPU/GPU/NNAPI), or device tier?*

- **H4₁:** The relative gap shrinks as model compute grows (fixed overhead amortised).
- **H4₂:** The gap is largest on low-end devices.

## RQ5: Startup and footprint
*What is the cold-start time to first inference and the app size delta?*

- **H5₁:** Flutter has longer cold start to first inference and a larger binary.

## Analysis mapping
| RQ | Primary metric(s) | Test | Effect size |
|---|---|---|---|
| RQ1 | `inference_native_ms` | Mann–Whitney U (per config) | Cliff's δ + median ratio with bootstrap 95% CI |
| RQ2 | stage times | same, per stage | share of gap per stage |
| RQ3 | `pss_mb`, `cpu_pct`, energy | same | Cliff's δ |
| RQ4 | ratio Flutter/native | trend across configs (Spearman ρ vs model FLOPs) | ρ with CI |
| RQ5 | `cold_start_ms`, size | Mann–Whitney U / descriptive | Cliff's δ |

All tests use one median per session (each launch for cold start), per ADR-0007.
Multiple comparisons: Holm–Bonferroni within each RQ family. α = 0.05.
Practical significance: |Cliff's δ| ≥ 0.33 (medium) **and** the ratio's 95% CI lies outside [0.95, 1.05].
This is the primary evidence; Holm-adjusted p-values are reported beside it.
