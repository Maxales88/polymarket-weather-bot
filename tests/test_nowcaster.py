import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from signals.nowcaster import observation_weight, blend


def test_observation_weight_range():
    from datetime import datetime
    now = datetime(2026, 1, 1, 12, 0)
    close = datetime(2026, 1, 1, 23, 59)
    w = observation_weight(now, close)
    assert 0 <= w <= 0.8


def test_blend_no_obs():
    assert blend(70.0, None, 0.5) == 70.0


def test_blend_with_obs():
    b = blend(70.0, 72.0, 0.5)
    assert 70.0 < b < 72.0
