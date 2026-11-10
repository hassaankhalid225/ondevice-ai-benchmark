import json

from benchkit.compare import compare_all
from benchkit.figures import make_all
from benchkit.io import apply_exclusions, load_raw
from benchkit.summarize import summarize
from benchkit.validate import load_validator, validate_file, validate_tree


def test_fixture_validates_only_when_synthetic_allowed(synthetic_raw):
    assert all(r.ok for r in validate_tree(synthetic_raw, allow_synthetic=True))
    assert not any(r.ok for r in validate_tree(synthetic_raw, allow_synthetic=False))


def test_validator_catches_bad_records(tmp_path):
    bad = tmp_path / "20261109_flutter_mobilenetv3_large_fp32_cpu_s01.jsonl"
    bad.write_text(json.dumps({"platform": "android_native", "session": 2}) + "\n{not json}\n")
    rep = validate_file(bad, load_validator(), allow_synthetic=True, max_errors=100)
    text = "\n".join(rep.errors)
    assert "required property" in text and "invalid JSON" in text and "disagrees with filename" in text


def test_validator_rejects_bad_filename(tmp_path):
    f = tmp_path / "results.jsonl"
    f.write_text("")
    assert any("filename" in e for e in validate_file(f, load_validator()).errors)


def test_end_to_end_pipeline_recovers_constructed_effects(synthetic_raw, tmp_path):
    df = load_raw(synthetic_raw)
    summ = summarize(df)
    assert set(summ["platform"]) == {"flutter", "android_native"}
    # warm-up excluded: 55 measure iterations x 3 sessions
    inf = summ[(summ.metric == "inference_ms") & (summ.platform == "flutter")]
    assert int(inf["n"].iloc[0]) == 165 and int(inf["n_sessions"].iloc[0]) == 3

    comp = compare_all(df, resamples=500).set_index("metric")
    # constructed: identical inference, 2x preprocessing
    assert comp.loc["inference_native_ms", "family"] == "RQ1"
    assert not comp.loc["inference_native_ms", "practical"]
    assert not comp.loc["inference_ms", "practical"]
    assert 1.7 < comp.loc["boundary_overhead_ms", "ratio"] < 2.3
    assert comp.loc["preprocess_ms", "practical"]
    assert 1.8 < comp.loc["preprocess_ms", "ratio"] < 2.2
    assert comp.loc["preprocess_ms", "iteration_median_ratio"] > 1.8
    # unit of analysis is the session (ADR-0007): 3 sessions, so p cannot reach significance
    assert comp.loc["preprocess_ms", "n_x"] == 3
    assert not comp.loc["preprocess_ms", "significant"]
    assert "cold_start_ms" in comp.index

    produced = make_all(summ, comp.reset_index(), tmp_path / "fig", tmp_path / "tab")
    names = {p.name for p in produced}
    assert {"rq1-inference-ratio.pdf", "rq2-stage-decomposition.pdf", "rq1-inference.tex"} <= names
    assert all(p.stat().st_size > 0 for p in produced)


def test_derived_timing_metrics(synthetic_raw):
    df = load_raw(synthetic_raw)
    m = df[df.phase == "measure"]
    assert ((m.inference_ms - m.inference_native_ms - m.boundary_overhead_ms).abs() < 1e-9).all()
    assert ((m.timer_residual_ms - 0.2).abs() < 1e-9).all()


def test_validator_requires_native_inference_time(synthetic_raw):
    path = next(synthetic_raw.rglob("*.jsonl"))
    recs = [json.loads(line) for line in path.read_text().splitlines()]
    for r in recs:
        r.pop("inference_native_ms", None)
    path.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    rep = validate_file(path, load_validator(), allow_synthetic=True, max_errors=100)
    assert any("inference_native_ms" in e for e in rep.errors)


def test_exclusions_remove_runs(synthetic_raw):
    df = load_raw(synthetic_raw)
    victim = df["run_id"].iloc[0]
    kept, excl = apply_exclusions(df, [{"run_id": victim, "reason": "test"}])
    assert victim not in set(kept["run_id"]) and len(kept) + len(excl) == len(df)


def test_warmup_model_load_idle_and_device_label(tmp_path):
    from benchkit.figures import _short_device
    from benchkit.summarize import metric_frame

    assert _short_device("dev-infinix-mobility-limited-infinix-x650c") == "infinix-x650c"
    assert _short_device("dev-samsung-a14") == "samsung-a14"

    # Model load collected during warmup iteration 0, idle_pss_mb in phase idle
    recs = []
    for plat, scale in [("flutter", 2.0), ("android_native", 1.0)]:
        for s in range(1, 4):
            recs.append({
                "device_id": "dev-test-phone", "os": "android", "model_id": "mobilenetv3_large",
                "precision": "fp32", "delegate": "cpu", "platform": plat, "session": s,
                "phase": "warmup", "status": "ok", "model_load_ms": 20.0 * scale,
            })
        for i in range(4):
            recs.append({
                "device_id": "dev-test-phone", "os": "android", "model_id": "app_baseline",
                "precision": "fp32", "delegate": "cpu", "platform": plat, "session": 1,
                "phase": "idle", "status": "ok", "idle_pss_mb": 35.0 * scale,
            })
    import pandas as pd
    df = pd.DataFrame(recs)
    assert len(metric_frame(df, "model_load_ms")) == 6
    assert len(metric_frame(df, "idle_pss_mb")) == 8
    comp = compare_all(df, metrics=["model_load_ms", "idle_pss_mb"], resamples=200).set_index("metric")
    assert comp.loc["model_load_ms", "n_x"] == 3 and 1.9 < comp.loc["model_load_ms", "ratio"] < 2.1
    assert comp.loc["idle_pss_mb", "n_x"] == 4 and comp.loc["idle_pss_mb", "family"] == "RQ3"
