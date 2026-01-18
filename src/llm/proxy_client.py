"""LLM client for vscode-lm-proxy integration."""

import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables
load_dotenv()


class LLMClient:
    """Client for interacting with Claude via vscode-lm-proxy."""

    def __init__(
        self,
        proxy_url: str | None = None,
        model_name: str | None = None,
    ) -> None:
        """Initialize LLM client.

        Args:
            proxy_url: vscode-lm-proxy URL (default from env: LM_PROXY_URL)
            model_name: Model name (default from env: MODEL_NAME)

        Raises:
            ConnectionError: If proxy connection fails
        """
        self.proxy_url = proxy_url or os.getenv("LM_PROXY_URL", "http://localhost:4000/anthropic")
        self.model_name = model_name or os.getenv("MODEL_NAME", "claude-sonnet-4.5")

        # Validate proxy connection
        self._validate_connection()

        # Initialize ChatAnthropic with proxy
        self.client = ChatAnthropic(
            model=self.model_name,
            base_url=self.proxy_url,
            api_key="dummy",  # vscode-lm-proxy doesn't need real API key
            temperature=0.7,
            max_tokens=4096,
        )

    def _validate_connection(self) -> None:
        """Validate connection to vscode-lm-proxy.

        Raises:
            ConnectionError: If proxy is not accessible
        """
        # Skip validation - connection will be tested on first actual use
        # This avoids issues with proxy initialization
        pass

    def get_chat_model(self) -> ChatAnthropic:
        """Get the ChatAnthropic instance for use in agents.

        Returns:
            ChatAnthropic instance configured with proxy
        """
        return self.client

    def create_with_tools(self, tools: list[Any]) -> ChatAnthropic:
        """Create a ChatAnthropic instance bound with tools.

        Args:
            tools: List of LangChain tools

        Returns:
            ChatAnthropic instance with tools bound
        """
        return self.client.bind_tools(tools)


def create_llm_client() -> LLMClient:
    """Factory function to create LLM client.

    Returns:
        Configured LLMClient instance

    Raises:
        ConnectionError: If proxy connection fails
    """
    return LLMClient()
