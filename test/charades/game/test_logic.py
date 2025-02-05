"""Tests for game logic functions."""

from unittest.mock import patch

import pytest
from django.conf import settings

from charades.game.logic import handle_game_message, handle_player_command
from charades.game.logic import handle_language_selection
from charades.game.logic import handle_opt_in
from charades.game.logic import handle_opt_out
from charades.game.logic import handle_word_description
from charades.game.models import GameSession
from charades.game.models import Player
from charades.game.utils import MESSAGES
from charades.game.utils import create_twiml_response


@pytest.fixture
def phone_number(request):
    """Fixture for test phone number.

    Generates a unique phone number for each test to avoid conflicts.
    """
    test_name = request.node.name
    # Use the test name and current time to generate a unique number
    unique_num = abs(hash(f"{test_name}{request.node.nodeid}")) % 10000000
    return f"+1206{unique_num:07d}"


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
    return "test"


@pytest.fixture
def active_game_session(active_player, word):
    """Fixture for active game session."""
    return GameSession.objects.create(
        player=active_player,
        word=word,
        language="en",
        status="active",
    )


@pytest.mark.django_db
class TestOptInLogic:
    """Tests for opt-in logic."""

    def test_new_player_opt_in(self, phone_number):
        """Test opting in a new player."""
        response = handle_opt_in(phone_number)

        # Check response
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["opt_in_success"])

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
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["opt_in_success"])

        # Check database
        player.refresh_from_db()
        assert player.is_active
        assert player.opted_in_at
        assert not player.opted_out_at

    def test_already_active_player_opt_in(self, active_player):
        """Test attempting to opt in an already active player."""
        response = handle_opt_in(active_player.phone_number)

        # Check response
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["already_opted_in"])

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

            assert response["code"] == 400
            assert "Failed to opt in" in response["twiml"]


@pytest.mark.django_db
class TestOptOutLogic:
    """Tests for opt-out logic."""

    def test_active_player_opt_out(self, active_player):
        """Test opting out an active player."""
        response = handle_opt_out(active_player.phone_number)

        # Check response
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["opt_out_success"])

        # Check database
        active_player.refresh_from_db()
        assert not active_player.is_active
        assert active_player.opted_out_at

    def test_inactive_player_opt_out(self, player):
        """Test opting out an already inactive player."""
        response = handle_opt_out(player.phone_number)

        # Check response
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["opt_out_success"])

        # Check database
        player.refresh_from_db()
        assert not player.is_active
        assert player.opted_out_at

    def test_opt_out_ends_active_sessions(self, active_player, active_game_session):
        """Test that opting out ends all active game sessions."""
        response = handle_opt_out(active_player.phone_number)

        # Check response
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["opt_out_success"])

        # Check database
        active_player.refresh_from_db()
        assert not active_player.is_active
        assert active_player.opted_out_at

        # Check that sessions were ended
        active_game_session.refresh_from_db()
        assert active_game_session.status == "timeout"
        assert active_game_session.completed_at

    def test_opt_out_database_error(self, phone_number):
        """Test handling of database errors during opt-out."""
        with patch(
            "charades.game.models.Player.get_or_create_player"
        ) as mock_get_or_create:
            mock_get_or_create.side_effect = Exception("Database error")
            response = handle_opt_out(phone_number)

            assert response["code"] == 400
            assert "Failed to opt out" in response["twiml"]


@pytest.mark.django_db
class TestGameMessageLogic:
    """Tests for game message handling logic."""

    def test_handle_active_game_message(self, active_player, active_game_session):
        """Test handling a message when player has an active game."""
        with patch("charades.game.logic.handle_word_description") as mock_handle_desc:
            mock_handle_desc.return_value = {"code": 200, "twiml": "test response"}
            response = handle_game_message(active_player, "test description")

            # Should delegate to handle_word_description
            mock_handle_desc.assert_called_once_with(active_player, "test description")
            assert response == {"code": 200, "twiml": "test response"}

    def test_handle_language_selection(self, active_player):
        """Test handling a valid language code."""
        with patch("charades.game.logic.handle_language_selection") as mock_handle_lang:
            mock_handle_lang.return_value = {"code": 200, "twiml": "test response"}
            response = handle_game_message(active_player, "EN")

            # Should delegate to handle_language_selection
            mock_handle_lang.assert_called_once_with(active_player, "EN")
            assert response == {"code": 200, "twiml": "test response"}

    def test_handle_invalid_message(self, active_player):
        """Test handling an invalid message (no active game, not a language code)."""
        response = handle_game_message(active_player, "invalid")

        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["how_to_play"])


@pytest.mark.django_db
class TestLanguageSelectionLogic:
    """Tests for language selection logic."""

    @patch("charades.game.logic.get_random_word")
    def test_valid_language_selection(self, mock_get_word, active_player):
        """Test selecting a valid language."""
        mock_get_word.return_value = "test"
        response = handle_language_selection(active_player, "EN")

        assert response["code"] == 200
        assert (
            MESSAGES["new_game"].format(
                language=settings.SUPPORTED_LANGUAGES["EN"],
                word="test",
            )
            in response["twiml"]
        )

        # Check that a game session was created
        session = active_player.gamesession_set.first()
        assert session.word == "test"
        assert session.language == "en"
        assert session.status == "active"

    def test_language_selection_error(self, active_player):
        """Test error handling in language selection."""
        with patch("charades.game.logic.get_random_word") as mock_get_word:
            mock_get_word.side_effect = Exception("API error")
            response = handle_language_selection(active_player, "EN")

            assert response["code"] == 400
            assert "Failed to start game" in response["twiml"]


