"""Tests for game utility functions."""

from charades.game.utils import create_twiml_response
from charades.game.utils import MESSAGES


def test_create_twiml_response():
    """Test creating TwiML responses."""
    # Test with simple message
    message = "Hello, world!"
    response = create_twiml_response(message)
    assert response == (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response><Message>Hello, world!</Message></Response>"
    )

    # Test with message containing special characters
    message = "Hello & goodbye!"
    response = create_twiml_response(message)
    assert response == (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response><Message>Hello &amp; goodbye!</Message></Response>"
    )


def test_message_templates():
    """Test that all message templates are valid and can be used with TwiML."""
    for _, message_text in MESSAGES.items():
        response = create_twiml_response(message_text)
        assert response.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert response.endswith("</Response>")
        assert "<Message>" in response
        assert "</Message>" in response


def test_message_templates_content():
    """Test that message templates contain expected content."""
    # Test opt-in success message
    assert "language code" in MESSAGES["opt_in_success"]
    assert "OPTOUT" in MESSAGES["opt_in_success"]

    # Test opt-out success message
    assert "LangGang" in MESSAGES["opt_out_success"]
    assert "opt back in" in MESSAGES["opt_out_success"]

    # Test already opted in message
    assert "language code" in MESSAGES["already_opted_in"]
    assert "OPTOUT" in MESSAGES["already_opted_in"]

    # Test error message
    assert "sorry" in MESSAGES["error_generic"].lower()
