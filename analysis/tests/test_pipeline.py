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
    assert not comp.loc["inference_ms", "practical"]
    assert comp.loc["preprocess_ms", "practical"]
    assert 1.8 < comp.loc["preprocess_ms", "ratio"] < 2.2
    assert comp.loc["preprocess_ms", "session_median_ratio"] > 1.8
    assert "cold_start_ms" in comp.index

    produced = make_all(summ, comp.reset_index(), tmp_path / "fig", tmp_path / "tab")
    names = {p.name for p in produced}
    assert {"rq1-inference-ratio.pdf", "rq2-stage-decomposition.pdf", "rq1-inference.tex"} <= names
    assert all(p.stat().st_size > 0 for p in produced)


def test_exclusions_remove_runs(synthetic_raw):
    df = load_raw(synthetic_raw)
    victim = df["run_id"].iloc[0]
    kept, excl = apply_exclusions(df, [{"run_id": victim, "reason": "test"}])
    assert victim not in set(kept["run_id"]) and len(kept) + len(excl) == len(df)
