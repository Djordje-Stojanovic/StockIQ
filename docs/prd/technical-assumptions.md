# Technical Assumptions

## Repository Structure: Monorepo
Single repository with minimal structure - agents/, api/, templates/ directories. No complex build systems or packaging.

## Service Architecture
**Direct OpenAI API calls with simple sequential orchestration.** Skip LangGraph complexity - use basic Python functions with direct OpenAI SDK calls. Each agent is a simple function that takes context and returns results.

## Testing Requirements  
**Manual testing only for MVP.** Skip automated testing infrastructure to meet 2-day timeline. Focus development time on agent prompt quality rather than test frameworks.

## Additional Technical Assumptions and Requests

**Core Technology Stack:**
- **FastAPI** - Minimal setup, auto docs, async support
- **OpenAI SDK** - Direct API calls, no wrapper frameworks  
- **Pydantic BaseModel** - Simple data validation only where needed
- **Python standard library** - Avoid unnecessary dependencies

**Agent Pattern:** Simple Python functions, not complex frameworks
```python
def assessment_agent(ticker: str, questions: List[str]) -> AssessmentResult:
    # Direct OpenAI API call with system prompt
    return structured_output
```

**Data Flow:** JSON files for configuration, simple dictionaries for agent handoffs
- No complex state management or graph workflows
- Agent results passed as simple Python dictionaries
- Context preservation through basic JSON serialization

**Frontend:** Plain HTML + minimal JavaScript
- Single page application with basic form handling
- No React, Vue, or complex frontend frameworks
- Direct API calls with fetch()

**PDF Generation:** Python `weasyprint` library
- HTML-to-PDF conversion (simpler than reportlab)
- CSS styling for professional appearance
- Skip complex charting libraries for MVP

**Configuration:** Simple .env + JSON config files
- Agent prompts in separate .txt files
- No YAML complexity, no configuration frameworks

**Error Handling:** Basic try/catch with graceful degradation
- If one agent fails, return partial results
- Simple logging to console/file
