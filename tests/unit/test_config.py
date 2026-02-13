"""Unit tests for configuration settings."""

import os


def test_settings_defaults():
    from core.config import Settings
    s = Settings(
        _env_file=None,
        enable_serpapi=True,
        enable_trends=True,
        no_network_mode=True,
    )
    assert s.default_model == "gpt-4o-mini"
    assert s.max_retries == 3
    assert s.enable_serpapi is True


def test_feature_flags_defaults():
    from core.config import Settings
    s = Settings(_env_file=None)
    assert s.enable_gsc is False
    assert s.enable_news is False
    assert s.enable_firmographics is False


def test_brand_colors():
    from core.config import Settings
    s = Settings(_env_file=None)
    colors = s.brand_colors
    assert colors["primary"] == "#5CBDBD"
    assert colors["secondary"] == "#3A9B9B"
    assert colors["tertiary"] == "#2D7A7A"


def test_seed_keywords():
    from core.config import Settings
    s = Settings(_env_file=None)
    assert "executive leadership" in s.seed_keywords
    assert len(s.seed_keywords) >= 3
