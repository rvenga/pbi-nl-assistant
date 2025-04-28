# app/services/pbix_parser.py
import os
import json
import tempfile
import zipfile
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pbix_metadata(uploaded_file) -> Dict[str, Any]:
    """Extract metadata from a PBIX file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Dictionary with tables, relationships, and visualizations
    """
    # Initialize metadata structure
    metadata = {
        "tables": [],
        "relationships": [],
        "visualizations": []
    }
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pbix') as tmp_file:
        # Write the uploaded file to the temporary file
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Open PBIX as a zip file
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            # List all files in the archive
            file_list = zip_ref.namelist()
            logger.info(f"Found {len(file_list)} files in PBIX")
            
            # Extract data model schema
            schema_files = [f for f in file_list if 'DataModelSchema' in f]
            if schema_files:
                logger.info(f"Found schema file: {schema_files[0]}")
                with zip_ref.open(schema_files[0]) as schema_file:
                    try:
                        schema_data = json.loads(schema_file.read().decode('utf-8'))
                        
                        # Extract tables
                        if 'model' in schema_data and 'tables' in schema_data['model']:
                            tables = schema_data['model']['tables']
                            logger.info(f"Found {len(tables)} tables in schema")
                            
                            for table in tables:
                                table_info = {
                                    'name': table.get('name', ''),
                                    'columns': [],
                                    'measures': []
                                }
                                
                                # Extract columns
                                if 'columns' in table:
                                    for column in table['columns']:
                                        table_info['columns'].append({
                                            'name': column.get('name', ''),
                                            'dataType': column.get('dataType', '')
                                        })
                                
                                # Extract measures
                                if 'measures' in table:
                                    for measure in table['measures']:
                                        table_info['measures'].append({
                                            'name': measure.get('name', ''),
                                            'expression': measure.get('expression', '')
                                        })
                                
                                metadata['tables'].append(table_info)
                        
                        # Extract relationships
                        if 'model' in schema_data and 'relationships' in schema_data['model']:
                            relationships = schema_data['model']['relationships']
                            logger.info(f"Found {len(relationships)} relationships in schema")
                            
                            for rel in relationships:
                                relationship = {
                                    'fromTable': rel.get('fromTable', ''),
                                    'fromColumn': rel.get('fromColumn', ''),
                                    'toTable': rel.get('toTable', ''),
                                    'toColumn': rel.get('toColumn', '')
                                }
                                metadata['relationships'].append(relationship)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing schema JSON: {str(e)}")
                        raise
            else:
                logger.warning("No DataModelSchema found in PBIX file!")
            
            # Look for layout files to extract visualization info
            layout_files = [f for f in file_list if 'Layout' in f and f.endswith('.json')]
            if layout_files:
                logger.info(f"Found {len(layout_files)} layout files")
                
                for layout_file in layout_files:
                    try:
                        with zip_ref.open(layout_file) as lf:
                            layout_data = json.loads(lf.read().decode('utf-8'))
                            
                            if 'sections' in layout_data:
                                for section in layout_data['sections']:
                                    if 'visualContainers' in section:
                                        viz_containers = section['visualContainers']
                                        
                                        for viz_container in viz_containers:
                                            if 'config' in viz_container:
                                                config = viz_container['config']
                                                if isinstance(config, str):
                                                    try:
                                                        config = json.loads(config)
                                                    except json.JSONDecodeError:
                                                        continue
                                                
                                                if 'singleVisual' in config:
                                                    viz_type = config['singleVisual'].get('visualType', 'unknown')
                                                    
                                                    viz_info = {
                                                        'type': viz_type,
                                                        'fields': []
                                                    }
                                                    
                                                    # Extract fields if available
                                                    if 'projections' in config['singleVisual']:
                                                        for role, projections in config['singleVisual']['projections'].items():
                                                            for projection in projections:
                                                                if 'queryRef' in projection:
                                                                    viz_info['fields'].append({
                                                                        'role': role,
                                                                        'field': projection['queryRef']
                                                                    })
                                                    
                                                    metadata['visualizations'].append(viz_info)
                    except Exception as e:
                        logger.error(f"Error processing layout file {layout_file}: {str(e)}")
            else:
                logger.warning("No layout files found in PBIX file!")
        
        # Summary after processing
        logger.info("Extraction complete")
        logger.info(f"- Tables: {len(metadata['tables'])}")
        logger.info(f"- Relationships: {len(metadata['relationships'])}")
        logger.info(f"- Visualizations: {len(metadata['visualizations'])}")
    
    except Exception as e:
        logger.error(f"Error extracting PBIX metadata: {str(e)}")
        raise
    
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)
    
    return metadata