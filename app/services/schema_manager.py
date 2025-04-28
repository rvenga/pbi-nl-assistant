# app/services/schema_manager.py

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
import tempfile
from datetime import datetime

from app.services.pbix_parser import extract_pbix_metadata
from app.services.tmdl_parser import TMDLParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemaManager:
    """Unified manager for Power BI schema data from different sources."""
    
    def __init__(self, data_dir: str = "./data/schemas"):
        """Initialize schema manager.
        
        Args:
            data_dir: Directory to store schema files
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
    
    def extract_from_pbix(self, uploaded_file) -> Dict[str, Any]:
        """Extract schema from a PBIX file.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Dictionary with table, relationship, and visualization information
        """
        try:
            # Use the existing PBIX parser
            metadata = extract_pbix_metadata(uploaded_file)
            
            # Save the extracted schema
            schema_id = f"pbix_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self._save_schema(schema_id, metadata)
            
            return metadata
        except Exception as e:
            logger.error(f"Error extracting from PBIX: {str(e)}")
            raise
    
    def extract_from_tmdl(self, directory_path: str) -> Dict[str, Any]:
        """Extract schema from TMDL files in a directory.
        
        Args:
            directory_path: Path to directory containing TMDL files
            
        Returns:
            Dictionary with clean schema information
        """
        try:
            # Use the TMDL parser
            parser = TMDLParser(directory_path)
            parser.parse_project()
            schema = parser.generate_clean_json()
            
            # Save the extracted schema
            schema_id = f"tmdl_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self._save_schema(schema_id, schema)
            
            return schema
        except Exception as e:
            logger.error(f"Error extracting from TMDL: {str(e)}")
            raise
    
    def extract_from_tmdl_files(self, files: Dict[str, bytes]) -> Dict[str, Any]:
        """Extract schema from TMDL file bytes (for web upload).
        
        Args:
            files: Dictionary of filename -> file content
            
        Returns:
            Dictionary with clean schema information
        """
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write files to the temporary directory
                for filename, content in files.items():
                    # Ensure directory exists
                    directory = os.path.dirname(os.path.join(temp_dir, filename))
                    os.makedirs(directory, exist_ok=True)
                    
                    # Write file
                    with open(os.path.join(temp_dir, filename), 'wb') as f:
                        f.write(content)
                
                # Use the TMDL parser
                parser = TMDLParser(temp_dir)
                parser.parse_project()
                schema = parser.generate_clean_json()
                
                # Save the extracted schema
                schema_id = f"tmdl_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self._save_schema(schema_id, schema)
                
                return schema
        except Exception as e:
            logger.error(f"Error extracting from TMDL files: {str(e)}")
            raise
    
    def _save_schema(self, schema_id: str, schema: Dict[str, Any]) -> None:
        """Save schema to a file.
        
        Args:
            schema_id: Unique identifier for the schema
            schema: Schema data to save
        """
        file_path = os.path.join(self.data_dir, f"{schema_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        
        logger.info(f"Schema saved to {file_path}")
    
    def load_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Load schema from a file.
        
        Args:
            schema_id: Identifier of the schema to load
            
        Returns:
            Dictionary with schema data or None if not found
        """
        file_path = os.path.join(self.data_dir, f"{schema_id}.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Schema file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            return None
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all available schemas.
        
        Returns:
            List of dictionaries with schema info
        """
        schemas = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                schema_id = filename[:-5]  # Remove .json extension
                schemas.append({
                    "id": schema_id,
                    "created": self._parse_timestamp_from_id(schema_id),
                    "type": "pbix" if schema_id.startswith("pbix_") else "tmdl"
                })
        
        # Sort by creation time, newest first
        schemas.sort(key=lambda x: x["created"], reverse=True)
        
        return schemas
    
    def _parse_timestamp_from_id(self, schema_id: str) -> str:
        """Parse timestamp from schema ID.
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            Formatted timestamp string
        """
        # Extract timestamp part
        parts = schema_id.split('_', 1)
        if len(parts) == 2 and len(parts[1]) == 14:  # YYYYMMDDhhmmss format
            try:
                timestamp = datetime.strptime(parts[1], '%Y%m%d%H%M%S')
                return timestamp.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        
        return "Unknown"
    
    def prepare_context(self, schema: Dict[str, Any]) -> str:
        """Prepare context string for LLM from schema.
        
        Args:
            schema: Schema data
            
        Returns:
            Context string for LLM
        """
        context = "# POWER BI SCHEMA\n\n"
        
        # Add tables section
        context += "## TABLES\n"
        for table in schema.get('tables', []):
            context += f"### Table: {table.get('name', '')}\n"
            
            # Add columns
            if table.get('columns'):
                context += "**Columns:**\n"
                for column in table.get('columns', []):
                    context += f"- {column.get('name', '')} ({column.get('dataType', '')})\n"
            
            context += "\n"
        
        # Add measures section
        if schema.get('measures'):
            context += "## MEASURES\n"
            for measure in schema.get('measures', []):
                table_name = measure.get('table', '')
                context += f"### {measure.get('name', '')} ({table_name})\n"
                context += f"```dax\n{measure.get('expression', '')}\n```\n\n"
        
        # Add relationships section
        if schema.get('relationships'):
            context += "## RELATIONSHIPS\n"
            for rel in schema.get('relationships', []):
                from_table = rel.get('fromTable', '')
                from_column = rel.get('fromColumn', '')
                to_table = rel.get('toTable', '')
                to_column = rel.get('toColumn', '')
                cardinality = f" ({rel.get('toCardinality', 'one')})" if 'toCardinality' in rel else ""
                active = " (inactive)" if not rel.get('isActive', True) else ""
                
                context += f"- {from_table}.[{from_column}] → {to_table}.[{to_column}]{cardinality}{active}\n"
        
        return context