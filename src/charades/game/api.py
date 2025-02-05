from urllib.parse import parse_qs

from ninja import NinjaAPI

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
        _ = TwilioIncomingMessageSchema(**schema_data)
    except ValueError as e:
        return TwilioErrorResponse(
            message=f"Invalid webhook payload: {str(e)}",
            code=400,
        )

    # TODO: Implement opt-in/opt-out handling
    # - When the user initiates interaction with the game, they do so by
    #   sending a message to the game's SMS number with the word "LangGang" (but
    #   treated case-insensitively) as the body.
    #   - Example: "LangGang" or "langGang"
    #   - We must create a record of their opt-in in the database, or update their
    #     opt-in status if they already have a record.
    #   - We must send a confirmation message to the user confirming their opt-in and
    #     requesting to opt out at any time by replying STOP. We also instruct the user
    #     to send a message with the language code they want to use (e.g. "en" or "ko")
    #     to start the game.
    # - When the user sends a message to the game's SMS number with the word
    #   "STOP" (but treated case-insensitively) as the body:
    #   - We must end any ongoing game sessions in the database.
    #   - We must update their opt-out status in the database.
    #   - We must send a confirmation message to the user confirming their opt-out.

    # TODO: Implement game logic
    # - When the user sends a message to the game's SMS number with the language
    #   code they want to use (e.g. "en" or "ko") as the body:
    #   - We must start a new game session for the user in the database.
    #   - We must send a message to the user with a noun word to describe and instruct
    #     them on how to play the game.
    # - When the user sends a message other than "STOP" to the game's SMS number while
    #   in a game session:
    #   - We must read their message as a description of the word.
    #   - We must evaluate the description using the OpenAI GPT model.
    #   - We must send a message to the user with the AI's evaluation of their
    #     description.
    #   - We must update the game session in the database with the user's description,
    #     the AI's response, and the current state of the game.

    return TwilioSuccessResponse(
        message="Message received",
        twiml=(
            "<?xml version='1.0' encoding='UTF-8'?><Response><Message>Thanks for your "
            "message! Feature coming soon.</Message></Response>"
        ),
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
