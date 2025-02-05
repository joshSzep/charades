"""Game logic for handling user interactions."""

from django.conf import settings
from django.db import transaction

from charades.game.ai_utils import evaluate_description
from charades.game.ai_utils import get_random_word
from charades.game.models import Player
from charades.game.utils import create_twiml_response
from charades.game.utils import MESSAGES


def handle_opt_in(
    phone_number: str,
) -> dict:
    """Handle opt-in request from a user.

    Args:
        phone_number: The phone number in E.164 format

    Returns:
        dict with twiml and code for response
    """
    try:
        with transaction.atomic():
            player, created = Player.get_or_create_player(phone_number)

            if not created and player.is_active:
                # Player exists and is already active
                return {
                    "twiml": create_twiml_response(MESSAGES["already_opted_in"]),
                    "code": 200,
                }

            # Opt in the player (handles both new and existing players)
            player.opt_in()

            return {
                "twiml": create_twiml_response(MESSAGES["opt_in_success"]),
                "code": 200,
            }
    except Exception as e:
        return {
            "twiml": create_twiml_response(f"Failed to opt in: {str(e)}"),
            "code": 400,
        }


def handle_opt_out(
    phone_number: str,
) -> dict:
    """Handle opt-out request from a user.

    Args:
        phone_number: The phone number in E.164 format

    Returns:
        dict with twiml and code for response
    """
    try:
        with transaction.atomic():
            player, _ = Player.get_or_create_player(phone_number)

            # End any active game sessions
            player.end_active_sessions()

            # Opt out the player
            player.opt_out()

            return {
                "twiml": create_twiml_response(MESSAGES["opt_out_success"]),
                "code": 200,
            }
    except Exception as e:
        return {
            "twiml": create_twiml_response(f"Failed to opt out: {str(e)}"),
            "code": 400,
        }


def handle_game_message(
    player: Player,
    message: str,
) -> dict:
    """Handle a game-related message from a player.

    This function:
    1. Checks if player has an active game session
    2. If yes, treats message as a word description
    3. If no, checks if message is a valid language code
    4. If neither, provides guidance on how to play

    Args:
        player: The Player instance
        message: The message from the player

    Returns:
        dict with twiml and code for response
    """
    try:
        # Check for active game session
        active_session = player.gamesession_set.filter(status="active").first()

        if active_session:
            # Player has active game - treat message as word description
            return handle_word_description(player, message)

        # No active game - check if message is a language code
        if len(message) == 2 and message.upper() in settings.SUPPORTED_LANGUAGES:
            return handle_language_selection(player, message)

        # Neither - provide guidance
        return {
            "twiml": create_twiml_response(MESSAGES["how_to_play"]),
            "code": 200,
        }

    except Exception as e:
        return {
            "twiml": create_twiml_response(f"Failed to process message: {str(e)}"),
            "code": 400,
        }


def handle_language_selection(
    player: Player,
    language_code: str,
) -> dict:
    """Handle language selection from a player.

    Args:
        player: The Player instance
        language_code: Two-letter ISO 639-1 language code (e.g. 'EN', 'KO')

    Returns:
        dict with twiml and code for response
    """
    try:
        with transaction.atomic():
            # End any existing active sessions
            player.end_active_sessions()

            # Get a random word in the selected language
            word = get_random_word(language_code)

            # Create new game session
            _ = player.gamesession_set.create(
                word=word,
                language=language_code.lower(),
            )

            return {
                "twiml": create_twiml_response(
                    MESSAGES["new_game"].format(
                        language=settings.SUPPORTED_LANGUAGES[language_code.upper()],
                        word=word,
                    ),
                ),
                "code": 200,
            }
    except Exception as e:
        return {
            "twiml": create_twiml_response(f"Failed to start game: {str(e)}"),
            "code": 400,
        }


def handle_word_description(
    player: Player,
    description: str,
) -> dict:
    """Handle a player's attempt to describe their word.

    Args:
        player: The Player instance
        description: The player's description of their word

    Returns:
        dict with twiml and code for response
    """
    try:
        with transaction.atomic():
            # Get active session
            session = player.gamesession_set.filter(status="active").first()
            if not session:
                return {
                    "twiml": create_twiml_response(MESSAGES["no_active_game"]),
                    "code": 200,
                }

            # Evaluate description using OpenAI
            score, feedback = evaluate_description(
                word=session.word,
                description=description,
                language=session.language,
            )

            # Complete the session with score
            session.complete(
                score=score,
                description=description,
                feedback=feedback,
            )

            return {
                "twiml": create_twiml_response(
                    MESSAGES["game_complete"].format(
                        score=score,
                        feedback=feedback,
                    ),
                ),
                "code": 200,
            }
    except Exception as e:
        return {
            "twiml": create_twiml_response(f"Failed to evaluate description: {str(e)}"),
            "code": 400,
        }


def handle_player_command(
    phone_number: str,
    command: str,
) -> dict:
    """Route player commands to appropriate handlers.

    This function:
    1. Handles opt-in/opt-out commands
    2. For other commands:
        a. Gets or creates player
        b. Verifies player is opted in
        c. Routes to game message handler

    Args:
        phone_number: The player's phone number in E.164 format
        command: The command text from the player (lowercase)

    Returns:
        dict with twiml and code for response
    """
    # Normalize command
    command = command.strip().lower()

    # Handle opt-in/opt-out first
    if command == "langgang":
        return handle_opt_in(phone_number)
    elif command == "optout":
        return handle_opt_out(phone_number)

    # Get or create player for other commands
    player, _ = Player.get_or_create_player(phone_number)

    # Check if player is opted in
    if not player.is_active:
        return {
            "twiml": create_twiml_response(MESSAGES["not_opted_in"]),
            "code": 200,
        }

    # Handle the game message
    return handle_game_message(player, command)
