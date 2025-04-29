# main.py
import streamlit as st
from app.ui.main_page import render_main_ui
from app.ui.sidebar import render_sidebar
import config

def main():
    # Page configuration
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    st.markdown(config.CSS, unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "metadata" not in st.session_state:
        st.session_state.metadata = None
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False
    if "model_context" not in st.session_state:
        st.session_state.model_context = ""
    
    # Render sidebar
    render_sidebar()
    
    # Chat controls (if file is uploaded)
    if st.session_state.file_uploaded:
        col1, col2 = st.columns([1, 9])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
    
    # Render main UI
    render_main_ui()

if __name__ == "__main__":
    main()