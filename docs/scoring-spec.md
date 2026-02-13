# Scoring Specification

## Overview

This document defines all scoring formulas used in the Leadership Topic Intelligence system.
All scores are deterministic and reproducible given the same input data.

## 1. Demand Signal (Composite)

The primary demand indicator combining multiple data sources:

```
demand_signal = (trends_momentum * W_TRENDS) + (serp_richness * W_SERP) + (paa_count * W_PAA) + (volume_normalized * W_VOLUME)
```

### Default Weights

| Weight | Variable | Default | Description |
|--------|----------|---------|-------------|
| W_TRENDS | trends_momentum | 0.30 | Google Trends momentum score |
| W_SERP | serp_richness | 0.30 | SERP feature density |
| W_PAA | paa_count | 0.20 | People Also Ask count (normalized 0-1) |
| W_VOLUME | volume_normalized | 0.20 | Search volume (when available) |

### Component Definitions

- **trends_momentum**: `(avg_last_3mo - avg_prior_3mo) / avg_prior_3mo`, clamped to [-1, 1]
- **serp_richness**: Count of SERP features present / max possible features, range [0, 1]
- **paa_count**: `min(paa_questions / 10, 1.0)` — normalized to [0, 1]
- **volume_normalized**: `min(volume / 10000, 1.0)` — normalized to [0, 1]. **Optional** — set to 0 if unavailable.

### Important Notes

- Volume is **additive when available, not required**
- Google Trends returns relative interest (0-100), NOT absolute demand
- Google Search Console impressions/clicks are the **strongest signal** but opt-in only
- When GSC data is available: `demand_signal += gsc_impressions_normalized * W_GSC` (W_GSC = 0.40, other weights reduced proportionally)

## 2. Opportunity Score

Identifies high-potential topics considering both demand and competition:

```
opportunity_score = demand_signal - (W_COMPETITION * competition) + (W_CPC * cpc_normalized)
```

| Weight | Variable | Default | Description |
|--------|----------|---------|-------------|
| W_COMPETITION | competition | 0.40 | Competition index (0-1) |
| W_CPC | cpc_normalized | 0.20 | CPC indicator (optional) |

- **competition**: SERP competition index from SerpAPI, range [0, 1]
- **cpc_normalized**: `min(cpc / 50, 1.0)`. Higher CPC suggests commercial value. Optional — set to 0 if unavailable.

## 3. Gap Score

Identifies topics where competitors have low coverage relative to demand:

```
gap_score = opportunity_score * (1 - competitor_coverage_ratio)
```

- **competitor_coverage_ratio**: Fraction of competitor domains covering this topic, range [0, 1]
- Gap score is highest when opportunity is high AND competitors are NOT covering the topic

## 4. Momentum Score

Detects trending and breakout topics:

```
momentum_score = trend_slope * breakout_multiplier
```

- **trend_slope**: Linear regression slope of Google Trends data over last 12 months
- **breakout_multiplier**:
  - 1.0 = stable
  - 1.5 = rising (>20% growth)
  - 3.0 = breakout (>100% growth or Google Trends "Breakout" tag)

### Breakout Detection

A keyword is flagged as **breakout** when:
1. Google Trends labels it as "Breakout" (>5000% growth), OR
2. `momentum > 1.0` AND `trend_slope > 0.5`

## 5. Score Ranges

All final scores are normalized to [0, 1] for consistent ranking:

| Score | Range | Interpretation |
|-------|-------|---------------|
| 0.0 - 0.2 | Low | Minimal opportunity |
| 0.2 - 0.4 | Below Average | Limited potential |
| 0.4 - 0.6 | Moderate | Worth monitoring |
| 0.6 - 0.8 | High | Strong opportunity |
| 0.8 - 1.0 | Very High | Priority target |

## 6. Reproducibility

- All scores are deterministic given same input data
- Random states fixed (KMeans random_state=42)
- Results cached with run_id + config_hash
- Same input produces same output guaranteed
