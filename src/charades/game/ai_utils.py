"""AI utilities for the game module."""

from django.conf import settings
from openai import OpenAI

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)


def get_random_word(
    language_code: str,
) -> str:
    """Get a random word suitable for the game using OpenAI.

    Args:
        language_code: ISO 639-1 language code (e.g., 'en' for English)

    Returns:
        str: A random common noun in the specified language
    """
    language_name = settings.SUPPORTED_LANGUAGES[language_code.upper()]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Generate one random, common noun in {language_name}. "
                    f"The word should be simple enough for language learners but "
                    f"interesting enough for practice. If the language uses a "
                    f"non-Latin alphabet, include both the native script and "
                    f"romanization in parentheses. For example, in Korean: "
                    f"사과 (sagwa). Respond with just the word, nothing else."
                ),
            }
        ],
        max_tokens=10,
        temperature=0.7,  # Add some randomness but not too much
    )
    return response.choices[0].message.content.strip()  # type: ignore


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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are evaluating a language learner's description of the word "
                    f"'{word}' in {language_name}. Score their description from "
                    f"0-100 based on: accuracy of the description (40%), grammar "
                    f"and structure (30%), and vocabulary usage (30%). Provide "
                    f"the score followed by a brief, encouraging feedback message "
                    f"in {language_name} with English translation in parentheses. "
                    f"Use this format exactly: \n"
                    f"SCORE: [0-100]\n"
                    f"FEEDBACK: [Your feedback in both languages]"
                ),
            },
            {
                "role": "user",
                "content": description,
            },
        ],
    )

    # Parse response to extract score and feedback
    result = response.choices[0].message.content.strip()  # type: ignore

    try:
        # Extract score and feedback using string parsing
        score_line = [line for line in result.split("\n") if line.startswith("SCORE:")][
            0
        ]
        feedback_line = [
            line for line in result.split("\n") if line.startswith("FEEDBACK:")
        ][0]

        score = int(score_line.replace("SCORE:", "").strip())
        feedback = feedback_line.replace("FEEDBACK:", "").strip()

        return score, feedback

    except (IndexError, ValueError) as _:
        # If parsing fails, return a default response
        return 50, "I had trouble evaluating your response, but keep practicing!"
