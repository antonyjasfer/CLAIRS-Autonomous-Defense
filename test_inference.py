import pytest
from inference import _classify_trend

def test_classify_trend_unknown():
    assert _classify_trend([], "pps") == "UNKNOWN"
    assert _classify_trend([{"pps": 100}], "pps") == "UNKNOWN"

def test_classify_trend_pps_surging():
    # delta > 1000
    history = [{"pps": 100}, {"pps": 1101}]
    assert _classify_trend(history, "pps") == "SURGING"

def test_classify_trend_pps_rising():
    # 200 < delta <= 1000
    history = [{"pps": 100}, {"pps": 301}]
    assert _classify_trend(history, "pps") == "RISING"
    history_edge = [{"pps": 100}, {"pps": 1100}]
    assert _classify_trend(history_edge, "pps") == "RISING"

def test_classify_trend_pps_falling():
    # delta < -200
    history = [{"pps": 500}, {"pps": 299}]
    assert _classify_trend(history, "pps") == "FALLING"

def test_classify_trend_pps_stable():
    # -200 <= delta <= 200
    history = [{"pps": 500}, {"pps": 500}]
    assert _classify_trend(history, "pps") == "STABLE"

    history_edge_high = [{"pps": 100}, {"pps": 300}]
    assert _classify_trend(history_edge_high, "pps") == "STABLE"

    history_edge_low = [{"pps": 300}, {"pps": 100}]
    assert _classify_trend(history_edge_low, "pps") == "STABLE"

def test_classify_trend_other_rising():
    # delta > 10
    history = [{"cpu": 20}, {"cpu": 31}]
    assert _classify_trend(history, "cpu") == "RISING"

def test_classify_trend_other_falling():
    # delta < -5
    history = [{"cpu": 50}, {"cpu": 44}]
    assert _classify_trend(history, "cpu") == "FALLING"

def test_classify_trend_other_stable():
    # -5 <= delta <= 10
    history = [{"cpu": 50}, {"cpu": 50}]
    assert _classify_trend(history, "cpu") == "STABLE"

    history_edge_high = [{"cpu": 50}, {"cpu": 60}]
    assert _classify_trend(history_edge_high, "cpu") == "STABLE"

    history_edge_low = [{"cpu": 50}, {"cpu": 45}]
    assert _classify_trend(history_edge_low, "cpu") == "STABLE"

def test_classify_trend_history_length_greater_than_2():
    # delta is history[-1] - history[0]
    # history length > 2
    # pps diff: 500 - 100 = 400 (RISING)
    history = [{"pps": 100}, {"pps": 9000}, {"pps": 500}]
    assert _classify_trend(history, "pps") == "RISING"
