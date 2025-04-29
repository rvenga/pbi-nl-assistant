# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
APP_TITLE = "Power BI NL Assistant"
APP_ICON = "📊"

# API settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

# Custom CSS for styling the app
CSS = """
<style>
    .chat-message {
        padding: 1rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #f0f2f6;
    }
    .chat-message.assistant {
        background-color: #e3f2fd;
    }
    .chat-message .content {
        display: inline-block;
    }
    .chat-message .role {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
    }
    .code-block {
        background-color: #1e1e1e;
        color: #dcdcdc;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        overflow-x: auto;
        margin: 1rem 0;
    }
    .measure-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    .visual-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2196F3;
    }
</style>
"""

# Example prompts to show in the sidebar
EXAMPLE_PROMPTS = [
    "How can I visualise TPR by sub_brand and region as a timeseries?",
    "Create a measure for sales YoY growth",
    "How should I visualize sales by region to spot trends and patterns?"
]