import logging
from urllib.parse import parse_qs
from django.conf import settings
from django.http import HttpRequest
from ninja import NinjaAPI

from charades.game.logic import (
    handle_player_command,
    handle_word_description,
    get_random_word,
)
from charades.game.renderers import TwiMLRenderer
from charades.game.schemas import TwilioIncomingMessageSchema
from charades.game.schemas import TwilioMessageStatusSchema
from charades.game.schemas import PlayerCommandSchema
from charades.game.schemas import TwilioIncomingVoiceSchema
from charades.game.utils import create_twiml_response
from charades.game.utils import create_voice_response
from charades.game.utils import VOICE_MESSAGES
from charades.game.models import Player

logger = logging.getLogger(__name__)

api = NinjaAPI(
    renderer=TwiMLRenderer(),
)


@api.post(
    "/webhooks/twilio/incoming",
    tags=["webhooks"],
)
def handle_incoming_message(
    request: HttpRequest,
) -> dict:
    """Handle incoming SMS messages from Twilio.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Processes opt-in/opt-out commands
    3. Handles game interactions (language selection and word descriptions)
    4. Returns TwiML response to Twilio
    """
    # Parse the URL-encoded payload from request.body
    body_str = request.body.decode("utf-8")
    params = parse_qs(body_str)

    # Convert the parsed params into our schema format
    # Note: parse_qs returns lists, so we take first item for each key
    schema_data = {
        "MessageSid": params["MessageSid"][0],
        "AccountSid": params["AccountSid"][0],
        "From": params["From"][0],
        "To": params["To"][0],
        "Body": params.get("Body", [None])[0],
        "NumMedia": params.get("NumMedia", ["0"])[0],
        "NumSegments": params.get("NumSegments", ["1"])[0],
        "SmsMessageSid": params["SmsMessageSid"][0],
        "SmsSid": params["SmsSid"][0],
        "SmsStatus": params.get("SmsStatus", [None])[0],
        "MessagingServiceSid": params.get("MessagingServiceSid", [None])[0],
        # Media fields
        "MediaContentType0": params.get("MediaContentType0", [None])[0],
        "MediaUrl0": params.get("MediaUrl0", [None])[0],
        # Geographic data
        "FromCity": params.get("FromCity", [None])[0],
        "FromState": params.get("FromState", [None])[0],
        "FromZip": params.get("FromZip", [None])[0],
        "FromCountry": params.get("FromCountry", [None])[0],
        "ToCity": params.get("ToCity", [None])[0],
        "ToState": params.get("ToState", [None])[0],
        "ToZip": params.get("ToZip", [None])[0],
        "ToCountry": params.get("ToCountry", [None])[0],
        # Additional fields
        "ApiVersion": params.get("ApiVersion", [None])[0],
    }

    # Create and validate the schema
    try:
        message = TwilioIncomingMessageSchema(**schema_data)
    except ValueError as e:
        return {
            "twiml": create_twiml_response(f"Invalid webhook payload: {str(e)}"),
            "code": 400,
        }

    # Handle messages without a body
    if not message.Body:
        return {
            "twiml": create_twiml_response("Message body is required"),
            "code": 400,
        }

    # Extract phone number and command
    phone_number = message.From
    command = message.Body.strip().lower()

    # Route command to appropriate handler
    return handle_player_command(phone_number, command)


@api.post(
    "/webhooks/twilio/status",
    tags=["webhooks"],
)
def handle_message_status(
    request: HttpRequest,
) -> dict:
    """Handle message status callbacks from Twilio.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Records message delivery status
    3. Handles failed message retries if needed
    """
    # Parse the URL-encoded payload from request.body
    body_str = request.body.decode("utf-8")
    params = parse_qs(body_str)

    # Convert the parsed params into our schema format
    # Note: parse_qs returns lists, so we take first item for each key
    schema_data = {
        "MessageSid": params["MessageSid"][0],
        "MessageStatus": params["MessageStatus"][0],
        "AccountSid": params["AccountSid"][0],
        "From": params["From"][0],
        "To": params["To"][0],
        # Error fields
        "ErrorCode": int(params["ErrorCode"][0]) if "ErrorCode" in params else None,
        "ErrorMessage": params.get("ErrorMessage", [None])[0],
        # Optional fields
        "ApiVersion": params.get("ApiVersion", [None])[0],
        "ChannelToAddress": params.get("ChannelToAddress", [None])[0],
        "ChannelPrefix": params.get("ChannelPrefix", [None])[0],
        "SmsSid": params.get("SmsSid", [None])[0],
        "SmsStatus": params.get("SmsStatus", [None])[0],
    }

    # Create and validate the schema
    try:
        _ = TwilioMessageStatusSchema(**schema_data)
    except ValueError as e:
        return {
            "twiml": create_twiml_response(f"Invalid webhook payload: {str(e)}"),
            "code": 400,
        }

    # For now, just acknowledge receipt
    return {
        "twiml": create_twiml_response("Status received"),
        "code": 200,
    }


