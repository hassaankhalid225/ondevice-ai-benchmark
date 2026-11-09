# Data

| Folder | Content | Rules |
|---|---|---|
| `raw/` | JSONL exported from devices, one sub-folder per `device_id` | **Immutable, append-only.** Never edit or delete. Committed to git. |
| `processed/` | CSV/Parquet produced by `analysis/benchkit` | Generated. Safe to delete and regenerate. Not committed. |

Every raw file must:
1. Follow the naming convention (`docs/CONVENTIONS.md`).
2. Validate: `make validate`.
3. Be referenced in an `experiments/EXP-xxx.md` log.

Bad session? Don't delete it. Note it in the EXP log and add it to `data/exclusions.yaml`
with a reason. The analysis applies exclusions in code and reports them.
