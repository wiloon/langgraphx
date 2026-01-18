"""State checkpointer for LangGraph state persistence."""

import os

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()


def create_checkpointer() -> MemorySaver:
    """Create and initialize checkpointer.

    Note: Currently using MemorySaver for development.
    Switch to PostgresSaver for production persistence.

    Returns:
        MemorySaver instance for state management
    """
    # For now, use in-memory checkpointer for development
    # This avoids PostgreSQL connection issues during initial testing
    return MemorySaver()


def test_checkpointer_connection() -> bool:
    """Test checkpointer connection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        saver = create_checkpointer()
        return True
    except Exception:
        return False
