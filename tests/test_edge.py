import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from signals.edge_calculator import edge, expected_value, adaptive_min_edge


def test_edge_yes():
    assert abs(edge(0.7, 0.5) - 0.2) < 1e-9


def test_expected_value_subtracts_fee():
    ev = expected_value(0.7, 0.5)
    assert ev < 0.2


def test_adaptive_min_edge():
    assert adaptive_min_edge(0.08, 3) < 0.08
    assert adaptive_min_edge(0.08, 48) > 0.08
