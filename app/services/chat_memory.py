# app/services/chat_memory.py

import streamlit as st
from typing import List, Dict, Any, Optional

class ChatMemory:
    """Manages chat history and context for the assistant."""
    
    def __init__(self, max_history: int = 20):
        """Initialize chat memory.
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history
        
        # Initialize session state for messages if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Initialize session state for chat context if not exists
        if "chat_context" not in st.session_state:
            st.session_state.chat_context = {}
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history.
        
        Args:
            role: The role of the sender (user or assistant)
            content: The message content
        """
        # Add message to history
        st.session_state.messages.append({"role": role, "content": content})
        
        # Trim history if it exceeds max_history
        if len(st.session_state.messages) > self.max_history:
            st.session_state.messages = st.session_state.messages[-self.max_history:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the chat history.
        
        Returns:
            List of message dictionaries
        """
        return st.session_state.messages
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """Get the last n messages in the chat history.
        
        Args:
            n: Number of messages to retrieve
            
        Returns:
            List of the last n message dictionaries
        """
        return st.session_state.messages[-n:] if st.session_state.messages else []
    
    def clear_history(self) -> None:
        """Clear the chat history."""
        st.session_state.messages = []
    
    def set_context(self, key: str, value: Any) -> None:
        """Set a context value that persists across the conversation.
        
        Args:
            key: Context key
            value: Context value
        """
        st.session_state.chat_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value.
        
        Args:
            key: Context key
            default: Default value if key doesn't exist
            
        Returns:
            Context value or default
        """
        return st.session_state.chat_context.get(key, default)
    
    def get_all_context(self) -> Dict[str, Any]:
        """Get all context values.
        
        Returns:
            Dictionary of all context values
        """
        return st.session_state.chat_context
    
    def clear_context(self) -> None:
        """Clear all context values."""
        st.session_state.chat_context = {}
    
    def format_history_for_llm(self, include_n: int = 10) -> str:
        """Format chat history for inclusion in LLM context.
        
        Args:
            include_n: Number of recent messages to include
            
        Returns:
            Formatted chat history string
        """
        recent_messages = self.get_last_n_messages(include_n)
        if not recent_messages:
            return ""
        
        history_text = "# RECENT CONVERSATION HISTORY\n\n"
        
        for msg in recent_messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            history_text += f"{role}: {content}\n\n"
        
        return history_text