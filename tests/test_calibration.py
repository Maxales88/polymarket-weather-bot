import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from metrics.calibration import brier_score, platt_calibrate, find_best_alpha, calibration_slope


def test_brier_perfect():
    assert brier_score([1.0, 0.0], [1.0, 0.0]) == 0.0


def test_brier_worst():
    assert abs(brier_score([1.0, 0.0], [0.0, 1.0]) - 1.0) < 1e-9


def test_platt_range():
    # alpha=1 leaves monotonic; check range
    assert 0.0 <= platt_calibrate(0.5, 1.3) <= 1.0


def test_find_best_alpha_returns_in_grid():
    preds = [0.9, 0.1, 0.8, 0.2]
    outs = [1, 0, 1, 0]
    a = find_best_alpha(preds, outs)
    assert 0.8 <= a <= 2.5


def test_calibration_slope():
    s = calibration_slope([0.1, 0.5, 0.9], [0.0, 0.5, 1.0])
    assert s > 0