@pytest.mark.django_db
class TestWordDescriptionLogic:
    """Tests for word description handling logic."""

    @patch("charades.game.logic.evaluate_description")
    def test_valid_word_description(
        self, mock_evaluate, active_player, active_game_session
    ):
        """Test handling a valid word description."""
        mock_evaluate.return_value = (85, "Good job!")
        response = handle_word_description(active_player, "test description")

        assert response["code"] == 200
        assert (
            MESSAGES["game_complete"].format(
                score=85,
                feedback="Good job!",
            )
            in response["twiml"]
        )

        # Check that the game session was completed
        active_game_session.refresh_from_db()
        assert active_game_session.status == "completed"
        assert active_game_session.score == 85
        assert active_game_session.completed_at
        assert active_game_session.user_description == "test description"
        assert active_game_session.feedback == "Good job!"

    def test_no_active_game(self, active_player):
        """Test handling a description when there's no active game."""
        response = handle_word_description(active_player, "test description")

        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["no_active_game"])

    def test_evaluation_error(self, active_player, active_game_session):
        """Test error handling during description evaluation."""
        with patch("charades.game.logic.evaluate_description") as mock_evaluate:
            mock_evaluate.side_effect = Exception("API error")
            response = handle_word_description(active_player, "test description")

            assert response["code"] == 400
            assert "Failed to evaluate description" in response["twiml"]


@pytest.mark.django_db
class TestPlayerCommandLogic:
    """Integration tests for player command handling logic."""

    def test_opt_in_command(self, phone_number):
        """Test handling of opt-in command."""
        response = handle_player_command(phone_number, "langgang")

        # Check response
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["opt_in_success"])

        # Verify player was created and opted in
        player = Player.objects.get(phone_number=phone_number)
        assert player.is_active
        assert player.opted_in_at
        assert not player.opted_out_at

    def test_opt_out_command(self, active_player, active_game_session):
        """Test handling of opt-out command."""
        response = handle_player_command(active_player.phone_number, "optout")

        # Check response
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["opt_out_success"])

        # Verify player was opted out
        active_player.refresh_from_db()
        assert not active_player.is_active
        assert active_player.opted_out_at

        # Verify game session was ended
        active_game_session.refresh_from_db()
        assert active_game_session.status == "timeout"
        assert active_game_session.completed_at

    def test_language_selection_command(self, active_player):
        """Test handling of language selection command."""
        with patch("charades.game.logic.get_random_word") as mock_get_word:
            mock_get_word.return_value = "test"
            response = handle_player_command(active_player.phone_number, "en")

            # Check response
            assert response["code"] == 200
            assert (
                MESSAGES["new_game"].format(
                    language=settings.SUPPORTED_LANGUAGES["EN"],
                    word="test",
                )
                in response["twiml"]
            )

            # Verify game session was created
            session = active_player.gamesession_set.first()
            assert session.word == "test"
            assert session.language == "en"
            assert session.status == "active"

    def test_word_description_command(self, active_player, active_game_session):
        """Test handling of word description command."""
        with patch("charades.game.logic.evaluate_description") as mock_evaluate:
            mock_evaluate.return_value = (85, "Good job!")
            response = handle_player_command(
                active_player.phone_number, "this is a test description"
            )

            # Check response
            assert response["code"] == 200
            assert (
                MESSAGES["game_complete"].format(
                    score=85,
                    feedback="Good job!",
                )
                in response["twiml"]
            )

            # Verify game session was completed
            active_game_session.refresh_from_db()
            assert active_game_session.status == "completed"
            assert active_game_session.score == 85
            assert active_game_session.completed_at
            assert active_game_session.user_description == "this is a test description"
            assert active_game_session.feedback == "Good job!"

    def test_command_from_inactive_player(self, player):
        """Test handling command from an inactive player."""
        response = handle_player_command(player.phone_number, "en")

        # Check response indicates player needs to opt in
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["not_opted_in"])

    def test_invalid_command_from_active_player(self, active_player):
        """Test handling invalid command from an active player."""
        response = handle_player_command(active_player.phone_number, "invalid command")

        # Check response provides guidance
        assert response["code"] == 200
        assert response["twiml"] == create_twiml_response(MESSAGES["how_to_play"])

    def test_command_error_handling(self, phone_number):
        """Test error handling in command processing."""
        with patch(
            "charades.game.models.Player.get_or_create_player"
        ) as mock_get_create:
            mock_get_create.side_effect = Exception("Database error")
            response = handle_player_command(phone_number, "langgang")

            assert response["code"] == 400
            expected_msg = create_twiml_response("Failed to opt in: Database error")
            assert response["twiml"] == expected_msg
