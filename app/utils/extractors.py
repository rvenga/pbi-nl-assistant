# app/utils/extractors.py
import re
from typing import List, Dict, Any

def extract_measures(text: str) -> List[Dict[str, str]]:
    """Extract measures from Claude's response.
    
    Args:
        text: Text to extract measures from
        
    Returns:
        List of dictionaries with name and expression keys
    """
    measures = []
    
    # Look for code blocks with DAX
    code_blocks = re.finditer(r"```(?:dax)?\s*([^`]+)```", text, re.DOTALL)
    
    for match in code_blocks:
        code = match.group(1).strip()
        extracted = _parse_dax_code(code)
        if extracted:
            measures.extend(extracted)
    
    # Also look for inline measure definitions (not in code blocks)
    inline_measures = re.finditer(r"([A-Za-z][A-Za-z0-9\s]*)\s*=\s*([^;]+);", text)
    
    for match in inline_measures:
        name = match.group(1).strip()
        expression = match.group(2).strip()
        
        # Only add if we don't already have this measure
        if not any(m['name'] == name for m in measures):
            measures.append({
                "name": name,
                "expression": expression
            })
    
    return measures

def _parse_dax_code(code: str) -> List[Dict[str, str]]:
    """Parse DAX code block to extract measures.
    
    Args:
        code: DAX code block
        
    Returns:
        List of dictionaries with name and expression keys
    """
    measures = []
    
    # Split by lines and look for assignments
    lines = code.split('\n')
    current_measure = None
    current_expression = []
    
    for line in lines:
        # Skip comments and empty lines when not in a measure definition
        if (line.strip().startswith('//') or not line.strip()) and not current_measure:
            continue
            
        # Look for measure definition (name = expression)
        match = re.match(r"([A-Za-z][A-Za-z0-9\s]*)\s*=\s*(.+)$", line)
        
        if match:
            # If we were already defining a measure, save it
            if current_measure and current_expression:
                measures.append({
                    "name": current_measure,
                    "expression": '\n'.join(current_expression)
                })
            
            # Start new measure
            current_measure = match.group(1).strip()
            current_expression = [match.group(2).strip()]
        elif current_measure:
            # Continue existing measure
            current_expression.append(line)
    
    # Add the last measure if there is one
    if current_measure and current_expression:
        measures.append({
            "name": current_measure,
            "expression": '\n'.join(current_expression)
        })
    
    return measures

def extract_visualization_recommendation(text: str) -> Dict[str, Any]:
    """Extract visualization recommendation from Claude's response.
    
    Args:
        text: Text to extract visualization from
        
    Returns:
        Dictionary with visualization recommendation or empty dict if none found
    """
    viz_info = {}
    
    # Extract visualization type
    viz_type_match = re.search(r"recommend(?:ed)?\s+(?:using|a|an)\s+([A-Za-z\s]+chart|[A-Za-z\s]+graph|[A-Za-z\s]+map|[A-Za-z\s]+visual|[A-Za-z\s]+table)", text, re.IGNORECASE)
    if viz_type_match:
        viz_info["type"] = viz_type_match.group(1).strip()
    
    # Extract fields
    fields = []
    field_matches = re.finditer(r"(axis|value|category|series|legend|tooltip|size|filter|slicer|drillthrough)(?:\s+should\s+be|\s*:)?\s+([^\n,.]+)", text, re.IGNORECASE)
    
    for match in field_matches:
        role = match.group(1).strip().lower()
        field = match.group(2).strip()
        
        # Clean up field name (remove "the", "use", etc.)
        field = re.sub(r"^(?:the|use|using|set\s+to|add|put)\s+", "", field, flags=re.IGNORECASE).strip()
        
        fields.append({
            "role": role,
            "field": field
        })
    
    if fields:
        viz_info["fields"] = fields
    
    return viz_info