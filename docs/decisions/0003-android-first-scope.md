# 0003 · Android-first; iOS optional

- **Status:** accepted
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** scope, roadmap, paper §Threats

## Context
Building and measuring on iOS requires a Mac and iPhone, which may not be available. Android
has a much larger share in the author's region and target audience, and exposes better
measurement APIs (PSS, thermal, charge counter).

## Decision
Android (Flutter vs Kotlin) is the core study and must be complete on ≥ 3 device tiers. iOS
(Flutter vs Swift) is added only if hardware is available and does not delay Phase 4.

## Consequences
- Paper title/abstract must say "Android" if iOS is not included.
- iOS absence is listed as a threat to external validity and future work.
