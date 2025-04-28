import streamlit as st
from app.services.llm_service import query_claude
from app.utils.formatters import format_dax
from app.utils.extractors import extract_measures
from app.ui.components import render_chat_message, render_measure_card

def render_main_ui():
    """Render the main UI area with chat interface."""
    st.title("Power BI Natural Language Assistant")

    # Check if file is uploaded
    if not st.session_state.file_uploaded:
        st.info("Please upload a PBIX file in the sidebar to get started.")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        # Render chat message
        render_chat_message(role, content)
        
        # Extract and display measures in a more structured way
        if role == "assistant":
            measures = extract_measures(content)
            if measures:
                st.markdown("### Generated Measures")
                for measure in measures:
                    render_measure_card(measure["name"], measure["expression"])
    
    # Chat input
    with st.container():
        user_input = st.chat_input("Ask me about measures or visualizations...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get response from Claude
            with st.spinner("Thinking..."):
                response = query_claude(user_input, st.session_state.model_context)
            
            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("👉 **Tip:** Be specific about what measures or visualizations you need.")