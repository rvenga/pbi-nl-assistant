# app/services/context_builder.py
from typing import Dict, Any, List

def generate_model_context(metadata: Dict[str, Any]) -> str:
    """Generate a context string for Claude based on the metadata.
    
    Args:
        metadata: Extracted PBI metadata
        
    Returns:
        Formatted context string for Claude
    """
    context = "# POWER BI REPORT STRUCTURE\n\n"
    
    # Add tables and columns
    context += _format_tables_and_columns(metadata.get('tables', []))
    
    # Add relationships
    context += _format_relationships(metadata.get('relationships', []))
    
    # Add visualizations
    context += _format_visualizations(metadata.get('visualizations', []))
    
    return context

def _format_tables_and_columns(tables: List[Dict[str, Any]]) -> str:
    """Format tables and columns information.
    
    Args:
        tables: List of table metadata
        
    Returns:
        Formatted string for tables and columns
    """
    result = "## TABLES AND COLUMNS\n"
    
    for table in tables:
        result += f"### Table: {table.get('name', '')}\n"
        
        # Add columns
        if table.get('columns'):
            result += "**Columns:**\n"
            for column in table.get('columns', []):
                result += f"- {column.get('name', '')} ({column.get('dataType', '')})\n"
        
        # Add measures
        if table.get('measures'):
            result += "**Measures:**\n"
            for measure in table.get('measures', []):
                expression = measure.get('expression', '')
                result += f"- {measure.get('name', '')}"
                if expression:
                    result += f" = {expression}"
                result += "\n"
        
        result += "\n"
    
    return result

def _format_relationships(relationships: List[Dict[str, Any]]) -> str:
    """Format relationships information.
    
    Args:
        relationships: List of relationship metadata
        
    Returns:
        Formatted string for relationships
    """
    if not relationships:
        return ""
    
    result = "## RELATIONSHIPS\n"
    for rel in relationships:
        result += f"- {rel.get('fromTable', '')}.{rel.get('fromColumn', '')} → "
        result += f"{rel.get('toTable', '')}.{rel.get('toColumn', '')}\n"
    
    result += "\n"
    return result

def _format_visualizations(visualizations: List[Dict[str, Any]]) -> str:
    """Format visualizations information.
    
    Args:
        visualizations: List of visualization metadata
        
    Returns:
        Formatted string for visualizations
    """
    if not visualizations:
        return ""
    
    result = "## EXISTING VISUALIZATIONS\n"
    
    for idx, viz in enumerate(visualizations):
        result += f"- Visualization {idx+1}: Type: {viz.get('type', 'Unknown')}\n"
        
        # Add fields if available
        if viz.get('fields'):
            result += "  Fields used:\n"
            for field in viz.get('fields', []):
                result += f"  - {field.get('role', '')}: {field.get('field', '')}\n"
    
    return result

def enrich_context_with_query(context: str, query: str) -> str:
    """Enrich the context with the current query for better results.
    
    Args:
        context: Base context from the PBI metadata
        query: Current user query
        
    Returns:
        Enhanced context with query-specific guidance
    """
    # Add specific guidance based on query type
    lower_query = query.lower()
    
    if "measure" in lower_query or "dax" in lower_query:
        context += "\nThe user is asking about creating a measure. Provide a complete DAX formula and explain how it works.\n"
    
    elif "visual" in lower_query or "chart" in lower_query or "graph" in lower_query or "show" in lower_query:
        context += "\nThe user is asking about visualizations. Recommend specific visualization types and explain which fields to use.\n"
    
    return context