"""Game logic for handling user interactions."""

from django.db import transaction

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
