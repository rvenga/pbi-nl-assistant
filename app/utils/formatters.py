# app/utils/formatters.py
import re

def format_dax(text: str) -> str:
    """Format DAX code blocks with syntax highlighting.
    
    Args:
        text: Text containing markdown code blocks
        
    Returns:
        Text with code blocks replaced by HTML formatted blocks
    """
    # Replace DAX code blocks with formatted HTML
    pattern = r"```(?:dax)?\s*([^`]+)```"
    
    def replace_with_code_block(match):
        code = match.group(1).strip()
        return f'<div class="code-block">{code}</div>'
    
    formatted_text = re.sub(pattern, replace_with_code_block, text, flags=re.DOTALL)
    return formatted_text

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