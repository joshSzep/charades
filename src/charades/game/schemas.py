from typing import Literal

from ninja import Schema


class TwilioIncomingMessageSchema(Schema):
    """Schema for incoming SMS webhook from Twilio."""

    # Core message fields
    MessageSid: str
    AccountSid: str
    From: str  # Phone number that sent the message
    To: str  # Your Twilio phone number
    Body: str  # Message content
    NumMedia: int = 0  # Number of media attachments

    # Message details
    MessagingServiceSid: str | None = None
    NumSegments: int = 1  # Number of segments for long messages
    SmsStatus: Literal["received"] = "received"
    SmsSid: str

    # Optional media fields (only present when NumMedia > 0)
    MediaContentType0: str | None = None
    MediaUrl0: str | None = None

    # Geographic data (if available)
    FromCity: str | None = None
    FromState: str | None = None
    FromZip: str | None = None
    FromCountry: str | None = None
    ToCity: str | None = None
    ToState: str | None = None
    ToZip: str | None = None
    ToCountry: str | None = None


class TwilioMessageStatusSchema(Schema):
    """Schema for message status callback webhook from Twilio."""

    MessageSid: str
    MessageStatus: Literal[
        "accepted",
        "queued",
        "sending",
        "sent",
        "failed",
        "delivered",
        "undelivered",
        "receiving",
        "received",
    ]
    AccountSid: str
    From: str
    To: str

    # Error fields (present when message fails)
    ErrorCode: int | None = None
    ErrorMessage: str | None = None

    # Optional fields
    ApiVersion: str | None = None
    ChannelToAddress: str | None = None
    ChannelPrefix: str | None = None
    SmsSid: str | None = None
    SmsStatus: str | None = None


class TwilioErrorResponse(Schema):
    """Schema for error responses we send back to Twilio."""

    message: str
    code: int = 400


class TwilioSuccessResponse(Schema):
    """Schema for TwiML responses we send back to Twilio."""

    message: str | None = None
    twiml: str
