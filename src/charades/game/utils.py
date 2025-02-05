"""Utility functions for the game module."""

from twilio.twiml.messaging_response import MessagingResponse


def create_twiml_response(message: str) -> str:
    """Create a TwiML response with the given message.

    Args:
        message: The message to send back to the user

    Returns:
        str: The TwiML response as a string
    """
    response = MessagingResponse()
    response.message(message)
    return str(response)


# Message templates
MESSAGES = {
    "opt_in_success": (
        "Welcome to LangGang Charades! 🎮 You're now opted in. "
        "To start playing, send a language code (e.g. EN for English or KO for"
        " Korean). You can opt out at any time by replying OPTOUT."
    ),
    "opt_out_success": (
        "You've been successfully opted out of LangGang Charades. "
        "Thanks for playing! Text LANG to opt back in anytime."
    ),
    "already_opted_in": (
        "You're already opted in to LangGang Charades! "
        "To play, send a language code (e.g. EN for English or KO for Korean). "
        "Or reply OPTOUT to opt out."
    ),
    "error_generic": ("Sorry, something went wrong. Please try again later."),
}
