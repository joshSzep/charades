"""LLM provider manager implementation."""

import logging
from typing import Callable
from typing import TypeVar

from charades.game.ai.base import LLMProvider

logger = logging.getLogger(__name__)

T = TypeVar("T")


class LLMProviderManager:
    """Manager class for LLM providers with fallback support."""

    def __init__(
        self,
        primary: LLMProvider,
        fallback: LLMProvider,
    ) -> None:
        """Initialize with primary and fallback providers.

        Args:
            primary: Primary LLM provider
            fallback: Fallback LLM provider
        """
        self.primary = primary
        self.fallback = fallback

    def _try_with_fallback(
        self,
        operation: str,
        primary_func: Callable[[], T],
        fallback_func: Callable[[], T],
    ) -> T:
        """Try primary function with fallback to secondary function.

        Args:
            operation: Name of the operation for logging
            primary_func: Primary function to try first
            fallback_func: Fallback function to try if primary fails

        Returns:
            T: Result from either primary or fallback function

        Raises:
            Exception: If both primary and fallback fail
        """
        try:
            return primary_func()
        except Exception as e:
            logger.warning(
                f"Primary provider failed for {operation}: {str(e)}, trying fallback",
            )
            return fallback_func()

    def get_random_word(
        self,
        language_code: str,
    ) -> str:
        """Get random word using primary provider with fallback.

        Args:
            language_code: ISO 639-1 language code (e.g., 'en' for English)

        Returns:
            str: Random word in target language
        """
        return self._try_with_fallback(
            operation="random word generation",
            primary_func=lambda: self.primary.get_random_word(language_code),
            fallback_func=lambda: self.fallback.get_random_word(language_code),
        )

    def evaluate_description(
        self,
        word: str,
        description: str,
        language: str,
    ) -> tuple[int, str]:
        """Evaluate description using primary provider with fallback.

        Args:
            word: The target word being described
            description: The player's description
            language: ISO 639-1 language code (e.g., 'en' for English)

        Returns:
            tuple: (score 0-100, feedback string)
        """
        return self._try_with_fallback(
            operation="description evaluation",
            primary_func=lambda: self.primary.evaluate_description(
                word,
                description,
                language,
            ),
            fallback_func=lambda: self.fallback.evaluate_description(
                word,
                description,
                language,
            ),
        )
