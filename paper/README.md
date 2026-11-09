# Paper

IEEE conference format (`IEEEtran`). Build with `make paper`, or upload to Overleaf:
upload `paper/` **and** `literature/references.bib`, then update the `\bibliography{}` path
in `main.tex` if the folder layout changes.

- `sections/`: one file per section; status tracked in `docs/PROGRESS.md`.
- `figures/`, `tables/`: **generated** by `make figures`. Never edit by hand.
- `\todo{}` marks missing content. Before submission: `grep -rn "\\todo" paper/sections` must return nothing.
- Use the `paper-writing` skill.
