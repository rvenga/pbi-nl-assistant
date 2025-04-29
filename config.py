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

# Conversation settings
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))

# Custom CSS for styling the app
CSS = CSS = """
<style>
    /* Base theme colors */
    :root {
        --primary-bg: #0D1117;
        --secondary-bg: #161B22;
        --teal-accent: #2DD4BF;
        --teal-dark: #0F766E;
        --teal-light: #5EEAD4;
        --text-primary: #E6E6E6;
        --text-secondary: #A3A3A3;
        --code-bg: #1E293B;
    }

    /* Global overrides */
    .stApp {
        background-color: var(--primary-bg);
        color: var(--text-primary);
    }

    /* Sidebar styling */
    .css-1avcm0n, .css-10oheav {
        background-color: var(--secondary-bg) !important;
    }

    .css-1544g2n {
        padding: 2rem 1rem;
    }

    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--teal-light) !important;
    }

    /* Button styling */
    .stButton > button {
        background-color: var(--teal-dark) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: var(--teal-accent) !important;
        color: var(--primary-bg) !important;
    }

    /* Chat message styling */
    .chat-message {
        padding: 1rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }

    .chat-message.user {
        background-color: var(--secondary-bg);
        border-left: 4px solid var(--teal-accent);
    }

    .chat-message.assistant {
        background-color: var(--secondary-bg);
        border-left: 4px solid var(--teal-light);
    }

    .chat-message .content {
        display: inline-block;
        color: var(--text-primary);
    }

    .chat-message .role {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: var(--teal-light);
    }

    /* Code block styling */
    .code-block {
        background-color: var(--code-bg);
        color: var(--teal-light);
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        overflow-x: auto;
        margin: 1rem 0;
        border-left: 3px solid var(--teal-accent);
    }

    /* Measure card styling */
    .measure-card {
        background-color: var(--secondary-bg);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--teal-accent);
    }

    /* Visual card styling */
    .visual-card {
        background-color: var(--secondary-bg);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--teal-light);
    }

    /* Input area styling */
    .stTextInput > div > div > input {
        background-color: var(--secondary-bg);
        color: var(--text-primary);
        border: 1px solid var(--teal-dark);
    }

    /* File uploader styling */
    .stFileUploader > div > label {
        background-color: var(--teal-dark);
        color: white;
    }

    .stFileUploader > div > button {
        background-color: var(--teal-dark) !important;
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--secondary-bg);
        color: var(--teal-light) !important;
        border-radius: 0.5rem;
    }
    
    .streamlit-expanderContent {
        background-color: var(--secondary-bg);
        border-top: none !important;
        border-radius: 0 0 0.5rem 0.5rem;
    }

    /* Success and info messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 0.5rem;
    }
    
    .stSuccess {
        background-color: rgba(45, 212, 191, 0.2) !important;
    }
    
    .stInfo {
        background-color: rgba(94, 234, 212, 0.2) !important;
    }
    
    .stWarning {
        background-color: rgba(251, 191, 36, 0.2) !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.2) !important;
    }
    
    /* Progress and spinner colors */
    .stProgress > div > div > div > div {
        background-color: var(--teal-accent) !important;
    }
    
    /* Table styling */
    .stTable thead th {
        background-color: var(--teal-dark);
        color: white;
    }
    
    .stTable tbody tr:nth-child(even) {
        background-color: var(--secondary-bg);
    }
    
    .stTable tbody tr:nth-child(odd) {
        background-color: var(--primary-bg);
    }
</style>
"""

# Example prompts to show in the sidebar
EXAMPLE_PROMPTS = [
    "How can I visualise TPR by sub_brand and region as a timeseries?",
    "Create a measure for sales YoY growth",
    "How should I visualize sales by region to spot trends and patterns?"
]