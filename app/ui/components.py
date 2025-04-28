import streamlit as st
from app.utils.formatters import format_dax

def render_chat_message(role: str, content: str):
    """Render a chat message with appropriate styling.
    
    Args:
        role: Either 'user' or 'assistant'
        content: The message content
    """
    with st.container():
        st.markdown(f"""
        <div class="chat-message {role}">
            <div class="role">{role.capitalize()}</div>
            <div class="content">{format_dax(content) if role == 'assistant' else content}</div>
        </div>
        """, unsafe_allow_html=True)

def render_measure_card(name: str, expression: str):
    """Render a card displaying a DAX measure.
    
    Args:
        name: The name of the measure
        expression: The DAX expression
    """
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