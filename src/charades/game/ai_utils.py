"""AI utilities for the game module."""

import json
import logging
from typing import Callable
from django.conf import settings
from openai import OpenAI
from anthropic import Anthropic

logger = logging.getLogger(__name__)

openai_client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)

anthropic_client = Anthropic(
    api_key=settings.ANTHROPIC_API_KEY,
)


def try_with_fallback(
    primary_func: Callable[[], str],
    fallback_func: Callable[[], str],
) -> str:
    """Try primary function with fallback to secondary function.

    Args:
        primary_func: Primary function to try first
        fallback_func: Fallback function to try if primary fails

    Returns:
        str: Result from either primary or fallback function
    """
    try:
        return primary_func()
    except Exception as e:
        logger.warning(f"Primary API call failed: {str(e)}, trying fallback")
        return fallback_func()


def get_random_word(
    language_code: str,
) -> str:
    """Get a random word suitable for the game using OpenAI or Anthropic.

    Args:
        language_code: ISO 639-1 language code (e.g., 'en' for English)

    Returns:
        str: A random common noun in the specified language
    """
    language_name = settings.SUPPORTED_LANGUAGES[language_code.upper()]
    prompt = (
        f"Generate one random, common noun in {language_name}. "
        f"The word should be simple enough for language learners but "
        f"interesting enough for practice. If the language uses a "
        f"non-Latin alphabet, include both the native script and "
        f"romanization in parentheses. For example, in Korean: "
        f"사과 (sagwa). Respond with just the word, nothing else."
    )

    def try_openai() -> str:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=10,
            temperature=0.7,  # Add some randomness but not too much
        )
        return response.choices[0].message.content.strip()  # type: ignore

    def try_anthropic() -> str:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()  # type: ignore

    return try_with_fallback(try_openai, try_anthropic)


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
    language_name = settings.SUPPORTED_LANGUAGES[language.upper()]
    prompt = (
        f"You are evaluating a language learner's description of the word "
        f"'{word}' in {language_name}. Score their description from "
        f"0-100 based on: accuracy of the description (40%), grammar "
        f"and structure (30%), and vocabulary usage (30%). Provide "
        f"the score followed by a brief, encouraging feedback message "
        f"in {language_name} with English translation in parentheses. "
        f"Use this json format exactly, with no additional text: \n"
        f"{{\n"
        f'"SCORE": [0-100],\n'
        f'"FEEDBACK": "[Your feedback in both languages]"\n'
        f"}}\n"
    )

    def try_openai() -> tuple[int, str]:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": description},
            ],
        )
        result = response.choices[0].message.content.strip()  # type: ignore
        return parse_evaluation_response(result)

    def try_anthropic() -> tuple[int, str]:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            system=prompt,
            messages=[{"role": "user", "content": description}],
        )
        result = response.content[0].text.strip()  # type: ignore
        return parse_evaluation_response(result)

    try:
        return try_with_fallback(try_openai, try_anthropic)  # type: ignore
    except Exception as e:
        logger.error(f"Both APIs failed to evaluate: {str(e)}")
        return 50, "I had trouble evaluating your response, but keep practicing!"


def parse_evaluation_response(result: str) -> tuple[int, str]:
    """Parse evaluation response to extract score and feedback.

    Args:
        result: Raw response from AI model in JSON format

    Returns:
        tuple: (score, feedback)

    Raises:
        ValueError: If parsing fails
    """
    try:
        data = json.loads(result)

        score = int(data["SCORE"])
        feedback = str(data["FEEDBACK"])

        return score, feedback
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Failed to parse evaluation response `{result}`: {str(e)}")
        raise ValueError(f"Failed to parse evaluation response: {str(e)}")
