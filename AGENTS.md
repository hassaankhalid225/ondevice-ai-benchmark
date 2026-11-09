# AGENTS.md

This repository's agent instructions live in **[CLAUDE.md](CLAUDE.md)**. They apply to every
AI coding agent (Claude Code, Codex, Cursor, Copilot, Gemini, etc.) and to human contributors.

Quick start for any agent:
1. Read `CLAUDE.md` (rules, repo map, commands).
2. Read `docs/PROGRESS.md` (current status and next actions).
3. Task playbooks are in `.claude/skills/<skill>/SKILL.md`. They are plain markdown, so follow
   them even if your tool doesn't support skills natively.
4. End of session: update `docs/PROGRESS.md` and `CHANGELOG.md`.

The most important rule: **never fabricate data, results or citations.**
