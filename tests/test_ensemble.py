import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from signals.ensemble import mean, std, combine


def test_mean():
    assert mean([1, 2, 3]) == 2.0


def test_std():
    assert std([1, 2, 3]) > 0


def test_combine():
    m, s, sp = combine({"a": 70.0, "b": 72.0})
    assert m == 71.0
    assert s > 0
