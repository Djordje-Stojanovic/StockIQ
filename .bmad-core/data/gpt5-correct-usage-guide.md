# GPT-5/5-mini Correct Usage Guide

## Key Principles

### Use the Right Model for the Job
- **GPT-5-mini**: Research, data gathering, web search (200,000 TPM limit)
- **GPT-5**: Complex analysis, reasoning, calculations (30,000 TPM limit)

### Token Management
- **Research Phase**: Use 32k context with high verbosity to get lots of data
- **Analysis Phase**: Use 12k context with medium verbosity for focused output
- **Always use "low" reasoning effort** to save tokens for actual output

### Rate Limits (Your Organization)
```
gpt-5:      30,000 TPM   (use for final analysis)
gpt-5-mini: 200,000 TPM  (use for research/web search)
```

## Correct Implementation Pattern

### Step 1: Research with GPT-5-mini
```python
# Use GPT-5-mini for web search - 200k TPM limit
temp_md = client.respond_with_web_search(
    messages=[...],
    reasoning_effort="low",     # Save tokens for output
    verbosity="high",          # Get lots of detail
    max_output_tokens=32000,   # Plenty of context
    use_complex_model=False    # GPT-5-mini (200k TPM)
)
```

### Step 2: Analysis with GPT-5  
```python
# Use GPT-5 for final analysis - 30k TPM limit
valuation_md = client.create_completion(
    messages=[...],
    reasoning_effort="low",     # Save tokens for output
    verbosity="medium",        # Focused output
    max_tokens=12000,          # Sufficient for analysis
    use_complex_model=True     # GPT-5 (30k TPM)
)
```

## Fixed Issues from Previous Attempts

### ✅ Token Starvation Fixed
- **Problem**: Was using 1800 tokens, GPT-5 spent all on reasoning
- **Solution**: Increased to 8k+ tokens, set reasoning="low"

### ✅ Response Structure Fixed
- **Problem**: Couldn't extract text from response.output
- **Solution**: Upgraded SDK to 1.101.0, use response.output_text

### ✅ Rate Limiting Fixed
- **Problem**: Hitting 30k TPM on both research and analysis
- **Solution**: Use GPT-5-mini (200k TPM) for research, GPT-5 for analysis only

## Working Workflow
1. **User request** → GPT-5-mini web search → **temp.md** (uses 200k TPM)
2. **temp.md + formulas** → GPT-5 analysis → **valuation.md** (uses 30k TPM)
3. **Done** - clean markdown files with real data

## Key Parameters That Work
- **SDK Version**: >= 1.101.0 (has working response.output_text)
- **Content Blocks**: Use typed blocks for tool compatibility
- **Reasoning**: Always "low" to save tokens
- **Retry Logic**: Exponential backoff for rate limits
- **Token Budget**: Be generous to prevent starvation

This approach maximizes your rate limits and gets you the most data for analysis.