import numpy as np
import pytest

from benchkit.stats import bootstrap_median_ratio_ci, cliffs_delta, cliffs_magnitude, compare_samples, describe, holm


def brute_cliffs(x, y):
    gt = sum(1 for a in x for b in y if a > b)
    lt = sum(1 for a in x for b in y if a < b)
    return (gt - lt) / (len(x) * len(y))


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_cliffs_delta_matches_bruteforce(seed):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 10, 40).astype(float)   # integers → ties exercised
    y = rng.integers(0, 12, 35).astype(float)
    assert cliffs_delta(x, y) == pytest.approx(brute_cliffs(x, y), abs=1e-12)


def test_cliffs_extremes_and_magnitude():
    assert cliffs_delta([5, 6, 7], [1, 2, 3]) == pytest.approx(1.0)
    assert cliffs_delta([1, 2, 3], [5, 6, 7]) == pytest.approx(-1.0)
    assert cliffs_magnitude(0.1) == "negligible"
    assert cliffs_magnitude(-0.2) == "small"
    assert cliffs_magnitude(0.4) == "medium"
    assert cliffs_magnitude(0.9) == "large"


def test_holm_known_values():
    # classic example: p = [0.01, 0.04, 0.03, 0.005], m = 4
    adj = holm(np.array([0.01, 0.04, 0.03, 0.005]))
    assert adj.tolist() == pytest.approx([0.03, 0.06, 0.06, 0.02])


def test_holm_nan_passthrough_and_cap():
    adj = holm(np.array([0.5, np.nan, 0.9]))
    assert np.isnan(adj[1])
    assert adj[0] == pytest.approx(1.0) and adj[2] == pytest.approx(1.0)


def test_bootstrap_ratio_contains_truth():
    rng = np.random.default_rng(7)
    x = rng.lognormal(np.log(20), 0.1, 300)
    y = rng.lognormal(np.log(10), 0.1, 300)
    r, lo, hi = bootstrap_median_ratio_ci(x, y, resamples=2000, seed=1)
    assert lo < 2.0 < hi and lo <= r <= hi


def test_bootstrap_is_deterministic():
    x, y = np.arange(1, 50.0), np.arange(2, 60.0)
    assert bootstrap_median_ratio_ci(x, y, resamples=500, seed=3) == bootstrap_median_ratio_ci(x, y, resamples=500, seed=3)


def test_describe_and_compare():
    d = describe(np.array([1, 2, 3, 4, 100.0]))
    assert d["median"] == 3 and d["n"] == 5
    c = compare_samples(np.full(30, 2.0) + np.linspace(0, 0.1, 30), np.full(30, 1.0) + np.linspace(0, 0.1, 30),
                        resamples=200)
    assert c.delta == pytest.approx(1.0) and c.p < 1e-6 and c.ratio > 1.8
