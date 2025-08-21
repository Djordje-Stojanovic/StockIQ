# External APIs

## OpenAI API

- **Purpose:** Powers all 5 AI agents with specialized prompts for institutional-grade analysis and collaborative research
- **Documentation:** https://platform.openai.com/docs
- **Base URL(s):** https://api.openai.com/v1
- **Authentication:** API Key (Bearer token)
- **Rate Limits:** Tier-based limits, monitoring required for deep research and chunked generation

**Key Endpoints Used:**
- `POST /chat/completions` - All agent interactions with structured outputs and deep research
- `POST /embeddings` - Potential future use for research similarity and cross-referencing

**Integration Notes:** Each agent can conduct private deep research using large context windows, then distill insights for shared database. Chunked generation requires careful token management across multiple API calls.

## MCP Server Integration

- **Purpose:** Real-time financial data access for comprehensive company analysis across all research agents
- **Documentation:** MCP server specific documentation
- **Base URL(s):** Configured via MCP protocol
- **Authentication:** MCP server authentication
- **Rate Limits:** Server-dependent

**Key Endpoints Used:**
- Financial data retrieval for ticker symbols
- Recent news and earnings information  
- Market data for peer analysis
- Historical financial data for company timeline research

**Integration Notes:** Critical for current market data integration across all research agents. Each agent can access independently for deep private research before contributing insights to shared database.
