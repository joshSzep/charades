from urllib.parse import parse_qs
from django.http import HttpRequest
from ninja import NinjaAPI

from charades.game.logic import handle_player_command
from charades.game.renderers import TwiMLRenderer
from charades.game.schemas import TwilioIncomingMessageSchema
from charades.game.schemas import TwilioMessageStatusSchema
from charades.game.schemas import PlayerCommandSchema
from charades.game.schemas import TwilioIncomingVoiceSchema
from charades.game.utils import create_twiml_response
from charades.game.utils import create_voice_response
from charades.game.utils import VOICE_MESSAGES

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
    payload: TwilioMessageStatusSchema,
) -> dict:
    """Handle message status callbacks from Twilio.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Records message delivery status
    3. Handles failed message retries if needed
    """
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
        "SpeechResult": params.get("SpeechResult", [None])[0],
        "Confidence": float(params["Confidence"][0])
        if "Confidence" in params
        else None,
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
        call = TwilioIncomingVoiceSchema(**schema_data)
    except ValueError as e:
        return {
            "twiml": create_voice_response(f"Invalid webhook payload: {str(e)}"),
            "code": 400,
        }

    if not call.SpeechResult:
        return {
            "twiml": create_voice_response(
                VOICE_MESSAGES["no_input"],
                gather_speech=True,
            ),
            "code": 200,
        }

    # Process the command through existing game logic
    result = handle_player_command(call.From, call.SpeechResult.lower())

    # Convert message response to voice response
    message = result["twiml"]
    if "message" in message:
        message = message.split(">")[1].split("<")[0]  # Extract message from TwiML

    return {
        "twiml": create_voice_response(
            message,
            gather_speech=True,
        ),
        "code": result["code"],
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
