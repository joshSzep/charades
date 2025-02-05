from urllib.parse import parse_qs

from ninja import NinjaAPI

from charades.game.logic import handle_opt_in
from charades.game.logic import handle_opt_out
from charades.game.schemas import TwilioErrorResponse
from charades.game.schemas import TwilioIncomingMessageSchema
from charades.game.schemas import TwilioMessageStatusSchema
from charades.game.schemas import TwilioSuccessResponse

api = NinjaAPI()


@api.get("/hello")
def hello(request):
    return {"message": "Hello, welcome to AI Language Charades!"}


@api.post(
    "/webhooks/twilio/incoming",
    response={
        200: TwilioSuccessResponse,
        400: TwilioErrorResponse,
    },
    tags=["webhooks"],
)
def handle_incoming_message(
    request,
) -> TwilioSuccessResponse | TwilioErrorResponse:
    """Handle incoming SMS messages from Twilio.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Processes opt-in/opt-out commands
    3. Handles game interactions (word descriptions)
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
        return TwilioErrorResponse(
            message=f"Invalid webhook payload: {str(e)}",
            code=400,
        )

    # Handle messages without a body
    if not message.Body:
        return TwilioErrorResponse(
            message="Message body is required",
            code=400,
        )

    # Case-insensitive command matching
    command = message.Body.strip().lower()

    # Handle opt-in/opt-out
    if command == "langgang":
        return handle_opt_in(message.From)
    elif command == "optout":
        return handle_opt_out(message.From)

    # TODO: Implement game logic for language selection and word description
    return TwilioErrorResponse(
        message="Game logic not yet implemented",
        code=400,
    )


@api.post(
    "/webhooks/twilio/status",
    response={
        200: dict,
        400: TwilioErrorResponse,
    },
    tags=["webhooks"],
)
def handle_message_status(
    request,
    payload: TwilioMessageStatusSchema,
) -> dict | TwilioErrorResponse:
    """Handle message status callbacks from Twilio.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Records message delivery status
    3. Handles failed message retries if needed
    """
    # TODO: Implement webhook signature validation
    # TODO: Implement status logging
    # TODO: Implement retry logic for failed messages
    return {"status": "received"}
