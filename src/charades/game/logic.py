"""Game logic for handling user interactions."""

from django.conf import settings
from django.db import transaction

from charades.game.ai_utils import evaluate_description
from charades.game.ai_utils import get_random_word
from charades.game.models import Player
from charades.game.schemas import TwilioErrorResponse
from charades.game.schemas import TwilioSuccessResponse
from charades.game.utils import create_twiml_response
from charades.game.utils import MESSAGES


def handle_opt_in(
    phone_number: str,
) -> TwilioSuccessResponse | TwilioErrorResponse:
    """Handle opt-in request from a user.

    Args:
        phone_number: The phone number in E.164 format

    Returns:
        Response with TwiML for success or error
    """
    try:
        with transaction.atomic():
            player, created = Player.get_or_create_player(phone_number)

            if not created and player.is_active:
                # Player exists and is already active
                return TwilioSuccessResponse(
                    twiml=create_twiml_response(MESSAGES["already_opted_in"]),
                )

            # Opt in the player (handles both new and existing players)
            player.opt_in()

            return TwilioSuccessResponse(
                twiml=create_twiml_response(MESSAGES["opt_in_success"]),
            )
    except Exception as e:
        return TwilioErrorResponse(
            message=f"Failed to opt in: {str(e)}",
            code=400,
        )


def handle_opt_out(
    phone_number: str,
) -> TwilioSuccessResponse | TwilioErrorResponse:
    """Handle opt-out request from a user.

    Args:
        phone_number: The phone number in E.164 format

    Returns:
        Response with TwiML for success or error
    """
    try:
        with transaction.atomic():
            player, _ = Player.get_or_create_player(phone_number)

            # End any active game sessions
            player.end_active_sessions()

            # Opt out the player
            player.opt_out()

            return TwilioSuccessResponse(
                twiml=create_twiml_response(MESSAGES["opt_out_success"]),
            )
    except Exception as e:
        return TwilioErrorResponse(
            message=f"Failed to opt out: {str(e)}",
            code=400,
        )


def handle_game_message(
    player: Player,
    message: str,
) -> TwilioSuccessResponse | TwilioErrorResponse:
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
        Response with appropriate TwiML
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
        return TwilioSuccessResponse(
            twiml=create_twiml_response(MESSAGES["how_to_play"]),
        )

    except Exception as e:
        return TwilioErrorResponse(
            message=f"Failed to process message: {str(e)}",
            code=400,
        )


def handle_language_selection(
    player: Player,
    language_code: str,
) -> TwilioSuccessResponse | TwilioErrorResponse:
    """Handle language selection from a player.

    Args:
        player: The Player instance
        language_code: Two-letter ISO 639-1 language code (e.g. 'EN', 'KO')

    Returns:
        Response with TwiML containing the word to describe
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

            return TwilioSuccessResponse(
                twiml=create_twiml_response(
                    MESSAGES["new_game"].format(
                        language=settings.SUPPORTED_LANGUAGES[language_code.upper()],
                        word=word,
                    ),
                ),
            )
    except Exception as e:
        return TwilioErrorResponse(
            message=f"Failed to start game: {str(e)}",
            code=400,
        )


def handle_word_description(
    player: Player,
    description: str,
) -> TwilioSuccessResponse | TwilioErrorResponse:
    """Handle a player's attempt to describe their word.

    Args:
        player: The Player instance
        description: The player's description of their word

    Returns:
        Response with TwiML containing the score and feedback
    """
    try:
        with transaction.atomic():
            # Get active session
            session = player.gamesession_set.filter(status="active").first()
            if not session:
                return TwilioSuccessResponse(
                    twiml=create_twiml_response(MESSAGES["no_active_game"]),
                )

            # Evaluate description using OpenAI
            score, feedback = evaluate_description(
                word=session.word,
                description=description,
                language=session.language,
            )

            # Complete the session with score
            session.complete(score=score)

            return TwilioSuccessResponse(
                twiml=create_twiml_response(
                    MESSAGES["game_complete"].format(
                        score=score,
                        feedback=feedback,
                    ),
                ),
            )
    except Exception as e:
        return TwilioErrorResponse(
            message=f"Failed to evaluate description: {str(e)}",
            code=400,
        )
