# app/ui/sidebar.py
# app/ui/sidebar.py
import os
import json
import tempfile
import streamlit as st
import traceback
import zipfile
import shutil
from app.services.schema_manager import SchemaManager
from app.services.context_builder import generate_model_context
from app.services.llm_service import query_claude, memory  # Import the memory instance
import config

# Initialize schema manager
schema_manager = SchemaManager()

def render_sidebar():
    """Render the sidebar UI with file upload and examples."""
    with st.sidebar:
        st.title("📊 Power BI Assistant")
        st.markdown("Upload a Power BI file to get started.")
        
        # Initialize file upload state if not exists
        if "file_type" not in st.session_state:
            st.session_state.file_type = "pbix"
        
        # File type selection
        file_type = st.radio(
            "Select file type to upload:",
            options=["PBIX File", "TMDL Files (Folder)"],
            index=0,
            key="file_type_radio"
        )
        st.session_state.file_type = "pbix" if file_type == "PBIX File" else "tmdl"
        
        # Process file upload based on type
        if st.session_state.file_type == "pbix":
            _render_pbix_upload()
        else:
            _render_tmdl_upload()
        
        # Show report summary if file is processed
        if getattr(st.session_state, 'file_uploaded', False) and hasattr(st.session_state, 'metadata'):
            _render_report_summary()
            
            # Add chat controls here
            if st.button("🗑️ Clear Chat"):
                memory.clear_history()
                st.rerun()
                
            _render_example_prompts()
        if st.session_state.file_uploaded:
            st.subheader("Memory Debug")
            if st.checkbox("Show memory contents"):
                # Get all messages in memory
                messages = memory.get_messages()
                
                # Display message count
                st.write(f"Messages in memory: {len(messages)}")
                
                # Display each message
                for i, msg in enumerate(messages):
                    st.write(f"Message {i+1}:")
                    st.write(f"Role: {msg['role']}")
                    st.write(f"Content: {msg['content'][:50]}..." if len(msg['content']) > 50 else f"Content: {msg['content']}")
                    st.write("---")

def _render_pbix_upload():
    """Render PBIX file upload interface."""
    uploaded_file = st.file_uploader("Choose a PBIX file", type=['pbix'])
    
    # Process uploaded file
    if uploaded_file and not st.session_state.file_uploaded:
        with st.spinner("Processing PBIX file..."):
            try:
                # Extract metadata with schema manager
                metadata = schema_manager.extract_from_pbix(uploaded_file)
                
                # Check if any data was extracted
                if not metadata.get('tables') and not metadata.get('relationships') and not metadata.get('visualizations'):
                    st.warning("No data could be extracted from this PBIX file.")
                    st.info("Please try a different file with proper data model and visualizations.")
                    return
                
                # Store metadata in session state
                st.session_state.metadata = metadata
                
                # Generate context for Claude
                model_context = generate_model_context(metadata)
                st.session_state.model_context = model_context
                
                # Clear the memory when loading a new file
                memory.clear_history()
                
                st.session_state.file_uploaded = True
                st.success("PBIX file processed successfully!")
                
            except Exception as e:
                st.error("Error processing PBIX file")
                with st.expander("View Error Details"):
                    st.code(traceback.format_exc())
                return

def _render_tmdl_upload():
    """Render TMDL folder upload interface."""
    st.markdown("Upload a ZIP file containing TMDL files")
    uploaded_zip = st.file_uploader("Choose a ZIP file", type=['zip'])
    
    # Process uploaded zip
    if uploaded_zip and not st.session_state.file_uploaded:
        with st.spinner("Processing TMDL files..."):
            try:
                # Create a temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extract the zip file
                    zip_path = os.path.join(temp_dir, "upload.zip")
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_zip.getvalue())
                    
                    # Extract zip contents
                    extract_dir = os.path.join(temp_dir, "extract")
                    os.makedirs(extract_dir, exist_ok=True)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    # Find the root directory of the project
                    project_dir = extract_dir
                    contents = os.listdir(project_dir)
                    
                    # If there's a single directory and it contains the project files, use that
                    if len(contents) == 1 and os.path.isdir(os.path.join(project_dir, contents[0])):
                        if os.path.exists(os.path.join(project_dir, contents[0], "model.tmdl")) or \
                           os.path.exists(os.path.join(project_dir, contents[0], "definition", "model.tmdl")):
                            project_dir = os.path.join(project_dir, contents[0])
                    
                    # Extract schema using schema manager
                    metadata = schema_manager.extract_from_tmdl(project_dir)
                    
                    # Check if any data was extracted
                    if not metadata.get('tables') and not metadata.get('relationships') and not metadata.get('measures', []):
                        st.warning("No data could be extracted from the TMDL files.")
                        st.info("Please check the structure of your ZIP file.")
                        return
                    
                    # Store metadata in session state
                    st.session_state.metadata = metadata
                    
                    # Generate context for Claude
                    model_context = schema_manager.prepare_context(metadata)
                    st.session_state.model_context = model_context
                    
                    # Clear the memory when loading a new file
                    memory.clear_history()
                    
                    st.session_state.file_uploaded = True
                    st.success("TMDL files processed successfully!")
            
            except Exception as e:
                st.error("Error processing TMDL files")
                with st.expander("View Error Details"):
                    st.code(traceback.format_exc())
                return

