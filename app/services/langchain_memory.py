# app/services/langchain_memory.py
from langchain.memory import ConversationBufferMemory, StreamlitChatMessageHistory
from langchain.schema import SystemMessage
import streamlit as st
from typing import List, Dict, Any, Optional
import logging

logging

class LangchainChatMemory:
    """Manages chat history and context using Langchain's memory components."""
    
    def __init__(self, max_history: int = 20):
        """Initialize Langchain-based chat memory.
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        # Initialize Streamlit-based message history
        self.message_history = StreamlitChatMessageHistory(key="langchain_messages")
        
        # Initialize ConversationBufferMemory with the StreamlitChatMessageHistory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=self.message_history,
            return_messages=True,
            output_key="output"
        )
        
        self.max_history = max_history
        
        # Initialize session state for chat context if not exists
        if "chat_context" not in st.session_state:
            st.session_state.chat_context = {}
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history.
        
        Args:
            role: The role of the sender (user or assistant)
            content: The message content
        """
        # Map role to LangChain's expected format
        if role == "user":
            self.message_history.add_user_message(content)
        elif role == "assistant":
            self.message_history.add_ai_message(content)
        elif role == "system":
            # LangChain handles system messages differently
            self.message_history.messages.append(SystemMessage(content=content))
        
        # Trim history if it exceeds max_history
        if len(self.message_history.messages) > self.max_history:
            # Keep only the most recent messages
            self.message_history.messages = self.message_history.messages[-self.max_history:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the chat history in the format expected by the app.
        
        Returns:
            List of message dictionaries
        """
        # Convert LangChain messages to the app's expected format
        converted_messages = []
        for message in self.message_history.messages:
            if hasattr(message, "type") and message.type == "system":
                role = "system"
            elif hasattr(message, "type") and message.type == "human":
                role = "user"
            elif hasattr(message, "type") and message.type == "ai":
                role = "assistant"
            else:
                continue
            
            converted_messages.append({
                "role": role,
                "content": message.content
            })
        
        return converted_messages
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """Get the last n messages in the chat history.
        
        Args:
            n: Number of messages to retrieve
            
        Returns:
            List of the last n message dictionaries
        """
        messages = self.get_messages()
        return messages[-n:] if messages else []
    
    def clear_history(self) -> None:
        """Clear the chat history."""
        self.message_history.clear()
    
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
    
    def format_history_for_anthropic(self) -> List[Dict[str, str]]:
        """Format chat history for inclusion in Anthropic/Claude API calls.
        
        Returns:
            List of message dictionaries in the format expected by Anthropic
        """
        # This returns messages in the format expected by Anthropic API
        return self.get_messages()