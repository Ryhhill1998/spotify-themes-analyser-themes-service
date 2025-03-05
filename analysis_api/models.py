from typing import Annotated

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    id: str
    lyrics: str


EmotionPercentage = Annotated[float, Field(ge=0, le=1)]


class EmotionalProfile(BaseModel):
    joy: EmotionPercentage
    sadness: EmotionPercentage
    anger: EmotionPercentage
    fear: EmotionPercentage
    love: EmotionPercentage
    hope: EmotionPercentage
    nostalgia: EmotionPercentage
    loneliness: EmotionPercentage
    confidence: EmotionPercentage
    despair: EmotionPercentage
    excitement: EmotionPercentage
    mystery: EmotionPercentage
    defiance: EmotionPercentage
    gratitude: EmotionPercentage
    spirituality: EmotionPercentage


class AnalysisResponse(AnalysisRequest):
    emotional_profile: EmotionalProfile
