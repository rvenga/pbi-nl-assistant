# app/ui/main_page.py
import streamlit as st
from app.services.llm_service import query_claude, memory
from app.ui.components import render_chat_message

def render_main_ui():
    """Render the main UI area with chat interface."""
    st.title("Power BI Natural Language Assistant")

    # Check if file is uploaded
    if not st.session_state.file_uploaded:
        st.info("Please upload a PBIX file in the sidebar to get started.")
        return
    
    # Display chat messages from LangChain memory
    for message in memory.get_messages():
        role = message["role"]
        content = message["content"]
        
        # Render chat message
        render_chat_message(role, content)
    
    # Chat input
    with st.container():
        user_input = st.chat_input("Ask me about measures or visualizations...")
        
        if user_input:
            # Add user message to display (already added to memory in query_claude)
            render_chat_message("user", user_input)
            
            # Get response from Claude
            with st.spinner("Thinking..."):
                response = query_claude(user_input, st.session_state.model_context)
            
            # Render assistant message (already added to memory in query_claude)
            render_chat_message("assistant", response)
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("👉 **Tip:** Be specific about what measures or visualizations you need.")