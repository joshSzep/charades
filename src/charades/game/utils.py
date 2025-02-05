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
        "Thanks for playing! Text LANGGANG to opt back in anytime."
    ),
    "already_opted_in": (
        "You're already opted in to LangGang Charades! "
        "To play, send a language code (e.g. EN for English or KO for Korean). "
        "Or reply OPTOUT to opt out."
    ),
    "error_generic": ("Sorry, something went wrong. Please try again later."),
    "how_to_play": (
        "To play LangGang Charades:\n"
        "1. Send a 2-letter language code to start a game:\n"
        "   - ES (Spanish)\n"
        "   - KO (Korean)\n"
        "   - FR (French)\n"
        "   - DE (German)\n"
        "   - EN (English)\n"
        "   - IT (Italian)\n"
        "   - JA (Japanese)\n"
        "   - PT (Portuguese)\n"
        "   - RU (Russian)\n"
        "   - BN (Bengali)\n"
        "   - FA (Persian)\n"
        "   - ZH (Chinese)\n"
        "2. I'll give you a word to describe\n"
        "3. Send your description and I'll evaluate it!\n\n"
        "Or reply OPTOUT to stop playing."
    ),
    "not_opted_in": (
        "You're not currently opted in to LangGang Charades. "
        "Text LANGGANG to start playing!"
    ),
    "new_game": (
        "Let's play in {language}! 🎮\n"
        "Your word is: {word}\n"
        "Please describe this word in {language}. I'll evaluate your description!"
    ),
    "no_active_game": (
        "You don't have an active game! Send a language code "
        "(e.g. EN for English or KO for Korean) to start playing."
    ),
    "game_complete": (
        "Score: {score}/100 🎯\n"
        "Feedback: {feedback}\n\n"
        "Send a language code to play again!"
    ),
    "invalid_language": (
        "Sorry, that language code isn't supported yet. "
        "Try: EN (English) or KO (Korean)"
    ),
}
