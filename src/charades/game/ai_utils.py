"""AI utilities for the game module."""

import logging

from charades.game.ai import llm_manager

logger = logging.getLogger(__name__)


def get_random_word(
    language_code: str,
) -> str:
    """Get a random word suitable for the game.

    Args:
        language_code: ISO 639-1 language code (e.g., 'en' for English)

    Returns:
        str: A random common noun in the specified language
    """
    return llm_manager.get_random_word(language_code)


def evaluate_description(
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
    return llm_manager.evaluate_description(word, description, language)
