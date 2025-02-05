"""Custom response renderers for the game module."""

from typing import Any

from django.http import HttpResponse
from ninja.renderers import BaseRenderer


class TwiMLRenderer(BaseRenderer):
    """Custom renderer for TwiML responses.

    Expects a dictionary with:
        - twiml: str - The TwiML response as a string
        - code: int - HTTP status code (default: 200)
    """

    media_type = "application/xml"

    def render(
        self,
        request: Any,
        data: dict,
        *,
        response_status: int | None,
    ) -> HttpResponse:
        """Render the response.

        Args:
            request: The request object
            data: Dictionary containing 'twiml' and optional 'code'
            response_status: Optional status code (ignored in favor of data['code'])

        Returns:
            HttpResponse with TwiML content and proper headers
        """
        # Get status code from data or default to 200
        status_code = data.get("code", 200)

        # Create response with TwiML content
        response = HttpResponse(
            data["twiml"],
            content_type=self.media_type,
            status=status_code,
        )

        return response
