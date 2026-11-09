---
name: progress-update
description: End-of-session bookkeeping that keeps the repo understandable for the next developer or AI agent. Update PROGRESS.md, CHANGELOG.md and ADRs. Use at the end of every working session or when asked "what's the status".
---

# Progress Update

Do all of these before ending a session in which anything changed:

1. **`docs/PROGRESS.md`**
   - Update `Last updated` date, `Current phase`, `Protocol` version.
   - Tick completed items; rewrite "Current focus" in 1–2 sentences.
   - "Next actions": 3–6 concrete, ordered tasks a stranger could start on, each naming the
     file(s) or skill involved.
   - Update "Paper section status", "Open questions / blockers", "Data collected".
2. **`CHANGELOG.md`**: new dated entry at the top (Added / Changed / Fixed / Data / Paper / Decisions).
   Describe outcomes, not keystrokes.
3. **ADRs**: if any methodology/tooling/scope decision was made, write
   `docs/decisions/NNNN-title.md` from the template. If protocol values changed, bump
   `benchmark-spec/protocol.yaml` `version`.
4. **Consistency check** (quick): does `CLAUDE.md` repo map still match the tree? Do
   `docs/02-methodology.md` and `protocol.yaml` agree? Fix drift now.
5. **Commit** with a Conventional Commit message (`docs(progress): …`).

When the user asks "status?" → summarise `docs/PROGRESS.md` (phase, focus, next 3 actions, blockers).
