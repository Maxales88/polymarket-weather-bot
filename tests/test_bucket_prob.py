import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from signals.bucket_prob import bucket_probability


def test_bucket_prob_range():
    p = bucket_probability(70.0, 2.0, 68.0, 72.0, df=4)
    assert 0.0 <= p <= 1.0
    assert p > 0.3


def test_bucket_prob_zero_std():
    assert bucket_probability(70.0, 0.0, 68.0, 72.0) == 0.0


def test_bucket_prob_invalid_range():
    assert bucket_probability(70.0, 2.0, 72.0, 68.0) == 0.0
