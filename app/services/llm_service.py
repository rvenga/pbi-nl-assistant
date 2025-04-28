# app/services/llm_service.py
import os
import requests
import config
from app.services.context_builder import enrich_context_with_query

def query_claude(prompt: str, context: str) -> str:
    """Query Claude API with the given prompt and context.
    
    Args:
        prompt: User's natural language query
        context: Context string with PBI metadata
        
    Returns:
        Claude's response as a string
    """
    if not config.ANTHROPIC_API_KEY:
        return "Error: Anthropic API key not found in environment variables."
    
    # Enrich context with query-specific guidance
    enhanced_context = enrich_context_with_query(context, prompt)
    
    # Construct system prompt
    system_prompt = _build_system_prompt(enhanced_context)
    
    # Setup API request
    headers = {
        "x-api-key": config.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # FIX: Updated API request structure
    data = {
        "model": config.CLAUDE_MODEL,
        "system": system_prompt,  # System as top-level parameter
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": config.MAX_TOKENS
    }
    
    # Call Claude API
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error calling Claude API: {str(e)}"

def _build_system_prompt(context: str) -> str:
    """Build the system prompt for Claude.
    
    Args:
        context: Enhanced context with PBI metadata
        
    Returns:
        Complete system prompt string
    """
    return f"""You are an expert Power BI consultant who specializes in helping users create DAX measures and visualizations.
Use the following information about the user's Power BI report structure:

{context}

When asked to create measures:
1. Provide the exact DAX formula using clear syntax that can be directly copied
2. Explain how the measure works in detail
3. Include comments in the DAX code when helpful
4. Suggest where the measure could be used in visualizations

When asked about visualizations:
1. Recommend the best visualization type based on the data structure
2. Specify which columns and measures to use
3. Provide guidance on formatting, filters, and other settings
4. Suggest drill-through or tooltip enhancements if appropriate

If you need to provide code, use the following format:
```dax
// DAX formula here
```

Always provide practical, implementation-focused answers based on the specific tables and measures in the user's report.
"""