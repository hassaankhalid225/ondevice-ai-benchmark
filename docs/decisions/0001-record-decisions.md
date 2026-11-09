# 0001 · Record methodology and architecture decisions as ADRs

- **Status:** accepted
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** process

## Context
A benchmark paper is only credible if reviewers can see *why* each methodological choice was
made and that choices weren't changed after seeing the data. Multiple people and AI agents
will work on this repo over months.

## Decision
Every decision affecting methodology, toolchain versions, scope or analysis is recorded as a
numbered ADR in `docs/decisions/` using `0000-template.md`. ADRs are never edited after
acceptance except to change status. A new ADR supersedes an old one.

## Consequences
- Slight overhead per decision; in exchange the "Methodology" and "Threats to validity"
  sections of the paper can be written directly from ADRs.
