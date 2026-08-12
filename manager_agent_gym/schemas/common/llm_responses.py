"""
Common LLM response schemas.
"""

from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Any

from ...schemas.core.tasks import SubtaskData


class LLMScoreLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LLMScoredResponse(BaseModel):
    """Response structure for LLM numeric scoring."""

    reasoning: str = Field(
        ..., description="Explanation of the assessment and rationale for the score"
    )
    score: float | LLMScoreLevel | bool = Field(
        ..., description="Numeric score assigned by LLM"
    )

    @field_validator("score", mode="before")
    @classmethod
    def _coerce_score(cls, v: Any) -> Any:
        if isinstance(v, str):
            val_lower = v.strip().lower()
            if val_lower in {"true", "yes", "pass", "passed"}:
                return True
            if val_lower in {"false", "no", "fail", "failed"}:
                return False
            if val_lower in {"low", "medium", "high"}:
                return LLMScoreLevel(val_lower)
            # Try to convert to float/int if it's a numeric string
            try:
                if "." in v:
                    return float(val_lower)
                return int(val_lower)
            except ValueError:
                pass
        return v


class SubtaskResponse(BaseModel):
    """Response schema for LLM-generated subtasks."""

    reasoning: str = Field(..., description="Explanation of the decomposition approach")
    subtasks: list[SubtaskData] = Field(
        ..., description="List of structured subtask data"
    )
