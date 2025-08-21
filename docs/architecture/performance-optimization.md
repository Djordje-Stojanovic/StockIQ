# Performance Optimization

## Token Budget Management

**Assessment phase**: 5,000 tokens max
- Question generation: 1,000 tokens
- Response processing: 2,000 tokens
- Expertise calculation: 1,000 tokens
- Report complexity determination: 1,000 tokens
- Buffer for retries and validation: Additional 1,000 tokens

**Research agents**: 50,000 tokens each max
- Deep private research phase: 40,000 tokens per agent
- Shared research contribution: 5,000 tokens per agent
- Cross-agent comments and collaboration: 3,000 tokens per agent
- Research database operations: 2,000 tokens per agent
- Circuit breaker at 45,000 tokens with graceful degradation

**Report generation**: 100,000 tokens max
- Section planning and structure: 5,000 tokens
- Chunked section generation: 80,000 tokens (8,000 per section average)
- Context preservation between sections: 10,000 tokens
- Final report merging and formatting: 5,000 tokens
- Adaptive scaling based on expertise level (±20,000 tokens)

**Total budget monitoring and alerts**
- Per-session token tracking with real-time monitoring
- Alert thresholds: 75% of budget consumed
- Automatic fallback modes when approaching limits
- Budget recovery through context compression and optimization
- Session-level budget caps: 250,000 tokens total

**Token Optimization Strategies**
- Context window sliding for large research databases
- Research summarization for handoffs between agents
- Intelligent content chunking with overlap minimization
- Dynamic prompt optimization based on research phase
- Caching of common research patterns and templates
