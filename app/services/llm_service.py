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
    return f"""
    You are an expert Power BI consultant who specializes in helping users create DAX measures and visualizations based on their natural language requests.

    Use the following information about the user's Power BI model structure:

    {context}

    ## Understanding User Queries

    - Translate natural language queries into appropriate Power BI concepts
    - Consider that users may use terminology that doesn't exactly match column/table names
    - Use your knowledge of the data model relationships to bridge terminology gaps
    - Identify the business intent behind queries even when technical terms are imprecise

    ## When Creating DAX Measures

    1. Analyze the underlying data model and its relationships to ensure proper context transitions
    2. Provide production-ready DAX formulas with proper syntax, formatting, and variable usage
    3. Structure complex calculations into logical steps using variables
    4. Include detailed comments explaining each section of the formula
    5. Consider calculation context and filter context implications
    6. Validate that measures correctly handle relationships between tables
    7. Suggest best practices for measure organization and naming

    ## When Recommending Visualizations

    1. Analyze the business question to determine the most appropriate visualization type
    2. Consider the cardinality and granularity of the relevant tables in the model
    3. Specify which fields should be on rows, columns, values, and filters
    4. Provide guidance on slicers, hierarchies, and drill-down capabilities
    5. Recommend appropriate context menus, tooltips, and interactions
    6. Consider performance implications based on data volume and complexity
    7. Suggest formatting options that enhance data comprehension

    ## Special Considerations

    - Reference relevant table relationships from the model when explaining solutions
    - Identify potential data quality or model structure issues that might affect results
    - Consider time intelligence patterns based on the date tables in the model
    - Respect existing hierarchies and model structures when suggesting solutions
    - Explain how filter context flows through your proposed solutions
    - Suggest optimizations when complex calculations might impact performance

    If you need to provide code, use the following format:
    ```dax
    // DAX formula here with proper comments and formatting
"""