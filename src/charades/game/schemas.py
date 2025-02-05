from typing import Literal

from ninja import Schema


class TwilioIncomingMessageSchema(Schema):
    """Schema for incoming SMS webhook from Twilio."""

    # Core message fields
    MessageSid: str
    AccountSid: str
    From: str
    To: str
    Body: str | None = None  # Can be empty for media-only messages

    # Message details
    NumMedia: str = "0"  # Twilio sends this as a string
    NumSegments: str = "1"  # Twilio sends this as a string
    SmsMessageSid: str
    SmsSid: str
    SmsStatus: str | None = None

    # Service identifiers
    MessagingServiceSid: str | None = None

    # Media fields (present when NumMedia > 0)
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

    # Additional optional fields
    ApiVersion: str | None = None
    ProfileName: str | None = None  # For channels that support sender profiles


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


class PlayerCommandSchema(Schema):
    """Schema for testing player commands directly without Twilio."""

    phone_number: str
    command: str


class TwilioIncomingVoiceSchema(Schema):
    """Schema for incoming voice webhook from Twilio."""

    # Core call fields
    CallSid: str
    AccountSid: str
    From: str
    To: str

    # Speech recognition results
    SpeechResult: str | None = None
    Confidence: float | None = None

    # Call status
    CallStatus: Literal[
        "queued",
        "ringing",
        "in-progress",
        "completed",
        "busy",
        "failed",
        "no-answer",
        "canceled",
    ]

    # Geographic data (if available)
    FromCity: str | None = None
    FromState: str | None = None
    FromZip: str | None = None
    FromCountry: str | None = None
    ToCity: str | None = None
    ToState: str | None = None
    ToZip: str | None = None
    ToCountry: str | None = None

    # Additional fields
    ApiVersion: str | None = None
    Direction: str | None = None
    ForwardedFrom: str | None = None
