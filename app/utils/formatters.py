# app/utils/formatters.py
import re
import pygments
from pygments.lexers import SqlLexer
from pygments.formatters import HtmlFormatter

def format_dax(text: str) -> str:
    """Format DAX code blocks for display.
    
    Extract DAX code blocks from markdown so they can be displayed with 
    Streamlit's st.code() function.
    
    Args:
        text: Text containing markdown code blocks
        
    Returns:
        Text with code blocks replaced by special markers and the extracted code blocks
    """
    # Extract code blocks for separate rendering
    pattern = r"```(?:dax)?\s*([^`]+)```"
    
    # Find all code blocks
    code_blocks = re.findall(pattern, text, flags=re.DOTALL)
    
    # Replace code blocks with placeholders
    cleaned_text = re.sub(pattern, "[[CODE_BLOCK]]", text, flags=re.DOTALL)
    
    return cleaned_text, code_blocks

def format_table_columns(table_data: dict) -> str:
    """Format table columns information for display.
    
    Args:
        table_data: Dictionary with table metadata
        
    Returns:
        Formatted HTML string
    """
    html = f"<h4>{table_data['name']}</h4>"
    html += "<table>"
    html += "<tr><th>Column</th><th>Data Type</th></tr>"
    
    for column in table_data.get('columns', []):
        html += f"<tr><td>{column.get('name', '')}</td><td>{column.get('dataType', '')}</td></tr>"
    
    html += "</table>"
    return html

def format_measure(measure_data: dict) -> str:
    """Format measure information for display.
    
    Args:
        measure_data: Dictionary with measure metadata
        
    Returns:
        Formatted HTML string
    """
    name = measure_data.get('name', '')
    expression = measure_data.get('expression', '')
    
    html = f"<div class='measure-block'>"
    html += f"<div class='measure-name'>{name}</div>"
    html += f"<div class='measure-expression code-block'>{expression}</div>"
    html += "</div>"
    
    return html

def format_visualization_spec(viz_spec: dict) -> str:
    """Format visualization specification for display.
    
    Args:
        viz_spec: Dictionary with visualization specification
        
    Returns:
        Formatted HTML string
    """
    viz_type = viz_spec.get('type', 'Unknown')
    title = viz_spec.get('title', viz_type)
    
    html = f"<div class='viz-spec'>"
    html += f"<div class='viz-title'>{title}</div>"
    html += f"<div class='viz-type'>Type: {viz_type}</div>"
    
    if 'fields' in viz_spec:
        html += "<div class='viz-fields'>"
        html += "<h5>Fields</h5>"
        html += "<ul>"
        for field in viz_spec['fields']:
            html += f"<li><b>{field.get('role', '')}:</b> {field.get('field', '')}</li>"
        html += "</ul>"
        html += "</div>"
    
    html += "</div>"
    return html

