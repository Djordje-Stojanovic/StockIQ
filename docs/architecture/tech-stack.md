# Tech Stack

## Overview

StockIQ employs a collaborative multi-agent architecture with FastAPI as the orchestration backbone, featuring 5 specialized AI agents that contribute to a shared research database through structured markdown files. The system uses Owner-Returns FCF/Share methodology (elite investor approaches from Buffett, Ackman, Terry Smith) rather than traditional DCF methods. This tech stack is optimized for institutional-grade financial analysis with local Windows 11 development.

## Platform & Infrastructure

**Platform:** Local Windows 11 Development  
**Key Services:**
- FastAPI application server
- OpenAI SDK for direct API calls
- Pandoc for markdown-to-PDF conversion
- Shared research database (file-based .md system)
- GPT-5 web search integration for real-time financial data
- Git-like versioning for research contributions

**Deployment Host and Regions:** Local development only - no cloud deployment required

## Technology Matrix

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Backend Language | Python | 3.11+ | Server logic and agent coordination | Excellent OpenAI SDK support, rich ecosystem for financial analysis |
| Backend Framework | FastAPI | 0.104+ | REST API and web interface | Auto-documentation, async support, minimal setup overhead |
| API Style | REST | OpenAPI 3.0 | Simple endpoints for assessment and reports | Straightforward for single-user application with limited endpoints |
| Frontend Language | JavaScript | ES2022 | Client-side interaction | Native browser support, minimal dependencies |
| Frontend Framework | Vanilla HTML/CSS/JS | N/A | Simple web interface | Eliminates complex framework overhead for basic ticker input and assessment |
| Authentication | None | N/A | Local-only application | Personal use application doesn't require auth complexity |
| Research Database | File-based .md system | N/A | Shared agent knowledge base | Natural for LLM reading/writing, version controllable, human readable |
| AI Integration | OpenAI SDK | 1.0+ | Direct API calls to GPT models | Official SDK provides optimal prompt control and structured outputs |
| PDF Generation | Pandoc | 3.0+ | Markdown to PDF conversion | Superior formatting, mature ecosystem, designed for academic/professional documents |
| LaTeX Engine | XeLaTeX | Latest | Professional PDF typography | Best-in-class document formatting for institutional reports |
| Data Validation | Pydantic | 2.0+ | Request/response validation | Type safety and automatic validation for agent data structures |
| Valuation Engine | Owner-Returns FCF/Share | Custom | Elite investor methodology | IRR decomposition, Price Ladder analysis, conservative stress testing using Buffett/Ackman approaches |
| HTTP Client | httpx | 0.25+ | External API calls and web requests | Async-first HTTP client that integrates well with FastAPI |
| Environment Config | python-dotenv | 1.0+ | Environment variable management | Simple configuration for API keys and settings |
| Code Formatting | ruff | 0.1+ | Code formatting and linting | Fast Python formatter following project CLAUDE.md standards |
| Development Server | uvicorn | 0.24+ | ASGI server for FastAPI | High-performance server with auto-reload for development |
| Markdown Processing | python-markdown | 3.5+ | Markdown parsing and manipulation | For merging and processing .md files between agents |

## Key Architectural Patterns

- **Collaborative Multi-Agent Research Database:** Agents contribute distilled insights via structured .md files while conducting deep private research
- **Deep Research with Distilled Output:** Each agent can consume 100k+ tokens privately but only contributes high-quality summaries to shared context
- **Markdown-Native Content Generation:** All outputs in markdown format for natural LLM writing and professional PDF conversion
- **Chunked Report Generation with Context Preservation:** Large reports generated in sections with rolling context from previous sections
- **Dynamic Single Template Scaling:** One adaptive template that scales content based on expertise level

## Development Environment

**Prerequisites:**
- Python 3.11+ with virtual environment (`venv_linux`)
- Pandoc for PDF generation
- XeLaTeX for professional typography
- OpenAI API access with GPT-5 web search capabilities

**Key Configuration:**
- Line length: 100 characters (enforced by ruff)
- Type hints required for all functions
- Google-style docstrings mandatory
- File-based research database with YAML metadata