# Power BI Natural Language Assistant

A powerful Streamlit web application that helps you generate DAX measures and visualization guidance for Power BI using natural language. Upload your Power BI files (PBIX or TMDL) and chat with an AI assistant to get assistance.

## Features

- **Multi-Format Support**: Process both PBIX files and TMDL file collections
- **Natural Language Interface**: Ask questions in plain English
- **DAX Measure Generation**: Get ready-to-use DAX formulas
- **Visualization Guidance**: Receive recommendations for visualization types
- **Context-Aware Responses**: All responses are based on your specific Power BI file structure

## Getting Started

### Prerequisites

- Python 3.8+
- An Anthropic API key (for Claude)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/rvenga/pbi-nl-assistant.git
   cd powerbi-nl-assistant
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   CLAUDE_MODEL=claude-3-sonnet-20240229
   ```

### Running the Application

Start the Streamlit app:
```
streamlit run main.py
```

The application will open in your default web browser at http://localhost:8501

## Usage

### Using the Web App

1. Choose the file type you want to upload (PBIX or TMDL Files)
2. Upload your file(s)
3. Wait for the file to be processed
4. Use the chat interface to ask questions about measures or visualizations
5. View the responses, including formatted DAX code

### Using the Command-Line Tool

For extracting schemas without using the web app:

```
python tools/extract_schema.py path/to/your/project --output schema.json
```

Options:
- `--raw`: Output raw parsed data instead of clean schema
- `--output/-o`: Specify output file path

## TMDL Parser

The TMDL parser can extract semantic data from Power BI TMDL files including:

- Tables, columns and their data types
- Measures and their DAX expressions
- Relationships between tables
- Model information and annotations

### Example TMDL Structure

A typical TMDL project structure might look like:

```
project/
 ┣ .pbi
 ┣ definition/
 ┃ ┣ cultures/
 ┃ ┣ roles/
 ┃ ┣ tables/
 ┃ ┃ ┣ table1.tmdl
 ┃ ┃ ┣ table2.tmdl
 ┃ ┣ model.tmdl
 ┃ ┗ relationships.tmdl
```

## Example Prompts

- "Create a measure for YoY growth percentage"
- "How should I visualize sales by region?"
- "Create a measure for running total"
- "What's the best way to show top 10 customers?"
- "Create a time intelligence measure for MTD sales"

## Project Structure

```
powerbi-nl-assistant/
├── .env                        # Environment variables
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── main.py                     # Main application entry point
├── config.py                   # Configuration settings
├── app/
│   ├── ui/                     # Streamlit UI components
│   ├── services/               # Core services
│   │   ├── pbix_parser.py      # PBIX extraction logic
│   │   ├── tmdl_parser.py      # TMDL extraction logic
│   │   ├── schema_manager.py   # Unified schema handling
│   │   ├── llm_service.py      # Claude API integration
│   │   └── context_builder.py  # Build LLM context from metadata
│   └── utils/                  # Helper utilities
├── tools/                      # Command-line tools
│   └── extract_schema.py       # Standalone schema extraction tool

```

## Limitations

- The app extracts basic metadata from PBIX files but cannot access all details
- Only works with correctly formatted PBIX files or TMDL structures
- Requires an internet connection to call Claude API
- Response quality depends on the quality of the metadata extracted

## Notes for Production Use

For a production environment, consider:
- Implementing proper authentication
- Adding database storage for file metadata
- Enhancing the parsers for better metadata extraction
- Adding visualization previews
- Improving error handling and logging