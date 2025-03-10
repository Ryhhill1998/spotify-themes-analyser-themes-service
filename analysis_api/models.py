from typing import Annotated

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    track_id: str
    lyrics: str


EmotionPercentage = Annotated[float, Field(ge=0, le=1)]


class EmotionalAnalysis(BaseModel):
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


class EmotionalProfile(AnalysisRequest):
    emotional_analysis: EmotionalAnalysis
