"""Synthetic fixtures. SYNTHETIC DATA: for testing the pipeline only (CLAUDE.md rule 7).

Never copy these generated files into data/raw or use them in the paper.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make `benchkit` importable


def _record(**kw) -> dict:
    base = {
        "schema_version": "1.0", "protocol_version": "0.1.0", "synthetic": True,
        "timestamp_utc": "2026-11-09T10:00:00Z", "device_id": "dev-test-phone", "os": "android",
        "os_version": "14", "api_level": 34, "app_version": "0.0.0-test", "build_mode": "release",
        "runtime": "litert", "runtime_version": "0.0.0", "model_id": "mobilenetv3_large",
        "model_sha256": "0" * 64, "precision": "fp32", "delegate": "cpu", "threads": 4,
        "input_index": 0, "status": "ok", "thermal_status": "none",
    }
    base.update(kw)
    return base


def write_session(dirpath: Path, platform: str, session: int, *, inf_scale: float,
                  pre_scale: float, seed: int, n: int = 60) -> Path:
    """Write one synthetic session file with cold_start, warmup and measure records."""
    rng = np.random.default_rng(seed)
    run_id = str(uuid.UUID(int=seed))
    recs = [_record(platform=platform, session=session, run_id=run_id, phase="cold_start",
                    iteration=0, cold_start_ms=float(300 * pre_scale), model_load_ms=40.0)]
    for i in range(n):
        phase = "warmup" if i < 5 else "measure"
        pre = float(rng.lognormal(np.log(4 * pre_scale), 0.1))
        inf = float(rng.lognormal(np.log(10 * inf_scale), 0.1))
        post = float(rng.lognormal(np.log(0.5), 0.1))
        recs.append(_record(platform=platform, session=session, run_id=run_id, phase=phase, iteration=i,
                            input_index=i % 50, preprocess_ms=pre, inference_ms=inf, postprocess_ms=post,
                            end_to_end_ms=pre + inf + post + 0.2, pss_mb=120.0 * pre_scale,
                            cpu_pct=180.0, output_digest="cls:1"))
    path = dirpath / "dev-test-phone" / f"20261109_{platform}_mobilenetv3_large_fp32_cpu_s{session:02d}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def synthetic_raw(tmp_path: Path) -> Path:
    """Flutter: same inference speed as native, ~2x slower preprocessing (by construction)."""
    root = tmp_path / "raw"
    for s in range(1, 4):
        write_session(root, "flutter", s, inf_scale=1.0, pre_scale=2.0, seed=100 + s)
        write_session(root, "android_native", s, inf_scale=1.0, pre_scale=1.0, seed=200 + s)
    return root
