# StockIQ

Collaborative multi-agent stock analysis platform featuring FastAPI backend and 5 specialized AI agents for institutional-grade investment research.

## Quick Start

### Prerequisites

- Python 3.11+ (tested with Python 3.13)
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd StockIQ
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   copy .env.example .env
   # Edit .env and add your OpenAI API key
   ```

### Running the Application

**Windows 11 Development Server:**
```bash
python run_dev.py
```

The application will be available at: http://127.0.0.1:8000

**Health Check:**
- Health endpoint: http://127.0.0.1:8000/health
- Web interface: http://127.0.0.1:8000/static/index.html

### Development

**Run Tests:**
```bash
python -m pytest tests/ -v
```

**Linting:**
```bash
ruff check .
```

**Auto-format:**
```bash
ruff format .
```

## Project Structure

```
StockIQ/
├── src/                     # Main application source
│   ├── main.py             # FastAPI application entry point
│   ├── routers/            # API route definitions
│   ├── agents/             # AI agent implementations
│   ├── services/           # Business logic services
│   ├── models/             # Pydantic data models
│   └── utils/              # Shared utilities
├── static/                 # Frontend assets
├── config/                 # Configuration files
├── tests/                  # Test suites
├── research_database/      # Shared research database
└── tmp/                    # Temporary files
```

## Architecture

- **Backend:** FastAPI with Pydantic v2 for data validation
- **Frontend:** Vanilla HTML/CSS/JS
- **AI Integration:** OpenAI SDK for direct API calls
- **Configuration:** Environment-based with .env files
- **Testing:** pytest with comprehensive unit and integration tests

## Current Features

- ✅ FastAPI application with health monitoring
- ✅ Complete project structure for multi-agent architecture
- ✅ Environment configuration management
- ✅ CORS middleware for local development
- ✅ Static file serving
- ✅ Comprehensive test coverage
- ✅ Code formatting and linting with ruff

## Next Steps

Future stories will implement:
- Assessment Agent for expertise evaluation
- Valuation Agent for financial analysis
- Strategic Agent for competitive analysis
- Historian Agent for company context
- Synthesis Agent for adaptive report generation