"""benchkit: analysis pipeline for the Flutter-vs-native on-device AI benchmark.

Pipeline: validate -> load (+exclusions) -> summarize -> compare -> figures.
See CLAUDE.md and .claude/skills/analyze-results/SKILL.md.
"""

from pathlib import Path

__version__ = "0.1.0"

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "benchmark-spec" / "result-schema.json"
PROTOCOL_PATH = REPO_ROOT / "benchmark-spec" / "protocol.yaml"
RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
EXCLUSIONS_PATH = REPO_ROOT / "data" / "exclusions.yaml"
FIGURES_DIR = REPO_ROOT / "paper" / "figures"
TABLES_DIR = REPO_ROOT / "paper" / "tables"

# Columns that identify one experimental configuration (platform excluded: it's the IV).
CONFIG_KEYS = ["device_id", "os", "model_id", "precision", "delegate"]

# Metric -> research-question family (Holm correction is applied within each family).
METRIC_FAMILIES: dict[str, str] = {
    "inference_ms": "RQ1",
    "preprocess_ms": "RQ2",
    "postprocess_ms": "RQ2",
    "end_to_end_ms": "RQ2",
    "pss_mb": "RQ3",
    "cpu_pct": "RQ3",
    "cold_start_ms": "RQ5",
    "model_load_ms": "RQ5",
}

# Which phase each metric is taken from.
METRIC_PHASE: dict[str, str] = {
    "cold_start_ms": "cold_start",
    "model_load_ms": "cold_start",
}
DEFAULT_PHASE = "measure"
