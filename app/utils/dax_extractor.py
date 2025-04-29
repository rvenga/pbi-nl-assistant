# app/utils/dax_extractor.py
"""
Helper utilities to identify DAX pattern types from user queries
and extract relevant templates.
"""

from typing import List, Dict, Any
import re
from app.prompts.dax_templates import DAX_PATTERNS, TIME_INTELLIGENCE_PATTERNS, STATISTICAL_PATTERNS

def identify_dax_pattern_from_query(query: str) -> List[Dict[str, Any]]:
    """Identify relevant DAX patterns based on user query.
    
    Args:
        query: User query text
        
    Returns:
        List of relevant pattern dictionaries with description and template
    """
    query = query.lower()
    relevant_patterns = []
    
    # Check for time intelligence patterns
    if any(term in query for term in ["ytd", "year to date", "this year", "year-to-date"]):
        relevant_patterns.append(TIME_INTELLIGENCE_PATTERNS["year_to_date"])
    
    if any(term in query for term in ["mtd", "month to date", "this month", "month-to-date"]):
        relevant_patterns.append(TIME_INTELLIGENCE_PATTERNS["month_to_date"])
    
    if any(term in query for term in ["qtd", "quarter to date", "this quarter", "quarter-to-date"]):
        relevant_patterns.append(TIME_INTELLIGENCE_PATTERNS["quarter_to_date"])
    
    if any(term in query for term in ["yoy", "year over year", "previous year", "last year", "year-over-year"]):
        relevant_patterns.append(DAX_PATTERNS["year_over_year"])
        if "percent" in query or "%" in query:
            relevant_patterns.append(DAX_PATTERNS["year_over_year_percent"])
    
    if any(term in query for term in ["previous month", "last month"]):
        relevant_patterns.append(TIME_INTELLIGENCE_PATTERNS["previous_month"])
    
    if any(term in query for term in ["previous quarter", "last quarter"]):
        relevant_patterns.append(TIME_INTELLIGENCE_PATTERNS["previous_quarter"])
    
    # Check for statistical patterns
    if any(term in query for term in ["percent of total", "percentage of total", "% of total"]):
        relevant_patterns.append(STATISTICAL_PATTERNS["percentage_of_total"])
    
    if any(term in query for term in ["variance", "difference", "gap"]):
        relevant_patterns.append(STATISTICAL_PATTERNS["variance"])
        if "percent" in query or "%" in query:
            relevant_patterns.append(STATISTICAL_PATTERNS["variance_percent"])
    
    # Check for other common patterns
    if any(term in query for term in ["running total", "cumulative", "running sum"]):
        relevant_patterns.append(DAX_PATTERNS["running_total"])
    
    if any(term in query for term in ["moving average", "rolling average"]):
        relevant_patterns.append(DAX_PATTERNS["moving_average"])
    
    if any(term in query for term in ["top", "ranking", "rank"]):
        relevant_patterns.append(DAX_PATTERNS["top_n"])
    
    # If nothing specific was found but it's a measure question, provide some common patterns
    if not relevant_patterns and any(term in query for term in ["measure", "dax", "calculate"]):
        # Provide the most commonly used patterns as fallback
        relevant_patterns.append(DAX_PATTERNS["year_over_year"])
        relevant_patterns.append(TIME_INTELLIGENCE_PATTERNS["month_to_date"])
        relevant_patterns.append(STATISTICAL_PATTERNS["percentage_of_total"])
    
    return relevant_patterns

def format_dax_patterns_for_context(patterns: List[Dict[str, Any]]) -> str:
    """Format DAX patterns for inclusion in context.
    
    Args:
        patterns: List of pattern dictionaries
        
    Returns:
        Formatted string with DAX patterns
    """
    if not patterns:
        return ""
    
    result = "\n## RELEVANT DAX PATTERNS\n"
    
    for pattern in patterns:
        result += f"\n**{pattern['description']}:**\n"
        result += f"```dax\n{pattern['template']}\n```\n"
    
    return result