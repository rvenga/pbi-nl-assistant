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
# In config.py
CSS = """
<style>
    /* Force dark theme */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
        background-color: var(--primary-bg) !important;
        color: var(--text-primary) !important;
    }
    
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
    .css-1avcm0n, .css-10oheav, [data-testid="stSidebar"] {
        background-color: var(--secondary-bg) !important;
    }

    /* Override any Streamlit light theme elements */
    .st-emotion-cache-1avcm0n, .st-emotion-cache-10oheav {
        background-color: var(--secondary-bg) !important;
    }

    .st-emotion-cache-1wbqy5l, .st-emotion-cache-1l16s73 {
        color: var(--text-primary) !important;
    }

    /* Rest of your existing CSS */
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
    .stTextInput > div > div > input, [data-testid="stWidgetLabel"] {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--teal-dark) !important;
    }

    /* File uploader styling */
    .stFileUploader > div > label {
        background-color: var(--teal-dark) !important;
        color: white !important;
    }

    .stFileUploader > div > button {
        background-color: var(--teal-dark) !important;
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader, .st-emotion-cache-ztfqz8 {
        background-color: var(--secondary-bg) !important;
        color: var(--teal-light) !important;
        border-radius: 0.5rem !important;
    }
    
    .streamlit-expanderContent, .st-emotion-cache-16idsys {
        background-color: var(--secondary-bg) !important;
        border-top: none !important;
        border-radius: 0 0 0.5rem 0.5rem !important;
    }

    /* Success and info messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 0.5rem !important;
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
    .stTable thead th, [data-testid="StyledFullScreenFrame"] thead th {
        background-color: var(--teal-dark) !important;
        color: white !important;
    }
    
    .stTable tbody tr:nth-child(even), [data-testid="StyledFullScreenFrame"] tbody tr:nth-child(even) {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .stTable tbody tr:nth-child(odd), [data-testid="StyledFullScreenFrame"] tbody tr:nth-child(odd) {
        background-color: var(--primary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    /* More specific selectors for various Streamlit elements */
    .st-emotion-cache-1gulkj5, .st-emotion-cache-1l16s73 {
        color: var(--text-primary) !important;
    }
    
    /* Force dark scrollbars */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--primary-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--teal-dark);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--teal-accent);
    }
</style>
"""

EXAMPLE_PROMPTS = [
    "How can I visualise TPR by sub_brand and region as a timeseries?",
    "Create a measure for sales YoY growth",
    "How should I visualize sales by region to spot trends and patterns?"
]