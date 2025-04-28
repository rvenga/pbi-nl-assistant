#!/usr/bin/env python
"""
Extract Power BI schema from TMDL files.

This command-line tool extracts semantic data from Power BI TMDL files
and creates a clean JSON representation of tables, relationships, and measures.

Usage:
  python extract_schema.py path/to/project/directory --output schema.json
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tmdl_parser import TMDLParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_schema(directory: str, output_file: str, raw: bool = False) -> None:
    """Extract schema from TMDL files and save to JSON.
    
    Args:
        directory: Path to project directory containing TMDL files
        output_file: Path to output JSON file
        raw: Whether to output raw parsed data instead of clean schema
    """
    logger.info(f"Extracting schema from: {directory}")
    
    # Initialize parser
    parser = TMDLParser(directory)
    
    # Parse project
    logger.info("Parsing project...")
    parser.parse_project()
    
    # Generate output
    if raw:
        logger.info("Generating raw schema...")
        result = {
            "model": parser.model_info,
            "tables": parser.tables_info,
            "relationships": parser.relationships
        }
    else:
        logger.info("Generating clean schema...")
        result = parser.generate_clean_json()
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    # Output summary
    if raw:
        logger.info(f"Tables found: {len(parser.tables_info)}")
        logger.info(f"Relationships found: {len(parser.relationships)}")
    else:
        logger.info(f"Tables: {len(result.get('tables', []))}")
        logger.info(f"Measures: {len(result.get('measures', []))}")
        logger.info(f"Relationships: {len(result.get('relationships', []))}")
    
    logger.info(f"Schema exported to: {output_file}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Extract Power BI schema from TMDL files')
    parser.add_argument('directory', help='Base directory of the Power BI project')
    parser.add_argument('--output', '-o', default='pbi_schema.json', help='Output JSON file')
    parser.add_argument('--raw', action='store_true', help='Output raw parsed data instead of clean schema')
    
    args = parser.parse_args()
    
    try:
        extract_schema(args.directory, args.output, args.raw)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()