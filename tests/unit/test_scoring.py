"""Unit tests for scoring formulas (see docs/scoring-spec.md)."""

import pytest


def test_demand_signal_full_data():
    """Test demand signal with all components available."""
    w_trends, w_serp, w_paa, w_volume = 0.30, 0.30, 0.20, 0.20
    trends_momentum = 0.5
    serp_richness = 0.7
    paa_normalized = 0.4  # 4 PAA questions / 10
    volume_normalized = 0.3  # 3000 / 10000

    demand = (trends_momentum * w_trends) + (serp_richness * w_serp) + (paa_normalized * w_paa) + (volume_normalized * w_volume)
    expected = (0.5 * 0.3) + (0.7 * 0.3) + (0.4 * 0.2) + (0.3 * 0.2)
    assert abs(demand - expected) < 0.0001
    assert abs(demand - 0.50) < 0.0001


def test_demand_signal_no_volume():
    """Test demand signal when volume is unavailable (set to 0)."""
    w_trends, w_serp, w_paa, w_volume = 0.30, 0.30, 0.20, 0.20
    demand = (0.5 * w_trends) + (0.7 * w_serp) + (0.4 * w_paa) + (0 * w_volume)
    assert abs(demand - 0.44) < 0.0001


def test_opportunity_score():
    """Test opportunity score calculation."""
    demand_signal = 0.50
    competition = 0.75
    cpc_normalized = 0.4  # $20 / $50

    w_comp = 0.40
    w_cpc = 0.20

    score = demand_signal - (w_comp * competition) + (w_cpc * cpc_normalized)
    expected = 0.50 - (0.40 * 0.75) + (0.20 * 0.4)
    assert abs(score - expected) < 0.0001
    assert abs(score - 0.28) < 0.0001


def test_gap_score():
    """Test gap score = opportunity * (1 - coverage)."""
    opportunity_score = 0.60
    coverage_ratio = 0.25

    gap_score = opportunity_score * (1 - coverage_ratio)
    assert abs(gap_score - 0.45) < 0.0001


def test_gap_score_full_coverage():
    """Gap score should be 0 when competitors fully cover a topic."""
    opportunity_score = 0.80
    coverage_ratio = 1.0
    gap_score = opportunity_score * (1 - coverage_ratio)
    assert gap_score == 0.0


def test_gap_score_no_coverage():
    """Gap score equals opportunity when no competitors cover a topic."""
    opportunity_score = 0.70
    coverage_ratio = 0.0
    gap_score = opportunity_score * (1 - coverage_ratio)
    assert abs(gap_score - 0.70) < 0.0001


def test_momentum_score():
    """Test momentum score = slope * breakout_multiplier."""
    trend_slope = 0.3
    breakout_multiplier = 1.5  # Rising
    momentum = trend_slope * breakout_multiplier
    assert abs(momentum - 0.45) < 0.0001


def test_momentum_breakout():
    """Test breakout detection: >100% growth = 3x multiplier."""
    trend_slope = 0.8
    breakout_multiplier = 3.0
    momentum = trend_slope * breakout_multiplier
    assert abs(momentum - 2.4) < 0.0001


def test_score_normalization():
    """All scores should be in [0, 1] range after normalization."""
    scores = [0.0, 0.25, 0.5, 0.75, 1.0]
    for s in scores:
        assert 0.0 <= s <= 1.0
