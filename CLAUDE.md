# CLAUDE.md: Operating Manual for AI Agents & Developers

> Read this file fully before doing anything in this repository.
> Then read `docs/PROGRESS.md` to see the current state and what to do next.

## 1. Project in one paragraph

**Title (working):** *Cross-Platform vs Native: A Performance Benchmark of On-Device Deep
Learning Inference in Flutter and Native Android/iOS Applications.*

We measure how much performance (latency, memory, CPU, energy, app size, cold start, FPS)
is lost or gained when the **same** on-device deep learning model is run through a
**Flutter** app versus a **native** (Kotlin / Swift) app, using the **same runtime
(LiteRT, formerly TensorFlow Lite)**, the same model files, the same inputs and the same
measurement harness. The output is an IEEE-format paper (arXiv preprint + conference
submission), plus a fully reproducible open-source benchmark suite.

- **Author:** Hassaan Khalid (BSSE, University of Sargodha). No supervisor: independent work.
- **Primary use:** final-year mandatory research paper; portfolio evidence for
  international research programs (Sakura Science, KAUST VSRP, Sabancı PURE, USTC FuSEP).

## 2. Session protocol (do this every time)

**At session start**
1. Read `docs/PROGRESS.md`. It is the single source of truth for status and next actions.
2. Read the docs relevant to the task (see the repo map below). Do not guess the methodology:
   it is defined in `docs/02-methodology.md` and `benchmark-spec/`.
3. If a task matches a skill in `.claude/skills/`, follow that skill.

**At session end**
1. Update `docs/PROGRESS.md`: tick finished items, update "Current focus" and "Next actions".
2. Add a dated entry to `CHANGELOG.md` (what changed, not how).
3. If you made a design or methodology decision, write an ADR in `docs/decisions/`
   (use `docs/decisions/0000-template.md`). Never change methodology silently.

## 3. Golden rules (non-negotiable: research integrity)

1. **Never fabricate data, results, or citations.** If a number is not produced by a script
   from a file in `data/raw/`, it does not go in the paper. If a reference cannot be verified
   (DOI / publisher page / arXiv), it does not go in `references.bib`.
2. **`data/raw/` is append-only and immutable.** Never edit, clean, or delete raw files.
   All cleaning happens in code (`analysis/benchkit`) and writes to `data/processed/`.
3. **Every number in the paper is traceable**: figure/table, then script, then processed file,
   then raw files. Figures and tables are *generated*, never hand-edited.
4. **Parity first.** Flutter and native apps must do *identical* work (same model bytes, same
   preprocessing, same threads/delegate, same iteration counts). Any unavoidable difference
   is documented in `benchmark-spec/harness-contract.md` and discussed in the paper.
5. **Release/profile builds only** for measurements. Flutter debug mode (JIT) is invalid data.
6. **Methodology changes need an ADR** and a version bump in `benchmark-spec/protocol.yaml`.
   Data collected under different protocol versions is never pooled.
7. Synthetic data exists **only** in `analysis/tests/fixtures/` for tests, and is labelled
   `synthetic: true`. It must never reach `data/` or `paper/`.
8. Paper prose is written to be the author's own: clear, specific, no filler or hype.
   AI may draft and edit, but the author must understand and be able to defend every sentence.

## 4. Repository map

