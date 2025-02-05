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
    payload: TwilioIncomingMessageSchema,
) -> TwilioSuccessResponse | TwilioErrorResponse:
    """Handle incoming SMS messages from Twilio.

    This endpoint:
    1. Validates the incoming webhook payload
    2. Processes opt-in/opt-out commands
    3. Handles game interactions (word descriptions)
    4. Returns TwiML response to Twilio
    """
    # TODO: Implement webhook signature validation
    # TODO: Implement opt-in/opt-out handling
    # TODO: Implement game logic
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
