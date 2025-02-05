"""AI module for language game interactions."""

from charades.game.ai.anthropic import AnthropicProvider
from charades.game.ai.manager import LLMProviderManager
from charades.game.ai.openai import OpenAIProvider

# Initialize providers
openai_provider = OpenAIProvider()
anthropic_provider = AnthropicProvider()

# Create manager with OpenAI as primary and Anthropic as fallback
llm_manager = LLMProviderManager(
    primary=openai_provider,
    fallback=anthropic_provider,
)
