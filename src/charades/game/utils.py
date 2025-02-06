"""Utility functions for the game module."""

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.voice_response import Gather


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


def create_voice_response(
    message: str,
    gather_speech: bool = False,
) -> str:
    """Create a TwiML voice response.

    Args:
        message: The message to speak to the user
        gather_speech: Whether to gather speech input after speaking

    Returns:
        str: The TwiML response as a string
    """
    response = VoiceResponse()

    # Add brief pause for better speech flow
    message = message.replace("\n", ". ")

    if gather_speech:
        gather = Gather(
            input="speech",
            timeout=5,
            action="/api/webhooks/twilio/voice/gather",
            method="POST",
        )
        gather.say(message)
        response.append(gather)

        # If no input received, redirect back to voice endpoint
        response.redirect("/api/webhooks/twilio/voice")
    else:
        response.say(message)

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

VOICE_MESSAGES = {
    "welcome": (
        "Welcome to Lang Gang Charades! "
        "I'll give you a word, and you describe it in your chosen language. "
        "To begin, say a language code like English or Korean."
    ),
    "not_understood": (
        "I didn't catch that. Please say a language name like English or Korean."
    ),
    "new_game": (
        "Great! Let's play in {language}. "
        "Your word is {word}. "
        "Please describe this word in {language}. "
        "Take your time, I'll listen to your description."
    ),
    "no_input": ("I didn't hear anything. Please try speaking again."),
    "game_complete": (
        "Thanks for your description! "
        "Your score is {score} out of 100. "
        "{feedback} "
        "Would you like to play again? Just say a language like English or Korean."
    ),
    "language_not_supported": (
        "Sorry, I don't support that language yet. "
        "Please choose from: English, Korean, Spanish, French, German, "
        "Italian, Japanese, Portuguese, Russian, Bengali, Persian, or Chinese."
    ),
    "how_to_play": (
        "Here's how to play Lang Gang Charades: "
        "First, choose your language by saying English, Korean, Spanish, or others. "
        "Then, I'll give you a word to describe in that language. "
        "Finally, speak your description and I'll evaluate it. "
        "Ready? Say a language to begin!"
    ),
}
