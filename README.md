# mdai-leadership-topic-intelligence

**M&D AI Academy — Leadership Topic Intelligence**

Search analytics and SEO intelligence platform for discovering what leadership topics corporations are actively searching for.

## Overview

This system combines multiple search intelligence sources (SerpAPI, Google Trends, Google Search Console) with AI-powered analysis to identify high-demand leadership training topics, content gaps, and emerging trends.

## Features

- **Keyword Discovery**: SerpAPI-powered SERP intelligence with related searches and People Also Ask
- **Trend Analysis**: Google Trends integration for momentum scoring and breakout detection
- **Topic Clustering**: TF-IDF + KMeans clustering with LLM-generated labels
- **Intent Segmentation**: Query intent classification (training, coaching, certification, etc.)
- **Competitive Analysis**: Lightweight content scraping and coverage mapping
- **Content Gap Detection**: Identify underserved topics with high demand
- **Scoring Engine**: Composite demand signals, opportunity scores, and gap scores
- **Report Generation**: Markdown reports with actionable insights

## Tech Stack

- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Search Intelligence**: SerpAPI, Google Trends (pytrends)
- **Clustering**: scikit-learn (TF-IDF + KMeans)
- **Storage**: SQLite via SQLAlchemy
- **LLM**: OpenAI + Anthropic (for cluster labeling, persona generation)
- **CLI**: Click + Rich

## Quick Start

```bash
# Clone
git clone https://github.com/M-D-Ai-Academy-LLC/mdai-leadership-topic-intelligence.git
cd mdai-leadership-topic-intelligence

# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in API keys

# Run
python run.py --task full -q "executive leadership"
```

## Architecture

```
src/
├── agents/          # Agent implementations
├── api/             # FastAPI endpoints
├── contracts/       # Strict I/O types per agent
├── core/            # Configuration and settings
├── integrations/    # External API clients
├── models/          # Pydantic data models
├── pipeline/        # Pipeline orchestration
├── storage/         # SQLite + caching layer
└── utils/           # Shared utilities
```

## Scoring Model

See `docs/scoring-spec.md` for complete scoring formulas.

## License

AGPL-3.0 — Copyright (c) 2026 M&D AI Academy LLC
