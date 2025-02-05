"""Base classes for LLM providers."""

from abc import ABC
from abc import abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_random_word(
        self,
        language_code: str,
    ) -> str:
        """Get a random word suitable for the game.

        Args:
            language_code: ISO 639-1 language code (e.g., 'en' for English)

        Returns:
            str: A random common noun in the specified language
        """
        pass

    @abstractmethod
    def evaluate_description(
        self,
        word: str,
        description: str,
        language: str,
    ) -> tuple[int, str]:
        """Evaluate a player's description of a word.

        Args:
            word: The target word being described
            description: The player's description
            language: ISO 639-1 language code (e.g., 'en' for English)

        Returns:
            tuple: (score 0-100, feedback string)
        """
        pass
