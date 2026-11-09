---
name: literature-review
description: Find, verify, read, note and cite papers for the Flutter-vs-native on-device AI benchmark. Use when searching literature, adding BibTeX, writing paper notes, or drafting related work.
---

# Literature Review

## Hard rule
**Never add a reference you have not seen on an authoritative page** (DOI resolver,
publisher site, arXiv, DBLP, ACL Anthology, IEEE Xplore, ACM DL). No reference "from memory".
If metadata can't be verified, keep `note = {TODO-verify}` and do not cite it in the paper.

## Workflow
1. **Search** using the queries in `literature/reading-list.md` → "Gaps to fill". Use Semantic
   Scholar / Google Scholar / DBLP / arXiv. Prefer peer-reviewed, 2019+, plus seminal older work.
2. **Triage** by title + abstract: add a row to the "Found" table with relevance ★–★★★ and
   status `to-read`. Reject off-topic papers quickly.
3. **Verify metadata** and add BibTeX to `literature/references.bib`:
   - key: `<firstauthorlowercase><year><firstsignificantword>`
   - include `doi` or `url`; full author list (no "and others" in final version)
   - remove `note = {TODO-verify}` only after checking the authoritative page
4. **Read** ★★★ papers fully, ★★ papers' method + results. Create
   `literature/notes/<key-ish>.md` from `_template.md`. Record numbers with page/figure refs.
5. **Update status** in `reading-list.md`.
6. **Synthesise**: group into themes for Related Work:
   (a) mobile DL benchmarking, (b) cross-platform framework performance,
   (c) runtime/delegate studies, (d) benchmarking methodology & statistics.
   For each theme: what's known → what's missing → how we fill it (the gap statement).

## Output quality
- Related work compares and contrasts; it is not a list of summaries.
- End each theme paragraph with the gap our study fills.
- Cite with `\cite{key}` in `paper/sections/02-related-work.tex`.

## Done when
≥ 15 papers `read` with notes, ≥ 5 on cross-platform performance, all cited entries verified,
related-work section drafted. Then update `docs/PROGRESS.md`.
