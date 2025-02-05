"""Anthropic LLM provider implementation."""

import json
import logging
from django.conf import settings
from anthropic import Anthropic

from charades.game.ai.base import LLMProvider
from charades.game.ai.models import EvaluationResponse
from charades.game.ai.prompts import get_random_word_prompt
from charades.game.ai.prompts import get_evaluation_prompt

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic implementation of LLM provider."""

    def __init__(self) -> None:
        """Initialize Anthropic client."""
        self.client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY,
        )

    def get_random_word(
        self,
        language_code: str,
    ) -> str:
        """Get random word using Anthropic.

        Args:
            language_code: ISO 639-1 language code (e.g., 'en' for English)

        Returns:
            str: Random word in target language

        Raises:
            Exception: If API call fails
        """
        language_name = settings.SUPPORTED_LANGUAGES[language_code.upper()]
        prompt = get_random_word_prompt(language_name)

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()  # type: ignore
        except Exception as e:
            logger.error(f"Anthropic random word generation failed: {str(e)}")
            raise

    def evaluate_description(
        self,
        word: str,
        description: str,
        language: str,
    ) -> tuple[int, str]:
        """Evaluate description using Anthropic.

        Args:
            word: The target word being described
            description: The player's description
            language: ISO 639-1 language code (e.g., 'en' for English)

        Returns:
            tuple: (score 0-100, feedback string)

        Raises:
            Exception: If API call or response parsing fails
        """
        language_name = settings.SUPPORTED_LANGUAGES[language.upper()]
        prompt = get_evaluation_prompt(word, language_name)

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system=prompt,
                messages=[{"role": "user", "content": description}],
            )
            result = response.content[0].text.strip()  # type: ignore

            # Parse and validate response
            data = json.loads(result)
            evaluation = EvaluationResponse(**data)
            return evaluation.score, evaluation.feedback

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Anthropic response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Anthropic evaluation failed: {str(e)}")
            raise
