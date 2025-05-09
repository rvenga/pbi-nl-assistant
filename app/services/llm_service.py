# app/services/llm_service.py
import requests
import config
from app.services.context_builder import enrich_context_with_query
from app.prompts.templates import SYSTEM_PROMPT_BASE
from app.utils.dax_extractor import identify_dax_pattern_from_query, format_dax_patterns_for_context
from app.services.langchain_memory import LangchainChatMemory
from typing import List, Dict, Any

# Initialize LangChain memory
memory = LangchainChatMemory(max_history=config.MAX_HISTORY_MESSAGES)

def query_claude(prompt: str, context: str, message_history: List[Dict[str, str]] = None) -> str:
    """Query Claude API with the given prompt, context, and conversation history.
    
    Args:
        prompt: User's natural language query
        context: Context string with PBI metadata
        message_history: List of previous messages in the conversation (deprecated, use LangChain memory)
        
    Returns:
        Claude's response as a string
    """
    if not config.ANTHROPIC_API_KEY:
        return "Error: Anthropic API key not found in environment variables."
    
    # Enrich context with query-specific guidance
    enhanced_context = enrich_context_with_query(context, prompt)
    
    # Add DAX templates for measure-related queries
    if any(keyword in prompt.lower() for keyword in ["measure", "dax", "calculate", "formula"]):
        # Identify relevant DAX patterns
        relevant_patterns = identify_dax_pattern_from_query(prompt)
        
        # Format and add them to the context
        dax_context = format_dax_patterns_for_context(relevant_patterns)
        enhanced_context += dax_context
    
    # Construct system prompt from template
    system_prompt = SYSTEM_PROMPT_BASE.format(context=enhanced_context)
    
    # Setup API request
    headers = {
        "x-api-key": config.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Get conversation history from LangChain memory
    messages = memory.format_history_for_anthropic()
    
    # If no messages or the last message isn't the current prompt, add it
    if not messages or messages[-1]["content"] != prompt:
        memory.add_message("user", prompt)
        messages = memory.format_history_for_anthropic()
    
    # Call Claude API
    try:
        data = {
            "model": config.CLAUDE_MODEL,
            "system": system_prompt,
            "messages": messages,
            "max_tokens": config.MAX_TOKENS
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            assistant_response = response.json()["content"][0]["text"]
            # Add assistant response to memory
            memory.add_message("assistant", assistant_response)
            return assistant_response
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error calling Claude API: {str(e)}"