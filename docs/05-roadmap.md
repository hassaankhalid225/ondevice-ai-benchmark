# 05 · Roadmap

Target: arXiv preprint by **end of February 2027** (before Sakura Science FY2027 rounds and
the Sabancı PURE / USTC FuSEP application windows). Dates are targets; update when they slip.

| Phase | Goal | Exit criteria | Target |
|---|---|---|---|
| **0 · Setup** | Repo, plan, protocol, pipeline | This scaffold | 2026-11-09 ✅ |
| **1 · Literature** | 15–25 papers read, gap stated | `reading-list.md` ≥ 15 read, related-work draft in `paper/sections/02-related-work.tex` | 2026-11-23 |
| **2 · Harness apps** | Flutter + Android native apps, parity-checked | Both apps produce schema-valid JSONL; output digests match on all inputs; ADR on versions | 2026-12-14 |
| **2b · iOS (optional)** | Swift app | Same exit criteria on 1 iPhone | if device available |
| **3 · Pilot** | 1 device, 1 model, all delegates | `EXP-001` logged, pipeline produces figures, protocol issues fixed (ADR) | 2026-12-21 |
| **4 · Full collection** | All devices × configs × 8 sessions | `EXP-002…` logged, `make validate` clean | 2027-01-18 |
| **5 · Analysis** | Stats, figures, tables | `make compare figures` reproducible from `data/raw` | 2027-01-31 |
| **6 · Writing** | Full paper draft | All sections, no `\todo`, internal review | 2027-02-14 |
| **7 · Release** | arXiv + code release + conference submission | arXiv ID in README; repo tagged `v1.0.0` | 2027-02-28 |

## Risks
| Risk | Mitigation |
|---|---|
| Not enough devices | Borrow from classmates/family; low+mid+high minimum; document |
| GPU/NNAPI delegate fails on some devices | Record `unsupported`; it's a result in itself |
| `tflite_flutter` lags LiteRT versions | Pin versions, document in ADR, discuss as a threat to validity |
| Time conflict with FYP (SafarAI) and jobs | Fixed weekly slots; Phase 2 apps kept minimal |
