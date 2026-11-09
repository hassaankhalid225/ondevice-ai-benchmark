# PROGRESS: Live Status

> **Update this file at the end of every working session.** It is the first thing the next
> person or agent reads. Keep "Next actions" concrete (a stranger should be able to start on it).

**Last updated:** 2026-11-09 · **Current phase:** 3 · Pilot (EXP-001) · **Protocol:** v0.3.0

## Current focus
Phase 1 (Literature Review) and Phase 2 (Benchmark Harness Applications for Flutter and Android Native)
are complete. All 6 LiteRT flatbuffer models (FP32 & INT8) are generated, verified, and pinned in `models/manifest.yaml`.
The 50 canonical vision and 50 text inputs are generated and synchronized. Both harness apps compile cleanly
with zero lint issues. All paper sections (Abstract, Introduction, Related Work, Methodology, Discussion,
Threats, Conclusion) have been drafted to high IEEE academic standards. Focus now shifts to registering physical
devices and running the initial pilot campaign (EXP-001).

## Next actions (in order)
1. [ ] Connect a physical Android device via USB, enable Developer Options/USB Debugging, and register device specifications in `docs/04-device-matrix.md`.
2. [ ] Build and install release APKs on the connected device (`apps/android_native_bench` and `apps/flutter_bench`).
3. [ ] Execute pilot campaign EXP-001 (Session 1), pull exported JSONL result files to `data/raw/<device_id>/`.
4. [ ] Run `python -m benchkit validate data/raw` and `python -m benchkit summarize data/raw` to verify schema compliance and stage timings.
5. [ ] Ask the university department whether the mandatory paper requires a designated supervisor and verify format requirements.

## Phase checklist
- [x] Phase 0 · Setup (2026-11-09)
- [x] Phase 1 · Literature (2026-11-09)
- [x] Phase 2 · Harness apps: Flutter & Android Native (2026-11-09)
- [ ] Phase 2b · iOS app (optional)
- [ ] Phase 3 · Pilot (EXP-001)
- [ ] Phase 4 · Full data collection
- [ ] Phase 5 · Analysis
- [ ] Phase 6 · Writing (Empirical results & discussion finalization)
- [ ] Phase 7 · Release (arXiv preprint + conference submission)

## Paper section status
| Section | File | Status | Reviewed |
|---|---|---|---|
| Abstract | `paper/sections/00-abstract.tex` | drafted | – |
| Introduction | `paper/sections/01-introduction.tex` | drafted (complete) | – |
| Related work | `paper/sections/02-related-work.tex` | drafted (25 verified refs) | – |
| Methodology | `paper/sections/03-methodology.tex` | drafted (complete) | – |
| Results | `paper/sections/04-results.tex` | structural draft (awaiting data) | – |
| Discussion | `paper/sections/05-discussion.tex` | drafted (complete with decision matrix) | – |
| Threats to validity | `paper/sections/06-threats.tex` | drafted (complete) | – |
| Conclusion | `paper/sections/07-conclusion.tex` | drafted (complete) | – |

## Open questions / blockers
- Does the university's mandatory research paper need a supervisor? **unknown (to ask department)**
- Does the first arXiv submission need an endorsement, and from whom? **check arXiv endorsement requirements for cs.LG/cs.SE**
- Is an iPhone available for Phase 2b? **optional / secondary**
- Does the department require a specific paper format (IEEE vs. own template)? **confirm with department**

## Data collected
_None yet._ (Pilot EXP-001 planned as next operational action).
