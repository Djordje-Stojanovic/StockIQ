# Source Tree

## Overview

StockIQ follows a research-centric monorepo structure with shared knowledge base organization, featuring agent-based directories with a collaborative research database. This structure supports the 5-agent collaborative multi-specialist architecture for institutional-grade investment research.

## Repository Structure

**Structure:** Research-centric monorepo with shared knowledge base  
**Monorepo Tool:** None - using research database structure  
**Package Organization:** Agent-based directories with shared research database

## Directory Tree

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
│   │   ├── valuation_agent.py      # DCF and financial analysis
│   │   ├── strategic_agent.py      # Competitive and market analysis
│   │   ├── historian_agent.py      # Company history and context
│   │   └── synthesis_agent.py      # Adaptive report synthesis
│   ├── services/                   # Enhanced business logic services
│   │   ├── __init__.py
│   │   ├── research_database.py    # Shared research database manager
│   │   ├── agent_coordinator.py    # Multi-agent collaboration
│   │   ├── chunked_generator.py    # Chunked report generation
│   │   ├── pandoc_converter.py     # Markdown to PDF conversion
│   │   └── mcp_client.py           # MCP integration
│   ├── models/                     # Enhanced data models
│   │   ├── __init__.py
│   │   ├── research_database.py    # Research file and metadata models
│   │   ├── assessment.py           # Assessment data structures
│   │   ├── collaboration.py        # Inter-agent collaboration models
│   │   └── reports.py              # Adaptive report formats
│   └── utils/                      # Enhanced utility functions
│       ├── __init__.py
│       ├── openai_client.py        # OpenAI SDK wrapper
│       ├── context_manager.py      # Token counting and context management
│       ├── markdown_processor.py   # Markdown parsing and merging
│       ├── file_operations.py      # Research database operations
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
│   │   ├── valuation_deep_research.txt
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

## Key Directory Purposes

### Core Application (`src/`)
- **main.py**: FastAPI application entry point
- **routers/**: API endpoints organized by functionality
- **agents/**: Five specialized AI agents for collaborative research
- **services/**: Business logic and cross-cutting concerns
- **models/**: Pydantic models for data validation
- **utils/**: Shared utility functions

### Frontend Assets (`static/`)
- **Vanilla HTML/CSS/JS**: Simple web interface
- **No complex framework**: Eliminates overhead for basic functionality
- **Real-time monitoring**: Research progress visualization

### Research Database (`research_database/`)
- **File-based .md system**: Natural for LLM reading/writing
- **Session isolation**: Per-session research directories
- **Agent organization**: Structured by research specialty
- **Metadata tracking**: YAML-based indexing and cross-references

### Configuration (`config/`)
- **Agent prompts**: Specialized prompts for each research agent
- **Pandoc templates**: Professional LaTeX templates for PDF generation
- **Application settings**: Centralized configuration management

### Development & Operations
- **tests/**: Comprehensive test coverage including agent collaboration
- **docs/**: Architecture documentation and API specs
- **tmp/**: Temporary files for report generation
- **.env**: Environment configuration (not committed)

## File Organization Principles

### Module Limits
- **Files**: Maximum 500 lines of code
- **Functions**: Under 50 lines each
- **Classes**: Under 100 lines each
- **Line length**: 100 characters maximum

### Naming Conventions
- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Research Database Structure
Each research session creates a structured hierarchy:
```
research_database/sessions/{session_id}/{ticker}/
├── valuation/          # DCF analysis, peer comparison
├── strategic/          # Competitive analysis, market dynamics
├── historical/         # Company timeline, leadership analysis
└── synthesis/          # Final report sections and thesis
```

### Virtual Environment
- **Use `venv_linux`** for all Python command execution
- **Isolate dependencies** from system Python
- **Consistent development environment** across all development activities

Keep it organized. One purpose per directory.