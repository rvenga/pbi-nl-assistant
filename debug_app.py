# app/services/alternative_parser.py
import os
import json
import tempfile
import zipfile
import logging
import re
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pbix_metadata(uploaded_file) -> Dict[str, Any]:
    """Extract metadata from a PBIX file without using any fallback sample data.
    
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
            
            # Try multiple extraction methods in sequence
            _try_extract_schema(zip_ref, file_list, metadata)
            _try_extract_from_datamodel(zip_ref, file_list, metadata)
            _try_extract_from_connections(zip_ref, file_list, metadata)
            _try_extract_from_layout(zip_ref, file_list, metadata)
            
            # Log what we found
            logger.info(f"Extraction complete - found {len(metadata['tables'])} tables, "
                       f"{len(metadata['relationships'])} relationships, "
                       f"{len(metadata['visualizations'])} visualizations")
    
    except Exception as e:
        logger.error(f"Error extracting PBIX metadata: {str(e)}")
        raise
    
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)
    
    return metadata

def _try_extract_schema(zip_ref, file_list: List[str], metadata: Dict[str, Any]) -> None:
    """Try to extract data from schema files."""
    # Check for DataModelSchema
    schema_files = [f for f in file_list if 'DataModelSchema' in f]
    
    if schema_files:
        logger.info(f"Found schema file: {schema_files[0]}")
        try:
            with zip_ref.open(schema_files[0]) as schema_file:
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
        
        except Exception as e:
            logger.error(f"Error extracting from schema: {str(e)}")

def _try_extract_from_datamodel(zip_ref, file_list: List[str], metadata: Dict[str, Any]) -> None:
    """Try to extract data from DataModel file."""
    if 'DataModel' in file_list:
        logger.info("Found DataModel file")
        try:
            # DataModel may be binary or have embedded strings we can extract
            with zip_ref.open('DataModel') as data_model_file:
                data = data_model_file.read()
                text_data = data.decode('utf-8', errors='ignore')
                
                # Look for table names in the text data
                table_matches = set(re.findall(r'(?:Table|TABLE|table)[\'"\s:=]+([A-Za-z0-9_]+)', text_data))
                
                for table_name in table_matches:
                    if len(table_name) > 2:  # Filter out short/invalid names
                        # Check if we already have this table
                        if not any(t['name'] == table_name for t in metadata['tables']):
                            # Try to find columns related to this table
                            column_pattern = rf'{re.escape(table_name)}[\[\.\s]+([A-Za-z0-9_]+)'
                            column_matches = set(re.findall(column_pattern, text_data))
                            
                            table_info = {
                                'name': table_name,
                                'columns': [{'name': col, 'dataType': 'unknown'} for col in column_matches if len(col) > 1],
                                'measures': []
                            }
                            
                            metadata['tables'].append(table_info)
                
                # Look for relationship patterns
                rel_pattern = r'([A-Za-z0-9_]+)\[([A-Za-z0-9_]+)\].*?([A-Za-z0-9_]+)\[([A-Za-z0-9_]+)\]'
                rel_matches = re.findall(rel_pattern, text_data)
                
                for match in rel_matches:
                    if len(match) == 4:
                        relationship = {
                            'fromTable': match[0],
                            'fromColumn': match[1],
                            'toTable': match[2],
                            'toColumn': match[3]
                        }
                        
                        # Add if not duplicate
                        if not any(r['fromTable'] == relationship['fromTable'] and 
                                  r['fromColumn'] == relationship['fromColumn'] and
                                  r['toTable'] == relationship['toTable'] and
                                  r['toColumn'] == relationship['toColumn'] 
                                  for r in metadata['relationships']):
                            metadata['relationships'].append(relationship)
        
        except Exception as e:
            logger.error(f"Error extracting from DataModel: {str(e)}")

def _try_extract_from_connections(zip_ref, file_list: List[str], metadata: Dict[str, Any]) -> None:
    """Try to extract data from Connections file."""
    if 'Connections' in file_list:
        logger.info("Found Connections file")
        try:
            with zip_ref.open('Connections') as conn_file:
                try:
                    conn_content = conn_file.read().decode('utf-8')
                    conn_data = json.loads(conn_content)
                    
                    # Extract table info from different connection formats
                    if 'Tables' in conn_data:
                        # DirectQuery or Import mode
                        tables = conn_data['Tables']
                        for table in tables:
                            name = table.get('Name', '')
                            if name and not any(t['name'] == name for t in metadata['tables']):
                                table_info = {
                                    'name': name,
                                    'columns': [],
                                    'measures': []
                                }
                                
                                if 'Columns' in table:
                                    for col in table['Columns']:
                                        table_info['columns'].append({
                                            'name': col.get('Name', ''),
                                            'dataType': col.get('DataType', 'unknown')
                                        })
                                
                                metadata['tables'].append(table_info)
                    
                    # Sometimes table info is in the Expressions section
                    elif 'Expressions' in conn_data:
                        expressions = conn_data['Expressions']
                        for expr in expressions:
                            if 'Name' in expr:
                                name = expr['Name']
                                if name and not any(t['name'] == name for t in metadata['tables']):
                                    metadata['tables'].append({
                                        'name': name,
                                        'columns': [],
                                        'measures': []
                                    })
                
                except json.JSONDecodeError:
                    # If not JSON, try to find table references in the text
                    content = conn_file.read().decode('utf-8', errors='ignore')
                    table_matches = set(re.findall(r'(?:Table|TABLE|table)[\'"\s:=]+([A-Za-z0-9_]+)', content))
                    
                    for table_name in table_matches:
                        if len(table_name) > 2 and not any(t['name'] == table_name for t in metadata['tables']):
                            metadata['tables'].append({
                                'name': table_name,
                                'columns': [],
                                'measures': []
                            })
        
        except Exception as e:
            logger.error(f"Error extracting from Connections: {str(e)}")

def _try_extract_from_layout(zip_ref, file_list: List[str], metadata: Dict[str, Any]) -> None:
    """Try to extract visualizations from Layout files."""
    # Standard layout files
    layout_files = [f for f in file_list if 'Layout' in f and f.endswith('.json')]
    
    # Also check for non-standard layouts
    if 'Report/Layout' in file_list:
        layout_files.append('Report/Layout')
    
    if not layout_files:
        logger.warning("No layout files found")
        return
    
    for layout_file in layout_files:
        try:
            logger.info(f"Processing layout file: {layout_file}")
            with zip_ref.open(layout_file) as lf:
                try:
                    layout_data = json.loads(lf.read().decode('utf-8'))
                    
                    # Process standard layout format
                    if 'sections' in layout_data:
                        for section in layout_data['sections']:
                            if 'visualContainers' in section:
                                for viz_container in section['visualContainers']:
                                    _process_visual_container(viz_container, metadata)
                    
                    # Some PBIX files use a different layout format
                    elif 'visualContainers' in layout_data:
                        for viz_container in layout_data['visualContainers']:
                            _process_visual_container(viz_container, metadata)
                
                except json.JSONDecodeError:
                    # If not JSON, try text-based extraction
                    content = lf.read().decode('utf-8', errors='ignore')
                    
                    # Look for visualization types
                    viz_types = re.findall(r'visualType[\'"\s:=]+([A-Za-z0-9_]+)', content)
                    for viz_type in viz_types:
                        if viz_type and viz_type.lower() not in ['null', 'undefined']:
                            metadata['visualizations'].append({
                                'type': viz_type,
                                'fields': []
                            })
        
        except Exception as e:
            logger.error(f"Error processing layout file {layout_file}: {str(e)}")

def _process_visual_container(viz_container: Dict[str, Any], metadata: Dict[str, Any]) -> None:
    """Process a visualization container to extract visualization info."""
    if 'config' not in viz_container:
        return
    
    config = viz_container['config']
    if isinstance(config, str):
        try:
            config = json.loads(config)
        except json.JSONDecodeError:
            return
    
    if 'singleVisual' in config:
        viz_type = config['singleVisual'].get('visualType', 'unknown')
        
        viz_info = {
            'type': viz_type,
            'fields': []
        }
        
        # Extract fields if available
        if 'projections' in config['singleVisual']:
            for role, projections in config['singleVisual']['projections'].items():
                if isinstance(projections, list):
                    for projection in projections:
                        if 'queryRef' in projection:
                            viz_info['fields'].append({
                                'role': role,
                                'field': projection['queryRef']
                            })
        
        metadata['visualizations'].append(viz_info)