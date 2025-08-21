# Backend Architecture

## Service Architecture

### Controller/Route Organization
```
src/
├── main.py                         # FastAPI application entry point
├── routers/
│   ├── assessment.py               # Assessment endpoints
│   ├── research.py                 # Research coordination endpoints
│   └── reports.py                  # Report generation endpoints
├── services/
│   ├── research_database.py        # Shared research database management
│   ├── agent_coordinator.py        # Multi-agent collaboration coordination
│   ├── chunked_generator.py        # Chunked report generation
│   └── pandoc_converter.py         # Markdown to PDF conversion
├── agents/
│   ├── base_agent.py               # Base agent with research database access
│   ├── assessment_agent.py         # User expertise assessment
│   ├── valuation_agent.py          # Financial valuation analysis
│   ├── strategic_agent.py          # Strategic and competitive analysis
│   ├── historian_agent.py          # Company historical research
│   └── synthesis_agent.py          # Final report synthesis
├── models/
│   ├── research_database.py        # Research file and metadata models
│   ├── assessment.py               # Assessment data structures
│   └── reports.py                  # Report generation models
├── utils/
│   ├── markdown_processor.py       # Markdown parsing and merging
│   ├── context_manager.py          # Token counting and context management
│   └── file_operations.py          # Research database file operations
└── config/
    ├── agent_prompts/               # AI agent prompt templates
    │   ├── valuation_deep_research.txt
    │   ├── strategic_collaboration.txt
    │   ├── historian_context_integration.txt
    │   └── synthesis_adaptive_scaling.txt
    └── pandoc_templates/            # PDF generation templates
        ├── institutional_report.latex
        └── executive_summary.latex
```

### Enhanced Controller Template
```python