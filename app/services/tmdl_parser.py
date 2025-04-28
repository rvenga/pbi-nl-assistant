# app/services/tmdl_parser.py

import os
import json
import re
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TMDLParser:
    """Parser for Power BI TMDL files to extract semantic model information."""
    
    def __init__(self, base_directory: str):
        """Initialize parser with project base directory.
        
        Args:
            base_directory: Path to the Power BI project directory
        """
        self.base_directory = base_directory
        self.tables_info = {}
        self.relationships = []
        self.model_info = {}
    
    def parse_project(self) -> Dict[str, Any]:
        """Parse the entire project and return structured data.
        
        Returns:
            Dictionary with model, tables and relationships information
        """
        logger.info(f"Parsing project in: {self.base_directory}")
        
        # Check if directory exists
        if not os.path.isdir(self.base_directory):
            logger.error(f"Directory not found: {self.base_directory}")
            return {
                "model": {},
                "tables": {},
                "relationships": []
            }
        
        # Parse model.tmdl
        model_path = os.path.join(self.base_directory, "model.tmdl")
        if os.path.exists(model_path):
            logger.info(f"Parsing model file: {model_path}")
            self.model_info = self.parse_model_file(model_path)
        else:
            model_path = os.path.join(self.base_directory, "definition", "model.tmdl")
            if os.path.exists(model_path):
                logger.info(f"Parsing model file: {model_path}")
                self.model_info = self.parse_model_file(model_path)
            else:
                logger.warning("No model.tmdl found")
        
        # Parse relationships.tmdl
        relationships_path = os.path.join(self.base_directory, "relationships.tmdl")
        if os.path.exists(relationships_path):
            logger.info(f"Parsing relationships file: {relationships_path}")
            self.relationships = self.parse_relationships_file(relationships_path)
        else:
            relationships_path = os.path.join(self.base_directory, "definition", "relationships.tmdl")
            if os.path.exists(relationships_path):
                logger.info(f"Parsing relationships file: {relationships_path}")
                self.relationships = self.parse_relationships_file(relationships_path)
            else:
                logger.warning("No relationships.tmdl found")
        
        # Find the tables directory (might be "tables" or "definition/tables")
        tables_dir = os.path.join(self.base_directory, "tables")
        if not os.path.exists(tables_dir):
            tables_dir = os.path.join(self.base_directory, "definition", "tables")
            if not os.path.exists(tables_dir):
                logger.warning("No tables directory found")
                tables_dir = None
        
        # Parse table files
        if tables_dir:
            logger.info(f"Found tables directory: {tables_dir}")
            table_files = [f for f in os.listdir(tables_dir) if f.endswith(".tmdl")]
            logger.info(f"Found {len(table_files)} table files")
            
            for file_name in table_files:
                table_path = os.path.join(tables_dir, file_name)
                table_name = file_name.replace(".tmdl", "")
                logger.info(f"Parsing table: {table_name}")
                self.tables_info[table_name] = self.parse_table_file(table_path)
        
        # Compile everything into a structured output
        result = {
            "model": self.model_info,
            "tables": self.tables_info,
            "relationships": self.relationships
        }
        
        return result
    
    def parse_model_file(self, file_path: str) -> Dict[str, Any]:
        """Parse model.tmdl file to extract model information.
        
        Args:
            file_path: Path to model.tmdl file
            
        Returns:
            Dictionary with model information
        """
        model_info = {
            "culture": "",
            "sourceQueryCulture": "",
            "tables": [],
            "annotations": {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract culture
                culture_match = re.search(r'culture:\s*([^\n]+)', content)
                if culture_match:
                    model_info["culture"] = culture_match.group(1).strip()
                
                # Extract source query culture
                source_culture_match = re.search(r'sourceQueryCulture:\s*([^\n]+)', content)
                if source_culture_match:
                    model_info["sourceQueryCulture"] = source_culture_match.group(1).strip()
                
                # Extract table references
                table_refs = re.findall(r'ref table ([^\n]+)', content)
                model_info["tables"] = [table.strip() for table in table_refs]
                
                # Extract annotations
                annotations = re.findall(r'annotation ([^\s]+)\s*=\s*([^\n]+)', content)
                for key, value in annotations:
                    model_info["annotations"][key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error parsing model file: {e}")
        
        return model_info
    
    def parse_relationships_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse relationships.tmdl file to extract relationship information.
        
        Args:
            file_path: Path to relationships.tmdl file
            
        Returns:
            List of dictionaries with relationship information
        """
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find all relationship blocks
                relationship_blocks = re.findall(r'relationship ([^\n]+)([^a-zA-Z0-9_][\s\S]*?)(?=relationship|$)', content)
                
                for rel_id, rel_content in relationship_blocks:
                    relationship = {
                        "id": rel_id.strip(),
                        "fromTable": "",
                        "fromColumn": "",
                        "toTable": "",
                        "toColumn": "",
                        "isActive": True,
                        "crossFilteringBehavior": "automatic",
                        "joinOnDateBehavior": "datePartOnly" if "joinOnDateBehavior" in rel_content else None
                    }
                    
                    # Extract relationship properties
                    from_match = re.search(r'fromColumn:\s*([^\n]+)', rel_content)
                    to_match = re.search(r'toColumn:\s*([^\n]+)', rel_content)
                    is_active_match = re.search(r'isActive:\s*([^\n]+)', rel_content)
                    
                    if from_match:
                        from_parts = from_match.group(1).strip().split('.')
                        if len(from_parts) == 2:
                            relationship["fromTable"] = from_parts[0].strip("'")
                            relationship["fromColumn"] = from_parts[1].strip("'")
                    
                    if to_match:
                        to_parts = to_match.group(1).strip().split('.')
                        if len(to_parts) == 2:
                            relationship["toTable"] = to_parts[0].strip("'")
                            relationship["toColumn"] = to_parts[1].strip("'")
                    
                    if is_active_match:
                        is_active_value = is_active_match.group(1).strip().lower()
                        relationship["isActive"] = is_active_value == "true"
                    
                    # Extract cardinality
                    to_cardinality_match = re.search(r'toCardinality:\s*([^\n]+)', rel_content)
                    if to_cardinality_match:
                        relationship["toCardinality"] = to_cardinality_match.group(1).strip()
                    
                    relationships.append(relationship)
        except Exception as e:
            logger.error(f"Error parsing relationships file: {e}")
        
        return relationships
    
    def parse_table_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a table.tmdl file to extract table schema and measures.
        
        Args:
            file_path: Path to table.tmdl file
            
        Returns:
            Dictionary with table information
        """
        table_info = {
            "name": "",
            "columns": [],
            "measures": [],
            "partitions": [],
            "annotations": {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract table name
                table_match = re.search(r'table ([^\n]+)', content)
                if table_match:
                    table_info["name"] = table_match.group(1).strip()
                
                # Extract columns
                column_blocks = re.findall(r'column ([^\n]+)([\s\S]*?)(?=column|measure|partition|annotation\s|$)', content)
                for col_name, col_content in column_blocks:
                    column = {
                        "name": col_name.strip(),
                        "dataType": "",
                        "formatString": "",
                        "lineageTag": "",
                        "summarizeBy": "none",
                        "annotations": {}
                    }
                    
                    # Extract column properties
                    data_type_match = re.search(r'dataType:\s*([^\n]+)', col_content)
                    if data_type_match:
                        column["dataType"] = data_type_match.group(1).strip()
                    
                    format_string_match = re.search(r'formatString:\s*([^\n]+)', col_content)
                    if format_string_match:
                        column["formatString"] = format_string_match.group(1).strip()
                    
                    lineage_tag_match = re.search(r'lineageTag:\s*([^\n]+)', col_content)
                    if lineage_tag_match:
                        column["lineageTag"] = lineage_tag_match.group(1).strip()
                    
                    summarize_by_match = re.search(r'summarizeBy:\s*([^\n]+)', col_content)
                    if summarize_by_match:
                        column["summarizeBy"] = summarize_by_match.group(1).strip()
                    
                    # Extract column annotations
                    col_annotations = re.findall(r'annotation ([^\s]+)\s*=\s*([^\n]+)', col_content)
                    for key, value in col_annotations:
                        column["annotations"][key.strip()] = value.strip()
                    
                    table_info["columns"].append(column)
                
                # Extract measures
                measure_blocks = re.findall(r'measure ([^\n]+)([\s\S]*?)(?=measure|column|partition|annotation\s|$)', content)
                for measure_name, measure_content in measure_blocks:
                    measure = {
                        "name": measure_name.strip(),
                        "expression": "",
                        "formatString": "",
                        "lineageTag": "",
                        "annotations": {}
                    }
                    
                    # Look for expression first - might be on the same line
                    if '=' in measure_name:
                        name_parts = measure_name.split('=', 1)
                        measure["name"] = name_parts[0].strip()
                        expression_start = name_parts[1].strip()
                        
                        # Check if there's more expression in the content
                        expr_lines = [expression_start]
                        for line in measure_content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('formatString:') and not line.startswith('lineageTag:') and not line.startswith('annotation'):
                                expr_lines.append(line)
                        
                        measure["expression"] = '\n'.join(expr_lines)
                    else:
                        # Expression might be on multiple lines
                        expr_lines = []
                        for line in measure_content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('formatString:') and not line.startswith('lineageTag:') and not line.startswith('annotation'):
                                expr_lines.append(line)
                        
                        measure["expression"] = '\n'.join(expr_lines)
                    
                    # Extract measure properties
                    format_string_match = re.search(r'formatString:\s*([^\n]+)', measure_content)
                    if format_string_match:
                        measure["formatString"] = format_string_match.group(1).strip()
                    
                    lineage_tag_match = re.search(r'lineageTag:\s*([^\n]+)', measure_content)
                    if lineage_tag_match:
                        measure["lineageTag"] = lineage_tag_match.group(1).strip()
                    
                    # Extract measure annotations
                    measure_annotations = re.findall(r'annotation ([^\s]+)\s*=\s*([^\n]+)', measure_content)
                    for key, value in measure_annotations:
                        measure["annotations"][key.strip()] = value.strip()
                    
                    table_info["measures"].append(measure)
                
                # Extract partitions
                partition_blocks = re.findall(r'partition ([^\n]+)([\s\S]*?)(?=partition|column|measure|annotation\s|$)', content)
                for partition_name, partition_content in partition_blocks:
                    partition = {
                        "name": partition_name.strip(),
                        "mode": "",
                        "source": ""
                    }
                    
                    # Extract partition properties
                    mode_match = re.search(r'mode:\s*([^\n]+)', partition_content)
                    if mode_match:
                        partition["mode"] = mode_match.group(1).strip()
                    
                    # Extract source (can be multi-line)
                    source_match = re.search(r'source\s*=\s*```([\s\S]*?)```', partition_content)
                    if source_match:
                        partition["source"] = source_match.group(1).strip()
                    
                    table_info["partitions"].append(partition)
                
                # Extract table annotations
                table_annotations = re.findall(r'annotation ([^\s]+)\s*=\s*([^\n]+)', content)
                for key, value in table_annotations:
                    table_info["annotations"][key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error parsing table file: {e}")
        
        return table_info
    
    def generate_clean_json(self) -> Dict[str, Any]:
        """Generate a clean, simplified JSON schema from the parsed model.
        
        Returns:
            Dictionary with clean schema
        """
        # First ensure we've parsed the project
        if not self.tables_info and not self.relationships:
            self.parse_project()
        
        clean_model = {
            "tables": [],
            "relationships": [],
            "measures": []
        }
        
        # Process tables and their columns
        for table_name, table_info in self.tables_info.items():
            clean_table = {
                "name": table_info.get('name', table_name),
                "columns": []
            }
            
            # Add columns
            for column in table_info.get('columns', []):
                clean_table['columns'].append({
                    "name": column.get('name', ''),
                    "dataType": column.get('dataType', ''),
                    "summarizeBy": column.get('summarizeBy', 'none')
                })
            
            clean_model['tables'].append(clean_table)
            
            # Collect measures
            for measure in table_info.get('measures', []):
                clean_model['measures'].append({
                    "name": measure.get('name', ''),
                    "expression": measure.get('expression', ''),
                    "table": table_info.get('name', table_name),
                    "formatString": measure.get('formatString', '')
                })
        
        # Process relationships
        for relationship in self.relationships:
            clean_relationship = {
                "fromTable": relationship.get('fromTable', ''),
                "fromColumn": relationship.get('fromColumn', ''),
                "toTable": relationship.get('toTable', ''),
                "toColumn": relationship.get('toColumn', ''),
                "isActive": relationship.get('isActive', True)
            }
            
            # Only add cardinality if it's specified
            if 'toCardinality' in relationship:
                clean_relationship['toCardinality'] = relationship['toCardinality']
            
            clean_model['relationships'].append(clean_relationship)
        
        return clean_model
    
    def output_json(self, output_file: str = "pbi_schema.json", clean: bool = True, indent: int = 2) -> None:
        """Parse the project and output the results as JSON.
        
        Args:
            output_file: Path to output JSON file
            clean: Whether to output clean schema or raw parsed data
            indent: JSON indentation level
        """
        # Parse project if not already parsed
        if not self.tables_info and not self.relationships:
            self.parse_project()
        
        # Generate output data
        if clean:
            result = self.generate_clean_json()
        else:
            result = {
                "model": self.model_info,
                "tables": self.tables_info,
                "relationships": self.relationships
            }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=indent)
        
        logger.info(f"Schema exported to: {output_file}")
        logger.info(f"Tables: {len(result.get('tables', []))}")
        logger.info(f"Measures: {len(result.get('measures', []) if 'measures' in result else [])}")
        logger.info(f"Relationships: {len(result.get('relationships', []))}")