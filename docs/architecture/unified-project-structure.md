# Unified Project Structure

```plaintext
StockIQ/
├── .github/                        # Future CI/CD workflows
├── src/                            # Main application source
│   ├── main.py                     # FastAPI application entry
│   ├── routers/                    # API route definitions
│   │   ├── __init__.py
│   │   ├── assessment.py           # Assessment endpoints
│   │   ├── research.py             # Collaborative research APIs
│   │   └── reports.py              # Chunked report generation
│   ├── agents/                     # Enhanced AI agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py           # Base agent with research DB access
│   │   ├── assessment_agent.py     # Expertise assessment
│   │   ├── valuation_agent.py      # Owner-Returns FCF/Share analysis
│   │   ├── strategic_agent.py      # Competitive and market analysis
│   │   ├── historian_agent.py      # Company history and context
│   │   └── synthesis_agent.py      # Adaptive report synthesis
│   ├── services/                   # Enhanced business logic services
│   │   ├── __init__.py
│   │   ├── research_database.py    # Shared research database manager
│   │   ├── agent_coordinator.py    # Multi-agent collaboration
│   │   ├── chunked_generator.py    # Chunked report generation
│   │   └── pandoc_converter.py     # Markdown to PDF conversion
│   ├── models/                     # Enhanced data models
│   │   ├── __init__.py
│   │   ├── research_database.py    # Research file and metadata models
│   │   ├── assessment.py           # Assessment data structures
│   │   ├── collaboration.py        # Inter-agent collaboration models
│   │   ├── owner_returns.py        # Owner-Returns FCF/Share data models
│   │   └── reports.py              # Adaptive report formats
│   └── utils/                      # Enhanced utility functions
│       ├── __init__.py
│       ├── openai_client.py        # OpenAI SDK wrapper
│       ├── context_manager.py      # Token counting and context management
│       ├── markdown_processor.py   # Markdown parsing and merging
│       ├── file_operations.py      # Research database operations
│       ├── owner_returns_engine.py # Owner-Returns FCF/Share calculation engine
│       └── validators.py           # Input validation
├── static/                         # Enhanced frontend assets
│   ├── css/
│   │   ├── styles.css              # Base institutional styling
│   │   └── research_monitor.css    # Research progress styling
│   ├── js/
│   │   ├── app.js                  # Main frontend logic
│   │   ├── assessment.js           # Assessment interface
│   │   ├── research_monitor.js     # Real-time research monitoring
│   │   └── utils.js                # Frontend utilities
│   └── index.html                  # Enhanced single page application
├── research_database/              # Shared research database
│   ├── meta/
│   │   ├── file_index.yaml         # Master file index
│   │   ├── cross_references.yaml   # Research interconnections
│   │   └── agent_activity.yaml     # Agent contribution tracking
│   └── sessions/                   # Per-session research directories
│       └── {session_id}/           # Individual session research
│           ├── {ticker}/
│           │   ├── valuation/
│           │   ├── strategic/
│           │   ├── historical/
│           │   └── synthesis/
├── config/                         # Enhanced configuration
│   ├── agent_prompts/              # Specialized agent prompts
│   │   ├── valuation_owner_returns.txt   # Owner-Returns FCF/Share methodology
│   │   ├── strategic_collaboration.txt
│   │   ├── historian_context_integration.txt
│   │   ├── synthesis_adaptive_scaling.txt
│   │   └── assessment_expertise_evaluation.txt
│   ├── pandoc_templates/           # Professional PDF templates
│   │   ├── institutional_report.latex
│   │   ├── executive_summary.latex
│   │   └── shared_styles.sty
│   └── settings.py                 # Application configuration
├── tmp/                            # Temporary files and caches
│   ├── sessions/                   # Session data persistence
│   ├── reports/                    # Generated PDF cache
│   └── markdown_temp/              # Temporary markdown processing
├── docs/                           # Enhanced documentation
│   ├── prd.md                      # Product requirements
│   ├── brief.md                    # Project brief
│   ├── architecture.md             # This document (v2.0)
│   └── api_documentation/          # Auto-generated API docs
├── tests/                          # Comprehensive testing
│   ├── unit/
│   │   ├── agents/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/
│   │   ├── research_workflows/
│   │   └── api_endpoints/
│   └── e2e/
│       ├── complete_analysis_flow/
│       └── collaborative_research/
├── .env.example                    # Enhanced environment template
├── requirements.txt                # Updated Python dependencies
├── pyproject.toml                  # Python project config with new tools
├── CLAUDE.md                       # Development guidelines
└── README.md                       # Updated project overview
```
