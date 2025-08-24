# Research Database Schema

## File-Based Research Database Structure

The research database uses a hierarchical file system with YAML metadata and markdown content:

```
research_database/
├── meta/
│   ├── file_index.yaml              # Master index with all file metadata
│   ├── cross_references.yaml        # Network of research connections
│   ├── agent_activity.yaml          # Track agent contributions and timing
│   └── session_metadata.yaml        # Session-specific research context
├── {ticker_symbol}/                 # Per-company research directory
│   ├── valuation/
│   │   ├── owner_returns_analysis_v1.md    # Owner-Returns FCF/Share methodology
│   │   ├── peer_comparison_v1.md    # Industry peer benchmarking
│   │   ├── financial_metrics_v1.md  # Key financial ratios and trends
│   │   └── comments/
│   │       ├── strategic_critique_v1.md    # Strategic agent feedback
│   │       └── historical_context_v1.md    # Historical agent additions
│   ├── strategic/
│   │   ├── competitive_moat_v1.md   # Competitive advantage analysis
│   │   ├── market_dynamics_v1.md    # Industry and market analysis
│   │   ├── strategic_risks_v1.md    # Risk assessment and mitigation
│   │   └── comments/
│   │       ├── valuation_implications_v1.md
│   │       └── historical_patterns_v1.md
│   ├── historical/
│   │   ├── company_timeline_v1.md   # Chronological company history
│   │   ├── leadership_analysis_v1.md # Management track record
│   │   ├── crisis_management_v1.md  # How company handled challenges
│   │   └── comments/
│   │       ├── valuation_context_v1.md
│   │       └── strategic_validation_v1.md
│   └── synthesis/
│       ├── investment_thesis_v1.md  # Final investment recommendation
│       ├── executive_summary_v1.md  # High-level findings
│       └── sections/
│           ├── introduction_v1.md
│           ├── valuation_section_v1.md
│           ├── strategic_section_v1.md
│           ├── historical_section_v1.md
│           └── conclusion_v1.md
```

## Research File Format Standard

Each research file follows this structure:

```markdown
---
title: "Owner-Returns FCF/Share Analysis for ASML Holding N.V."
author: "ValuationAgent"
created_at: "2025-08-21T10:00:00Z"
updated_at: "2025-08-21T10:30:00Z"
version: 1
topic: "valuation"
subtopic: "owner_returns_model"
ticker: "ASML"
session_id: "sess_123456"
cross_references:
  - "strategic/competitive_moat_v1.md"
  - "historical/company_timeline_v1.md"
confidence_level: 0.85
data_sources:
  - "MCP Financial Data Server"
  - "ASML 2024 Annual Report (10-K)"
  - "Semiconductor Industry Analysis"
  - "Peer Company Financials"
word_count: 2847
estimated_reading_time: "12 minutes"
---