def _render_report_summary():
    """Render a summary of the uploaded report."""
    st.subheader("Report Summary")
    
    # Get metadata with proper error handling
    if not hasattr(st.session_state, 'metadata'):
        st.warning("No metadata available")
        return
    
    metadata = st.session_state.metadata
    
    # Display summary based on file type
    if st.session_state.file_type == "pbix":
        _render_pbix_summary(metadata)
    else:
        _render_tmdl_summary(metadata)

def _render_pbix_summary(metadata):
    """Render summary for PBIX file."""
    # Display summary
    tables = metadata.get('tables', [])
    relationships = metadata.get('relationships', [])
    visualizations = metadata.get('visualizations', [])
    
    # Display counts
    st.markdown(f"**Tables:** {len(tables)}")
    if len(tables) > 0:
        with st.expander("Show Tables"):
            for table in tables:
                st.markdown(f"- **{table.get('name', 'Unnamed')}** "
                            f"({len(table.get('columns', []))} columns, "
                            f"{len(table.get('measures', []))} measures)")
    
    st.markdown(f"**Relationships:** {len(relationships)}")
    if len(relationships) > 0:
        with st.expander("Show Relationships"):
            for rel in relationships:
                st.markdown(f"- {rel.get('fromTable', '')}.[{rel.get('fromColumn', '')}] → "
                            f"{rel.get('toTable', '')}.[{rel.get('toColumn', '')}]")
    
    st.markdown(f"**Visualizations:** {len(visualizations)}")
    if len(visualizations) > 0:
        with st.expander("Show Visualizations"):
            for idx, viz in enumerate(visualizations):
                st.markdown(f"- Viz {idx+1}: {viz.get('type', 'Unknown')}")

def _render_tmdl_summary(metadata):
    """Render summary for TMDL files."""
    # Display summary
    tables = metadata.get('tables', [])
    relationships = metadata.get('relationships', [])
    measures = metadata.get('measures', [])
    
    # Display counts
    st.markdown(f"**Tables:** {len(tables)}")
    if len(tables) > 0:
        with st.expander("Show Tables"):
            for table in tables:
                st.markdown(f"- **{table.get('name', 'Unnamed')}** "
                            f"({len(table.get('columns', []))} columns)")
    
    st.markdown(f"**Measures:** {len(measures)}")
    if len(measures) > 0:
        with st.expander("Show Measures"):
            # Group measures by table
            measures_by_table = {}
            for measure in measures:
                table_name = measure.get('table', 'Unknown')
                if table_name not in measures_by_table:
                    measures_by_table[table_name] = []
                measures_by_table[table_name].append(measure)
            
            # Display measures by table
            for table_name, table_measures in measures_by_table.items():
                st.markdown(f"**{table_name}**")
                for measure in table_measures:
                    st.markdown(f"- {measure.get('name', '')}")
    
    st.markdown(f"**Relationships:** {len(relationships)}")
    if len(relationships) > 0:
        with st.expander("Show Relationships"):
            for rel in relationships:
                cardinality = f" ({rel.get('toCardinality', '')})" if 'toCardinality' in rel else ""
                st.markdown(f"- {rel.get('fromTable', '')}.[{rel.get('fromColumn', '')}] → "
                            f"{rel.get('toTable', '')}.[{rel.get('toColumn', '')}]{cardinality}")

def _render_example_prompts():
    """Render example prompt buttons."""
    st.subheader("Example Prompts")
    
    for example in config.EXAMPLE_PROMPTS:
        if st.button(example):
            # Add user message to memory
            memory.add_message("user", example)
            
            # Get response from Claude
            with st.spinner("Thinking..."):
                response = query_claude(example, st.session_state.model_context)
            
            # Note: The assistant message is added to memory in query_claude
            st.rerun()

# Add this at the bottom of sidebar.py
def render_chat_controls():
    """Render chat controls in the sidebar."""
    if st.session_state.file_uploaded:
        if st.button("🗑️ Clear Chat"):
            memory.clear_history()
            st.rerun()