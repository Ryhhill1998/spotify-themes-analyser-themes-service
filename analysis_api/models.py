from typing import Annotated
from enum import Enum
from pydantic import BaseModel, Field


class AnalysisRequestBase(BaseModel):
    track_id: str
    lyrics: str
    

class EmotionalProfileRequest(AnalysisRequestBase):
    pass


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


class EmotionalProfileResponse(EmotionalProfileRequest):
    emotional_profile: EmotionalProfile


class Emotion(Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    LOVE = "love"
    HOPE = "hope"
    NOSTALGIA = "nostalgia"
    LONELINESS = "loneliness"
    CONFIDENCE = "confidence"
    DESPAIR = "despair"
    EXCITEMENT = "excitement"
    MYSTERY = "mystery"
    DEFIANCE = "defiance"
    GRATITUDE = "gratitude"
    SPIRITUALITY = "spirituality"


class EmotionalTagsRequest(AnalysisRequestBase):
    emotion: str


class EmotionalTagsResponse(EmotionalTagsRequest):
    pass
