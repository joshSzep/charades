"""Prompt templates for LLM interactions."""


def get_random_word_prompt(language_name: str) -> str:
    """Get prompt for random word generation.

    Args:
        language_name: Full name of the language (e.g., 'English')

    Returns:
        str: Formatted prompt
    """
    return (
        f"Generate one random, common noun in {language_name}. "
        f"The word should be simple enough for language learners but "
        f"interesting enough for practice. If the language uses a "
        f"non-Latin alphabet, include both the native script and "
        f"romanization in parentheses. For example, in Korean: "
        f"사과 (sagwa). Respond with just the word, nothing else."
    )


def get_evaluation_prompt(
    word: str,
    language_name: str,
) -> str:
    """Get prompt for evaluating descriptions.

    Args:
        word: The target word being described
        language_name: Full name of the language (e.g., 'English')

    Returns:
        str: Formatted prompt
    """
    return (
        f"You are evaluating a language learner's description of the word "
        f"'{word}' in {language_name}. Their description should be in {language_name}."
        f"Score their description from 0-100 based on: accuracy of the description "
        f"(40%), grammar and structure (30%), and vocabulary usage (30%). "
        f"Provide the score followed by a brief, encouraging feedback message "
        f"in {language_name} with English translation in parentheses. "
        f"Use this json format exactly, with no additional text: \n"
        f"{{\n"
        f'"score": [0-100],\n'
        f'"feedback": "[Your feedback in both languages]"\n'
        f"}}\n"
    )