```
CLAUDE.md                  ← you are here (agent/dev operating manual)
AGENTS.md                  ← pointer for non-Claude agents (Codex, Cursor, Copilot…)
README.md                  ← public-facing overview + quickstart
CHANGELOG.md               ← dated log of changes
Makefile                   ← make test | validate | summarize | compare | figures | paper
.claude/
  settings.json            ← permissions (raw data is write-protected)
  skills/                  ← task playbooks (see §5)
docs/
  00-project-overview.md   ← goals, scope, contributions, people, venues
  01-research-questions.md ← RQs + hypotheses (H1..Hn)
  02-methodology.md        ← experimental protocol (THE reference)
  03-metrics.md            ← exact definition + measurement method of every metric
  04-device-matrix.md      ← devices, OS versions, how to register a device
  05-roadmap.md            ← phases, milestones, deadlines
  PROGRESS.md              ← live status + next actions (update every session)
  CONVENTIONS.md           ← naming, commits, branches, file formats
  decisions/               ← ADRs (architecture/methodology decision records)
literature/
  references.bib           ← verified BibTeX only (paper/ uses this file)
  reading-list.md          ← papers to read / read, with status
  notes/                   ← one markdown note per paper (template inside)
benchmark-spec/
  protocol.yaml            ← machine-readable protocol (iterations, warmup, configs)
  result-schema.json       ← JSON Schema every raw result record must satisfy
  harness-contract.md      ← what every benchmark app MUST implement identically
models/
  manifest.yaml            ← model registry (id, task, precision, sha256, source, license)
  README.md                ← how to obtain/convert/verify models (binaries are git-ignored)
apps/
  flutter_bench/           ← Flutter harness app (to be built, Phase 2)
  android_native_bench/    ← Kotlin harness app (to be built, Phase 2)
  ios_native_bench/        ← Swift harness app (optional, Phase 2b)
experiments/               ← one EXP-xxx.md log per data-collection campaign
data/
  raw/                     ← immutable JSONL exported from devices
  processed/               ← generated by analysis (safe to delete and regenerate)
analysis/
  benchkit/                ← Python package: validate, summarize, compare, plot
  tests/                   ← pytest (uses synthetic fixtures only)
  requirements.txt
paper/
  main.tex                 ← IEEEtran conference paper (Overleaf-ready)
  sections/                ← one .tex file per section
  figures/ tables/         ← GENERATED by analysis, never hand-edited
```

## 5. Skills (playbooks in `.claude/skills/`)

| Skill | Use when |
|---|---|
| `literature-review` | finding, verifying, reading and citing papers |
| `benchmark-app-dev` | building or changing the Flutter / native harness apps |
| `run-experiment` | collecting data on a physical device |
| `analyze-results` | validating raw data, statistics, generating figures/tables |
| `paper-writing` | drafting or revising any paper section |
| `progress-update` | end-of-session bookkeeping (PROGRESS, CHANGELOG, ADRs) |

## 6. Commands

```bash
# one-time
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r analysis/requirements.txt

# daily
make test                     # pytest for analysis pipeline
make validate                 # schema-check every file in data/raw/
make summarize                # → data/processed/summary.csv
make compare                  # → data/processed/comparisons.csv (stats tests)
make figures                  # → paper/figures/*.pdf + paper/tables/*.tex
make paper                    # build paper/main.pdf (needs latexmk), or upload paper/ to Overleaf
```
No `make` on Windows? Run the underlying command, e.g.
`python -m benchkit validate data/raw` (from the `analysis/` folder, or with `PYTHONPATH=analysis`).

## 7. Conventions (summary; full version in `docs/CONVENTIONS.md`)

- **Commits:** Conventional Commits: `feat(app-flutter): …`, `data(exp-002): …`,
  `docs(method): …`, `paper(results): …`, `fix(analysis): …`.
- **Raw file name:** `data/raw/<device_id>/<YYYYMMDD>_<platform>_<model_id>_<delegate>_s<NN>.jsonl`
- **IDs:** devices `dev-<brand>-<model>` (e.g. `dev-samsung-a14`), models from `models/manifest.yaml`,
  experiments `EXP-001`…, ADRs `NNNN-kebab-title.md`, hypotheses `H1`…
- **Python:** 3.10+, type hints, `ruff`-clean, functions small and pure where possible.
- **Units:** milliseconds (ms), megabytes (MB = 10^6 bytes, state it), percent (%), milliamp-hours (mAh).

## 8. Definition of done

- **Code:** tests pass, works on a clean clone, documented in the relevant README.
- **Data:** validates against `result-schema.json`, logged in an `experiments/EXP-xxx.md`.
- **Paper section:** every claim cited or backed by a generated figure/table; review
  status noted in `docs/PROGRESS.md`.

## 9. Things an agent must NOT do

- Do not invent benchmark numbers, "example results", or citations, not even as placeholders
  in the paper. Use `\todo{}` markers instead.
- Do not touch `data/raw/` (except adding new files exported from devices).
- Do not change `benchmark-spec/protocol.yaml` without an ADR.
- Do not commit model binaries, keystores, `.env`, or personal data.
- Do not "simplify" the statistics (e.g. switch to mean ± SD, t-tests) without an ADR.
