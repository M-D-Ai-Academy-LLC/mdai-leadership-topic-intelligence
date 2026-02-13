# Process Infographics (Layman-Friendly)

This page explains how the platform turns raw search signals into practical topic recommendations.

![Pipeline Overview](../visualizations/pipeline-overview.svg)

Use this visual in presentations, onboarding, and stakeholder updates.

## 1) Big Picture: From Question to Report

```mermaid
flowchart LR
    A["You ask: What leadership topics matter now?"] --> B["Collect signals\nGoogle + Trends + SERP clues"]
    B --> C["Group similar searches\ninto topic clusters"]
    C --> D["Understand intent\nlearn, buy, compare, certify"]
    D --> E["Check competitor coverage\nwhere others are weak"]
    E --> F["Score opportunities\nrank by demand and gap"]
    F --> G["Generate plain-English report\nwith next best topics"]
```

## 2) Data Inputs Explained in Plain English

```mermaid
mindmap
  root((Search Intelligence Inputs))
    Google Trends
      Rising interest over time
      Breakout signals
    Search Results Pages
      Related searches
      People also ask
      SERP features
    Optional Internal Data
      Site impressions
      Existing content coverage
```

## 3) How Topic Prioritization Works

Think of this like a triage board:

- High demand + low competitor coverage = highest priority
- High demand + high coverage = competitive but still valuable
- Low demand + low coverage = monitor, do not prioritize

```mermaid
quadrantChart
    title Topic Priority Map
    x-axis Low Competitor Coverage --> High Competitor Coverage
    y-axis Low Demand --> High Demand
    quadrant-1 Competitive Bet
    quadrant-2 Immediate Opportunity
    quadrant-3 Low Priority
    quadrant-4 Crowded + Low Return
    "Executive coaching for first-time leaders": [0.22, 0.84]
    "Leadership certification online": [0.71, 0.88]
    "Leadership quote wallpapers": [0.55, 0.22]
    "Emerging manager training": [0.18, 0.76]
```

## 4) What the Pipeline Does at Each Stage

```mermaid
sequenceDiagram
    participant User as Team
    participant R as Research Agent
    participant C as Cluster Agent
    participant I as Intent Agent
    participant G as Gap Agent
    participant Rep as Report Agent

    User->>R: Seed query (example: executive leadership)
    R-->>User: Keyword universe + trend enrichment
    R->>C: Keyword set
    C-->>User: Topic clusters + labels
    C->>I: Clustered topics
    I-->>User: Intent segments and personas
    I->>G: Segments + competitor signals
    G-->>User: Gap opportunities ranked
    G->>Rep: Final ranked inputs
    Rep-->>User: Actionable report and recommendations
```

## 5) A Simple Mental Model

```mermaid
flowchart TD
    A["Demand: Are people searching?"] --> B["Intent: Why are they searching?"]
    B --> C["Coverage: Has everyone already answered it?"]
    C --> D["Action: Build content where demand is real\nand coverage is weak"]
```

## 6) How to Read Final Recommendations

- Start with topics that are both rising and under-covered.
- Prefer clusters with clear buyer or learner intent.
- Use breakout topics for short-term campaigns.
- Use steady-demand topics for evergreen content.

## Reusable Asset

- Source graphic: `visualizations/pipeline-overview.svg`
- Recommended embed: `![Pipeline Overview](../visualizations/pipeline-overview.svg)`
