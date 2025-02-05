"""Tests for game logic functions."""

from unittest.mock import patch

import pytest

from charades.game.logic import handle_opt_in
from charades.game.logic import handle_opt_out
from charades.game.models import GameSession
from charades.game.models import Player
from charades.game.models import Word
from charades.game.schemas import TwilioErrorResponse, TwilioSuccessResponse
from charades.game.utils import MESSAGES


@pytest.fixture
def phone_number(request):
    """Fixture for test phone number.

    Generates a unique phone number for each test to avoid conflicts.
    """
    test_name = request.node.name
    # Use the test name to generate a unique number
    unique_num = abs(hash(test_name)) % 10000
    return f"+1206555{unique_num:04d}"


@pytest.fixture
def player(phone_number):
    """Fixture for test player."""
    return Player.objects.create(phone_number=phone_number)


@pytest.fixture
def active_player(player):
    """Fixture for active test player."""
    player.opt_in()
    return player


@pytest.fixture
def word():
    """Fixture for test word."""
    return Word.objects.get_or_create(text="test", language="en")[0]


@pytest.mark.django_db
class TestOptInLogic:
    """Tests for opt-in logic."""

    def test_new_player_opt_in(self, phone_number):
        """Test opting in a new player."""
        response = handle_opt_in(phone_number)

        # Check response
        assert isinstance(response, TwilioSuccessResponse)
        assert response.twiml
        assert MESSAGES["opt_in_success"] in response.twiml

        # Check database
        player = Player.objects.get(phone_number=phone_number)
        assert player.is_active
        assert player.opted_in_at
        assert not player.opted_out_at

    def test_existing_inactive_player_opt_in(self, player):
        """Test opting in an existing but inactive player."""
        assert not player.is_active
        response = handle_opt_in(player.phone_number)

        # Check response
        assert isinstance(response, TwilioSuccessResponse)
        assert response.twiml
        assert MESSAGES["opt_in_success"] in response.twiml

        # Check database
        player.refresh_from_db()
        assert player.is_active
        assert player.opted_in_at
        assert not player.opted_out_at

    def test_already_active_player_opt_in(self, active_player):
        """Test attempting to opt in an already active player."""
        response = handle_opt_in(active_player.phone_number)

        # Check response
        assert isinstance(response, TwilioSuccessResponse)
        assert response.twiml
        assert MESSAGES["already_opted_in"] in response.twiml

        # Check database - should be unchanged
        active_player.refresh_from_db()
        assert active_player.is_active
        assert active_player.opted_in_at
        assert not active_player.opted_out_at

    def test_opt_in_database_error(self, phone_number):
        """Test handling of database errors during opt-in."""
        with patch(
            "charades.game.models.Player.get_or_create_player"
        ) as mock_get_or_create:
            mock_get_or_create.side_effect = Exception("Database error")
            response = handle_opt_in(phone_number)

            assert isinstance(response, TwilioErrorResponse)
            assert response.message.startswith("Failed to opt in")
            assert response.code == 400


@pytest.mark.django_db
class TestOptOutLogic:
    """Tests for opt-out logic."""

    def test_active_player_opt_out(self, active_player):
        """Test opting out an active player."""
        response = handle_opt_out(active_player.phone_number)

        # Check response
        assert isinstance(response, TwilioSuccessResponse)
        assert response.twiml
        assert MESSAGES["opt_out_success"] in response.twiml

        # Check database
        active_player.refresh_from_db()
        assert not active_player.is_active
        assert active_player.opted_out_at

    def test_inactive_player_opt_out(self, player):
        """Test opting out an already inactive player."""
        response = handle_opt_out(player.phone_number)

        # Check response
        assert isinstance(response, TwilioSuccessResponse)
        assert response.twiml
        assert MESSAGES["opt_out_success"] in response.twiml

        # Check database
        player.refresh_from_db()
        assert not player.is_active
        assert player.opted_out_at

    def test_opt_out_ends_active_sessions(self, active_player, word):
        """Test that opting out ends all active game sessions."""
        # Create some game sessions
        session = GameSession.objects.create(
            player=active_player,
            word=word,
            status="active",
        )

        response = handle_opt_out(active_player.phone_number)

        # Check response
        assert isinstance(response, TwilioSuccessResponse)
        assert response.twiml
        assert MESSAGES["opt_out_success"] in response.twiml

        # Check database
        active_player.refresh_from_db()
        assert not active_player.is_active
        assert active_player.opted_out_at

        # Check that sessions were ended
        session.refresh_from_db()
        assert session.status == "timeout"
        assert session.completed_at

    def test_opt_out_database_error(self, phone_number):
        """Test handling of database errors during opt-out."""
        with patch(
            "charades.game.models.Player.get_or_create_player"
        ) as mock_get_or_create:
            mock_get_or_create.side_effect = Exception("Database error")
            response = handle_opt_out(phone_number)

        assert isinstance(response, TwilioErrorResponse)
        assert response.message.startswith("Failed to opt out")
        assert response.code == 400
