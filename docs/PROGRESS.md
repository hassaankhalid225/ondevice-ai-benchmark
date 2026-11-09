# PROGRESS: Live Status

> **Update this file at the end of every working session.** It is the first thing the next
> person or agent reads. Keep "Next actions" concrete (a stranger should be able to start on it).

**Last updated:** 2026-11-09 · **Current phase:** 3 · Pilot (EXP-001) · **Protocol:** v0.3.0

## Current focus
Phase 1 (Literature Review) and Phase 2 (Benchmark Harness Applications for Flutter and Android Native)
are complete and fully verified. Both release APKs have been built and verified on disk:
- Android Native: `apps/android_native_bench/app/build/outputs/apk/release/app-release.apk` (65.6 MB, R8 minified)
- Flutter: `apps/flutter_bench/build/app/outputs/flutter-apk/app-release.apk` (118.2 MB, AOT release)
All 6 LiteRT flatbuffer models (FP32 & INT8) are verified with cryptographic SHA-256 digests.
An automated ADB runner (`analysis/benchkit/runner.py`) has been added to orchestrate pre-flight checks,
APK deployment, headless execution, data extraction, and schema validation. Analysis test suite has 21 passing tests (100% clean).
`experiments/EXP-001.md` is authored and ready for execution.

## Next actions (in order)
1. [ ] Connect a physical Android device via USB with USB Debugging enabled.
2. [ ] Run `python -m benchkit devices` to inspect hardware properties and copy row into `docs/04-device-matrix.md`.
3. [ ] Run `python -m benchkit install` to deploy both release APKs to the device.
4. [ ] Run `python -m benchkit run --device <device_id> --session 1` to execute Session 1 of pilot campaign EXP-001.
5. [ ] Run `python -m benchkit validate data/raw` and `python -m benchkit summarize data/raw` to verify schema compliance and stage timings.
6. [ ] Ask the university department whether the mandatory paper requires a designated supervisor and verify format requirements.

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
