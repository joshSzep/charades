"""Data models for LLM responses."""

from pydantic import BaseModel
from pydantic import Field


class EvaluationResponse(BaseModel):
    """Model for evaluation responses from LLMs."""

    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Score from 0-100",
    )
    feedback: str = Field(
        ...,
        min_length=1,
        description="Feedback message in target language with English translation",
    )
