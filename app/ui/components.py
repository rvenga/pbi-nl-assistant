import streamlit as st
from app.utils.formatters import format_dax

def render_chat_message(role: str, content: str):
    """Render a chat message with appropriate styling.
    
    Args:
        role: Either 'user' or 'assistant'
        content: The message content
    """
    with st.container():
        st.markdown(f"**{role.capitalize()}**")
        
        if role == 'assistant':
            # Format the content and extract code blocks
            cleaned_text, code_blocks = format_dax(content)
            
            # Split the cleaned text by code block markers
            text_parts = cleaned_text.split("[[CODE_BLOCK]]")
            
            # Display text and code blocks alternately
            for i, part in enumerate(text_parts):
                if part.strip():
                    st.markdown(part)
                
                # If there's a code block after this text part, display it
                if i < len(code_blocks):
                    st.code(code_blocks[i], language="sql")  # Using SQL for highlighting
        else:
            # Regular rendering for user messages
            st.markdown(content)
        
        st.markdown("---")

def render_measure_card(name: str, expression: str):
    """Render a card displaying a DAX measure.
    
    Args:
        name: The name of the measure
        expression: The DAX expression
    """
    # Since we're not using this anymore, we can keep it for compatibility
    # or remove it if it's not referenced elsewhere
    st.markdown(f"""
    <div class="measure-card">
        <strong>{name}</strong><br>
        <div class="code-block">{expression}</div>
    </div>
    """, unsafe_allow_html=True)

def render_visual_card(title: str, viz_type: str, fields: list):
    """Render a card displaying visualization guidance.
    
    Args:
        title: Title for the visualization
        viz_type: Type of visualization recommended
        fields: List of fields to use
    """
    fields_html = "<br>".join([f"• {field}" for field in fields])
    
    st.markdown(f"""
    <div class="visual-card">
        <strong>{title}</strong><br>
        <p><b>Visualization type:</b> {viz_type}</p>
        <p><b>Fields to use:</b><br>{fields_html}</p>
    </div>
    """, unsafe_allow_html=True)