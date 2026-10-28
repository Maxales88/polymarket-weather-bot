import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from broker.sizing import kelly_fraction_yes, size_position


def test_kelly_yes_basic():
    f = kelly_fraction_yes(0.7, 0.5)
    assert abs(f - 0.4) < 1e-9


def test_kelly_no_edge():
    assert kelly_fraction_yes(0.5, 0.5) == 0.0


def test_size_position_fractional():
    amt = size_position(0.7, 0.5, bankroll=1000.0, kelly_multiplier=0.25, max_trade_usdc=1000)
    # full kelly 0.4 * 0.25 = 0.1 -> 100
    assert abs(amt - 100.0) < 1e-6


def test_size_position_zero_on_no_edge():
    assert size_position(0.5, 0.5, bankroll=1000.0) == 0.0


def test_size_position_cap():
    amt = size_position(0.99, 0.5, bankroll=10000.0, kelly_multiplier=1.0, max_trade_usdc=15.0)
    assert amt <= 15.0