@api.post(
    "/webhooks/twilio/voice",
    tags=["webhooks"],
)
def handle_voice_call(
    request: HttpRequest,
) -> dict:
    """Handle incoming voice calls from Twilio.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Greets the caller
    3. Prompts for language selection
    4. Gathers speech input
    """
    # Parse the URL-encoded payload from request.body
    body_str = request.body.decode("utf-8")
    params = parse_qs(body_str)

    # Convert the parsed params into our schema format
    schema_data = {
        "CallSid": params["CallSid"][0],
        "AccountSid": params["AccountSid"][0],
        "From": params["From"][0],
        "To": params["To"][0],
        "CallStatus": params["CallStatus"][0],
        # Optional fields
        "FromCity": params.get("FromCity", [None])[0],
        "FromState": params.get("FromState", [None])[0],
        "FromZip": params.get("FromZip", [None])[0],
        "FromCountry": params.get("FromCountry", [None])[0],
        "ToCity": params.get("ToCity", [None])[0],
        "ToState": params.get("ToState", [None])[0],
        "ToZip": params.get("ToZip", [None])[0],
        "ToCountry": params.get("ToCountry", [None])[0],
        "ApiVersion": params.get("ApiVersion", [None])[0],
        "Direction": params.get("Direction", [None])[0],
        "ForwardedFrom": params.get("ForwardedFrom", [None])[0],
    }

    # Create and validate the schema
    try:
        _ = TwilioIncomingVoiceSchema(**schema_data)
    except ValueError as e:
        return {
            "twiml": create_voice_response(f"Invalid webhook payload: {str(e)}"),
            "code": 400,
        }

    return {
        "twiml": create_voice_response(
            VOICE_MESSAGES["welcome"],
            gather_speech=True,
        ),
        "code": 200,
    }


@api.post(
    "/webhooks/twilio/voice/gather",
    tags=["webhooks"],
)
def handle_voice_gather(
    request: HttpRequest,
) -> dict:
    """Handle gathered speech input from voice calls.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Processes the speech recognition result
    3. Routes to appropriate game logic
    4. Returns TwiML response with next prompt
    """
    # Parse the URL-encoded payload
    body_str = request.body.decode("utf-8")
    params = parse_qs(body_str)

    # Get the speech result
    speech_result = params.get("SpeechResult", [None])[0]
    if not speech_result:
        return {
            "twiml": create_voice_response(
                VOICE_MESSAGES["no_input"],
                gather_speech=True,
            ),
            "code": 200,
        }

    # Get caller's phone number
    phone_number = params.get("From", [None])[0]
    if not phone_number:
        return {
            "twiml": create_voice_response(
                VOICE_MESSAGES["error_generic"],
                gather_speech=False,
            ),
            "code": 400,
        }

    # Convert speech to language code
    speech_lower = speech_result.lower()
    speech_lower = speech_lower.strip()
    speech_lower = speech_lower.strip(".")
    language_map = {
        "english": "EN",
        "korean": "KO",
        "spanish": "ES",
        "french": "FR",
        "german": "DE",
        "italian": "IT",
        "japanese": "JA",
        "portuguese": "PT",
        "russian": "RU",
        "bengali": "BN",
        "persian": "FA",
        "chinese": "ZH",
    }
    logger.critical(f"speech_lower: {speech_lower}")

    language_code = language_map.get(speech_lower)

    # Get or create player
    try:
        player, _ = Player.get_or_create_player(phone_number)
    except Exception as _:
        return {
            "twiml": create_voice_response(
                VOICE_MESSAGES["error_generic"],
                gather_speech=False,
            ),
            "code": 400,
        }

    # Check for active game
    active_session = player.gamesession_set.filter(status="active").first()

    if active_session:
        # Handle word description
        result = handle_word_description(player, speech_result)
        # Convert SMS response to voice response
        message = result["twiml"].replace("Score:", "").replace("\n", ". ")
        return {
            "twiml": create_voice_response(message, gather_speech=True),
            "code": result["code"],
        }
    elif language_code:
        # Get or create player
        try:
            player, _ = Player.get_or_create_player(phone_number)
        except Exception as _:
            return {
                "twiml": create_voice_response(
                    VOICE_MESSAGES["error_generic"],
                    gather_speech=False,
                ),
                "code": 400,
            }

        # End any existing active sessions
        player.end_active_sessions()

        # Get a random word in the selected language
        word = get_random_word(language_code)

        # Create new game session
        _ = player.gamesession_set.create(
            word=word,
            language=language_code.lower(),
        )

        # Return voice response with the word
        return {
            "twiml": create_voice_response(
                VOICE_MESSAGES["new_game"].format(
                    language=settings.SUPPORTED_LANGUAGES[language_code.upper()],
                    word=word,
                ),
                gather_speech=True,
            ),
            "code": 200,
        }
    else:
        # Neither active game nor valid language - provide guidance
        return {
            "twiml": create_voice_response(
                VOICE_MESSAGES["how_to_play"],
                gather_speech=True,
            ),
            "code": 200,
        }


@api.post(
    "/test/player-command",
    tags=["testing"],
)
def test_player_command(
    request: HttpRequest,
    payload: PlayerCommandSchema,
) -> dict:
    """Test endpoint to directly invoke handle_player_command.

    This endpoint allows testing the game logic without Twilio webhooks.
    It expects a phone number and command, and returns the same response
    format as the Twilio webhooks.
    """
    return handle_player_command(
        phone_number=payload.phone_number,
        command=payload.command,
    )
