from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class Player(models.Model):
    # Reverse relationship to GameSession
    gamesession_set: "models.Manager[GameSession]"

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Player's phone number in E.164 format",
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Whether the player has opted in to receive messages",
    )
    opted_in_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the player last opted in",
    )
    opted_out_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the player last opted out",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the player record was created",
    )

    def __str__(self) -> str:
        return self.phone_number

    def opt_in(self) -> None:
        """Opt the player in to receive messages."""
        self.is_active = True
        self.opted_in_at = timezone.now()
        self.opted_out_at = None
        self.save()

    def opt_out(self) -> None:
        """Opt the player out from receiving messages."""
        self.is_active = False
        self.opted_out_at = timezone.now()
        self.save()

    @classmethod
    def get_or_create_player(
        cls,
        phone_number: str,
    ) -> tuple["Player", bool]:
        """Get or create a player with the given phone number.

        Args:
            phone_number: The phone number in E.164 format

        Returns:
            tuple: (Player instance, bool indicating if player was created)
        """
        return cls.objects.get_or_create(phone_number=phone_number)

    def end_active_sessions(self) -> None:
        """End all active game sessions for this player."""
        self.gamesession_set.filter(status="active").update(
            status="timeout",
            completed_at=timezone.now(),
        )


class Word(models.Model):
    text = models.CharField(
        max_length=100,
        help_text="The word to be described",
    )
    language = models.CharField(
        max_length=2,
        help_text="ISO 639-1 language code (e.g., 'es' for Spanish)",
    )

    def __str__(self) -> str:
        return f"{self.text} ({self.language})"

    class Meta:
        unique_together = [
            "text",
            "language",
        ]


class GameSession(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("timeout", "Timeout"),
    ]

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        help_text="Player participating in this game session",
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.PROTECT,
        help_text="Word assigned for this game session",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current status of the game session",
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the game session started",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the game session was completed or timed out",
    )
    score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score from 0-100 based on AI evaluation",
    )

    def __str__(self) -> str:
        return f"{self.player} - {self.word} ({self.status})"

    def complete(
        self,
        score: int,
    ) -> None:
        """Mark the game session as completed with a score."""
        self.status = "completed"
        self.completed_at = timezone.now()
        self.score = score
        self.save()

    def timeout(self) -> None:
        """Mark the game session as timed out."""
        self.status = "timeout"
        self.completed_at = timezone.now()
        self.save()
